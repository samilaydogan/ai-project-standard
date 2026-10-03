"""Isolated negative contracts; no Docker/package execution or dependency resolution."""

import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import project_runner


def compose_available():
    return bool(shutil.which('docker')) and subprocess.run(
        ['docker', 'compose', 'version'], capture_output=True, timeout=5, check=False).returncode == 0


class RuntimeContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "source"
        self.root.mkdir()
        self.source = Path(__file__).resolve().parents[1]
        for name in ('.dockerignore', 'pyproject.toml', 'source-exclusions.json', 'scripts/foundation_contract.py', 'scripts/reference_tests.py',
            'scripts/test_controls.py',
            'scripts/release_commit.py',
            'scripts/release_preview.py',
            'scripts/preview_health.py',
            'release-preview-profile.json',
            'release-commit-profile.json',
            'test-control-profile.json', 'scripts/test_network_guard.py', 'scripts/scaffold_status.py', 'INSTALLATION.md', 'MIGRATION_RECOVERY.md', 'OPERATIONS_RUNBOOK.md', 'THIRD_PARTY_LICENSE_INVENTORY.md', "run.sh", ".env.example", ".gitignore", "execution-profile.json",
                     "compose.yaml", "scripts/project_runner.py", "scripts/health_scaffold.py",
                     "scripts/scaffold_lint.py"):
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(self.source / name, target)
        self.base = json.loads((self.root / "execution-profile.json").read_text())
        self.profile = copy.deepcopy(self.base)

    def save(self):
        (self.root / "execution-profile.json").write_text(json.dumps(self.profile))

    def load(self):
        self.save()
        return project_runner.load(self.root)

    def reject(self, message):
        with self.assertRaisesRegex(ValueError, message):
            self.load()

    def mode_b(self):
        self.profile["runtime"]["delivery_modes"] = ["B"]
        self.profile["runtime"]["package_apply"] = {
            "status": "NOT CONFIGURED", "entrypoint": "apply_package.sh", "state_root": "../apply-state"
        }

    def docker(self):
        self.profile = json.loads((self.source / "execution-profile.docker.json").read_text())

    def static_docker_json(self):
        self.docker()
        compose = json.loads((self.root / "compose.yaml").read_text())
        service = compose["services"]["scaffold"]
        service.pop("build")
        service["image"] = "python:3.11-slim"
        service["ports"] = ["127.0.0.1:8080:8080"]
        service["environment"] = {
            "APP_CONTAINER_LISTEN_HOST": "0.0.0.0", "APP_CONTAINER_PORT": "8080",
            "APP_HEALTH_PATH": "/health",
        }
        return json.dumps(compose, separators=(",", ":"))

    def test_native_day_zero_explicit_and_no_env_required(self):
        self.assertEqual(self.load()["runtime"]["docker"]["status"], "NOT APPLICABLE")
        self.assertFalse((self.root / ".env").exists())

    def test_invalid_or_missing_runtime_mode(self):
        for value in ("automatic", "", None):
            with self.subTest(value=value):
                self.profile["runtime"]["runtime_mode"] = value
                self.reject("runtime_mode")

    def test_unavailable_native_is_not_runnable(self):
        self.profile["commands"]["dev"].update(status="NOT CONFIGURED", argv=[])
        self.reject("runnable dev")
        self.profile = copy.deepcopy(self.base)
        self.profile["runtime"]["native"]["dev_command"] = "help"
        self.reject("runnable dev")

    def test_native_cannot_silently_enable_container(self):
        self.profile["runtime"]["network"]["container_port"] = 8080
        self.reject("native container")

    def test_delivery_modes_coherent(self):
        for modes in ([], ["C"], ["A", "A"]):
            with self.subTest(modes=modes):
                self.profile["runtime"]["delivery_modes"] = modes
                self.reject("delivery_modes")

    def test_mode_a_cannot_hide_apply(self):
        self.profile["runtime"]["package_apply"]["state_root"] = "../apply-state"
        self.reject("A-only")

    def test_mode_a_cannot_enable_facade_apply(self):
        self.profile["commands"]["apply-package"] = {
            "status": "READY", "mutability": "mutating",
            "argv": ["python3", "-c", "raise SystemExit(9)"], "prerequisites": []
        }
        self.reject("A-only cannot enable")

    def test_hybrid_requires_two_runnable_families(self):
        self.docker()
        self.profile["commands"]["docker-dev"] = self.profile["commands"]["dev"]
        self.profile["commands"]["dev"] = self.base["commands"]["dev"]
        self.profile["runtime"]["runtime_mode"] = "hybrid"
        self.profile["runtime"]["docker"]["dev_command"] = "docker-dev"
        self.profile["runtime"]["native"] = {"status": "READY", "dev_command": "dev"}
        self.load()
        self.profile["runtime"]["native"]["status"] = "NOT APPLICABLE"
        self.reject("runnable dev")

    def test_mode_b_declared_pending_without_fake_applier(self):
        self.mode_b()
        self.load()
        result = subprocess.run([str(self.root / "run.sh"), "doctor"], text=True, capture_output=True)
        self.assertEqual(result.returncode, 3)
        self.assertIn("bootstrap NOT CONFIGURED", result.stdout)
        self.assertFalse((self.root.parent / "apply-state").exists())

    def test_ready_bootstrap_requires_real_executable(self):
        self.mode_b()
        self.profile["runtime"]["package_apply"]["status"] = "READY"
        self.reject("bootstrap must exist")
        (self.root / "apply_package.sh").write_text("#!/bin/sh\nexit 9\n")
        self.reject("bootstrap must exist")
        (self.root / "apply_package.sh").chmod(0o755)
        self.load()  # Static validation does not execute this failing synthetic bootstrap.

    def test_internal_ancestor_and_substitution_state_roots_rejected(self):
        self.mode_b()
        for path in (".", "state", str(self.root), str(self.root.parent), "$HOME/state"):
            with self.subTest(path=path):
                self.profile["runtime"]["package_apply"]["state_root"] = path
                self.reject("REL-APPLY-STATE")

    def test_symlink_into_source_is_not_external_state(self):
        self.mode_b()
        (self.root.parent / "outside").symlink_to(self.root, target_is_directory=True)
        self.profile["runtime"]["package_apply"]["state_root"] = "../outside/state"
        self.reject("outside")

    def test_internal_artifacts_rejected(self):
        self.profile["runtime"]["storage"]["artifact_root"] = "build/artifacts"
        self.reject("artifacts must be outside")

    def test_secret_examples_rejected_without_disclosing_values(self):
        environment = self.profile["runtime"]["environment"]
        environment["optional_env_keys"].append("APP_SECRET")
        environment["secret_env_keys"].append("APP_SECRET")
        path = self.root / ".env.example"
        path.write_text(path.read_text() + "APP_SECRET=synthetic-forbidden-value\n")
        with self.assertRaisesRegex(ValueError, "secret example must be empty") as ctx:
            self.load()
        self.assertNotIn("synthetic-forbidden-value", str(ctx.exception))

    def test_empty_secret_contract_and_required_runtime_pending(self):
        environment = self.profile["runtime"]["environment"]
        environment["required_env_keys"].append("APP_SECRET")
        environment["secret_env_keys"].append("APP_SECRET")
        path = self.root / ".env.example"
        path.write_text(path.read_text() + "APP_SECRET=\n")
        self.load()
        env = dict(os.environ)
        env.pop("APP_SECRET", None)
        result = subprocess.run([str(self.root / "run.sh"), "doctor"], env=env, text=True, capture_output=True)
        self.assertEqual(result.returncode, 3)
        self.assertIn("missing required environment key APP_SECRET", result.stdout)
        (self.root / ".env").write_text("APP_SECRET=synthetic-runtime-only\n")
        result = subprocess.run([str(self.root / "run.sh"), "doctor"], env=env, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("synthetic-runtime-only", result.stdout)

    def test_example_inventory_and_secret_classification(self):
        path = self.root / ".env.example"
        path.write_text(path.read_text() + "APP_TOKEN_TTL_SECONDS=3600\n")
        self.profile["runtime"]["environment"]["optional_env_keys"].append("APP_TOKEN_TTL_SECONDS")
        self.load()  # Token lifetime is configuration, not the token secret.
        path.write_text(path.read_text() + "APP_TOKEN=\n")
        self.reject("example inventory")
        self.profile["runtime"]["environment"]["optional_env_keys"].append("APP_TOKEN")
        self.reject("must be classified")

    def test_env_must_be_ignored_and_distinct(self):
        (self.root / ".gitignore").write_text("# no env protection\n")
        self.reject("must be gitignored")
        shutil.copy2(self.source / ".gitignore", self.root / ".gitignore")
        self.profile["runtime"]["environment"]["env_path"] = ".env.example"
        self.reject("must differ")

    def test_tracked_env_rejected_without_reading_secret(self):
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        (self.root / ".env").write_text("synthetic-local-secret\n")
        subprocess.run(["git", "-C", str(self.root), "add", "-f", ".env"], check=True)
        self.reject("may not be tracked")

    def test_ports_and_health_must_be_explicit(self):
        for value in (0, 65536, True, "8080"):
            with self.subTest(value=value):
                self.profile["runtime"]["network"]["host_port"] = value
                self.reject("port must")
        self.profile = copy.deepcopy(self.base)
        self.profile["runtime"]["network"]["health_path"] = "NOT APPLICABLE"
        self.reject("health path or health command")

    def test_docker_reference_static_contract(self):
        self.docker()
        compose_path = self.root / "compose.yaml"
        compose = json.loads(compose_path.read_text())
        service = compose["services"]["scaffold"]
        service.pop("build")
        service["image"] = "python:3.11-slim"
        service["ports"] = ["127.0.0.1:8080:8080"]
        service["environment"] = {
            "APP_CONTAINER_LISTEN_HOST": "0.0.0.0", "APP_CONTAINER_PORT": "8080",
            "APP_HEALTH_PATH": "/health",
        }
        compose_path.write_text(json.dumps(compose))
        self.save()
        # A fake docker command would leave a sentinel if the validator invoked it.
        fake = self.root / "docker"
        fake.write_text("#!/bin/sh\ntouch validator-ran-docker\nexit 9\n")
        fake.chmod(0o755)
        after = {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in self.root.rglob('*') if p.is_file()}
        with patch.dict(os.environ, {"PATH": str(self.root) + os.pathsep + os.environ["PATH"]}):
            project_runner.load(self.root)
        self.assertEqual(after, {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in self.root.rglob('*') if p.is_file()})
        self.assertFalse((self.root / "validator-ran-docker").exists())

    def test_duplicate_json_members_fail_before_static_verification(self):
        safe = self.static_docker_json()
        path = self.root / "compose.yaml"
        path.write_text(safe)
        self.load()
        cases = {
            "service name": safe.replace('"scaffold":{',
                                         '"scaffold":{"profiles":["optional"]},"scaffold":{', 1),
            "root services": safe.replace('"services":{', '"services":{},"services":{', 1),
            "service image": safe.replace('"image":"python:3.11-slim"',
                                           '"image":"alpine","image":"python:3.11-slim"', 1),
            "environment": safe.replace('"APP_CONTAINER_PORT":"8080"',
                                        '"APP_CONTAINER_PORT":"9999","APP_CONTAINER_PORT":"8080"', 1),
            "healthcheck": safe.replace('"healthcheck":{',
                                        '"healthcheck":{"test":["CMD","false"],', 1),
            "top-level volume": safe.replace('"services":{',
                                             '"volumes":{"data":{},"data":{}},"services":{', 1),
            "long port": safe.replace('"ports":["127.0.0.1:8080:8080"]',
                                      '"ports":[{"target":9999,"target":8080}]', 1),
            "long volume": safe.replace('"services":{',
                                        '"volumes":{"data":{}},"services":{', 1).replace(
                                            '"image":"python:3.11-slim"',
                                            '"image":"python:3.11-slim","volumes":[{"target":"/a","target":"/b"}]', 1),
        }
        for name, source in cases.items():
            with self.subTest(name=name):
                path.write_text(source)
                with patch.object(project_runner, "compose_render", side_effect=AssertionError(
                        "duplicate JSON must not fall back to Compose")):
                    self.reject("duplicate JSON Compose member")

    def test_nonstandard_json_constants_rejected_at_any_depth(self):
        for value in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(value=value):
                source = '{"name":"project-scaffold","services":{"scaffold":' \
                         '{"image":"alpine","environment":{"X":' + value + '}}}}'
                with self.assertRaisesRegex(ValueError, "invalid JSON Compose constant"):
                    project_runner.strict_compose_json(source)

    def test_surrogate_escapes_cannot_static_pass_when_compose_rejects_them(self):
        safe = json.loads(self.static_docker_json())
        path = self.root / "compose.yaml"
        for value in ("\ud800", "\udc00", "😀"):
            with self.subTest(value=repr(value)):
                changed = copy.deepcopy(safe)
                changed["services"]["scaffold"]["environment"]["UNICODE"] = value
                path.write_text(json.dumps(changed))
                self.reject("invalid JSON Compose Unicode escape")
        literal = json.dumps({"X": r"\ud800"})
        self.assertEqual(project_runner.strict_compose_json(literal)["X"], r"\ud800")
        changed = copy.deepcopy(safe)
        changed["services"]["scaffold"]["environment"]["UNICODE"] = "😀"
        path.write_text(json.dumps(changed, ensure_ascii=False))
        self.load()

    def test_invalid_json_file_syntax_does_not_fall_back_to_yaml(self):
        safe = self.static_docker_json()
        self.profile["runtime"]["docker"]["compose_file"] = "compose.json"
        path = self.root / "compose.json"
        for name, source in {
            "trailing comma": safe[:-1] + ",}",
            "comment": safe + " # comment",
            "invalid escape": safe.replace("python:3.11-slim", "python:\\q"),
        }.items():
            with self.subTest(name=name):
                path.write_text(source)
                self.reject("invalid JSON Compose source")

    def test_invalid_json_top_level_is_not_a_compose_project(self):
        self.static_docker_json()
        path = self.root / "compose.yaml"
        for source in ("[]", "null", '"text"', "42"):
            with self.subTest(source=source):
                path.write_text(source)
                self.reject("invalid Compose services")

    def test_yaml_only_syntax_cannot_take_static_json_path(self):
        safe = self.static_docker_json()
        path = self.root / "compose.yaml"
        for source in (safe[:-1] + ",}", safe + " # YAML comment"):
            with self.subTest(source=source[-20:]):
                path.write_text(source)
                with patch.object(project_runner.shutil, "which", return_value=None):
                    with self.assertRaises(project_runner.ComposeUnavailable):
                        self.load()

    @unittest.skipUnless(compose_available(), "Docker Compose CLI unavailable")
    def test_duplicate_yaml_mapping_and_json_member_both_fail(self):
        self.static_docker_json()
        (self.root / "compose.yaml").write_text('''name: project-scaffold
services:
  scaffold:
    image: alpine
  scaffold:
    image: alpine
''')
        self.reject("rendering failed")

    def test_static_compose_subset_is_positive_and_excludes_effective_features(self):
        self.docker()
        compose = json.loads((self.root / "compose.yaml").read_text())
        service = compose["services"]["scaffold"]
        service.pop("build")
        service["image"] = "python:3.11-slim"
        service["ports"] = ["127.0.0.1:8080:8080"]
        service["environment"] = {"APP_CONTAINER_LISTEN_HOST": "0.0.0.0",
                                  "APP_CONTAINER_PORT": "8080", "APP_HEALTH_PATH": "/health"}
        self.assertTrue(project_runner.static_compose_eligible(compose))
        for location, key, value in (("service", "profiles", ["optional"]),
                                     ("service", "depends_on", ["other"]),
                                     ("service", "command", ["serve"]),
                                     ("service", "networks", ["custom"]),
                                     ("service", "ports", [{"published": 8080, "target": 8080}]),
                                     ("root", "include", ["other.yaml"]),
                                     ("root", "x-extension", {"value": "literal"})):
            with self.subTest(key=key):
                changed = copy.deepcopy(compose)
                target = changed if location == "root" else changed["services"]["scaffold"]
                target[key] = value
                self.assertFalse(project_runner.static_compose_eligible(changed))

    @unittest.skipUnless(compose_available(), "Docker Compose CLI unavailable")
    def test_profiled_primary_is_absent_in_effective_json_and_yaml(self):
        self.docker()
        source = json.loads((self.root / "compose.yaml").read_text())
        service = source["services"]["scaffold"]
        service.pop("build")
        service["image"] = "python:3.11-slim"
        service["profiles"] = ["optional"]
        for data in (json.dumps(source), '''name: project-scaffold
services:
  scaffold:
    image: python:3.11-slim
    profiles: [optional]
    ports: ["${APP_BIND_HOST:-127.0.0.1}:${APP_HOST_PORT:-8080}:${APP_CONTAINER_PORT:-8080}"]
    environment:
      APP_CONTAINER_LISTEN_HOST: "${APP_CONTAINER_LISTEN_HOST:-0.0.0.0}"
      APP_CONTAINER_PORT: "${APP_CONTAINER_PORT:-8080}"
      APP_HEALTH_PATH: "${APP_HEALTH_PATH:-/health}"
    healthcheck:
      test: ["CMD", "python3", "/health"]
'''):
            with self.subTest(serialization=data[:1]):
                (self.root / "compose.yaml").write_text(data)
                with patch.dict(os.environ, {"COMPOSE_PROFILES": "optional"}):
                    self.reject("effective primary Compose service missing")

    def test_profiled_json_without_compose_is_pending(self):
        self.docker()
        source = json.loads((self.root / "compose.yaml").read_text())
        service = source["services"]["scaffold"]
        service.pop("build")
        service["image"] = "python:3.11-slim"
        service["profiles"] = ["optional"]
        (self.root / "compose.yaml").write_text(json.dumps(source))
        with patch.object(project_runner.shutil, "which", return_value=None):
            with self.assertRaises(project_runner.ComposeUnavailable):
                self.load()

    def test_resolution_dependent_json_requires_compose(self):
        self.docker()
        with patch.object(project_runner.shutil, "which", return_value=None):
            with self.assertRaises(project_runner.ComposeUnavailable):
                self.load()

    def test_docker_missing_compose_or_service_rejected(self):
        self.docker()
        self.profile["runtime"]["docker"]["compose_file"] = "missing.json"
        self.reject("missing file")
        self.docker()
        self.profile["runtime"]["docker"]["primary_service"] = "missing"
        self.reject("primary Compose")

    def test_compose_mapping_health_and_secrets_rejected(self):
        self.docker()
        base = json.loads((self.root / "compose.yaml").read_text())
        for defect in ("port", "health", "health-disabled", "secret", "secret-default", "listen"):
            with self.subTest(defect=defect):
                compose = copy.deepcopy(base)
                service = compose["services"]["scaffold"]
                if defect == "port":service["ports"] = ["0.0.0.0:9999:8080"]
                if defect == "health":del service["healthcheck"]
                if defect == "health-disabled":service["healthcheck"]["test"] = ["NONE"]
                if defect == "secret":service["environment"]["APP_PASSWORD"] = "synthetic-forbidden"
                if defect == "secret-default":service["environment"]["APP_PASSWORD"] = "${APP_PASSWORD:-synthetic-forbidden}"
                if defect == "listen":service["environment"]["APP_CONTAINER_LISTEN_HOST"] = "127.0.0.1"
                (self.root / "compose.yaml").write_text(json.dumps(compose))
                self.reject("EXEC-RUNTIME|SEC-ENV")

    def test_invalid_yaml_honest_failure(self):
        self.docker()
        (self.root / "compose.yaml").write_text("services: [\n")
        self.reject("Compose rendering failed")

    @unittest.skipUnless(compose_available(), "Docker Compose CLI unavailable")
    def test_ordinary_yaml_uses_read_only_effective_compose(self):
        self.docker()
        (self.root / "compose.yaml").write_text('''name: project-scaffold
services:
  scaffold:
    image: python:3.11-slim
    ports:
      - "${APP_BIND_HOST:-127.0.0.1}:${APP_HOST_PORT:-8080}:${APP_CONTAINER_PORT:-8080}"
    environment:
      APP_CONTAINER_LISTEN_HOST: "${APP_CONTAINER_LISTEN_HOST:-0.0.0.0}"
      APP_CONTAINER_PORT: "${APP_CONTAINER_PORT:-8080}"
      APP_HEALTH_PATH: "${APP_HEALTH_PATH:-/health}"
    healthcheck:
      test: ["CMD", "python3", "-c", "print('/health')"]
''')
        self.load()
        compose_path = self.root / 'compose.yaml'
        compose_path.write_text(compose_path.read_text().replace(
            'APP_HEALTH_PATH: "${APP_HEALTH_PATH:-/health}"',
            'APP_HEALTH_PATH: "${APP_HEALTH_PATH:-/health}"\n      EXTRA: "${UNDECLARED_VALUE}"'))
        self.reject('diagnostics')

    def test_storage_applicability_coherent(self):
        self.profile["runtime"]["storage"]["data_roots"] = ["data"]
        self.reject("inapplicable storage")

    def test_unknown_profile_fields_rejected(self):
        self.profile["runtime"]["magic"] = True
        self.reject("runtime schema")


if __name__ == "__main__":
    unittest.main()
