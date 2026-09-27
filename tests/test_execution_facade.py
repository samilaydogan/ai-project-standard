"""Isolated dispatcher safety, literal argv, signals and real loopback reference."""

import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import unittest
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import project_runner


class ExecutionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="facade space ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        source = Path(__file__).resolve().parents[1]
        for name in [
            '.dockerignore',
            'pyproject.toml',
            'source-exclusions.json',
            'scripts/foundation_contract.py',
            'scripts/reference_tests.py',
            'scripts/test_controls.py',
            'test-control-profile.json',
            'scripts/test_network_guard.py',
            'scripts/scaffold_status.py',
            'INSTALLATION.md',
            'MIGRATION_RECOVERY.md',
            'OPERATIONS_RUNBOOK.md',
            'THIRD_PARTY_LICENSE_INVENTORY.md',
            ".env.example",
            ".gitignore",
            "run.sh",
            "execution-profile.json",
            "scripts/project_runner.py",
            "scripts/health_scaffold.py",
            "scripts/scaffold_lint.py",
        ]:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source / name, path)
        self.config = json.loads((self.root / "execution-profile.json").read_text())

    def save(self):
        (self.root / "execution-profile.json").write_text(json.dumps(self.config))

    def run_command(self, *args):
        return subprocess.run(
            [str(self.root / "run.sh"), *args], capture_output=True, text=True, check=False
        )

    def fingerprint(self):
        return {
            str(p.relative_to(self.root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in self.root.rglob("*")
            if p.is_file()
        }

    def test_help_doctor_no_mutation(self):
        before = self.fingerprint()
        for command in ["help", "doctor"]:
            result = self.run_command(command)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(before, self.fingerprint())

    def test_doctor_accepts_prepared_interpreter_symlink_without_execution(self):
        (self.root / "python-link").symlink_to(sys.executable)
        self.config["commands"]["test"]["prerequisites"] = [
            {"kind": "file", "value": "python-link"}
        ]
        self.save()
        self.assertEqual(self.run_command("doctor").returncode, 0)

    def test_owner_tokens_are_conditional_not_executable_backends(self):
        source = Path(__file__).resolve().parents[1]
        workflow = (source / 'AGENT_WORKFLOW.md').read_text()
        rows = {line.split('|')[1].strip(): line for line in workflow.splitlines()
                if line.startswith('| TEST_') or line.startswith('| RELEASE_')}
        expected = {
            'TEST_DURUM': ('actually-read-only', 'no start/resume/closure', 'NOT CONFIGURED'),
            'TEST_LOG': ('redact', 'Log text alone', 'identity/exit/count'),
            'TEST_DEVAM': ('SAME', 'RUNNING', 'NEXT'),
            'TEST_DURDUR': ('exact active job', 'declared safe cancellation', 'PID reuse', 'cross-service'),
            'RELEASE_COMMIT': ('ALREADY VALIDATED', 'closure/build/retest/tag/push/production', 'HEAD/index'),
            'RELEASE_PREVIEW': ('committed/pinned', 'clean isolated', 'secrets', 'production data'),
        }
        self.assertEqual(set(rows), set(expected))
        for token, clauses in expected.items():
            for clause in clauses:
                self.assertIn(clause, rows[token])
            self.assertNotIn(token, self.config['commands'])
        for token in ('TEST_DURDUR', 'RELEASE_COMMIT', 'RELEASE_PREVIEW', 'release-commit'):
            before = self.fingerprint()
            result = self.run_command(token)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertEqual(before, self.fingerprint())
        for phrase in ('HOLD preserves a safe checkpoint', 'Do not begin NEXT automatically.',
                       'only bounded CURRENT/already-authorized scope', 'Closure is not RELEASE_COMMIT authorization'):
            self.assertIn(phrase, workflow)

    def test_invalid_and_unavailable(self):
        self.assertEqual(self.run_command("unknown").returncode, 2)
        self.config["commands"]["lint"].update(status="NOT CONFIGURED", argv=[])
        self.save()
        result = self.run_command("lint")
        self.assertEqual(result.returncode, 3)
        self.assertIn("NOT CONFIGURED", result.stdout)

    def test_missing_prerequisite_doctor_pending(self):
        self.config["commands"]["dev"]["prerequisites"] = [
            {"kind": "executable", "value": "missing-facade-executable-xyz"}
        ]
        self.save()
        before = self.fingerprint()
        result = self.run_command("doctor")
        self.assertEqual(result.returncode, 3)
        self.assertIn("PENDING", result.stdout)
        self.assertEqual(before, self.fingerprint())

    def test_literal_arguments_and_child_exit(self):
        self.config["commands"]["test"]["argv"] = [
            sys.executable,
            "-B",
            "-c",
            "import json,sys;print(json.dumps(sys.argv[1:]));sys.exit(17)",
        ]
        self.save()
        args = ["space argument", "$(touch bad)", ";exit 0", "--", "quote'\"", ""]
        result = self.run_command("test", *args)
        self.assertEqual(result.returncode, 17)
        self.assertEqual(json.loads(result.stdout), args)
        self.assertFalse((self.root / "bad").exists())

    def test_signal_preserved(self):
        self.config["commands"]["test"]["argv"] = [
            sys.executable,
            "-B",
            "-c",
            "import os,signal;os.kill(os.getpid(),signal.SIGTERM)",
        ]
        self.save()
        self.assertEqual(self.run_command("test").returncode, -signal.SIGTERM)

    def test_missing_python_help_fallback(self):
        env = os.environ.copy()
        env["PATH"] = "/usr/bin:/bin"
        # Use a shell-local command override, not actual host dependency removal.
        result = subprocess.run(
            [
                "/bin/bash",
                "-c",
                'function command(){ return 1; }; export -f command; bash "$1" help',
                "--",
                str(self.root / "run.sh"),
            ],
            env=env,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PENDING", result.stdout)

    def test_help_invalid_configuration_is_available(self):
        (self.root / "execution-profile.json").write_text("not JSON")
        self.assertEqual(self.run_command("help").returncode, 0)
        self.assertEqual(self.run_command("doctor").returncode, 3)

    def test_static_rejects_unsafe_profile(self):
        for change in ["apply-readonly", "missing-baseline", "mode", "symlink"]:
            with self.subTest(change=change):
                if change == "apply-readonly":
                    self.config["commands"]["apply-package"] = dict(self.config["commands"]["test"])
                    self.config["commands"]["apply-package"]["mutability"] = "read-only"
                    self.save()
                elif change == "missing-baseline":
                    del self.config["commands"]["doctor"]
                    self.save()
                elif change == "mode":
                    (self.root / "run.sh").chmod(0o644)
                else:
                    (self.root / "run.sh").unlink()
                    (self.root / "run.sh").symlink_to("/bin/bash")
                with self.assertRaises(ValueError):
                    project_runner.load(self.root)

    def test_real_reference_health(self):
        before = self.fingerprint()
        child = subprocess.Popen(
            [str(self.root / "run.sh"), "dev", "--port", "0"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            line = child.stdout.readline().strip()
            self.assertTrue(line.startswith("Reference health: http://127.0.0.1:"), line)
            url = line.removeprefix("Reference health: ")
            with urllib.request.urlopen(url, timeout=3) as response:
                self.assertEqual(json.load(response), {"status": "ok"})
            child.send_signal(signal.SIGTERM)
            self.assertEqual(child.wait(timeout=3), -signal.SIGTERM)
            self.assertEqual(before, self.fingerprint())
        finally:
            if child.poll() is None:
                child.kill()
                child.wait(timeout=3)
            child.stdout.close()
            child.stderr.close()


if __name__ == "__main__":
    unittest.main()
