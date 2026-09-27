# Agent workflow

Normative owners and precedence are defined in [DOCUMENT_GOVERNANCE.md](DOCUMENT_GOVERNANCE.md). Rule metadata is in [POLICY_RULES.json](POLICY_RULES.json); summaries below defer to their detailed owners.

## WF-PRESERVE: Preflight and preservation

Read the profile, adoption manifest, state, handoff and execution plan. Audit branch, HEAD, status/diff, local modifications, runtime paths, metadata and evidence. Preserve unrelated work. Do not reset, stash, clean or overwrite it to make checks pass. Follow explicit read-only boundaries; an isolated checkout must not discard authoritative uncommitted source.

## WF-SCOPE: Authorized execution

Act within the authorized CURRENT contract, source truth and verified dependencies. Keep edits bounded. Future intent is not implementation. Do not begin NEXT automatically. Isolated branches/worktrees or disposable test staging may be used when useful.

Within that boundary, the coding agent may inspect, implement, debug, run applicable checks and resolve routine engineering choices without repeated `continue` prompts. A Supervisor reasoning layer may interpret the roadmap, request bounded investigation, propose architecture or corrections and review a closure candidate. Neither role name grants new approval power. Stop for review when a choice would materially change architecture, roadmap scope/order/dependencies, security or compatibility boundaries, required acceptance, or closure; preserve a safe checkpoint when authority or evidence is missing. Existing owner/human approval boundaries for exceptions, semantic adoption, commits, releases and production remain with their canonical owners.

Ordinary `continue` resumes only bounded CURRENT/already-authorized scope. HOLD preserves a safe checkpoint. These six conversational tokens express intent; backend availability is separately declared in PROJECT_PROFILE.md under EXEC-MUTATION, never inferred from a token.

| Owner token | Bounded conversational semantics |
| --- | --- |
| TEST_DURUM | Query only the currently active formal test via a declared actually-read-only status adapter; no start/resume/closure authority. If unavailable report NOT CONFIGURED / PENDING. |
| TEST_LOG | Read and redact only the current test log. Log text alone cannot establish terminal PASS; identity/exit/count evidence is required. |
| TEST_DEVAM | Verify the identity-bound terminal result. PASS resumes only the SAME already-authorized step; RUNNING continues waiting; failed/missing/stale results keep a safe checkpoint. No new scope or NEXT auto-start. |
| TEST_DURDUR | Identify the exact active job and use only its declared safe cancellation mechanism. No blind kill, PID reuse or cross-service interruption. If safe cancellation is unavailable, report NOT CONFIGURED. |
| RELEASE_COMMIT | Explicit human commit authorization for an ALREADY VALIDATED candidate. No implicit closure/build/retest/tag/push/production publish/deployment or new scope. Local mapping may be NOT CONFIGURED; inspect actual HEAD/index after any attempt, including nonzero exit. |
| RELEASE_PREVIEW | Separate authorized preview of an already committed/pinned release identity in a clean isolated environment. No dev-launch substitution, source reset, copied real secrets or shared production data. Local mapping may be NOT CONFIGURED. |

Detailed evidence belongs to TEST-REPORT/TEST-IDENTITY; release identity and delivery boundaries to REL-ARTIFACT/REL-PRODUCTION. Closure is not RELEASE_COMMIT authorization. Candidate creation is not production publish. Owner first-install confirmation affects delivery eligibility only; it does not establish unrelated runtime/release acceptance.

## WF-COMMANDS: Local execution protocol

Use applicable project-owned commands through the declared execution facade; [EXECUTION_FACADE.md](EXECUTION_FACADE.md) owns dispatch and mutation boundaries. PROJECT_PROFILE.md owns safe environments and stronger local protocols. Run applicable checks, await terminal evidence and diagnose environment failures within a bounded scope. A user-observed long-run protocol applies only when explicitly declared locally. This generic model is a new standard choice; it does not replace a consumer's stronger existing protocol or invent missing tooling.

## WF-CLOSURE: Closure orchestration

Before CLOSED, verify CURRENT acceptance, positive/negative guards, preservation, metadata and document/catalog alignment. Detailed test identity, projected/actual and screenshot evidence belong to [TESTING_AND_EVIDENCE.md](TESTING_AND_EVIDENCE.md); migration/artifact gates belong to [MIGRATION_AND_RELEASE_POLICY.md](MIGRATION_AND_RELEASE_POLICY.md). Update history and CURRENT/NEXT only after required gates pass. Documentation/governance closure is separate from application release. Closure, commit, artifact creation and production deployment are separately authorized actions. This summary cannot weaken an owner's gate.

Finishing implementation permits a closure-candidate report, not CLOSED. A Supervisor review recommendation or packet cannot itself advance CURRENT/NEXT or authorize protected release actions. Apply the existing closure gate and actual authorized decision before any transition.

## WF-PORTABLE: Account- and session-independent work transfer

Correctness-critical scope, decisions, state and evidence must be reconstructable from durable project/source records plus an explicit portable packet for the current transfer. A formal handoff may retain or reference that packet; neither substitutes for the durable records. The recipient must be able to access the cited records and verify protected decisions through the approved authority channel. Never rely solely on a shared account, chat history, hidden memory or session state. A new coding-agent session must re-read the active standard identity (pinned companion when adopted), project profile, single live execution plan, state, handoff, source/diff and current assignment packet; a new Supervisor session must be able to review the returned packet and cited evidence without the coding agent's conversation. If required authority or facts cannot be reconstructed, report the gap and continue only independently safe work within the verified boundary.

An assignment/handoff, bounded investigation request/report, meaningful checkpoint or closure candidate uses the same transport-neutral envelope whether copied manually, transferred as a file or routed by future tooling. Carry packet kind/ID and task ID; issuer role and decision authority/reference; time; active standard identity/pin where applicable and source/HEAD plus relevant uncommitted-diff identity; authorized scope and exclusions; planning locator/revision and declared-versus-directly-verified status; applicable gates; observations separated from assertions; evidence references and required hashes; authorized decisions, unresolved questions, requested next decision and safe work while waiting. Transport the bounded decision/evidence subset and durable references, not an unnecessary copy of full project state. Cite the canonical source for each fact and redact secrets. Missing fields are explicit PENDING/NOT APPLICABLE with rationale, never silently inferred. `SUPERVISOR_PACKET.template.md` in the active standard or pinned companion is a supporting form, not another rule owner.

A packet is not self-authenticating or a second CURRENT/NEXT owner. Verify protected-action authority through the project's approved channel; an AI Supervisor may recommend but has no delegated approval power by title. PACKET references and optional state projections cannot replace EXECUTION_PLAN.md, TEST-CLOSURE, ADP-STRUCTURE or release authorization.

## WF-HANDOFF: Reporting and transfer

Report changed files, applicable source identity, actual commands/results, limitations and pointers. Preserve useful work and a safe resumption point if blocked. Transfer sanitized full required source, lockfiles, governance and the pinned companion standard; a delta alone is not self-contained. Secret/data safety belongs to [SECURITY_BASELINE.md](SECURITY_BASELINE.md). Templates, mocks and static renders are not release or approval proof.
