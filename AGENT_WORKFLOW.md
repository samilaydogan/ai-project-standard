# Agent workflow

Normative owners and precedence are defined in [DOCUMENT_GOVERNANCE.md](DOCUMENT_GOVERNANCE.md). Rule metadata is in [POLICY_RULES.json](POLICY_RULES.json); summaries below defer to their detailed owners.

## WF-PRESERVE: Preflight and preservation

Read the profile, adoption manifest, state, handoff and execution plan. Audit branch, HEAD, status/diff, local modifications, runtime paths, metadata and evidence. Preserve unrelated work. Do not reset, stash, clean or overwrite it to make checks pass. Follow explicit read-only boundaries; an isolated checkout must not discard authoritative uncommitted source.

## WF-SCOPE: Authorized execution

Act within the authorized CURRENT contract, source truth and verified dependencies. Keep edits bounded. Future intent is not implementation. Do not begin NEXT automatically. Isolated branches/worktrees or disposable test staging may be used when useful.

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

## WF-HANDOFF: Reporting and transfer

Report changed files, applicable source identity, actual commands/results, limitations and pointers. Preserve useful work and a safe resumption point if blocked. Transfer sanitized full required source, lockfiles, governance and the pinned companion standard; a delta alone is not self-contained. Secret/data safety belongs to [SECURITY_BASELINE.md](SECURITY_BASELINE.md). Templates, mocks and static renders are not release or approval proof.
