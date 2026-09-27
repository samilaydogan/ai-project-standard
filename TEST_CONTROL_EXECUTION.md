# Executable TEST controls — supporting adapter guide

This guide describes `scripts/test_controls.py`; it is not a policy owner. Conversational semantics remain [AGENT_WORKFLOW.md](AGENT_WORKFLOW.md), evidence/closure remain [TESTING_AND_EVIDENCE.md](TESTING_AND_EVIDENCE.md), dispatch remains [EXECUTION_FACADE.md](EXECUTION_FACADE.md), and project applicability/authorization remain the local profile. No control edits execution documents, resumes code by itself, grants closure/NEXT/release authority or authenticates owner intent.

## Explicit start versus controls

The supplied adapter runs stdlib unittest discovery only; it does not execute arbitrary shell strings or install dependencies. Projects using other runners retain an explicit NOT CONFIGURED adapter until separately integrated and accepted. Configure optional project-owned `test-control-profile.json` and facade mappings deliberately; shipping reference files does not automatically opt a consumer into formal testing. Profiles and commands use existing configuration/argv mechanisms; no new generic invariant or required consumer file is created.

Example for an already authorized step:

```sh
./run.sh formal-test --work-unit UNIT-A --step STEP-1
./run.sh test-durum
./run.sh test-log
./run.sh test-devam --job JOB_ID --work-unit UNIT-A --step STEP-1
./run.sh test-durdur --job JOB_ID --work-unit UNIT-A --step STEP-1
```

Equivalent portable entrypoint: `python3 -B scripts/test_controls.py run|status|log|continue|stop` with the same options. CLI tokens map TEST_DURUM→test-durum/status, TEST_LOG→test-log/log, TEST_DEVAM→test-devam/continue, TEST_DURDUR→test-durdur/stop. The uppercase words retain conversational meanings and are not new shell commands. `formal-test` is a separate explicitly authorized start, never implied by any control. Each job gets a random non-PID ID; start prints its terminal ID, while status exposes the active ID during the run. Job/step/unit arguments are required for stop and continuation; a packet or CLI argument is not proof that the work was authorized.

## State and identity

Profile schema 1 declares an external private state_root, explicit source_paths, test_directory/pattern, timeout_seconds and lease_seconds. State cannot overlap/contain source; symlink paths fail closed. Configure collision-safe project-local roots outside source; mutable state is not a release member. Relevant source/test/dependency/lock/config/tool inputs must be included in source_paths per the local evidence contract. The adapter binds sorted bytes/modes, config, its own bytes, Python version and executable identity. Missing/symlink source members or drift fail closed. The reference binds scripts/tests and every distribution member plus the manifest, because checker tests consume the full distribution. Canonical contracts, configuration, supporting forms and pyproject are therefore included; there are no third-party dependencies/locks. No all-project fingerprint is inferred from an incomplete local source scope.

One exclusive active.lock prevents concurrent starts; its private owner.json binds the active lock to the exact job. Missing or mismatched active ownership reports PENDING, never RUNNING. Atomic current.json records active-job identity, selection, counts, observed status, worker heartbeat and events. Terminal job-ID JSON is retained separately; a later run replaces only the current pointer, not previous terminal archives. Orphan locks/evidence are never reclaimed automatically; separately investigate/reconcile an interrupted worker, preserving state. Local private filesystem ownership is the trust boundary; hashes are not cryptographic sender authentication. A same-user attacker can replace unsigned evidence, so human review must use trusted artifacts. No state path, test name, assertion message, raw output or secret is echoed on malformed input.

## Observation and continuation

Status/log/continue only read existing bytes and compute current source identity; they do not mkdir, write, start, resume or cancel. RUNNING means a fresh worker observation, not guaranteed future liveness; a stale lease reports PENDING/unknown. Cancellation requests do not renew worker liveness. TEST_LOG returns at most 128 allowlisted events and count summaries. Raw Python, fd and child stdout/stderr are discarded during test execution; this strict redaction design sacrifices diagnostics instead of attempting unsafe heuristic secret masking. Use a separately authorized isolated targeted debugging run for detailed failures, not TEST_LOG.

Terminal evidence requires actual unittest counts and completion/exit, not log text. Run counts follow testsRun; failing/skipped subtests count unique parent outcomes. Fixture errors can produce failed outcomes with zero testsRun, and are reported as such rather than negative passed counts. PASS requires a nonempty selection, zero failures/errors/unexpected successes, zero skips/expected failures, unchanged relevant inputs and no cancellation. This adapter conservatively holds continuation for any skips; it never claims skipped requirements PASS. Empty discovery, malformed/import failure, stale/missing evidence, FAILED/SKIPPED/TIMED_OUT/INVALID/CANCELLED states cannot authorize continuation. Returned pattern explicitly limits the accepted selection; targeted PASS is not full-suite acceptance. TEST_DEVAM returns SAME_AUTHORIZED_STEP_ELIGIBLE only for the exact job/unit/step on PASS. It executes no continuation: the receiving actor must verify existing authority and required local gates before resuming that same step.

## Cooperative stop and time bounds

TEST_DURDUR serializes an identity-bound cancellation request with worker updates/finalization. It never reads or signals a PID, kills a process group, or interrupts another service. While a single test/fixture is executing, stop reports CANCEL_REQUESTED/AWAIT_WORKER_ACK; it is not STOPPED. Worker observes at unittest boundaries, halts further scheduling, and writes terminal CANCELLED (exit 130), retaining evidence. If completion wins the serialization race, stop returns ALREADY_TERMINAL without changing bytes; if request wins, finalization cannot report PASS. Repeated requests are safe. A replaced job, wrong unit/step, stale source/worker or unsafe lock blocks the request.

Timeout is cooperative at test boundaries (exit 124), not a hard interrupt of arbitrary blocking native/test code. An indefinitely blocked test may remain cancellation-requested; no hard-stop or real-time guarantee is claimed. Worker heartbeats disclose activity; on worker loss stale evidence is PENDING. Projects needing immediate interruption must separately declare and accept a safe executor before claiming that capability. Existing ./run.sh test retains its bounded subprocess timeout; this optional adapter does not weaken that full-suite gate. Start sanitizes inherited environment to PATH/LANG/LC_CTYPE, disposable HOME/TMPDIR, and uses the reference loopback-only network guard. It is a test harness, not an OS sandbox for hostile test code.

Exit codes: 0 verified PASS or successful observation/request (not acceptance), 1 failed tests, 3 unavailable/invalid/stale or ineligible continuation, 4 skipped tests, 124 boundary timeout, 130 acknowledged cancellation. The JSON status/eligible fields—not exit 0 alone—define the scope of a result.
