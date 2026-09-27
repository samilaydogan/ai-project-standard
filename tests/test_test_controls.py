"""Disposable positive/negative acceptance for cooperative formal-job controls."""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import types
import unittest
import uuid
from pathlib import Path

spec = importlib.util.spec_from_file_location("bounded_test_controls", Path(__file__).resolve().parents[1] / "scripts/test_controls.py")
controls = importlib.util.module_from_spec(spec)
spec.loader.exec_module(controls)


class TestControls(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="test-control-acceptance-")
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.root = self.base / "source"
        self.root.mkdir()
        (self.root / "tests").mkdir()
        self.state = self.base / "state"
        self.cfg = {"schema_version": 1, "state_root": str(self.state), "source_paths": ["tests"],
                    "test_directory": "tests", "pattern": "test_*.py", "timeout_seconds": 10, "lease_seconds": 3}
        self.write_cfg()
        self.case = self.root / "tests" / ("test_" + uuid.uuid4().hex + ".py")
        self.gate_name = "gate_" + uuid.uuid4().hex
        self.gate = types.ModuleType(self.gate_name)
        self.gate.entered = threading.Event()
        self.gate.release = threading.Event()
        sys.modules[self.gate_name] = self.gate
        self.addCleanup(sys.modules.pop, self.gate_name, None)

    def write_cfg(self):
        (self.root / "test-control-profile.json").write_text(json.dumps(self.cfg))

    def fixture(self, body="pass"):
        self.case.write_text("import unittest, os, time\nclass Fixture(unittest.TestCase):\n    def test_case(self):\n        " + body.replace("\n", "\n        ") + "\n")

    def run_job(self):
        return controls.run(self.root, "UNIT-A", "STEP-1")

    def record(self):
        return controls.read(self.state / "current.json")

    def op(self, op, **kw):
        r = self.record()
        return controls.control(self.root, op, r["job"], "UNIT-A", "STEP-1", **kw)

    def running(self):
        self.fixture(f"import {self.gate_name} as gate\ngate.entered.set()\nassert gate.release.wait(5)")
        outcome = []
        worker = threading.Thread(target=lambda: outcome.append(self.run_job()))
        worker.start()
        self.addCleanup(self.gate.release.set)
        self.assertTrue(self.gate.entered.wait(3))
        return worker, outcome

    def test_pass_and_same_step_eligibility_no_pointer_mutation(self):
        self.fixture()
        plan = self.root / "EXECUTION_PLAN.md"
        plan.write_text("CURRENT UNIT-A; NEXT UNIT-B; no transitions authorized")
        before = plan.read_bytes()
        result, code = self.run_job()
        self.assertEqual((result["status"], code), ("PASS", 0))
        self.assertEqual(result["counts"], {"run": 1, "passed": 1, "failed": 0, "skipped": 0})
        self.assertTrue(self.op("continue")["eligible"])
        self.assertEqual(self.op("continue")["action"], "SAME_AUTHORIZED_STEP_ELIGIBLE")
        self.assertEqual(plan.read_bytes(), before)

    def test_failure_is_not_eligible(self):
        self.fixture("self.fail('secret failure text')")
        result, code = self.run_job()
        self.assertEqual((result["status"], code), ("FAIL", 1))
        self.assertFalse(self.op("continue")["eligible"])
        self.assertNotIn("secret", (self.state / "current.json").read_text())

    def test_skip_and_expected_failure_are_not_pass(self):
        self.fixture("self.skipTest('private reason')")
        result, code = self.run_job()
        self.assertEqual((result["status"], code), ("SKIPPED", 4))
        self.assertEqual(result["counts"]["skipped"], 1)
        self.assertFalse(self.op("continue")["eligible"])

    def test_subtest_failures_count_parent_cases_truthfully(self):
        self.fixture("for i in range(3):\n    with self.subTest(i=i):\n        self.fail('redacted')")
        result, _ = self.run_job()
        self.assertEqual(result["counts"], {"run": 1, "passed": 0, "failed": 1, "skipped": 0})
        self.assertFalse(self.op("continue")["eligible"])

    def test_expected_failure_and_unexpected_success(self):
        self.case.write_text("import unittest\nclass Fixture(unittest.TestCase):\n    @unittest.expectedFailure\n    def test_case(self):\n        self.fail('redacted')\n")
        result, _ = self.run_job()
        self.assertEqual(result["status"], "SKIPPED")
        self.assertEqual(result["counts"]["skipped"], 1)
        self.assertFalse(self.op("continue")["eligible"])

    def test_fixture_failure_with_zero_tests_still_fails(self):
        self.case.write_text("import unittest\nclass Fixture(unittest.TestCase):\n    @classmethod\n    def setUpClass(cls):\n        raise RuntimeError('redacted')\n    def test_case(self):\n        pass\n")
        result, _ = self.run_job()
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["counts"], {"run": 0, "passed": 0, "failed": 1, "skipped": 0})
        self.assertFalse(self.op("continue")["eligible"])

    def test_unexpected_success_is_failure_not_eligible(self):
        self.case.write_text("import unittest\nclass Fixture(unittest.TestCase):\n    @unittest.expectedFailure\n    def test_case(self):\n        pass\n")
        result, code = self.run_job()
        self.assertEqual((result["status"], code), ("FAIL", 1))
        self.assertEqual(result["counts"], {"run": 1, "passed": 0, "failed": 1, "skipped": 0})
        self.assertFalse(self.op("continue")["eligible"])

    def test_active_ownership_mismatch_or_missing_fails_closed(self):
        worker, outcome = self.running()
        owner = self.state / "active.lock" / "owner.json"
        original = owner.read_bytes()
        try:
            controls.atomic(owner, {"job": "different-job"})
            for op in ("status", "log", "continue", "stop"):
                with self.subTest(op=op), self.assertRaisesRegex(ValueError, "ownership"):
                    self.op(op)
            owner.unlink()
            with self.assertRaisesRegex(ValueError, "missing"):
                self.op("status")
        finally:
            owner.write_bytes(original)
            self.gate.release.set()
            worker.join(5)
        self.assertEqual(outcome[0][0]["status"], "PASS")

    def test_empty_discovery_is_invalid(self):
        self.fixture()
        result, code = controls.run(self.root, "UNIT-A", "STEP-1", "absent*.py")
        self.assertEqual((result["status"], code), ("INVALID", 3))
        self.assertFalse(self.op("continue")["eligible"])

    def test_missing_reads_do_not_create_state(self):
        for op in ("status", "log", "continue", "stop"):
            with self.subTest(op=op), self.assertRaises((ValueError, OSError)):
                controls.control(self.root, op, "job", "UNIT-A", "STEP-1")
        self.assertFalse(self.state.exists())

    def test_status_log_continue_reads_are_byte_read_only(self):
        self.fixture()
        self.run_job()
        before = {p.name: p.read_bytes() for p in self.state.iterdir() if p.is_file()}
        for op in ("status", "log", "continue"):
            self.op(op)
        after = {p.name: p.read_bytes() for p in self.state.iterdir() if p.is_file()}
        self.assertEqual(before, after)

    def test_source_and_config_drift_fail_closed(self):
        self.fixture()
        self.run_job()
        self.case.write_text(self.case.read_text() + "# changed input\n")
        with self.assertRaisesRegex(ValueError, "stale"):
            self.op("continue")
        with self.assertRaisesRegex(ValueError, "stale"):
            self.op("stop")

    def test_configuration_drift_is_stale(self):
        self.fixture()
        self.run_job()
        self.cfg["timeout_seconds"] = 11
        self.write_cfg()
        with self.assertRaisesRegex(ValueError, "stale"):
            self.op("continue")

    def test_changed_source_during_run_invalidates_terminal(self):
        worker, outcome = self.running()
        try:
            self.case.write_text(self.case.read_text() + "# runtime drift\n")
        finally:
            self.gate.release.set()
            worker.join(5)
        self.assertEqual(outcome[0][0]["status"], "INVALID")

    def test_previous_job_identity_and_archive_retained(self):
        self.fixture()
        old, _ = self.run_job()
        old_archive = (self.state / (old["job"] + ".json")).read_bytes()
        new, _ = self.run_job()
        self.assertNotEqual(old["job"], new["job"])
        self.assertEqual((self.state / (old["job"] + ".json")).read_bytes(), old_archive)
        with self.assertRaisesRegex(ValueError, "wrong active"):
            controls.control(self.root, "stop", old["job"], "UNIT-A", "STEP-1")

    def test_cancel_requests_cannot_renew_dead_worker(self):
        self.fixture()
        self.run_job()
        r = self.record()
        r.update(status="RUNNING", exit=None, started=time.time() - 100,
                 worker_updated=time.time() - 100, updated=time.time())
        r["cancel_requested"] = True
        controls.atomic(self.state / "current.json", r)
        with self.assertRaisesRegex(ValueError, "lease"):
            self.op("status")

    def test_cli_fresh_process_environment_and_redaction(self):
        self.fixture("self.assertNotIn('PRIVATE_TEST_SECRET', os.environ)\nprint('sensitive stdout')")
        scripts = self.root / "scripts"
        scripts.mkdir()
        actual = Path(__file__).resolve().parents[1]
        for name in ("test_controls.py", "test_network_guard.py"):
            shutil.copy2(actual / "scripts" / name, scripts / name)
        argv = [sys.executable, "-B", str(scripts / "test_controls.py")]
        env = dict(os.environ, PRIVATE_TEST_SECRET="do-not-propagate")
        run = subprocess.run(argv + ["run", "--work-unit", "UNIT-A", "--step", "STEP-1"],
                             capture_output=True, text=True, env=env, check=False)
        self.assertEqual(run.returncode, 0, run.stdout)
        result = json.loads(run.stdout)
        self.assertEqual(result["status"], "PASS")
        follow = subprocess.run(argv + ["continue", "--job", result["job"],
                                       "--work-unit", "UNIT-A", "--step", "STEP-1"],
                                capture_output=True, text=True, check=False)
        self.assertEqual(follow.returncode, 0, follow.stdout)
        self.assertTrue(json.loads(follow.stdout)["eligible"])
        self.assertNotIn("sensitive stdout", run.stdout + run.stderr)

    def test_wrong_job_work_unit_step_rejected(self):
        self.fixture()
        self.run_job()
        r = self.record()
        for args in (("wrong", "UNIT-A", "STEP-1"), (r["job"], "UNIT-B", "STEP-1"), (r["job"], "UNIT-A", "STEP-2")):
            with self.subTest(args=args), self.assertRaises(ValueError):
                controls.control(self.root, "continue", *args)

    def test_log_redaction_uses_no_raw_streams_or_names(self):
        self.fixture("print('PASSWORD=private-token')\nos.write(2, b'authorization-secret')")
        self.run_job()
        log = json.dumps(self.op("log"))
        self.assertNotIn("private-token", log)
        self.assertNotIn("authorization-secret", log)
        self.assertNotIn(self.case.name, log)
        self.assertIn("RAW_OUTPUT_NOT_RETAINED", log)

    def test_cancel_request_is_not_stop_ack_and_no_pid_used(self):
        worker, outcome = self.running()
        try:
            self.assertEqual(self.op("status")["status"], "RUNNING")
            self.assertFalse(self.op("continue")["eligible"])
            response = self.op("stop")
            self.assertEqual(response["status"], "CANCEL_REQUESTED")
            self.assertEqual(response["stop"], "AWAIT_WORKER_ACK")
            self.assertTrue(worker.is_alive())
            self.assertEqual(self.op("status")["status"], "CANCEL_REQUESTED")
        finally:
            self.gate.release.set()
            worker.join(5)
        self.assertFalse(worker.is_alive())
        self.assertEqual(outcome[0][0]["status"], "CANCELLED")
        self.assertEqual(outcome[0][1], 130)
        self.assertFalse(self.op("continue")["eligible"])
        self.assertNotIn("pid", self.record())

    def test_repeated_cancel_and_terminal_race_preserve_terminal(self):
        self.fixture()
        result, _ = self.run_job()
        before = (self.state / "current.json").read_bytes()
        for _ in range(3):
            response = self.op("stop")
            self.assertEqual(response["stop"], "ALREADY_TERMINAL")
            self.assertEqual(response["status"], result["status"])
        self.assertEqual(before, (self.state / "current.json").read_bytes())

    def test_concurrent_cancel_completion_serialized(self):
        worker, outcome = self.running()
        try:
            self.op("stop")
            self.op("stop")
        finally:
            self.gate.release.set()
            worker.join(5)
        self.assertEqual(outcome[0][0]["status"], "CANCELLED")
        self.assertEqual(self.op("stop")["stop"], "ALREADY_TERMINAL")

    def test_busy_and_orphan_ownership_never_reclaimed(self):
        self.fixture()
        self.state.mkdir(mode=0o700)
        (self.state / "active.lock").mkdir()
        with self.assertRaises(FileExistsError):
            self.run_job()
        self.assertTrue((self.state / "active.lock").exists())

    def test_stale_lease_reports_unknown_not_running(self):
        self.fixture()
        self.run_job()
        r = self.record()
        old_time = time.time() - 100
        r.update(status="RUNNING", exit=None, started=old_time, updated=old_time, worker_updated=old_time)
        controls.atomic(self.state / "current.json", r)
        with self.assertRaisesRegex(ValueError, "lease"):
            self.op("status")
        with self.assertRaisesRegex(ValueError, "lease"):
            self.op("stop")

    def test_timeout_at_test_boundary_not_pass(self):
        self.cfg["timeout_seconds"] = 1
        self.write_cfg()
        self.fixture("time.sleep(1.05)")
        result, code = self.run_job()
        self.assertEqual((result["status"], code), ("TIMED_OUT", 124))
        self.assertFalse(self.op("continue")["eligible"])

    def test_tampered_counts_and_terminal_ack_rejected(self):
        self.fixture()
        self.run_job()
        r = self.record()
        r["counts"]["failed"] = 1
        controls.atomic(self.state / "current.json", r)
        with self.assertRaises(ValueError):
            self.op("continue")

    def test_unknown_log_payload_fails_without_echo(self):
        self.fixture()
        self.run_job()
        r = self.record()
        r["events"].append({"event": "PASSWORD=secret", "time": time.time()})
        controls.atomic(self.state / "current.json", r)
        with self.assertRaisesRegex(ValueError, "unrecognized"):
            self.op("log")

    def test_source_state_overlap_and_symlinks_rejected(self):
        self.fixture()
        self.cfg["state_root"] = str(self.root / "state")
        self.write_cfg()
        with self.assertRaisesRegex(ValueError, "outside"):
            self.run_job()
        self.cfg["state_root"] = str(self.state)
        self.write_cfg()
        (self.root / "tests" / "link.py").symlink_to(self.case)
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.run_job()


if __name__ == "__main__":
    unittest.main()
