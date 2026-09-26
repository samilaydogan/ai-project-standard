# Migration and release policy

## REL-METADATA: Versions and lifecycle states

Actual source metadata defines app version, compatible base, schema and migration head. Record absent systems as NOT APPLICABLE/PENDING. Standard and application versions are independent. Documentation alone does not bump the app version unless local policy requires it. Distinguish development migration (not distributed), published migration (distributed history), candidate (frozen artifact awaiting required gates), released artifact (accepted immutable identity), and production acceptance (separate authorized environment/external gates). READY standard content does not itself publish an app or Git release.

A REAL newly instantiated consumer initializes its own application version to 0.1.0, independently of standard VERSION. The distributed project-scaffold application 0.0.0 is explicitly internal/reference-only and must not survive unchanged into a real consumer. PROJECT_PROFILE declares the canonical version source; initialize it, profile identity and any editable-root frozen lock metadata coherently, then project state from those facts. Existing consumer adoption/upgrade preserves its actual application version; it never resets it to 0.1.0. The one-time initialization checklist belongs to INSTALLATION.template.md. This is a NEW generic initialization decision, not an executable installer.

## REL-MIGRATION: Development and published migrations

Migrations are forward-only/idempotent; verify isolated upgrade/rerun, constraints/backfill and data/configuration preservation. Schema changes are separate from bulk content migration. A create-tables helper is not proof of an upgrade chain. Development migrations may be revised before distribution under verified local contracts. Published migrations are immutable by default: add successors.

Emergency reconciliation of published history is allowed only under a documented explicitly authorized recovery procedure: incident/recovery rationale; evidence a successor cannot safely solve it; compatibility/data-preservation analysis; before/after artifact identity; migration plus rollback/recovery verification; and audit/changelog record. Do not silently replace already-distributed history: record affected installations, identities, distribution and recovery instructions. This is an explicitly new generic policy, not a claim of unchanged source practice. It cannot waive required security, identity, evidence or release gates.

## REL-RECOVERY: Recovery and cutover

Record backup/source/schema identity before real upgrades. Prefer verified roll-forward; when restoring, restore matching source, database, keys and configuration together. No silent down-migration, source deletion or unapproved destructive reset. Where byte migration applies, checksums/completeness validation precede cutover. Recovery requires explicit safe scope and operator authorization under SEC-SAFETY.

## REL-ARTIFACT: Minimum release evidence

Build from an identified immutable source snapshot; deltas require a verified immutable previous baseline. Minimum evidence records candidate/member inventory and hashes, source/dependency/runner/safe-config identities, app/base/schema/migration metadata, exclusion policy, relevant modes, applicable build/startup/health checks, isolated real upgrade and same-version rerun/preservation results, commands/counts/exits/limits, and required gate statuses. Missing required identity or evidence fails closed. Keep post-build validation/attestation outside frozen candidate identity to avoid self-reference. A mocked launcher is not live container proof. Do not silently rewrite released artifacts. Preserve stronger local fingerprint, format-marker, attestation and reproducibility contracts; generic adoption cannot replace them with weaker evidence.

RELEASE_COMMIT authorizes only committing an already validated candidate. It does not implicitly authorize closure, build, retest, tag, push, production publish/deployment or new feature scope. If a local commit adapter returns nonzero, inspect and report actual HEAD/index: failure exit does not prove no Git mutation. A candidate or closure is not commit authority.

RELEASE_PREVIEW is a separately authorized clean isolated preview of an already committed/pinned release identity with source/config identity recorded. Do not substitute normal dev launch, reset source, copy real secrets or attach shared production data. Missing project-local preview tooling is NOT CONFIGURED/PENDING; no engine is supplied. Owner first-install confirmation establishes delivery eligibility only, never unrelated runtime, formal release or production acceptance.

## REL-PRODUCTION: Release versus production authorization

Required formal testing/closure gates belong to TEST-FORMAL/TEST-CLOSURE. Technical acceptance and production authorization are separate. Required live/provider/field/legal/deployment approvals remain PENDING until actual scoped evidence and authorization exist; local protocol tests cannot replace them. Production publishing/commit/deployment require actual user scope and the local contract. A technical release may retain explicit external debt only where its contract permits; this never grants production acceptance.

Explicit package application is separate from dependency preparation and runtime startup; EXECUTION_FACADE.md owns routing. Optional apply-package must retain local identity/backup/recovery gates. A facade does not implement missing attestation or live upgrade acceptance.

## REL-APPLY-STATE: Source, state and artifact separation

Keep four owners distinct: (1) version-controlled PROJECT SOURCE, (2) application RUNTIME STATE, (3) mutable PACKAGE-APPLY STATE, (4) RELEASE/HANDOFF ARTIFACTS. Previous payload/snapshots, pre-apply rollback backups, delta extraction/staging, apply manifests/journals and verification metadata must use an external configurable package_apply.state_root. Released ZIPs/manifests/attestations/handoff bundles use an external storage.artifact_root. Roots may be configured relative to source (resolved externally) or per-user/installer-owned locations; no platform-specific absolute path is invariant. A root must neither be inside source nor contain source, including through symlinks. Each consumer chooses collision-safe local ownership and retention/recovery policy. Runtime data has separately declared roots; it is not package-apply state.

Version-controlled installer code, neutral templates and intentional synthetic fixtures are actual project content; their presence is not permission to keep mutable snapshots/backups in source. Do not generalize historical project-root previous/apply folders. Existing local state is truthful migration debt: preserve bytes, identities and readers until an explicitly authorized migration proves collision safety, failure/recovery and compatible pointers. Do not delete/move it as hygiene or invent migration acceptance.

This new owner-accepted distribution/state safety boundary is NON-WAIVABLE in this release. The owner's explicit MUST boundary is enforced uniformly instead of granting automatic legacy exceptions; runtime data/source preservation remains protected. A consumer with root-local active apply state cannot close unqualified Mode B adoption until migration or genuinely inapplicable package delivery is source-backed. Merely relabeling an active updater as NOT APPLICABLE is not compliance. This is new generic policy, not unchanged extraction of every source-project path.

## REL-DATA-CONTRACT: Explicit database, persistence, migration and backup applicability

Schema-3 foundation declares database none/embedded/container/external and none/sqlite/postgres/mysql/project_defined engine. No engine is universal. Stateful choices declare isolated test DB, host/name/ports, symbolic secret env mapping, health argv and data owner as applicable. Container DB has a distinct declared Compose database-role service with coherent env/health/volume; external DB has no local DB-role service. Named volumes use volume:name; source-local data requires unified exclusions. Runtime storage lists must match declared persistent roots.

Migration applicability, forward-idempotent strategy, current/target/version source, preflight and recovery are explicit. Source behind DB fails closed; automatic_down_migration is false. Partial recovery and compatibility of data/schema/source are documented. A stateful schema exempt from migrations records a rationale in its recovery document; missing tools are PENDING/NOT_IMPLEMENTED, not acceptance. REL-MIGRATION owns published immutability and emergency procedure.

Backup applicability declares scope, external root, retention, integrity metadata, verify/drill and restore command availability. Formal backup claims require identity/hash; destructive restore needs explicit confirmation, pre-restore safety backup, data/schema/source compatibility and secure key preservation. Required migration backup cannot be absent or pending at execution acceptance. Static schema validation does not run or prove migration, backup, restore or recovery. No generic engine is supplied in v0.2.0.
