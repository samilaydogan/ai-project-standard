# Adoption, exceptions and upgrades

## ADP-INTEGRITY: Reviewed content and portable validation

Audit current source/metadata/governance and safe commands before adoption. Select reviewed content, verify the complete standard release manifest, and pin its SHA-256 plus version in standard-adoption.json. Copy the manifest's required invariant set exactly. Instantiate required project-owned documents from facts; unknowns stay PENDING. Hash integrity detects drift, not malicious replacement of both manifest and pin: reviewers must use a trusted source/checker.

A consumer retains a complete pinned companion snapshot at `.project-standard/<version>/`, consisting of every release-listed file and standard-release.json, or explicitly supplies an independently obtained matching snapshot. Default portable commands: `python3 -B scripts/check_standard.py` and `python3 -B scripts/check_docs.py .`. No unversioned sibling is required. Explicit CLI: `python3 -B scripts/check_standard.py --standard /path/to/pinned/snapshot --consumer /path/to/consumer`. Copies of both checkers, ADOPTION.md and POLICY_RULES.json are invariants. Audit reports are excluded from distribution.

Local reviewed content snapshots are allowed without inventing a commit/tag. Record exact hash and source kind; READY/FINAL means validated content, not already published immutable Git history. Before public Git release distribution use a reviewed immutable tag/commit and retain the manifest. Earlier unaccepted/unpublished DRAFT/RC bytes are not final released history. No automatic remote upgrade or custom package manager is introduced.

## ADP-STRUCTURE: Required adoption structure and states

POLICY_RULES.json and the trusted checker define the documented fixed invariant/distribution/required project-document sets. Required project-owned inventory: PROJECT_PROFILE.md, PROJECT_STATE.md, EXECUTION_PLAN.md, CAPABILITY_CATALOG.md, ROADMAP_CHANGELOG.md, HANDOFF.md and STANDARD_ADOPTION_HISTORY.md. Optional JSON state projects the same facts. Manifest schema 2 records standard/version/date/source reference, release hash, all invariant hashes, owned files, exceptions and semantic_acceptance.

Separate: INTEGRITY PASS (listed bytes/pin match); ADOPTION STRUCTURE PASS (required artifacts and exception metadata valid); SEMANTIC ACCEPTANCE APPROVED/PENDING (recorded human decision for this exact hash); and runtime/release acceptance (not assessed by these checkers). APPROVED requires real authority/date/decision reference, scope, reviewed manifest hash and an owned evidence file; the checker validates that record, not the person's authority or the evidence's factual quality. Never infer approval from hash equality. `--require-semantic` fails unless the recorded acceptance is APPROVED. A PENDING record is a valid structure but not accepted adoption.

## ADP-EXCEPT: Non-waivable core and narrow exceptions

The registry marks core rules non-waivable. No exception may waive truthful reporting, fabricated approval/PASS/evidence prohibitions, secret protection, formal exact identity, required fail-closed security/authorization, required formal release/closure gates or production/shared-data safety. Mechanism/integrity rules are protected too. A profile may strengthen or select explicitly permitted applicability; implementation debt remains truthful debt, not an invented compliance claim.

A waivable-rule exception requires a unique id, real rule ID and its canonical owner path, specific scope/reason/risk/compensating_control, actual approved_by and approved_on, review_on and APPROVED status. Approval cannot be in the future; review remains valid through its date in UTC and expiry blocks structure. Record decisions in STANDARD_ADOPTION_HISTORY.md. A new standard hash requires explicit re-review and updated semantic acceptance; the checker cannot authorize human decisions.

Copied-file drift additionally requires exact expected_sha256. Only the named waivable Markdown rule block may change; the preamble and every other block remain byte-identical. Multiple changed blocks need individual eligible exceptions, all pinned to the same actual file hash. No checker, registry or non-waivable block drift is permitted. Semantic exceptions without file drift still require real eligible rule IDs and narrow scope. Never use a waiver to bypass a protected rule via another block; reviewers must reject such conflicting changes even if structural checks pass. Integrity tooling proves block boundaries/hashes, not semantic equivalence.

## ADP-UPGRADE: Reviewed upgrades and adoption history

Review old/new changelog, rule differences, immutable manifests/references and consumer effects. Preserve the prior pin/copies/profile/exceptions; copy reviewed invariants, deliberately merge project facts, re-review exceptions and update version/reference/release hash/invariant map together. Run integrity/structure, bounded docs checks and relevant local validation. Record review/approval/result/debt in STANDARD_ADOPTION_HISTORY.md and reference it in handoff. Change product ROADMAP_CHANGELOG only if product scope/order/dependency actually changes. No auto-upgrade when a remote branch moves. On failure keep accurate PENDING state; restore only your own safely revertible adoption change. Application/data recovery belongs to REL-RECOVERY.
