# v0.1.1 final bounded-split validation

Owner-authorized scope: execution facade, delivery modes/bootstrap interface, external apply/artifact state, checked-in environment and day-zero native/optional Compose contract. Standard implementation only; consumers were read-only. Broad operational tooling remains deferred in [OPERATIONAL_TOOLING_SCOPE.md](../OPERATIONAL_TOOLING_SCOPE.md). No future business features, release/commit/tag/push or consumer adoption occurred.

## Policies and schema

New EXEC-DELIVERY (ordinary waiver metadata) declares A/B/transition and apply_package.sh interface. EXEC-RUNTIME, SEC-ENV and REL-APPLY-STATE are non-waivable core. The external boundary is deliberately stronger than the audit's optional waiver proposal under the owner's explicit MUST decision; no automatic legacy exception. Source-owned code/intentional fixtures differ from mutable backups/staging. Canonical ownership remains execution/security/release respectively.

Execution profile schema2 has fixed runtime families; standard manifest remains schema3, adoption schema2. There are 47 rule IDs, 34 protected core IDs, 13 invariant files and 42 distribution files. .env.example/.gitignore/native/Compose/reference assets are project-owned at instantiation, not byte-invariant consumer runtime. Checker validates native/template/Docker profile references without executing mapped commands. It detects declared source-internal or source-containing apply/artifact roots, including symlink resolution. Actual local updater behavior still requires source-backed review and runtime acceptance.

## Exact applicable results

| Command / context | Pass | Fail | Skip | Exit / evidence |
| --- | ---: | ---: | ---: | --- |
| ./run.sh test, initial sandbox | 70 | 1 | 0 | 1; real health failed; separate ./run.sh dev --port 0 returned PermissionError on socket.bind |
| ./run.sh test, first permitted loopback run | 71 | 0 | 0 | 0; same test unchanged, environment resolved |
| ./run.sh test, final standard source / permitted loopback | 73 | 0 | 0 | 0; includes hybrid, A-only apply rejection and negative readiness subcases |
| fresh distribution ./run.sh help | command PASS | 0 | 0 | 0; only declared vocabulary |
| fresh distribution ./run.sh doctor | command PASS | 0 | 0 | 0; no .env created/runtime started |
| fresh distribution ./run.sh test / permitted loopback | 73 | 0 | 0 | 0; complete versioned reference without sibling dependency |
| fresh distribution ./run.sh lint | bounded check PASS | 0 | 0 | 0; Python scripts/tests syntax and whitespace only |
| fresh ./run.sh dev --port 0 with runtime-local .env APP_HEALTH_PATH=/ready | native health PASS | 0 | 0 | response 200 with status ok; SIGTERM preserved; temporary .env removed; source distribution unchanged |
| docker compose --env-file .env.example -f compose.yaml config --format json | config PASS | 0 | 0 | 0; explicit host/container mapping and healthcheck; no daemon/start/build/pull |
| docker image inspect python:3.11-slim, sandbox | NOT VERIFIED | 1 environmental error | 0 | 1; socket permission denied |
| same image inspect, permitted read-only path | NOT VERIFIED | 1 environmental error | 0 | 1; Docker daemon unavailable |
| docker compose up | NOT RUN | NOT ASSESSED | NOT RUN | no Docker runtime acceptance; no daemon start/image acquisition/dependency installation |
| python3 -B scripts/generate_release.py --status FINAL | generated | 0 | 0 | 0; only reviewed candidate manifest |
| python3 -B scripts/generate_release.py --check | manifest PASS | 0 | 0 | 0 |
| python3 -B scripts/check_standard.py --standard . | INTEGRITY PASS | 0 | 0 | 0; consumer semantic/runtime acceptance NOT ASSESSED |
| python3 -B scripts/check_docs.py . | bounded docs PASS | 0 | 0 | 0; inline local links/non-template placeholders/JSON only; neutrality/facts not assessed |
| git diff --check | whitespace PASS | 0 | 0 | 0 |

Test numbers count unittest methods; protected-core exception rejection covers each of 34 IDs through subtests, not 34 extra reported test methods. Relevant negative cases include missing/invalid pins, protected/unknown/expired exceptions, drift; invalid delivery/runtime/applicability; missing env/ignore/classification/empty secret contract, tracked real env; internal/ancestor/symlink roots; missing/non-executable bootstrap; missing Compose/service, mismatched ports/listen, absent/disabled health, literal secrets including interpolated secret defaults; non-secret token lifetime remains valid; non-runnable native help and unsupported YAML. Static Docker parsing explicitly supports JSON-compatible YAML only. This is a documented portable subset, not universal YAML validation.

The default reference is native Mode A; Docker is explicitly NOT APPLICABLE there. The optional Docker reference configuration is verified; Docker runtime remains NOT RUN. Conditional runtime limitation does not grant container acceptance or block validated native content. No secret-bearing real env exists in source/distribution; example contains only five safe network keys. Synthetic forbidden-secret strings are deliberate isolated negative fixtures, not real credentials. A bounded classifier does not replace review of shipped content.

## Manifest / readiness

Version 0.1.1, schema3, status FINAL (validated local content; UNRELEASED).
Manifest SHA-256: `dec2a18a896dc30013af8717fbc85ce01ed1cc8aad93c037af2e19fd8eaaab9f`.
Prior unreleased candidate hash is historical; 0.1.0 tag and all historical published identities remain unchanged. No consumer pin is refreshed. Final status/hash verification occurred after the same source/test distribution passed; status promotion itself creates no runtime approval.

READY TO RELEASE for this bounded standard scope, subject to explicit user release authorization. No automatic commit/tag/push. Optional Docker live/runtime and package apply/recovery are not accepted. AuthHub adoption remains PENDING; AH-01 HOLD / NOT STARTED.

## Consumer impact (no changes)

The existing consumer snapshot still verifies against its own previous pinned content; that is not verification/adoption of this new manifest. To adopt, review/refresh the complete companion/invariants/pin with new semantic acceptance, correct preferred launcher and stale baseline docs, extend its source-backed schema2 runtime/env/delivery declarations, and migrate active root-local previous/backup/apply state externally. Mode B cannot be silently relabeled inapplicable while active updater exists. Preserve historical bytes/reader compatibility and prove failure/recovery in a separately authorized migration.

Existing YAML Compose can be represented in JSON-compatible syntax without changing behavior for static checking; real host/listen/ports/volumes must be explicitly recorded from source. Do not copy neutral reference APP defaults, switch host bind or remove existing volumes as adoption. Compatibility shim remains local; distinct external bootstrap must be independently available before installation. Live Docker/package upgrade/recovery acceptance is required when closing changed installer/state/runtime behavior or claiming that acceptance, not implied by integrity/structure/native scaffold PASS.

Operation source/practice repository, all L/112 work, CURRENT/NEXT and release metadata remain untouched. No adoption attempted there. Final byte/mode/Git evidence is captured externally in the task report; repository-only validation docs are excluded from consumer distribution.
