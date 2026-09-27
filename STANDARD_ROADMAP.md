# ai-project-standard official roadmap

Revision: R1. Date: 2026-09-27. Planning authority: this repository-owned file, configured by PROJECT_PROFILE.md. Rn is a project-local monotonically increasing planning revision, independent of standard release VERSION. Scope/order/dependency/acceptance changes require an authorized revision and ROADMAP_CHANGELOG record; factual execution updates do not silently rewrite planning intent. Exact bytes are identified by Git commit plus file hash. EXECUTION_PLAN.md alone owns live CURRENT/NEXT; this roadmap defines intended order and unit contracts.

## Ordered work-unit map

| ID | Title | Recorded execution status | Dependencies |
| --- | --- | --- | --- |
| STD-SUP-01 | Portable Supervisor-controlled development baseline | CLOSED | none |
| STD-TEST-01 | Generic executable TEST controls | CLOSED | STD-SUP-01 CLOSED |
| STD-REL-01 | Explicit validated-candidate commit control | CLOSED | STD-TEST-01 CLOSED |
| STD-REL-02 | Isolated committed-identity preview control | CLOSED | STD-REL-01 CLOSED |

Statuses above reflect the owner-authorized closure record; consult EXECUTION_PLAN.md for sole live CURRENT/NEXT and PROJECT_STATE.md for technical facts. Completed units are retained. No code implementation is authorized by selecting a unit.

## STD-SUP-01 — completed baseline

CLOSED at standard 0.2.2 FINAL, commit cd2c377318775e1d3477b97297273b5253575e73. Accepted portable workflow, templates and truthful planning projection. Evidence: [closure record](docs/SUPERVISOR_CAPABILITY_CLOSURE.md). This baseline is not reopened. Live two-AI runtime acceptance remains future dogfood evidence.

## Shared planned-unit contract

Each planned unit starts NOT STARTED; a separate owner assignment is required for IN PROGRESS. Closure requires actual acceptance evidence, source/dependency/runner/config identity per TEST-IDENTITY, positive and negative tests, full ./run.sh test for code/control changes, lint, checker/docs/manifest coherence, truthful counts/exits/skips, preservation, projected/actual transition and owner-authorized closure. Failed/missing/stale evidence holds closure; no automatic NEXT start. Project profile defines applicability. Use a portable assignment/checkpoint/closure packet under WF-PORTABLE. Supervisor recommends; approved owner channel authorizes protected actions. Implementation, closure, commit, preview, tag/push/publication and production are distinct permissions. Changes to distributed bytes require deliberate candidate/version/manifest handling under existing owners; R1 does not predetermine a release number or publish a release.

## STD-TEST-01 — generic executable TEST controls

CLOSED: 0.2.3 FINAL local content; owner-authorized closure decision and final exact evidence in [closure record](docs/packets/STD-TEST-01-CLOSURE.md). Commit identity is the Git commit carrying that record; no self-referential hash. Contract below is retained unchanged.

Purpose: implement the already-defined TEST_DURUM, TEST_LOG, TEST_DEVAM and TEST_DURDUR behavior with one coherent active-job identity and terminal-evidence contract. Baseline: run.sh/project_runner dispatch and reference_tests.py offer bounded synchronous unittest execution; scaffold_status.py queries health, not an active formal test. No executable token adapters exist.

Dependencies: STD-SUP-01 CLOSED. Scope: generic configured interfaces for active formal-job status, redacted log retrieval, identity-bound terminal verification/same-step continuation eligibility, and exact-job safe cancellation. Discover the smallest local job/evidence ownership model during implementation; document storage outside source where mutable, configuration, recovery and unavailable states. Preserve conversational meanings in AGENT_WORKFLOW and evidence rules in TESTING_AND_EVIDENCE. No new authority or second pointer.

Required outcomes/acceptance: status/log do not start/resume/cancel/mutate jobs; logs alone never prove PASS. TEST_DEVAM recognizes RUNNING and terminal exit/count/skip/source staleness and only enables the SAME already-authorized step after valid PASS. TEST_DURDUR targets an identified job with cancellation race/PID-reuse/cross-service protection, retains failure/cancellation evidence, and never returns PASS for cancellation. Missing adapters/jobs/results fail closed with explicit NOT CONFIGURED/PENDING. Tests cover success, failure, skips, missing/stale identity, timeout, redaction, cancellation races and unauthorized scope/NEXT changes; external/live systems are not required.

Closure: shared contract plus reproducible disposable synthetic active/terminal/cancelled job evidence and a fresh-session report; real owner-observed/local stronger protocols remain local. Expected transition: STD-TEST-01 CLOSED makes STD-REL-01 eligible, still NOT STARTED until assigned. Exclusions: TEST/RELEASE implementation during bootstrap; release control code, UI/screenshot engine, distributed worker fleet, provider acceptance, consumer adoption, transport automation, production jobs, broad v0.3.0 operational tooling. No automatic test start merely from status/log tokens.

## STD-REL-01 — validated-candidate commit control

CLOSED: 0.2.4 FINAL local reviewed content; decision and final evidence in [closure record](docs/packets/STD-REL-01-CLOSURE.md). Source identity is the Git commit carrying that record, avoiding self-reference. Original contract below is retained unchanged.

Purpose: execute RELEASE_COMMIT narrowly against an already validated candidate with actual scoped human authorization. Dependencies: STD-TEST-01 CLOSED. Baseline: conversational contract only; Git CLI exists, generic protected commit adapter does not.

Scope/outcomes: explicit project-aware commit interface, candidate/input/index identity preflight, authorization reference, bounded file scope and accurate post-operation HEAD/index report. Candidate validation evidence must exist before execution; invocation does not infer closure, build, retest or broader scope. Decide integration/API details after source inspection, not from this plan.

Acceptance/evidence: disposable Git tests prove validated authorized success, absent/wrong/stale approval rejection, dirty unrelated/index drift rejection or safe bounded preservation, failure/hook behavior and actual HEAD/index reporting even on nonzero exit. No reset/stash/clean/history rewriting or credential exposure. Shared closure contract applies; no real main mutation is a test fixture. Expected transition: CLOSED makes STD-REL-02 eligible; NEXT is not started automatically.

Protected boundary/exclusions: semantic adoption, exceptions and production need their own approvals; no tag/push/release/build/preview, automatic staging of unrelated work, signing identity assertion or generic authority authentication service. Implementation approval cannot authorize the protected commit being tested on a real repository.

## STD-REL-02 — committed-identity isolated preview control

CLOSED: 0.2.5 FINAL local reviewed content; owner decision and final evidence in [closure record](docs/packets/STD-REL-02-CLOSURE.md). Known R1 executable units are fully CLOSED; deferred protocol-stability/transport decision remains separate. Original contract below is retained unchanged.

Purpose: implement RELEASE_PREVIEW as a separately authorized isolated preview, not normal development launch. Dependencies: STD-REL-01 CLOSED and preview-specific owner assignment. Baseline: health scaffold and local commands exist, clean release preview adapter does not.

Scope/outcomes: select an already committed/pinned identity, verify source/config/evidence, obtain declared project preview command and prerequisites, prepare clean isolated staging and report actual startup/health/stop/retention results. No reset of the authoritative worktree, inherited real secrets/shared data or implicit dependency/image installation. Missing preview prerequisites remain NOT CONFIGURED/PENDING.

Acceptance/evidence: disposable source/environment tests cover identity mismatch, dirty inputs, unauthorized/missing prerequisites, secret/data isolation, cleanup/preservation, child failure and truthful health evidence. A mocked launcher proves only isolated interface behavior; any claimed live preview requires actual applicable startup/health evidence. Apply shared closure contract. Expected transition: CLOSED completes known executable-control work; NEXT becomes NONE only through an authorized execution-plan update.

Protected boundary/exclusions: separate preview approval; no production publish/deploy, consumer changes, tag/push, package installer, mandatory Docker or external-service integration. Commit authorization alone never authorizes preview.

## Deferred decision gate

After TEST and RELEASE protocol evidence stabilizes, owner may authorize a separate protocol-stability review and decide whether copy/paste remains sufficient or transport automation merits new roadmap work. No implementation unit or automation permission is created now. Other OPERATIONAL_TOOLING_SCOPE.md rows remain deferred, not silently accepted into this roadmap. Consumer adoption belongs to separately authorized consumer tasks outside this repository roadmap.
