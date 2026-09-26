# {{PROJECT_NAME}} profile

- Technical authority: current local source and actual release metadata.
- Product roadmap authority: {{ROADMAP_AUTHORITY_OR_PENDING}}.
- Architecture/ownership boundary: {{SOURCE_BACKED_BOUNDARY}}.
- Safe commands and isolated environment: {{COMMANDS_OR_PENDING}}.
- Formal application release definition and configured suite/gates (TEST-FORMAL): {{RELEASE_CONTRACT_OR_PENDING}}.
- Exact formal evidence scope/exclusions/config/runner identities (TEST-IDENTITY, REL-ARTIFACT): {{IDENTITY_POLICY}}.
- Closure gate and permitted recorded manual path (TEST-CLOSURE): {{AUTOMATION_OR_LOW_RISK_MANUAL_CONTRACT}}.
- Screenshot and status-filter triggers (TEST-SCREENSHOT, UI-LIST): {{EXPLICIT_UI_APPLICABILITY}}.
- Additional capability verification dimensions (GOV-STATE): {{LOCAL_STATUS_MEANINGS}}.
- Stronger local protocols and exception references: {{LOCAL_RULES}}.
- Portable companion standard and adoption history: {{PINNED_SNAPSHOT_AND_HISTORY}}.
- External/persistent data boundaries (SEC-SAFETY): {{SAFE_SCOPE}}.

## Execution declaration (EXEC-FACADE / EXEC-ADOPTION)

Canonical behavior: [EXECUTION_FACADE.md](EXECUTION_FACADE.md). Instantiate [execution-profile.template.json](execution-profile.template.json) as execution-profile.json; retain a project-owned executable run.sh and invariant scripts/project_runner.py. Declare default/dev/test/lint, formal full-test if applicable, migration/screenshot/package/apply-package extensions, argv, prerequisites, availability and mutability. Reference helpers explicitly with ./ paths. Record unavailable commands honestly and compatibility launcher removal boundaries. Local stronger observation/approval protocols remain binding. Declare container dependency builds separately from host dependency preparation. The included health/lint/test assets form a stdlib-only reference; adapting them is project-owned work, not changing invariant dispatcher policy.

## Fixed machine contract: execution-profile.json schema 3

This project-owned JSON is the machine projection of this profile; policy owners remain invariant. Instantiate the runnable native [execution-profile.template.json](execution-profile.template.json). An optional [execution-profile.docker.json](execution-profile.docker.json) plus [compose.yaml](compose.yaml) and [Dockerfile.scaffold](Dockerfile.scaffold) supplies the same health baseline for Docker. Do not infer Docker applicability from those files merely being shipped.

| runtime family | Exact keys / semantics |
| --- | --- |
| root | runtime_mode = native/docker/hybrid; execution_facade = run.sh; delivery_modes = nonempty unique A/B list |
| package_apply | status READY / NOT CONFIGURED when B applies, otherwise all fields NOT APPLICABLE; entrypoint role apply_package.sh (real executable path when READY); state_root external configured path when B applies |
| environment | env_example_path, env_path (distinct safe local paths); required_env_keys, optional_env_keys, secret_env_keys (unique uppercase-key lists; secret is subset; example contains exactly required+optional keys) |
| network | bind_host explicit IPv4; host_port integer 1..65535; container_listen_host and container_port explicit when Docker/hybrid, otherwise NOT APPLICABLE; health_path beginning / OR health_command nonempty argv, the other NOT APPLICABLE |
| docker | status READY with compose_file, compose_project_name, primary_service, dev_command mapped READY when Docker/hybrid; otherwise every field NOT APPLICABLE |
| native | status READY and dev_command mapped READY when native/hybrid; otherwise every field NOT APPLICABLE |
| storage | status READY plus data_roots/volume_roots lists when persistent storage applies; otherwise status NOT APPLICABLE with both lists empty; artifact_root always external (may be an unused declared output location) |

Existing commands own dev/start/test/lint and optional extensions, literal argv, prerequisite lists, mutability and availability. No service is executed by static validation. Runtime fields describe declared intent; isolated native/Compose/health and package/recovery acceptance are separate evidence. NOT CONFIGURED Mode B reports PENDING, not a working installer. External roots resolve ~ and relative paths; environment/shell substitutions in paths are unsupported. Choose project-specific collision-safe state/artifact directories externally at instantiation. Standard examples use a neutral relative external artifact directory and no persistent data/volumes.

Record producer/artifact/receiving instructions, bootstrap bundle availability, dependency preparation separately, preserve/rollback/failure retention, stronger local identity gates and any legacy state migration debt. The v0.2.0 checker requires JSON-compatible Compose syntax; actual docker compose config and runtime gates remain local. No claim that the included optional Docker image is already available locally. Required/optional/secret inventories apply to actual local source facts, not aspirational features.

## Foundation projection (DEV-FOUNDATION / REL-DATA-CONTRACT / SEC-FOUNDATION / TEST-CLASSES)

Every section below is required, including explicit NOT_APPLICABLE/NOT_CONFIGURED/PENDING fields. Existing command/runtime availability retains spaced READY / NOT CONFIGURED / NOT APPLICABLE for compatibility; foundation enums use underscores. Section key spelling/types are fixed in the distributed [validator](scripts/foundation_contract.py) and fully instantiated JSON examples. No absent architecture choice is inferred. Unknown keys are rejected.

| foundation section | Machine declarations / local decisions |
| --- | --- |
| identity | project_name, project_slug, application_version, version_source; standard/application versions independent |
| toolchain | language/runtime/range; manifest path/format/hash; lock path/format/hash/manifest-review binding/policy; build/test/lint runner; entrypoint/facade |
| database | database_mode none/embedded/container/external; engine none/sqlite/postgres/mysql/project_defined; host/host_port/listen_port/name; user/password/connection env keys; data_root/compose_service/health argv; required_at_day_zero/test_isolation |
| migration | applicability/strategy/command/preflight/schema source/current/target; automatic_down_migration=false; source_behind_database_fail_closed=true; backup requirement; recovery strategy/command/document |
| persistent_data | runtime/DB roots; blob mode none/local/object_store/external/project_defined; local root/retention/quota/upload applicability |
| hygiene | source-exclusions.json, .gitignore and .dockerignore contract paths; bounded glob/directory forms |
| backup | applicability/scope/external root; integrity metadata/verify/restore/confirmation/pre-restore backup/retention/key preservation/rationale |
| background_jobs | none/in_process/worker/external/project_defined; command/service/persistence dependency/retry-idempotency owner/health applicability |
| authentication | none/external/project_defined; generic integration class/callback/public env keys/session owner/project authorization |
| observability | logging format/strategy/correlation/redaction; health/readiness command/destination/retention |
| testing | six independently applicable classes, command/timeout/network/state; no inherited credentials/skip PASS/mock live; identity staleness |
| third_party | inventory path/review status/bundled assets/rationale; unknown is never approved |
| ui | applicability/rationale; health-only reference is NOT_APPLICABLE |
| local_stronger_rules | project-owned references/rationale; never silently weaken invariant core |
| operations | installation/recovery/runbook paths |

Manifest adapters: PEP 621/npm compare identity/version/range; uv/package-lock compare limited root metadata and dependency declarations. All bind exact bytes; declared other formats and frozen dependency preparation require local review/gates. No resolver or universal compiler/lock parser exists. Data roots match runtime.storage lists (volume:name maps to volume_roots name); source-local data must be excluded across all targets. DB-role Compose services declare x-foundation-role=database; external mode forbids any local declared DB-role service. Arbitrary YAML and undisclosed external tooling cannot be semantically certified by this static adapter.

Record actual application choices and debt: {{FOUNDATION_DECISIONS_OR_PENDING}}. Migration/restore/backup/worker command absence is explicit debt. Doctor reports it; integrity/structure PASS does not imply readiness of those operations, license approval, production health or release acceptance.
