# {{PROJECT_NAME}} operations runbook

Start in foreground with `./run.sh dev` / `./run.sh start`. `./run.sh status` / `./run.sh health` perform only a local health probe, exit 0 for the reference contract and exit 3/PENDING otherwise. They do not start, migrate, restore, install or call providers. `./run.sh doctor` checks declared prerequisites/applicability statically; it cannot certify production acceptance.

The reference emits bounded JSONL response events to stderr, with generated correlation IDs and status only. It never logs headers, query strings, request bodies or personal data. Startup address is a diagnostic line on stdout. Health/readiness are the same stateless reference endpoint. No business telemetry, log rotation or support-bundle builder is included; retention is explicitly NOT_APPLICABLE for this foreground reference. A deployment owner must set retention and access control before retained production logging.

There is no database, queue, authentication, blob storage or backup engine. Select applicability explicitly before adding any. Background work, if introduced, needs persistence/retry/idempotency ownership and health/status applicability. Bounded retry, leases/recovery and dead-letter handling are optional stronger local patterns, not a provided queue. External authentication never owns consumer business authorization; sessions and local authorization remain project-owned.

Tests use temporary synthetic state, a bounded timeout, loopback-only networking and a sanitized child environment. Unit and isolated acceptance are applicable; integration, live acceptance, e2e and screenshot QA are NOT_APPLICABLE for this health-only baseline. Mock/synthetic PASS is not live acceptance; skip is not PASS. Failed/unavailable checks remain failed/PENDING. Record real command, context, counts, exit and limitations; invalidate evidence after relevant source/config changes.

Troubleshooting: check Python availability and `doctor`, inspect the declared host port for collisions, and run the safe local health command after startup. Do not paste .env or secret-bearing logs into reports. Stop with Ctrl-C; there is no silent service restart. Source exclusions govern Git, Docker, source release, fingerprints and handoffs. Mode B packages require an external bootstrap/applier, external apply state, and reviewed recovery acceptance. The optional Compose example needs separate config and runtime evidence. Production/shared-data changes require the deployment owner's authorization and local stronger gates.

## Instantiation record

Declare actual owners, command mappings, modes, paths, applicability, evidence and unresolved debt: {{PROJECT_LOCAL_DECISIONS_OR_PENDING}}. Replace reference facts with current source-backed facts before acceptance.
