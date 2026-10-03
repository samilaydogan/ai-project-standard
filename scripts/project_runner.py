"""Small argv dispatcher and static execution-profile validator; no package resolver."""

from __future__ import annotations

import fnmatch
import ipaddress
import json
import os
import re
import shutil
import sys
import subprocess
from pathlib import Path

BASE = {"help", "doctor", "dev", "test", "lint"}
IDENTIFIER = re.compile(r"[a-z][a-z0-9-]*")


def local_file(root, name):
    path = Path(name)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != name or name == ".":
        raise ValueError(f"EXEC-ADOPTION: unsafe local path {name}")
    target = root
    for part in path.parts:
        target = target / part
        if target.is_symlink():
            raise ValueError(f"EXEC-ADOPTION: symlink {name}")
    if not target.is_file():
        raise ValueError(f"EXEC-ADOPTION: missing file {name}")
    return target



NA = "NOT APPLICABLE"
ENV_KEY = re.compile(r"[A-Z][A-Z0-9_]*")
SECRET_NAME = re.compile(r"(?:^|_)(?:SECRET|PASSWORD|TOKEN|CREDENTIAL|PRIVATE_KEY|API_KEY)$")
COMPOSE_TOOL_KEYS = frozenset({"PATH", "HOME", "LANG", "LC_CTYPE", "TMPDIR", "COMPOSE_DISABLE_ENV_FILE"})
COMPOSE_REFERENCE = re.compile(r"\$(?:\{([A-Za-z_][A-Za-z0-9_]*)[^}]*\}|([A-Za-z_][A-Za-z0-9_]*))")
COMPOSE_HOME_PATH = re.compile(r"~(?:[A-Za-z0-9_.-]+)?/")
STATIC_COMPOSE_ROOT = frozenset({"name", "services", "volumes"})
STATIC_COMPOSE_SERVICE = frozenset({"image", "ports", "environment", "healthcheck", "volumes",
                                    "x-foundation-role", "hostname", "read_only", "cap_drop",
                                    "security_opt", "restart"})
STATIC_COMPOSE_HEALTH = frozenset({"test", "interval", "timeout", "retries", "start_period"})


def strict_compose_json(source):
    """Parse JSON Compose without losing duplicate members or non-JSON constants."""
    # Python combines valid surrogate escape pairs into Unicode characters, while
    # Compose's YAML input parser rejects even those escaped forms. Literal UTF-8
    # characters remain supported; only source escape syntax is disallowed here.
    for match in re.finditer(r"(\\+)u([dD][89a-fA-F][0-9a-fA-F]{2})", source):
        if len(match.group(1)) % 2:
            raise ValueError("EXEC-RUNTIME: invalid JSON Compose Unicode escape")

    def unique_members(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise ValueError(f"EXEC-RUNTIME: duplicate JSON Compose member {key!r}")
            value[key] = item
        return value

    def invalid_constant(value):
        raise ValueError(f"EXEC-RUNTIME: invalid JSON Compose constant {value}")

    value = json.loads(source, object_pairs_hook=unique_members, parse_constant=invalid_constant)

    def valid_unicode(item):
        if isinstance(item, str):
            if any(0xd800 <= ord(char) <= 0xdfff for char in item):
                raise ValueError("EXEC-RUNTIME: invalid JSON Compose Unicode escape")
        elif isinstance(item, dict):
            for key, member in item.items():
                valid_unicode(key)
                valid_unicode(member)
        elif isinstance(item, list):
            for member in item:
                valid_unicode(member)

    valid_unicode(value)
    return value


class ComposeUnavailable(ValueError):
    """The required read-only Compose verifier cannot run in this environment."""


def compose_references(value):
    """Find real Compose substitutions; paired dollars escape a literal dollar."""
    if isinstance(value, dict):
        for key, item in value.items():
            yield from compose_references(key)
            yield from compose_references(item)
    elif isinstance(value, list):
        for item in value:
            yield from compose_references(item)
    elif isinstance(value, str):
        offset = 0
        while offset < len(value):
            if value[offset] != "$":
                offset += 1
                continue
            end = offset
            while end < len(value) and value[end] == "$":
                end += 1
            if (end - offset) % 2:
                match = COMPOSE_REFERENCE.match(value, end - 1)
                if match:
                    yield match.group(1) or match.group(2)
                    offset = match.end()
                    continue
            offset = end


def compose_source_values(value):
    """Walk source values before Compose can normalize machine-local paths."""
    if isinstance(value, dict):
        for item in value.values():
            yield from compose_source_values(item)
    elif isinstance(value, list):
        for item in value:
            yield from compose_source_values(item)
    else:
        yield value


def static_compose_eligible(value):
    """A small positive JSON subset with literal, always-active service topology.

    Unsupported Compose features use the effective CLI model, never a raw-source PASS.
    In particular, profiles, includes, inheritance and service dependencies are not
    represented here. The CLI's implicit default network is not a verified foundation
    fact; explicit network configuration therefore requires resolution.
    """
    def literal(item, *, allow_empty=False):
        if isinstance(item, str):
            return (bool(item) or allow_empty) and "$" not in item and not item.startswith(("./", "../")) \
                and item not in {".", ".."} and not COMPOSE_HOME_PATH.search(item)
        return False

    def strings(items):
        return isinstance(items, list) and all(literal(item) for item in items)

    if (not isinstance(value, dict) or not set(value) <= STATIC_COMPOSE_ROOT
            or not literal(value.get("name")) or not isinstance(value.get("services"), dict)
            or not value["services"]):
        return False
    volumes = value.get("volumes", {})
    if not isinstance(volumes, dict) or any(not literal(name) or definition != {}
                                            for name, definition in volumes.items()):
        return False
    for name, service in value["services"].items():
        if (not literal(name) or not isinstance(service, dict)
                or not set(service) <= STATIC_COMPOSE_SERVICE
                or not literal(service.get("image"))):
            return False
        if "ports" in service and not strings(service["ports"]):
            return False
        if "volumes" in service and not strings(service["volumes"]):
            return False
        if "environment" in service:
            environment = service["environment"]
            if (not isinstance(environment, dict)
                    or any(not literal(key) or not literal(item, allow_empty=True)
                           for key, item in environment.items())):
                return False
        if "healthcheck" in service:
            health = service["healthcheck"]
            if (not isinstance(health, dict) or not set(health) <= STATIC_COMPOSE_HEALTH
                    or not strings(health.get("test"))
                    or any(not literal(health[key]) for key in ("interval", "timeout", "start_period")
                           if key in health)
                    or ("retries" in health and (type(health["retries"]) is not int
                                                 or health["retries"] < 0))):
                return False
        if any(not literal(service[key]) for key in ("x-foundation-role", "hostname", "restart")
               if key in service):
            return False
        if "read_only" in service and type(service["read_only"]) is not bool:
            return False
        if any(not strings(service[key]) for key in ("cap_drop", "security_opt") if key in service):
            return False
    return True


def compose_needs_resolution(root, docker, source):
    """YAML and JSON outside the explicit static subset need the effective model."""
    path = local_file(root, docker["compose_file"])
    try:
        strict_compose_json(path.read_text())
    except json.JSONDecodeError as exc:
        if path.suffix.lower() == ".json":
            raise ValueError("EXEC-RUNTIME: invalid JSON Compose source") from exc
        return True
    return not static_compose_eligible(source)


def shape(value, keys, label):
    if not isinstance(value, dict) or set(value) != set(keys):
        raise ValueError(f"EXEC-RUNTIME: invalid {label} schema")


def declared_path(root, name, label):
    if not isinstance(name, str) or not name or "\0" in name:
        raise ValueError(f"EXEC-RUNTIME: invalid {label} path")
    path = Path(name)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != name or name == ".":
        raise ValueError(f"EXEC-RUNTIME: unsafe {label} path")
    target = root
    for part in path.parts:
        target /= part
        if target.is_symlink():
            raise ValueError(f"EXEC-RUNTIME: symlink {label}")
    return target


def env_contract(root, env):
    shape(env, {"env_example_path", "env_path", "required_env_keys", "optional_env_keys",
                "secret_env_keys"}, "environment")
    example = local_file(root, env["env_example_path"])
    declared_path(root, env["env_path"], "local env")
    if env["env_path"] == env["env_example_path"]:
        raise ValueError("SEC-ENV: local env and example must differ")
    groups = []
    for field in ("required_env_keys", "optional_env_keys", "secret_env_keys"):
        values = env[field]
        if (not isinstance(values, list) or not all(isinstance(v, str) and ENV_KEY.fullmatch(v)
                                                  for v in values) or len(values) != len(set(values))):
            raise ValueError(f"SEC-ENV: invalid {field}")
        groups.append(set(values))
    required, optional, secrets = groups
    if required & optional or not secrets <= required | optional:
        raise ValueError("SEC-ENV: overlapping/unclassified environment keys")
    values = {}
    for line in example.read_text().splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, sep, value = line.partition("=")
        if not sep or not ENV_KEY.fullmatch(key) or key in values:
            raise ValueError("SEC-ENV: example must use unique KEY=value lines")
        values[key] = value
    if set(values) != required | optional:
        raise ValueError("SEC-ENV: example inventory differs from declared keys")
    for key, value in values.items():
        if SECRET_NAME.search(key) and key not in secrets:
            raise ValueError(f"SEC-ENV: secret-like key must be classified {key}")
        if key in secrets and value:
            raise ValueError(f"SEC-ENV: secret example must be empty {key}")
        if "-----BEGIN" in value:
            raise ValueError(f"SEC-ENV: key material forbidden {key}")
    ignored = False
    for pattern in local_file(root, ".gitignore").read_text().splitlines():
        pattern = pattern.strip()
        if not pattern or pattern.startswith("#"):
            continue
        negate = pattern.startswith("!")
        pattern = pattern.lstrip("!").lstrip("/")
        if fnmatch.fnmatch(env["env_path"], pattern):
            ignored = not negate
    if not ignored:
        raise ValueError("SEC-ENV: local env must be gitignored")
    # Static Git query only; never creates .env, executes consumer commands or resolves dependencies.
    if shutil.which("git") and (root / ".git").exists():
        result = subprocess.run(["git", "-C", str(root), "ls-files", "--", env["env_path"]],
                                capture_output=True, text=True,
                                env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"}, check=False)
        if result.returncode or result.stdout.strip():
            raise ValueError("SEC-ENV: real local env may not be tracked")
    return values


def compose_source(root, docker):
    """Parse the actual Compose file; JSON remains usable without Docker installed."""
    path = local_file(root, docker["compose_file"])
    try:
        value = strict_compose_json(path.read_text())
    except json.JSONDecodeError as exc:
        if path.suffix.lower() == ".json":
            raise ValueError("EXEC-RUNTIME: invalid JSON Compose source") from exc
        value = compose_render(root, docker, no_interpolate=True)
    if not isinstance(value, dict) or not isinstance(value.get("services"), dict):
        raise ValueError("EXEC-RUNTIME: invalid Compose services")
    # The declared .env.example is the only environment-file input to static
    # verification. Compose's service env_file would read arbitrary local bytes.
    if any(isinstance(service, dict) and "env_file" in service
           for service in value["services"].values()):
        raise ValueError("SEC-ENV: Compose service env_file is not a verified input")
    if any(isinstance(item, str) and COMPOSE_HOME_PATH.search(item)
           for item in compose_source_values(value)):
        raise ValueError("SEC-ENV: HOME-relative Compose path is not a verified input")
    references = set(compose_references(value))
    if references & COMPOSE_TOOL_KEYS:
        raise ValueError("SEC-ENV: Compose tool environment is not interpolation authority")
    return value


def compose_render(root, docker, *, no_interpolate=False, override=None, env_values=None, secrets=()):
    """Read-only Compose rendering; never start services or disclose rendered secrets."""
    path = local_file(root, docker["compose_file"])
    # Isolate interpolation from caller overrides and private .env files. Declared
    # example values, then the single tested override, are the only inputs.
    environment = {key: os.environ[key] for key in ("PATH", "HOME", "LANG", "LC_CTYPE", "TMPDIR")
                   if key in os.environ}
    if env_values is not None:
        environment.update({key: value for key, value in env_values.items()
                            if key not in COMPOSE_TOOL_KEYS})
        for key in secrets:
            environment[key] = "compose-verification-only"
    if override is not None:
        if set(override) & COMPOSE_TOOL_KEYS:
            raise ValueError("SEC-ENV: Compose tool environment cannot be overridden")
        environment.update(override)
    # Consumer values must not re-enable private .env loading or redirect the
    # Compose project/file/profiles used for the evidence render.
    for key in tuple(environment):
        if key.startswith(("COMPOSE_", "DOCKER_")):
            environment.pop(key)
    environment["COMPOSE_DISABLE_ENV_FILE"] = "1"
    if not no_interpolate:
        # PATH/HOME and locale/temp variables are needed by the CLI on some
        # platforms, but are never implicit Compose interpolation authority.
        compose_source(root, docker)
    if shutil.which("docker", path=environment.get("PATH")) is None:
        raise ComposeUnavailable("EXEC-RUNTIME: Docker Compose verification unavailable")
    try:
        availability = subprocess.run(["docker", "compose", "version"], cwd=root, env=environment,
                                      capture_output=True, text=True, timeout=20, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ComposeUnavailable("EXEC-RUNTIME: Docker Compose verification unavailable") from exc
    if availability.returncode:
        raise ComposeUnavailable("EXEC-RUNTIME: Docker Compose verification unavailable")
    command = ["docker", "compose", "-f", str(path), "config", "--format", "json"]
    if no_interpolate:
        command.extend(["--no-interpolate", "--no-normalize", "--no-path-resolution"])
    try:
        result = subprocess.run(command, cwd=root, env=environment, capture_output=True,
                                text=True, timeout=20, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ComposeUnavailable("EXEC-RUNTIME: Docker Compose verification unavailable") from exc
    if result.returncode:
        raise ValueError("EXEC-RUNTIME: read-only Docker Compose rendering failed")
    if result.stderr.strip():
        # Compose may substitute an undefined variable with empty text, warn, and
        # still exit zero. Any diagnostic makes the effective proof non-accepting.
        raise ValueError("EXEC-RUNTIME: Docker Compose diagnostics prevent verification")
    try:
        value = json.loads(result.stdout)
    except ValueError as exc:
        raise ValueError("EXEC-RUNTIME: invalid Docker Compose JSON output") from exc
    if not isinstance(value, dict):
        raise ValueError("EXEC-RUNTIME: invalid Docker Compose output")
    return value


def rendered_ports(service):
    """Normalize Docker Compose's resolved long port records, rejecting ambiguity."""
    ports = service.get("ports", [])
    if not isinstance(ports, list):
        raise ValueError("EXEC-RUNTIME: invalid Compose ports")
    result = []
    for row in ports:
        if not isinstance(row, dict) or row.get("protocol", "tcp") != "tcp":
            raise ValueError("EXEC-RUNTIME: unsupported Compose port record")
        try:
            result.append((row.get("host_ip", ""), int(row["published"]), int(row["target"])))
        except (KeyError, ValueError, TypeError) as exc:
            raise ValueError("EXEC-RUNTIME: unresolved Compose port") from exc
    return result


def compose_contract(root, docker, network, env_values, secrets):
    compose = compose_source(root, docker)
    rendered = None
    if compose_needs_resolution(root, docker, compose):
        rendered = compose_render(root, docker, env_values=env_values, secrets=secrets)
    if (compose.get("name", rendered.get("name") if rendered else None)
            != docker["compose_project_name"]):
        raise ValueError("EXEC-RUNTIME: Compose project name mismatch")
    service = compose.get("services", {}).get(docker["primary_service"])
    if not isinstance(service, dict):
        raise ValueError("EXEC-RUNTIME: primary Compose service missing")
    if rendered is not None and not isinstance(rendered.get("services", {}).get(docker["primary_service"]), dict):
        raise ValueError("EXEC-RUNTIME: effective primary Compose service missing")
    def expand(text):
        if not isinstance(text, str):
            return text
        def replace(match):
            key, default = match.groups()
            if key not in env_values or env_values[key] != default:
                raise ValueError("EXEC-RUNTIME: Compose default/example mismatch")
            return default
        return re.sub(r"\$\{([A-Z][A-Z0-9_]*):-([^}]+)\}", replace, text)
    binding = f"{network['bind_host']}:{network['host_port']}:{network['container_port']}"
    if rendered is None:
        if binding not in [expand(v) for v in service.get("ports", [])]:
            raise ValueError("EXEC-RUNTIME: Compose host/container port mapping mismatch")
    else:
        actual = rendered.get("services", {}).get(docker["primary_service"], {})
        if (network["bind_host"], network["host_port"], network["container_port"]) not in rendered_ports(actual):
            raise ValueError("EXEC-RUNTIME: Compose host/container port mapping mismatch")
    health = service.get("healthcheck", {})
    if not isinstance(health, dict) or health.get("disable") or not isinstance(health.get("test"), list) or len(health["test"]) < 2 or health["test"][0] not in {"CMD", "CMD-SHELL"}:
        raise ValueError("EXEC-RUNTIME: Compose healthcheck required")
    if network["health_path"] == NA and health["test"] != ["CMD", *network["health_command"]]:
        raise ValueError("EXEC-RUNTIME: Compose health command mismatch")
    environment = service.get("environment", {})
    if not isinstance(environment, dict):
        raise ValueError("SEC-ENV: static Compose environment must be a mapping")
    health_text = " ".join(str(v) for v in health["test"])
    if network["health_path"] != NA and network["health_path"] not in health_text:
        if "APP_HEALTH_PATH" not in health_text or expand(environment.get("APP_HEALTH_PATH")) != network["health_path"]:
            raise ValueError("EXEC-RUNTIME: Compose health path binding mismatch")
    for key, value in environment.items():
        if key in secrets or SECRET_NAME.search(key):
            if value and not (isinstance(value, str) and re.fullmatch(r"\$\{[A-Z][A-Z0-9_]*(?::\?[^}]*)?\}", value)):
                raise ValueError(f"SEC-ENV: literal Compose secret forbidden {key}")
    for key, expected in (("APP_CONTAINER_LISTEN_HOST", network["container_listen_host"]),
                          ("APP_CONTAINER_PORT", str(network["container_port"])),
                          ("APP_HEALTH_PATH", network["health_path"])):
        if key in environment and expand(environment[key]) != expected:
            raise ValueError(f"EXEC-RUNTIME: Compose network environment mismatch {key}")
    if rendered is not None:
        actual = rendered["services"][docker["primary_service"]]
        actual_health = actual.get("healthcheck", {})
        if (not isinstance(actual_health, dict) or actual_health.get("disable")
                or not isinstance(actual_health.get("test"), list)
                or len(actual_health["test"]) < 2):
            raise ValueError("EXEC-RUNTIME: effective Compose healthcheck missing")
        actual_environment = actual.get("environment", {})
        if not isinstance(actual_environment, dict):
            raise ValueError("EXEC-RUNTIME: effective Compose environment missing")
        for key, expected in (("APP_CONTAINER_LISTEN_HOST", network["container_listen_host"]),
                              ("APP_CONTAINER_PORT", str(network["container_port"])),
                              ("APP_HEALTH_PATH", network["health_path"])):
            if key in environment and actual_environment.get(key) != expected:
                raise ValueError(f"EXEC-RUNTIME: effective Compose environment mismatch {key}")
        if network["health_path"] != NA:
            actual_health_text = " ".join(str(value) for value in actual_health["test"])
            if (network["health_path"] not in actual_health_text
                    and ("APP_HEALTH_PATH" not in actual_health_text
                         or actual_environment.get("APP_HEALTH_PATH") != network["health_path"])):
                raise ValueError("EXEC-RUNTIME: effective Compose health path mismatch")


def runtime_contract(root, config):
    runtime = config["runtime"]
    shape(runtime, {"runtime_mode", "execution_facade", "delivery_modes", "package_apply",
                    "environment", "network", "docker", "native", "storage"}, "runtime")
    mode = runtime["runtime_mode"]
    if mode not in {"docker", "native", "hybrid"} or runtime["execution_facade"] != "run.sh":
        raise ValueError("EXEC-RUNTIME: invalid runtime_mode/execution_facade")
    modes = runtime["delivery_modes"]
    if not isinstance(modes, list) or not modes or len(modes) != len(set(modes)) or not set(modes) <= {"A", "B"}:
        raise ValueError("EXEC-DELIVERY: delivery_modes must declare A, B or both")
    package = runtime["package_apply"]
    shape(package, {"status", "entrypoint", "state_root"}, "package_apply")
    if "B" not in modes:
        if any(v != NA for v in package.values()):
            raise ValueError("EXEC-DELIVERY: Mode A-only package family must be NOT APPLICABLE")
        if config["commands"].get("apply-package", {}).get("status") == "READY":
            raise ValueError("EXEC-DELIVERY: Mode A-only cannot enable apply-package")
    else:
        if package["status"] not in {"READY", "NOT CONFIGURED"}:
            raise ValueError("EXEC-DELIVERY: Mode B requires explicit apply applicability")
        if not isinstance(package["entrypoint"], str) or Path(package["entrypoint"]).name != "apply_package.sh":
            raise ValueError("EXEC-DELIVERY: bootstrap role is apply_package.sh")
        state = package["state_root"]
        if not isinstance(state, str) or not state or "\0" in state or state == NA:
            raise ValueError("REL-APPLY-STATE: external state root required")
        if "$" in state or "\\" in state:
            raise ValueError("REL-APPLY-STATE: shell substitutions/escaped roots unsupported")
        state_path = Path(state).expanduser()
        if not state_path.is_absolute():
            state_path = root / state_path
        resolved = state_path.resolve()
        source = root.resolve()
        if resolved.is_relative_to(source) or source.is_relative_to(resolved):
            raise ValueError("REL-APPLY-STATE: state root must be outside and not contain source")
        if package["status"] == "READY":
            entry = Path(package["entrypoint"]).expanduser()
            if not entry.is_absolute():
                entry = declared_path(root, package["entrypoint"], "bootstrap")
            if not entry.is_file() or entry.is_symlink() or not entry.stat().st_mode & 0o111:
                raise ValueError("EXEC-DELIVERY: READY bootstrap must exist and be executable")
        elif package["entrypoint"] != "apply_package.sh":
            raise ValueError("EXEC-DELIVERY: unconfigured bootstrap uses declared generic role")
    values = env_contract(root, runtime["environment"])
    network = runtime["network"]
    shape(network, {"bind_host", "host_port", "container_listen_host", "container_port",
                    "health_path", "health_command"}, "network")
    def host(value):
        try:
            ipaddress.IPv4Address(value)
        except (ValueError, TypeError):
            raise ValueError("EXEC-RUNTIME: bind/listen host must be an explicit IP address") from None
    def port(value):
        if type(value) is not int or not 1 <= value <= 65535:
            raise ValueError("EXEC-RUNTIME: declared port must be 1..65535")
    host(network["bind_host"])
    port(network["host_port"])
    health = network["health_path"]
    command = network["health_command"]
    if health == NA:
        if not isinstance(command, list) or not command or not all(isinstance(v, str) and v for v in command):
            raise ValueError("EXEC-RUNTIME: health path or health command required")
        for arg in command:
            if arg.startswith("./"):
                local_file(root, arg[2:])
    elif (not isinstance(health, str) or not health.startswith("/") or any(c in health for c in " ?#\n\r")
          or command != NA):
        raise ValueError("EXEC-RUNTIME: invalid health path/command")
    docker, native = runtime["docker"], runtime["native"]
    shape(docker, {"status", "compose_file", "compose_project_name", "primary_service", "dev_command"}, "docker")
    shape(native, {"status", "dev_command"}, "native")
    for family, applies in ((docker, mode in {"docker", "hybrid"}), (native, mode in {"native", "hybrid"})):
        if not applies:
            if any(v != NA for v in family.values()):
                raise ValueError("EXEC-RUNTIME: inapplicable runtime family must be NOT APPLICABLE")
        else:
            mapped = config["commands"].get(family["dev_command"], {})
            if (family["status"] != "READY" or mapped.get("status") != "READY"
                    or mapped.get("mutability") != "mutating" or not mapped.get("argv")):
                raise ValueError("EXEC-RUNTIME: alternative runnable dev contract required")
    if mode in {"docker", "hybrid"}:
        local_file(root, docker["compose_file"])
        for key in ("compose_project_name", "primary_service"):
            if not isinstance(docker[key], str) or not re.fullmatch(r"[a-z][a-z0-9_-]*", docker[key]):
                raise ValueError(f"EXEC-RUNTIME: invalid {key}")
        host(network["container_listen_host"])
        port(network["container_port"])
        compose_contract(root, docker, network, values, runtime["environment"]["secret_env_keys"])
    elif network["container_listen_host"] != NA or network["container_port"] != NA:
        raise ValueError("EXEC-RUNTIME: native container fields must be NOT APPLICABLE")
    storage = runtime["storage"]
    shape(storage, {"status", "data_roots", "volume_roots", "artifact_root"}, "storage")
    for key in ("data_roots", "volume_roots"):
        if not isinstance(storage[key], list) or not all(isinstance(v, str) and v for v in storage[key]):
            raise ValueError(f"EXEC-RUNTIME: invalid {key}")
    if storage["status"] == NA:
        if storage["data_roots"] or storage["volume_roots"]:
            raise ValueError("EXEC-RUNTIME: inapplicable storage cannot declare data/volumes")
    elif storage["status"] != "READY" or not (storage["data_roots"] or storage["volume_roots"]):
        raise ValueError("EXEC-RUNTIME: storage roots required")
    artifact = storage["artifact_root"]
    if not isinstance(artifact, str) or not artifact or artifact == NA:
        raise ValueError("REL-APPLY-STATE: external artifact root required")
    if "$" in artifact or "\\" in artifact:
        raise ValueError("REL-APPLY-STATE: shell substitutions/escaped roots unsupported")
    artifact_path = Path(artifact).expanduser()
    if not artifact_path.is_absolute():
        artifact_path = root / artifact_path
    if artifact_path.resolve().is_relative_to(root.resolve()) or root.resolve().is_relative_to(artifact_path.resolve()):
        raise ValueError("REL-APPLY-STATE: artifacts must be outside and not contain source")
    return values


def load(root, profile_name="execution-profile.json"):
    def unique(pairs):
        obj = {}
        for key, value in pairs:
            if key in obj:
                raise ValueError(f"EXEC-ADOPTION: duplicate key {key}")
            obj[key] = value
        return obj

    config = json.loads(
        local_file(root, profile_name).read_text(), object_pairs_hook=unique
    )
    if (
        not isinstance(config, dict)
        or set(config)
        != {"schema_version", "facade", "default", "commands", "compatibility_launchers", "runtime", "foundation"}
        or config["schema_version"] != 3
        or config["facade"] != "run.sh"
    ):
        raise ValueError("EXEC-ADOPTION: invalid profile schema/facade")
    if not local_file(root, "run.sh").stat().st_mode & 0o111:
        raise ValueError("EXEC-ADOPTION: facade not executable")
    commands = config["commands"]
    if (
        not isinstance(commands, dict)
        or not commands.keys() >= BASE
        or config["default"] not in commands
    ):
        raise ValueError("EXEC-ADOPTION: missing baseline/default command")
    for name, row in commands.items():
        if (
            not IDENTIFIER.fullmatch(name)
            or not isinstance(row, dict)
            or set(row) != {"status", "mutability", "argv", "prerequisites"}
        ):
            raise ValueError(f"EXEC-ADOPTION: invalid command {name}")
        if row["status"] not in {"READY", "NOT CONFIGURED", "NOT APPLICABLE"} or row[
            "mutability"
        ] not in {"read-only", "mutating"}:
            raise ValueError(f"EXEC-ADOPTION: invalid classification {name}")
        argv = row["argv"]
        if not isinstance(argv, list) or not all(
            isinstance(v, str) and v and "\0" not in v for v in argv
        ):
            raise ValueError(f"EXEC-ADOPTION: invalid argv {name}")
        if name == "test" and row["status"] != "READY":
            raise ValueError("EXEC-ADOPTION: test requires configured base validation")
        if name in {"help", "doctor"}:
            if argv or row["status"] != "READY" or row["mutability"] != "read-only":
                raise ValueError(f"EXEC-READONLY: reserved command {name}")
        elif (row["status"] == "READY") != bool(argv):
            raise ValueError(f"EXEC-ADOPTION: availability/argv mismatch {name}")
        if (
            name in {"apply-package", "migrate", "dev", "start", "restart", "stop", "down", "up"}
            and row["mutability"] != "mutating"
        ):
            raise ValueError(f"EXEC-MUTATION: {name} must be mutating")
        if name in {"status", "health", "logs", "example-logs"} and row["mutability"] != "read-only":
            raise ValueError(f"EXEC-READONLY: {name} must be read-only")
        if not isinstance(row["prerequisites"], list):
            raise ValueError(f"EXEC-ADOPTION: prerequisites {name}")
        for req in row["prerequisites"]:
            if (
                not isinstance(req, dict)
                or set(req) != {"kind", "value"}
                or req["kind"] not in {"file", "executable"}
                or not isinstance(req["value"], str)
                or not req["value"]
            ):
                raise ValueError(f"EXEC-ADOPTION: prerequisite schema {name}")
            if req["kind"] == "file":
                path = Path(req["value"])
                if path.is_absolute() or ".." in path.parts:
                    raise ValueError(f"EXEC-ADOPTION: unsafe prerequisite path {name}")
        for index, arg in enumerate(argv):
            if arg.startswith("./"):
                target = local_file(root, arg[2:])
                if index == 0 and not target.stat().st_mode & 0o111:
                    raise ValueError(f"EXEC-ADOPTION: mapped command not executable {name}")
    launchers = config["compatibility_launchers"]
    if not isinstance(launchers, list):
        raise ValueError("EXEC-ADOPTION: compatibility inventory")
    seen = set()
    for row in launchers:
        if (
            not isinstance(row, dict)
            or set(row) != {"path", "removal_boundary"}
            or not isinstance(row["removal_boundary"], str)
            or not row["removal_boundary"].strip()
            or row["path"] in seen
        ):
            raise ValueError("EXEC-ADOPTION: compatibility schema/duplicate")
        seen.add(row["path"])
        if not local_file(root, row["path"]).stat().st_mode & 0o111:
            raise ValueError("EXEC-ADOPTION: compatibility launcher not executable")
    runtime_contract(root, config)
    from foundation_contract import validate
    validate(root, config)
    return config


def main():
    root = Path(__file__).resolve().parents[1]
    args = sys.argv[1:]
    requested = args[0] if args else None
    try:
        config = load(root)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"PENDING: {exc}")
        if requested in {"help", "-h", "--help"}:
            print("Commands: help doctor dev test lint; configuration PENDING")
            return 0
        return 3
    command = requested or config["default"]
    if command in {"-h", "--help"}:
        command = "help"
    if command == "help":
        for name, row in config["commands"].items():
            print(f"{name}: {row['status']}; {row['mutability']}")
        return 0
    if command not in config["commands"]:
        print(f"Unknown command: {command}; use ./run.sh help", file=sys.stderr)
        return 2
    if command == "doctor":
        failures = []
        if sys.version_info < (3, 11):  # noqa: UP036 -- doctor diagnoses older interpreters
            failures.append("Python >=3.11 required")
        for name, row in config["commands"].items():
            if name not in {"help", "doctor"} and row["status"] == "READY" and not shutil.which(str(root / row["argv"][0]) if row["argv"][0].startswith("./") else row["argv"][0]):
                failures.append(f"{name}: missing executable {row['argv'][0]}")
            if row["status"] != "READY":
                print(f"{name}: {row['status']}")
                continue
            for req in row["prerequisites"]:
                try:
                    ok = (
                        bool(shutil.which(req["value"]))
                        if req["kind"] == "executable"
                        else (root / req["value"]).is_file()
                    )
                except (OSError, ValueError):
                    ok = False
                if not ok:
                    failures.append(f"{name}: missing {req['kind']} {req['value']}")
        from foundation_contract import validate
        failures.extend(validate(root, config))
        environment = config["runtime"]["environment"]
        available = {}
        local_env = root / environment["env_path"]
        if local_env.is_file():
            for line in local_env.read_text().splitlines():
                if line.strip() and not line.lstrip().startswith("#"):
                    key, sep, value = line.partition("=")
                    if not sep:
                        failures.append("malformed runtime-local env; expected KEY=value")
                    else:
                        available[key] = value
        available.update(os.environ)
        for key in environment["required_env_keys"]:
            if not available.get(key):
                failures.append(f"missing required environment key {key}")
        package = config["runtime"]["package_apply"]
        if package["status"] == "NOT CONFIGURED":
            failures.append("Mode B bootstrap NOT CONFIGURED; no package acceptance")
        for failure in failures:
            print(f"PENDING: {failure}")
        print(
            "BASELINE CHECKS PASS"
            if not failures
            else "doctor PENDING; prepare declared prerequisites explicitly"
        )
        return 3 if failures else 0
    row = config["commands"][command]
    if row["status"] != "READY":
        print(
            f"{command}: {row['status']}; "
            "configure in execution-profile.json and PROJECT_PROFILE.md"
        )
        return 3
    os.chdir(root)
    argv = row["argv"] + args[1:]
    try:
        os.execvpe(argv[0], argv, os.environ)
    except OSError as exc:
        print(
            f"PENDING: {command}: {exc}; prepare declared prerequisites explicitly", file=sys.stderr
        )
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
