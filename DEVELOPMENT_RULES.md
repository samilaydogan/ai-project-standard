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

## DEV-LICENSE: Dependency review

Before adopting a third-party dependency, record version, source, license/redistribution decision and shipped assets. Missing rights require review, not assumed permission. This explicitly new generic scope includes all third-party dependencies; product budgets, approved stacks and stronger local rejection rules remain local. It does not provide legal approval.
