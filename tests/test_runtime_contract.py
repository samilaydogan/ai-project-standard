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


class RuntimeContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "source"
        self.root.mkdir()
        self.source = Path(__file__).resolve().parents[1]
        for name in ('.dockerignore', 'pyproject.toml', 'source-exclusions.json', 'scripts/foundation_contract.py', 'scripts/reference_tests.py', 'scripts/test_network_guard.py', 'scripts/scaffold_status.py', 'INSTALLATION.md', 'MIGRATION_RECOVERY.md', 'OPERATIONS_RUNBOOK.md', 'THIRD_PARTY_LICENSE_INVENTORY.md', "run.sh", ".env.example", ".gitignore", "execution-profile.json",
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

    def test_compose_unsupported_yaml_honest_failure(self):
        self.docker()
        (self.root / "compose.yaml").write_text("services:\n  scaffold: {}\n")
        self.reject("JSON-compatible YAML")

    def test_storage_applicability_coherent(self):
        self.profile["runtime"]["storage"]["data_roots"] = ["data"]
        self.reject("inapplicable storage")

    def test_unknown_profile_fields_rejected(self):
        self.profile["runtime"]["magic"] = True
        self.reject("runtime schema")


if __name__ == "__main__":
    unittest.main()
