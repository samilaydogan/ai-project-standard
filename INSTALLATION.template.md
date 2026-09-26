# {{PROJECT_NAME}} installation

Python 3.11 or newer and a POSIX shell are required. No third-party Python dependencies are declared in pyproject.toml; lockfile is explicitly NOT_APPLICABLE. Normal commands never install, resolve or update packages. A consumer with dependencies must review manifest/lock identity and declare frozen preparation separately from resolution. Container image availability is a separate prerequisite; no automatic pull is evidence of acceptance.

Use `./run.sh help`, `./run.sh doctor`, `./run.sh dev` (or `start`), `./run.sh status`, `./run.sh health`, `./run.sh test`, and `./run.sh lint`. Dev stays foreground; stop with Ctrl-C. Status/health never start the service and report PENDING when unavailable. The reference probe is loopback-only. Native host/port defaults are 127.0.0.1:8080. For a local collision, `./run.sh dev --port 8081` and `./run.sh health --port 8081` are explicit overrides.

execution-profile.json schema 3 and PROJECT_PROFILE own actual applicability. The stateless default declares database, worker, authentication, blob storage and backup as none/NOT_APPLICABLE. No migration/restore/install engine is provided. Persisting domain data requires an explicit new profile choice and isolated acceptance before domain work.

.env.example is a safe contract, not production configuration. .env is optional for this reference, private and excluded. Secret examples must remain empty; obtain real secrets from the deployment owner. Never echo them in logs or handoffs. Runtime/DB data, backups, test state and apply state are excluded by source-exclusions.json. Artifact and Mode B apply-state roots must be outside source. No state directories are created by doctor.

Optional Docker: select execution-profile.docker.json deliberately as the active project-owned profile in a separate approved adaptation. Validate `docker compose --env-file .env.example -f compose.yaml config` before runtime acceptance. Its host mapping and container listen address are distinct. Native acceptance and Compose configuration do not prove Docker runtime or production readiness.

Delivery Mode A uses the worktree. Mode B declares a separately provided bootstrap/apply_package.sh and external apply state; the shipped entry is NOT CONFIGURED, not an installer. Review package identity, recovery and private data preservation before use. Installation, production credentials, ports, backups and deployment authorization remain project-owner responsibilities. See [runbook](OPERATIONS_RUNBOOK.md), [recovery](MIGRATION_RECOVERY.md), and [license inventory](THIRD_PARTY_LICENSE_INVENTORY.md).

## Instantiation record

Declare actual owners, command mappings, modes, paths, applicability, evidence and unresolved debt: {{PROJECT_LOCAL_DECISIONS_OR_PENDING}}. Replace reference facts with current source-backed facts before acceptance.
