"""Bounded formal-job evidence and controls; no policy/roadmap/approval authority."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import threading
import time
import tempfile
import unittest
import uuid
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from pathlib import Path

ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}")
EVENTS = {"STARTED", "HEARTBEAT", "TEST_FINISHED", "CANCEL_REQUESTED", "TERMINAL"}
TERMINAL = {"PASS", "FAIL", "SKIPPED", "CANCELLED", "TIMED_OUT", "INVALID"}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    need(not path.is_symlink() and path.is_file(), "PENDING: missing/unsafe evidence")
    def unique(pairs):
        result = {}
        for key, value in pairs:
            need(key not in result, "PENDING: duplicate evidence key")
            result[key] = value
        return result
    return json.loads(path.read_text(), object_pairs_hook=unique)


def atomic(path, value):
    need(not path.is_symlink(), "PENDING: unsafe state member")
    temp = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(value, f, sort_keys=True)
        f.write("\n")
    os.replace(temp, path)


def safe_relative(root, name):
    path = Path(name)
    need(not path.is_absolute() and ".." not in path.parts and bool(path.parts), "PENDING: unsafe source scope")
    p = root
    for part in path.parts:
        p /= part
        need(not p.is_symlink(), "PENDING: source symlink")
    need(p.exists(), "PENDING: missing source input")
    return p


def profile(root):
    p = root / "test-control-profile.json"
    cfg = read(p)
    need(set(cfg) == {"schema_version", "state_root", "source_paths", "test_directory", "pattern", "timeout_seconds", "lease_seconds"}
         and cfg["schema_version"] == 1, "NOT CONFIGURED: test-control profile")
    need(isinstance(cfg["source_paths"], list) and cfg["source_paths"]
         and len(set(cfg["source_paths"])) == len(cfg["source_paths"]), "NOT CONFIGURED: source scope")
    need(isinstance(cfg["timeout_seconds"], int) and 1 <= cfg["timeout_seconds"] <= 3600
         and isinstance(cfg["lease_seconds"], int) and 3 <= cfg["lease_seconds"] <= 300,
         "NOT CONFIGURED: timeout/lease")
    need(isinstance(cfg["pattern"], str) and re.fullmatch(r"[A-Za-z0-9_*?.-]+", cfg["pattern"]), "NOT CONFIGURED: pattern")
    directory = safe_relative(root, cfg["test_directory"])
    need(directory.is_dir(), "NOT CONFIGURED: test directory")
    raw = Path(cfg["state_root"]).expanduser()
    state = raw if raw.is_absolute() else root / raw
    # Reject symlinks in the entire declared state path, including parent aliases.
    for p in (state, *state.parents):
        need(not p.is_symlink(), "PENDING: state symlink")
    state = state.resolve()
    need(not state.is_relative_to(root) and not root.is_relative_to(state), "PENDING: state must be outside source")
    return cfg, state


def identity(root, cfg):
    inventory = {}
    for name in cfg["source_paths"]:
        p = safe_relative(root, name)
        members = [p] if p.is_file() else sorted(p.rglob("*"))
        for f in members:
            need(not f.is_symlink(), "PENDING: source symlink")
            if f.is_file() and "__pycache__" not in f.parts and f.suffix != ".pyc":
                key = f.relative_to(root).as_posix()
                inventory[key] = {"sha256": digest(f.read_bytes()), "mode": f.stat().st_mode & 0o777}
    # Bind the configuration and actual runtime as well as configured source/locks.
    inventory["test-control-profile.json"] = {"sha256": digest((root / "test-control-profile.json").read_bytes()), "mode": (root / "test-control-profile.json").stat().st_mode & 0o777}
    return {"members": dict(sorted(inventory.items())), "runtime": sys.version,
            "adapter_sha256": digest(Path(__file__).read_bytes()),
            "executable_sha256": digest(Path(sys.executable).read_bytes())}


@contextmanager
def mutation(state):
    lock = state / "mutation.lock"
    need(not lock.is_symlink(), "PENDING: unsafe lock")
    for _ in range(200):
        try:
            lock.mkdir(mode=0o700)
            break
        except FileExistsError:
            time.sleep(0.005)
    else:
        raise ValueError("PENDING: mutation busy; no stale-lock removal")
    try:
        yield
    finally:
        lock.rmdir()


def event(record, name):
    need(name in EVENTS, "PENDING: invalid event")
    record["updated"] = time.time()
    if name != "CANCEL_REQUESTED":
        record["worker_updated"] = record["updated"]
    record["events"] = (record["events"] + [{"event": name, "time": record["updated"]}])[-128:]


def validate_record(record):
    keys = {"schema_version", "job", "work_unit", "step", "source", "pattern", "status", "started", "updated", "worker_updated", "cancel_requested", "exit", "counts", "events"}
    need(isinstance(record, dict) and set(record) == keys and record["schema_version"] == 1, "PENDING: malformed job evidence")
    for key in ("job", "work_unit", "step"):
        need(isinstance(record[key], str) and ID.fullmatch(record[key]), "PENDING: invalid job identity")
    need(record["status"] in TERMINAL | {"RUNNING"} and type(record["cancel_requested"]) is bool, "PENDING: invalid status")
    need(all(isinstance(record[k], (int, float)) and not isinstance(record[k], bool) for k in ("started", "updated", "worker_updated"))
         and record["started"] <= record["worker_updated"] <= record["updated"] <= time.time() + 2, "PENDING: invalid timestamp")
    need(isinstance(record["pattern"], str) and re.fullmatch(r"[A-Za-z0-9_*?.-]+", record["pattern"]), "PENDING: invalid selection")
    c = record["counts"]
    need(isinstance(c, dict) and set(c) == {"run", "passed", "failed", "skipped"}
         and all(type(v) is int and v >= 0 for v in c.values())
         and c["passed"] + c["skipped"] <= c["run"]
         and c["passed"] == max(0, c["run"] - c["failed"] - c["skipped"]), "PENDING: invalid counts")
    need(isinstance(record["events"], list) and len(record["events"]) <= 128, "PENDING: invalid log")
    for e in record["events"]:
        need(isinstance(e, dict) and set(e) == {"event", "time"} and e["event"] in EVENTS
             and isinstance(e["time"], (int, float)), "PENDING: unrecognized log event")
    if record["status"] == "RUNNING":
        need(record["exit"] is None, "PENDING: running with terminal exit")
    else:
        need(type(record["exit"]) is int and record["events"] and record["events"][-1]["event"] == "TERMINAL", "PENDING: incomplete terminal evidence")
    if record["status"] == "PASS":
        need(record["exit"] == 0 and c["run"] > 0 and c["failed"] == c["skipped"] == 0
             and not record["cancel_requested"], "PENDING: contradictory PASS")
    return record


def observe(root, job=None, work_unit=None, step=None):
    cfg, state = profile(root)
    record = validate_record(read(state / "current.json"))
    need(job is None or record["job"] == job, "PENDING: wrong active job")
    need(work_unit is None or record["work_unit"] == work_unit, "PENDING: wrong work unit")
    need(step is None or record["step"] == step, "PENDING: wrong authorized step")
    need(record["source"] == identity(root, cfg), "PENDING: stale source/dependency/config/runner identity")
    if record["status"] == "RUNNING":
        need(time.time() - record["worker_updated"] <= cfg["lease_seconds"], "PENDING: stale worker lease; liveness unknown")
        need((state / "active.lock").is_dir() and not (state / "active.lock").is_symlink(),
             "PENDING: no active worker ownership; liveness unknown")
        need(read(state / "active.lock" / "owner.json") == {"job": record["job"]},
             "PENDING: active worker ownership mismatch; liveness unknown")
    return cfg, state, record


def control(root, operation, job=None, work_unit=None, step=None):
    cfg, state, record = observe(root, job, work_unit, step)
    if operation == "stop":
        need(job and work_unit and step, "PENDING: explicit job/work-unit/step required for stop")
        if record["status"] != "RUNNING":
            return {"job": record["job"], "status": record["status"], "stop": "ALREADY_TERMINAL"}
        with mutation(state):
            _, _, record = observe(root, job, work_unit, step)
            if record["status"] != "RUNNING":
                return {"job": record["job"], "status": record["status"], "stop": "ALREADY_TERMINAL"}
            record["cancel_requested"] = True
            event(record, "CANCEL_REQUESTED")
            atomic(state / "current.json", record)
        return {"job": record["job"], "status": "CANCEL_REQUESTED", "stop": "AWAIT_WORKER_ACK"}
    result = {"job": record["job"], "work_unit": record["work_unit"], "step": record["step"],
              "status": "CANCEL_REQUESTED" if record["status"] == "RUNNING" and record["cancel_requested"] else record["status"],
              "counts": record["counts"], "exit": record["exit"], "pattern": record["pattern"],
              "worker_observed_at": record["worker_updated"]}
    if operation == "log":
        # Never print arbitrary strings from state, paths, test names or test output.
        result["events"] = record["events"]
        result["log_policy"] = "ALLOWLISTED_EVENTS_ONLY; RAW_OUTPUT_NOT_RETAINED"
    if operation == "continue":
        need(job and work_unit and step, "PENDING: explicit job/work-unit/step required for continuation")
        result["eligible"] = record["status"] == "PASS"
        result["action"] = "SAME_AUTHORIZED_STEP_ELIGIBLE" if result["eligible"] else "WAIT" if record["status"] == "RUNNING" else "HOLD"
        result["authority"] = "NO_EXECUTION_CLOSURE_NEXT_OR_RELEASE_AUTHORITY"
    return result


class ControlledResult(unittest.TestResult):
    def __init__(self, publish, should_cancel):
        super().__init__()
        self.publish = publish
        self.should_cancel = should_cancel

    def startTest(self, test):
        if self.should_cancel():
            self.stop()
        super().startTest(test)

    def stopTest(self, test):
        super().stopTest(test)
        self.publish("TEST_FINISHED", self)
        if self.should_cancel():
            self.stop()


def counts(result):
    # unittest may report several failing/skipped subtests for one testsRun case.
    # Count unique parent cases, with failures taking precedence over skips.
    def key(test):
        parent = getattr(test, "test_case", None)
        return (parent if isinstance(parent, unittest.TestCase) else test).id()
    failed_cases = {key(test) for test, _ in result.failures + result.errors}
    failed_cases.update(key(test) for test in result.unexpectedSuccesses)
    skipped_cases = {key(test) for test, _ in result.skipped + result.expectedFailures}
    failed = len(failed_cases)
    skipped = len(skipped_cases - failed_cases)
    # setUpClass/module errors can produce failed outcomes without testsRun.
    return {"run": result.testsRun, "passed": max(0, result.testsRun - failed - skipped),
            "failed": failed, "skipped": skipped}


@contextmanager
def suppressed_output():
    # Also suppress direct fd/child output; no heuristic secret detector is used.
    saved = [os.dup(fd) for fd in (1, 2)]
    try:
        with open(os.devnull, "w") as sink:
            for fd in (1, 2):
                os.dup2(sink.fileno(), fd)
            with redirect_stdout(sink), redirect_stderr(sink):
                yield
    finally:
        for fd, backup in zip((1, 2), saved):
            os.dup2(backup, fd)
            os.close(backup)


def run(root, work_unit, step, pattern=None):
    need(ID.fullmatch(work_unit or "") and ID.fullmatch(step or ""), "PENDING: work-unit/step required")
    cfg, state = profile(root)
    pattern = pattern or cfg["pattern"]
    need(re.fullmatch(r"[A-Za-z0-9_*?.-]+", pattern), "PENDING: invalid discovery pattern")
    state.mkdir(mode=0o700, parents=True, exist_ok=True)
    need(state.stat().st_mode & 0o077 == 0, "PENDING: state directory must be private")
    source = identity(root, cfg)
    active = state / "active.lock"
    # Never reclaim orphaned active ownership automatically or kill a recorded PID.
    active.mkdir(mode=0o700)
    job = uuid.uuid4().hex
    atomic(active / "owner.json", {"job": job})
    started = time.time()
    record = {"schema_version": 1, "job": job, "work_unit": work_unit, "step": step,
              "source": source, "pattern": pattern, "status": "RUNNING", "started": started,
              "updated": started, "worker_updated": started, "cancel_requested": False, "exit": None,
              "counts": {"run": 0, "passed": 0, "failed": 0, "skipped": 0}, "events": []}
    done = threading.Event()
    problem = []
    timed_out = False

    def publish(name, result=None):
        with mutation(state):
            old = read(state / "current.json")
            need(old["job"] == job, "PENDING: worker identity replaced")
            record["cancel_requested"] = old["cancel_requested"]
            # Preserve a concurrent stop event.
            record["events"] = old["events"]
            if result is not None:
                record["counts"] = counts(result)
            event(record, name)
            atomic(state / "current.json", record)

    def cancelled():
        nonlocal timed_out
        timed_out = time.monotonic() - clock > cfg["timeout_seconds"]
        return timed_out or read(state / "current.json")["cancel_requested"]

    def heartbeat():
        while not done.wait(1):
            try:
                publish("HEARTBEAT")
            except (ValueError, OSError, KeyError) as exc:
                problem.append(type(exc).__name__)
                return

    clock = time.monotonic()
    thread = None
    result = None
    try:
        with mutation(state):
            event(record, "STARTED")
            atomic(state / "current.json", record)
        thread = threading.Thread(target=heartbeat, daemon=True)
        thread.start()
        # Adapter is explicitly stdlib unittest, not an arbitrary shell command.
        # Raw output is suppressed, never persisted or returned by TEST_LOG.
        with suppressed_output():
            suite = unittest.defaultTestLoader.discover(str(safe_relative(root, cfg["test_directory"])), pattern=pattern)
            result = ControlledResult(publish, cancelled)
            if not cancelled():
                suite.run(result)
        done.set()
        thread.join()
        with mutation(state):
            old = read(state / "current.json")
            need(old["job"] == job, "PENDING: worker identity replaced")
            record["cancel_requested"] = old["cancel_requested"]
            record["events"] = old["events"]
            record["counts"] = counts(result)
            cancelled()
            if record["source"] != identity(root, cfg) or problem:
                status, code = "INVALID", 3
            elif timed_out:
                status, code = "TIMED_OUT", 124
            elif record["cancel_requested"]:
                status, code = "CANCELLED", 130
            elif record["counts"]["failed"]:
                status, code = "FAIL", 1
            elif record["counts"]["skipped"]:
                status, code = "SKIPPED", 4
            elif not result.testsRun:
                status, code = "INVALID", 3
            else:
                status, code = "PASS", 0
            record["status"], record["exit"] = status, code
            event(record, "TERMINAL")
            atomic(state / "current.json", record)
            archive = state / (job + ".json")
            need(not archive.exists(), "PENDING: existing terminal archive")
            atomic(archive, record)
        return {"job": job, "status": status, "exit": code, "counts": record["counts"], "pattern": pattern}, code
    finally:
        done.set()
        if thread is not None:
            thread.join()
        (active / "owner.json").unlink()
        active.rmdir()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("run", "status", "log", "continue", "stop"))
    parser.add_argument("--work-unit")
    parser.add_argument("--step")
    parser.add_argument("--job")
    parser.add_argument("--pattern")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        if args.operation == "run":
            # Explicitly opt-in adapter starts tests with no inherited credentials.
            safe_env = {k: os.environ[k] for k in ("PATH", "LANG", "LC_CTYPE") if k in os.environ}
            with tempfile.TemporaryDirectory(prefix="formal-test-environment-") as tmp:
                os.environ.clear()
                guard = root / "scripts/test_network_guard.py"
                (Path(tmp) / "sitecustomize.py").write_bytes(guard.read_bytes())
                os.environ.update(safe_env, HOME=tmp, TMPDIR=tmp, PYTHONPATH=tmp, PYTHONDONTWRITEBYTECODE="1")
                import test_network_guard  # noqa: F401 -- reference loopback-only adapter
                os.chdir(root)
                result, code = run(root, args.work_unit, args.step, args.pattern)
        else:
            need(args.pattern is None, "PENDING: selection cannot change for an existing job")
            result = control(root, args.operation, args.job, args.work_unit, args.step)
            code = 0 if args.operation != "continue" or result["eligible"] else 3
        print(json.dumps(result, sort_keys=True))
        return code
    except Exception:
        # Never echo exception text containing paths, logs or config/credential values.
        print(json.dumps({"status": "PENDING", "eligible": False, "reason": "MISSING_UNSAFE_STALE_OR_UNAVAILABLE_JOB; INSPECT_LOCAL_CONTRACT"}))
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
