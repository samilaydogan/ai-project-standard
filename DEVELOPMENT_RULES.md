# Development rules

Canonical general engineering rules; security, evidence, release and UI details defer to their respective owners under [DOCUMENT_GOVERNANCE.md](DOCUMENT_GOVERNANCE.md).

## DEV-BOUNDARY: Contracts and ownership

Current source and explicit contracts win over assumptions. Keep domain ownership and public compatibility boundaries explicit in PROJECT_PROFILE.md. A shared service must not silently absorb a consuming application's business authorization. This generic ownership rule is explicitly accepted new policy, informed by source ownership practice.

## DEV-CHANGE: Focused compatible changes

Prefer existing contracts and focused changes; do not weaken tests to obtain PASS. Versioned behavior uses explicit contract/format markers where available, not incidental release numbers. Preserve historical regression facts. Breaking changes require compatibility analysis, an upgrade path and explicit acceptance. Preserve data/configuration and identity semantics.

## DEV-REMOTE: Remote mutations

For operations with external side effects, define timeout/retry limits and whether retry is safe under the transport/provider contract. Where duplicate execution is possible, specify idempotency or reconciliation before enabling retries. Never automatically retry an ambiguous unsafe action. Test concurrency, replay, negative paths and idempotency where applicable; do not claim controls absent from source. This generalizes domain-specific practice and does not require unsupported provider features.

## DEV-HYGIENE: Source artifacts

Exclude secrets, runtime state, backups, database volumes, caches, OS metadata and generated evidence from source/release artifacts, even if historically tracked. Preserve local bytes; do not delete them as routine hygiene. Unrelated working-tree changes do not themselves require a clean repository. Release snapshot exclusions and identities belong to REL-ARTIFACT.


Execution hygiene: preserve lock/manifests unless their change is authorized. Runtime startup, environment dependency preparation and release artifact application are distinct; execution behavior belongs to [EXECUTION_FACADE.md](EXECUTION_FACADE.md), artifact recovery to MIGRATION_AND_RELEASE_POLICY.md. No actor-exclusive package-manager policy is implied.

## DEV-LICENSE: Dependency review

Before adopting a third-party dependency, record version, source, license/redistribution decision and shipped assets. Missing rights require review, not assumed permission. This explicitly new generic scope includes all third-party dependencies; product budgets, approved stacks and stronger local rejection rules remain local. It does not provide legal approval.

Source hygiene distinguishes source, runtime state, package-apply state and release/handoff artifacts. Canonical external apply/artifact ownership is REL-APPLY-STATE, not an invitation to retain root snapshots under an ignore rule. Checked-in environment contract and runtime-local ignored env belong to SEC-ENV; explicit runtime/network configuration belongs to EXEC-RUNTIME. Preserve unrelated historical/local bytes while recording migration debt.

## DEV-FOUNDATION: Explicit day-zero identity, toolchain and source exclusions

Schema-3 execution-profile.json declares identity/version source, runtime range, dependency manifest/lock identities, build/test/lint runners, entrypoint and facade. It is language-neutral; the Python stdlib implementation is a reference. Manifest/lock changes are explicit reviewable work. Normal run.sh never silently resolves or updates dependencies. Frozen preparation is distinct from resolution. Known PEP 621/npm and uv/package-lock adapters check limited structural coherence plus hashes/review binding; declared other formats require local semantic verification. Hash equality is not dependency-solver correctness. A no-lock policy is explicit local review debt unless the parsed manifest has no third-party dependencies.

source-exclusions.json is the single project-owned path inventory for Git, Docker context when applicable, source release/packages, future fingerprints and handoffs. Secrets, dependency caches, runtime/DB data, backups, apply state and test/build artifacts must be excluded. .env.example is a reviewed safe source exception. Static matching supports bounded glob/directory forms, not every Git/Docker ignore semantic. Releases use an explicit member allowlist and reject excluded members. Backup/apply/artifact boundaries remain under their canonical owners. No future builder/fingerprint engine is implied.
