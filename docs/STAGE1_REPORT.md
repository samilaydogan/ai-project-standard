# Historical Stage 1 report — superseded readiness assessment

The following is the initial Stage 1 record, retained as history. Its usable/READY and semantic-adoption assumptions were superseded by the full provenance audit: the prior unpublished hash was DRAFT/RC, and consumer integrity was not semantic acceptance. The authorized reconciliation result is in [RECONCILIATION_VALIDATION.md](RECONCILIATION_VALIDATION.md), with [NEW_POLICY_REGISTER.md](NEW_POLICY_REGISTER.md). The initial `.gitattributes` inventory entry was pre-existing, not Stage 1-created. Initial protected evidence qualifications remain historical facts.

---

# Stage 1 completion report — 2026-09-26

## Generic standard

Repository: `/Users/samil/Documents/GitHub/ai-project-standard`; branch `codex/stage1-standard-baseline`; HEAD `43f9801e75ee3a394495a6ac1b001811c28a3003` (initial repository commit unchanged). Standard **0.1.0** prepared as local uncommitted content; no release tag, Git commit, push or application runtime created. User explicitly authorized using the already-created empty repository, overriding the original stop-if-existing condition.

[Extraction matrix](EXTRACTION_MATRIX.md): 173 root/docs/process candidates classified before creating baseline files. No entire candidate qualified as A (generic as-is); B files were rewritten/parameterized, C structures became fact-free templates, D business/legal/application material was excluded. [Provenance](PROVENANCE.md) records each result's origins, generalization/removal and copy/template treatment. Audit source identifiers live only in provenance records, never generic policy assumptions.

Final inventory:

- `.gitattributes`
- `ADOPTION.md`
- `AGENT_WORKFLOW.md`
- `CAPABILITY_CATALOG.template.md`
- `CHANGELOG.md`
- `DEVELOPMENT_RULES.md`
- `DOCUMENT_GOVERNANCE.md`
- `EXECUTION_PLAN.template.md`
- `HANDOFF.template.md`
- `MIGRATION_AND_RELEASE_POLICY.md`
- `PROJECT_PROFILE.template.md`
- `PROJECT_STATE.template.json`
- `PROJECT_STATE.template.md`
- `README.md`
- `ROADMAP_CHANGELOG.template.md`
- `SECURITY_BASELINE.md`
- `TESTING_AND_EVIDENCE.md`
- `UI_IMPLEMENTATION_STANDARDS.md`
- `VERSION`
- `docs/EXTRACTION_MATRIX.md`
- `docs/PROVENANCE.md`
- `docs/evidence/protected-summary.json`
- `scripts/check_docs.py`
- `scripts/check_standard.py`
- `standard-adoption.template.json`
- `standard-release.json`
- `docs/STAGE1_REPORT.md` (this audit-only report).

Consumer model: eight unchanged invariant files, project-owned instantiated documents, SHA-256-pinned version/release manifest, explicit approved/review-dated exceptions (none for the first consumer), reviewed manual upgrades with atomic pin/hash updates. Release hashes give a stable content pin without fabricating an immutable Git tag. A reviewed immutable release reference should be published later before broader distribution; no automatic package manager or remote upgrade is introduced.

Quality: policy/template vocabulary leak check, placeholders, relative file links, version/hash integrity and consistency checks PASS. Explicit review of business/provider/project-name terms found only source filenames and audit provenance in non-distributed audit docs; no business entities, roles, provider names, source release facts or source roadmap IDs in generic invariants/templates. Standard v0.1.0 is usable for new local projects with its verified manifest; publication/remote release was not requested.

## AuthHub adoption

Repository: `/Users/samil/Documents/GitHub/ai-auth-hub`; branch `codex/stage1-standard-adoption`; HEAD `c3c3e51bd32a8cd1bfcb34ceb7428eb516bb6a2d` unchanged. Standard **0.1.0** adopted; [consumer audit](../../ai-auth-hub/docs/STANDARD_ADOPTION_AUDIT.md), [manifest](../../ai-auth-hub/standard-adoption.json) and [validation](../../ai-auth-hub/docs/STAGE1_VALIDATION.md) hold detailed evidence.

Changed existing file: `README.md` (additive governance entry). Added:

- `AGENT_WORKFLOW.md`
- `CAPABILITY_CATALOG.md`
- `DEVELOPMENT_RULES.md`
- `DOCUMENT_GOVERNANCE.md`
- `EXECUTION_PLAN.md`
- `HANDOFF.md`
- `MIGRATION_AND_RELEASE_POLICY.md`
- `PROJECT_PROFILE.md`
- `PROJECT_STATE.json`
- `PROJECT_STATE.md`
- `ROADMAP_CHANGELOG.md`
- `SECURITY_BASELINE.md`
- `TESTING_AND_EVIDENCE.md`
- `UI_IMPLEMENTATION_STANDARDS.md`
- `docs/CURRENT_ARCHITECTURE.md`
- `docs/STAGE1_VALIDATION.md`
- `docs/STANDARD_ADOPTION_AUDIT.md`
- `scripts/check_standard.py`
- `standard-adoption.json`

Source truth: Google broker authorize/callback/token/userinfo; central User/ExternalIdentity; exact callback allowlist; required S256 PKCE; hash-backed consumed transactions/codes, opaque bearer tokens; SiteMembership.id as client-specific sub; hint-matched central session reuse; setup/admin/client UI and file config/SQL state. Capability catalog records bounded source implementation, verification limits and disabled UI scaffolds without promising new integrations. Consumer business authorization remains outside AuthHub.

Execution: BASELINE-1 CLOSED (documentation only), CURRENT NONE, NEXT STAGE2-PLANNING PENDING/NOT STARTED. No earlier historical roadmap or release closure fabricated. Stage 2 feature sequence/dependencies/acceptance/release families intentionally PENDING. Current debt includes missing migration chain/general revocation/security audit, process-local locking/rate limits, nonce without ID-token validation, logout without server-wide revocation and unverified production/replica/PostgreSQL/live acceptance. These are absence statements, not an executable feature plan.

Validation: root **88 passed / 6 skipped**, example **3 passed**, exit 0. Skips require unavailable historical ZIPs. Active source/example lint PASS; whole-repo lint **36 I001 findings**, exit 1, all existing hidden backup/update copies. 37 Python files parsed successfully; no configured type checker. Real initial harness failure (HOME omitted) corrected without source/test changes; deprecation warning recorded. Integrity happy path and five fail-closed negative probes, docs/link/leakage/state/whitespace checks and `git diff --check` PASS. Browser QA NOT APPLICABLE (UI unchanged); live Google, actual Docker/ZIP upgrade, production logging/TLS, PostgreSQL and deployment acceptance PENDING. See consumer validation for exact commands/environment/source hashes.

Consumer initial byte audit: all 263 initial files preserved except authorized README append; pre-existing `.DS_Store` change preserved. Runtime/application versions, locks, update/backups and persistent state untouched. Git changes are new docs/checker/manifest plus README; `.DS_Store` was already modified at start. No staging, commits or push performed.

## Protected repository verification and safety

[Permanent protected summary](evidence/protected-summary.json) compares pre/post full non-Git file SHA-256 maps and Git HEAD/branch/status/worktree-list/binary-diff identity. Main tree: 5,940 files; source/governance/L/112 and Git state identical, but two ignored OS metadata files (`.DS_Store`, `docs/.DS_Store`) differ. Consequently whole-directory byte equality is **not** claimed. No write, checkout, commit, reset, stash, clean, release or pointer operation was performed there; the metadata difference's origin is not established by the snapshots and was not reverted. Preview tree: 512 files, exact byte-map and Git-state equality.

All protected roadmap pointers/release metadata and active L/112 source match initial bytes. Initial modified/untracked work is preserved. This qualification is explicit rather than hiding OS metadata changes behind an absolute unchanged-worktree claim.

No production OAuth call, real credential use, production/shared persistent DB mutation, future AuthHub feature implementation or future-direction input occurred. Package-index access installed frozen test dependencies only; tests ran from a disposable credential-free source copy with real IP socket connections blocked.

Temporary detailed initial/final snapshots, source manifests, negative probes and test outputs: `/private/tmp/stage1-baseline/`. Permanent consumer validation and this report retain essential results and identities without including raw runtime data, credentials or personal profiles.

## Exact next task — not started

**Stage 2: Audit the current AuthHub baseline, introduce the future-direction note explicitly as product intent, design the future identity architecture and produce an executable AuthHub roadmap with source-backed gaps, ordered dependencies, per-step goals/non-negotiables/acceptance, security/compatibility/migration evidence gates and CURRENT/NEXT discipline. Separate implemented, partial, pending and not-started states; do not implement features during planning.**

Stage 1 stops here. No Stage 2 work begun.
