# Agent workflow

Normative owners and precedence are defined in [DOCUMENT_GOVERNANCE.md](DOCUMENT_GOVERNANCE.md). Rule metadata is in [POLICY_RULES.json](POLICY_RULES.json); summaries below defer to their detailed owners.

## WF-PRESERVE: Preflight and preservation

Read the profile, adoption manifest, state, handoff and execution plan. Audit branch, HEAD, status/diff, local modifications, runtime paths, metadata and evidence. Preserve unrelated work. Do not reset, stash, clean or overwrite it to make checks pass. Follow explicit read-only boundaries; an isolated checkout must not discard authoritative uncommitted source.

## WF-SCOPE: Authorized execution

Act within the authorized CURRENT contract, source truth and verified dependencies. Keep edits bounded. Future intent is not implementation. Do not begin NEXT automatically. Isolated branches/worktrees or disposable test staging may be used when useful.

## WF-COMMANDS: Local execution protocol

Use commands and safe environments owned by PROJECT_PROFILE.md. Run applicable checks, await terminal evidence and diagnose environment failures within a bounded scope. A user-observed long-run protocol applies only when explicitly declared locally. This generic model is a new standard choice; it does not replace a consumer's stronger existing protocol or invent missing tooling.

## WF-CLOSURE: Closure orchestration

Before CLOSED, verify CURRENT acceptance, positive/negative guards, preservation, metadata and document/catalog alignment. Detailed test identity, projected/actual and screenshot evidence belong to [TESTING_AND_EVIDENCE.md](TESTING_AND_EVIDENCE.md); migration/artifact gates belong to [MIGRATION_AND_RELEASE_POLICY.md](MIGRATION_AND_RELEASE_POLICY.md). Update history and CURRENT/NEXT only after required gates pass. Documentation/governance closure is separate from application release. Closure, commit, artifact creation and production deployment are separately authorized actions. This summary cannot weaken an owner's gate.

## WF-HANDOFF: Reporting and transfer

Report changed files, applicable source identity, actual commands/results, limitations and pointers. Preserve useful work and a safe resumption point if blocked. Transfer sanitized full required source, lockfiles, governance and the pinned companion standard; a delta alone is not self-contained. Secret/data safety belongs to [SECURITY_BASELINE.md](SECURITY_BASELINE.md). Templates, mocks and static renders are not release or approval proof.
