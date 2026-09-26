# Migration and release policy

## REL-METADATA: Versions and lifecycle states

Actual source metadata defines app version, compatible base, schema and migration head. Record absent systems as NOT APPLICABLE/PENDING. Standard and application versions are independent. Documentation alone does not bump the app version unless local policy requires it. Distinguish development migration (not distributed), published migration (distributed history), candidate (frozen artifact awaiting required gates), released artifact (accepted immutable identity), and production acceptance (separate authorized environment/external gates). READY standard content does not itself publish an app or Git release.

## REL-MIGRATION: Development and published migrations

Migrations are forward-only/idempotent; verify isolated upgrade/rerun, constraints/backfill and data/configuration preservation. Schema changes are separate from bulk content migration. A create-tables helper is not proof of an upgrade chain. Development migrations may be revised before distribution under verified local contracts. Published migrations are immutable by default: add successors.

Emergency reconciliation of published history is allowed only under a documented explicitly authorized recovery procedure: incident/recovery rationale; evidence a successor cannot safely solve it; compatibility/data-preservation analysis; before/after artifact identity; migration plus rollback/recovery verification; and audit/changelog record. Do not silently replace already-distributed history: record affected installations, identities, distribution and recovery instructions. This is an explicitly new generic policy, not a claim of unchanged source practice. It cannot waive required security, identity, evidence or release gates.

## REL-RECOVERY: Recovery and cutover

Record backup/source/schema identity before real upgrades. Prefer verified roll-forward; when restoring, restore matching source, database, keys and configuration together. No silent down-migration, source deletion or unapproved destructive reset. Where byte migration applies, checksums/completeness validation precede cutover. Recovery requires explicit safe scope and operator authorization under SEC-SAFETY.

## REL-ARTIFACT: Minimum release evidence

Build from an identified immutable source snapshot; deltas require a verified immutable previous baseline. Minimum evidence records candidate/member inventory and hashes, source/dependency/runner/safe-config identities, app/base/schema/migration metadata, exclusion policy, relevant modes, applicable build/startup/health checks, isolated real upgrade and same-version rerun/preservation results, commands/counts/exits/limits, and required gate statuses. Missing required identity or evidence fails closed. Keep post-build validation/attestation outside frozen candidate identity to avoid self-reference. A mocked launcher is not live container proof. Do not silently rewrite released artifacts. Preserve stronger local fingerprint, format-marker, attestation and reproducibility contracts; generic adoption cannot replace them with weaker evidence.

## REL-PRODUCTION: Release versus production authorization

Required formal testing/closure gates belong to TEST-FORMAL/TEST-CLOSURE. Technical acceptance and production authorization are separate. Required live/provider/field/legal/deployment approvals remain PENDING until actual scoped evidence and authorization exist; local protocol tests cannot replace them. Production publishing/commit/deployment require actual user scope and the local contract. A technical release may retain explicit external debt only where its contract permits; this never grants production acceptance.
