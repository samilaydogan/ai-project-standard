# Testing, QA and evidence

## TEST-APPLICABILITY: Change-specific validation

Targeted development iterations use risk-based targeted/regression checks; security, identity, migration, compatibility and release integrity changes require broader coverage under the local contract. Documentation/governance checkpoints verify affected facts, supported links, adopted invariant integrity and consistency. They are not automatically formal application releases or full-suite runs. Local commands, changed-doc scope and supplemental checks belong to PROJECT_PROFILE.md. The affected-doc gate is explicitly accepted new generic policy.


Facade acceptance: isolate help/doctor/status from mutations; test dispatch, unavailable/invalid commands, literal argv, child exits/signals and compatibility transitions. Static execution structure PASS does not start or validate services or prove installation/recovery. EXECUTION_FACADE.md owns command semantics; this owner retains evidence applicability.

## TEST-FORMAL: Formal application release gate

Every formal application release must pass the project's configured full suite/formal release test gate and applicable package/upgrade gates. The profile/release contract defines what constitutes that gate; an undefined or unrun required gate is PENDING, never PASS. A release cannot be labeled PASS without running the configured gate for the accepted inputs. Reliable existing results may be reused only when TEST-IDENTITY proves unchanged relevant inputs. This universal requirement is explicitly NEW generic standard policy, not unchanged extraction of risk/contract-dependent source practice. Stronger local execution protocols remain in force.

## TEST-GUARDS: Security acceptance and test doubles

Security acceptance cannot be proven by bypassing the guard being accepted. Controlled mocks/test doubles remain valid for unit or negative-path isolation when the claimed scope and limitations are explicit. They must not convert a bypassed production guard, missing live check or mocked launcher into successful security/release acceptance. Isolation and external-data safety belong to SEC-SAFETY.

## TEST-REPORT: Truthful results

Report real command, runtime/context, exit status, passed/failed/skipped counts and limitations. Missing or unavailable evidence is PENDING (or justified NOT APPLICABLE); failed evidence is FAIL; skipped/not-run/stale evidence is never PASS. A suite's aggregate terminal result must disclose skips; an individually skipped requirement remains unverified and blocks acceptance if the local contract requires it. Never fabricate results or approvals. Routine targeted reports need a lightweight source identity only when the local contract requires it, not universal pre/post full fingerprints.

## TEST-IDENTITY: Formal evidence identity

Formal release/closure gates bind evidence to exact relevant source, runner/tooling, dependency/lock identity and sanitized configuration per the local release contract. Use a documented sorted relative-path/SHA-256 member inventory including relevant tests/dependencies/tools and excluding secrets/runtime/generated state. Record pre/post identity when a gate relies on source stability. Record modes/policy identity when artifact contracts depend on them; preserve stronger local formats and attestations. Separate governance identity if closure-only docs are excluded from release-source identity. HEAD alone does not identify an uncommitted tree. Relevant input changes invalidate evidence; never weaken an existing exact-source gate through adoption.

## TEST-CLOSURE: Projected and actual state

For pointer/state-changing closure, record projected/actual stable IDs, status, dependencies, metadata and transition. Apply an existing automated closure gate when applicable and required by the project contract. A manual path is permitted only for documentation/governance-only or equivalent low-risk pointer/state work, with no applicable automated closure gate, explicit local-contract permission and a recorded checklist/result. It never replaces an existing applicable automated formal release/closure gate. If required comparison/evidence is missing or mismatched, closure stays PENDING/FAIL and pointers do not advance. No automation is invented by this policy.

## TEST-SCREENSHOT: Screenshot evidence

The local execution contract/profile must define the screenshot applicability trigger and required route/surface, persona, viewport, supported theme and interaction coverage before accepting UI work. Do not substitute a vague material-change judgment for a declared trigger. Use disposable synthetic data. Real browser artifacts and static template renders are distinct evidence types. Required but unavailable browser evidence is PENDING, never PASS; genuinely inapplicable work records NOT APPLICABLE with rationale. Do not install tooling solely because a template contains a screenshot field. UI implementation applicability belongs to UI-APPLY and UI-LIST.

Day-zero acceptance covers runnable native health and declared profile/environment behavior, plus docker compose config for an applicable Docker reference when available. An unavailable Docker engine/config or image/runtime run is disclosed PENDING/NOT RUN, not PASS. Do not pull/build images, install dependencies or run consumer package/DB commands through an integrity checker. A native default may pass its applicable runtime gate without claiming Docker runtime acceptance. Package/bootstrap state changes require separate safe apply/failure/recovery verification; template interfaces never imply those tests passed.

## TEST-CLASSES: Explicit isolated and live test dimensions

Schema-3 foundation classifies unit, integration, isolated_acceptance, live_acceptance, e2e and screenshot_qa independently as APPLICABLE, NOT_APPLICABLE, PENDING or NOT_CONFIGURED. Applicable mappings declare bounded timeout, network and state. Isolated classes use temporary synthetic state without inherited production credentials; live network is disabled except explicitly authorized live classes. Local stronger gates stay binding. Skip is never PASS, mock/synthetic is never live acceptance, and relevant source/config changes stale evidence. These truth/security boundaries are non-waivable.

The reference test helper is a bounded stdlib-unittest harness, sanitizes its child environment and denies outbound socket connections except loopback before DNS. It supports no live class, sandbox escape, acceptance worker, progress/attestation framework or production-safe test guarantee. Project-owned live/e2e/screenshot adapters require separate authorization and evidence. v0.3.0 owns broader runner design; profile metadata alone cannot enforce arbitrary consumer commands.
