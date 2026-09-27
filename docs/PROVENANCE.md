# Neutral provenance summary

This current summary is product-independent. Exact extraction file/line references, source hashes, local paths, branch/commit identities and consumer validation records were exported to maintainer storage outside this repository before cleanup. They are not consumer policy, distribution members or an adoption dependency. Published historical Git content is unchanged; this summary describes the current candidate, not retroactively anonymized history.

Source practice informs preservation, truthful state, bounded execution, security, evidence and release/recovery rules. Explicit generic decisions extend that practice. A/B/C denote extraction/generalization/synthesis; D denotes new generic policy. The decision register preserves semantic differences rather than claiming unchanged extraction.

| Canonical rule / owner | Neutral source category | Provenance class | Semantic decision |
| --- | --- | --- | --- |
| WF-PRESERVE / AGENT_WORKFLOW.md | source execution sequencing and preservation practice | B/C | Preserved principle; generic parameters/implementation names removed; no new obligation |
| WF-SCOPE / AGENT_WORKFLOW.md | source execution sequencing and preservation practice | B/C | Preserved principle; generic parameters/implementation names removed; no new obligation |
| WF-COMMANDS / AGENT_WORKFLOW.md | source execution sequencing and preservation practice | B/C | N08 — see final decision register |
| WF-CLOSURE / AGENT_WORKFLOW.md | source execution sequencing and preservation practice | B/C | Preserved principle; generic parameters/implementation names removed; no new obligation |
| WF-HANDOFF / AGENT_WORKFLOW.md | source execution sequencing and preservation practice | B/C | Preserved principle; generic parameters/implementation names removed; no new obligation |
| DEV-BOUNDARY / DEVELOPMENT_RULES.md | source engineering and compatibility practice | B/C | N09 — see final decision register |
| DEV-CHANGE / DEVELOPMENT_RULES.md | source engineering and compatibility practice | B/C | Preserved principle; generic parameters/implementation names removed; no new obligation |
| DEV-REMOTE / DEVELOPMENT_RULES.md | source engineering and compatibility practice | B/C | N10 — see final decision register |
| DEV-HYGIENE / DEVELOPMENT_RULES.md | source engineering and compatibility practice | B/C | Preserved principle; generic parameters/implementation names removed; no new obligation |
| DEV-LICENSE / DEVELOPMENT_RULES.md | source engineering and compatibility practice | B/C | N11 — see final decision register |
| GOV-TRUTH / DOCUMENT_GOVERNANCE.md | source document ownership and factual-state practice | B/C | Preserved principle; generic parameters/implementation names removed; no new obligation |
| GOV-OWNERS / DOCUMENT_GOVERNANCE.md | source document ownership and factual-state practice | B/C | N12, N13, N23 — see final decision register |
| GOV-PRECEDENCE / DOCUMENT_GOVERNANCE.md | source document ownership and factual-state practice | D; source ownership inspired | N23 — see final decision register |
| GOV-STATE / DOCUMENT_GOVERNANCE.md | source document ownership and factual-state practice | B/C | N12, N14 — see final decision register |
| SEC-SECRETS / SECURITY_BASELINE.md | source secret, security-control and logging practice | B/C | Preserved principle; generic parameters/implementation names removed; no new obligation |
| SEC-AUTHZ / SECURITY_BASELINE.md | source secret, security-control and logging practice | B/C | Preserved principle; generic parameters/implementation names removed; no new obligation |
| SEC-LOGGING / SECURITY_BASELINE.md | source secret, security-control and logging practice | B/C | Preserved principle; generic parameters/implementation names removed; no new obligation |
| SEC-SAFETY / SECURITY_BASELINE.md | source secret, security-control and logging practice | B/C | Preserved principle; generic parameters/implementation names removed; no new obligation |
| TEST-APPLICABILITY / TESTING_AND_EVIDENCE.md | source testing, exact-evidence and closure practice | B/C | N02 — see final decision register |
| TEST-FORMAL / TESTING_AND_EVIDENCE.md | source testing, exact-evidence and closure practice | D (explicit D1) | N01 — see final decision register |
| TEST-GUARDS / TESTING_AND_EVIDENCE.md | source testing, exact-evidence and closure practice | B/C | N03 — see final decision register |
| TEST-REPORT / TESTING_AND_EVIDENCE.md | source testing, exact-evidence and closure practice | B/C | N04 — see final decision register |
| TEST-IDENTITY / TESTING_AND_EVIDENCE.md | source testing, exact-evidence and closure practice | B/C | N04, N20 — see final decision register |
| TEST-CLOSURE / TESTING_AND_EVIDENCE.md | source testing, exact-evidence and closure practice | B/C | N05, N06 — see final decision register |
| TEST-SCREENSHOT / TESTING_AND_EVIDENCE.md | source testing, exact-evidence and closure practice | B/C | N07 — see final decision register |
| REL-METADATA / MIGRATION_AND_RELEASE_POLICY.md | source migration, release-artifact and recovery practice | B/C | N15 — see final decision register |
| REL-MIGRATION / MIGRATION_AND_RELEASE_POLICY.md | source migration, release-artifact and recovery practice | B + D (authorized emergency recovery decision) | N16 — see final decision register |
| REL-RECOVERY / MIGRATION_AND_RELEASE_POLICY.md | source migration, release-artifact and recovery practice | B/C | Preserved principle; generic parameters/implementation names removed; no new obligation |
| REL-ARTIFACT / MIGRATION_AND_RELEASE_POLICY.md | source migration, release-artifact and recovery practice | B/C | N20 — see final decision register |
| REL-PRODUCTION / MIGRATION_AND_RELEASE_POLICY.md | source migration, release-artifact and recovery practice | B/C | Preserved principle; generic parameters/implementation names removed; no new obligation |
| UI-APPLY / UI_IMPLEMENTATION_STANDARDS.md | source UI access, presentation and QA practice | B/C | N17 — see final decision register |
| UI-ACCESS / UI_IMPLEMENTATION_STANDARDS.md | source UI access, presentation and QA practice | B/C | Preserved principle; generic parameters/implementation names removed; no new obligation |
| UI-LIST / UI_IMPLEMENTATION_STANDARDS.md | source UI access, presentation and QA practice | B/C | N18 — see final decision register |
| UI-MAPPING / UI_IMPLEMENTATION_STANDARDS.md | source UI access, presentation and QA practice | B/C | N17 — see final decision register |
| ADP-INTEGRITY / ADOPTION.md | explicit standard-product adoption decisions | D | N19, N29 — see final decision register |
| ADP-STRUCTURE / ADOPTION.md | explicit standard-product adoption decisions | D | N25, N27 — see final decision register |
| ADP-EXCEPT / ADOPTION.md | explicit standard-product adoption decisions | D | N21 — see final decision register |
| ADP-UPGRADE / ADOPTION.md | explicit standard-product adoption decisions | D | N19, N24 — see final decision register |

## Execution extension

| Rule / artifact | Neutral origin | Classification |
| --- | --- | --- |
| EXEC-FACADE / EXEC-DISPATCH | source runtime facade; explicit generic execution decision | B inspiration + D new vocabulary/portable dispatcher |
| EXEC-READONLY | source inspection/bootstrap hazards; explicit diagnostic safety decision | D corrected nonmutation boundary |
| EXEC-MUTATION | source runtime facade and first consumer legacy package-apply layer | B responsibility separation + D explicit lifecycle routing |
| EXEC-ADOPTION | explicit portable execution-profile/checker decision | D static/executable adoption contract |
| health scaffold / bounded lint / base tests | explicit day-zero standard-product decision | D stdlib reference capability |

No source-specific brands, providers, business entities, roadmap IDs, real release/schema examples or execution protocols become generic mandates. Stronger local gates remain project-owned. Source runtime/container dependencies and release delta artifacts remain distinct. An actor-exclusive mutation rule was not established and is not introduced.

## Distribution boundary

POLICY_RULES.json and standard-release.json own the exact fixed distribution/invariant inventory. Normative policy, neutral templates, generic tooling/tests, executable reference assets and standard version/manifest are consumer-facing. Current neutral summaries under docs are repository-readable, but are not invariant/adoption distribution members. Exact extraction evidence, source snapshots and temporary audit term lists remain outside the current tree and fixed distribution. No companion/adoption step copies maintainer evidence.

## Final bounded-split provenance

EXEC-DELIVERY: historical externally generated application delivery is accepted owner history; local full/delta apply mechanics inform B generalization, explicit generic Mode A/B/profile/bootstrap is D. Dependency resolver actor exclusivity remains unestablished and is not a rule. REL-APPLY-STATE is D: safer configurable external mutable-state/artifact ownership, not unchanged extraction of every local source path. Existing root snapshot debt must not become the generic pattern. SEC-ENV combines B secret hygiene with D example/key-classification/checker contract. EXEC-RUNTIME and optional neutral native/Compose example are D day-zero choices, not inherited business/DB architecture. The owner-authorized non-waivable boundary is explicit; earlier audit suggested ordinary waiver as an option, not accepted policy. Broader B/C reusable tools and G new designs remain unimplemented v0.2 scope.

## v0.2.0 continuation — owner-approved NEW foundation decisions

The unreleased v0.1.1 candidate is superseded before publication, with its implementation preserved and expanded. Published 0.1.0 remains immutable. DEV-FOUNDATION (toolchain/exclusions), REL-DATA-CONTRACT (DB/persistence/backup/migration applicability), SEC-FOUNDATION (authentication/observability) and TEST-CLASSES (isolated/live dimensions) are NEW generic rules accepted by the owner continuation request, not unchanged extraction. Local data/release/security practices motivate them; the fixed schema, license/ops templates and bounded reference harness are new generic/reference implementations. No universal PostgreSQL, identity provider, business model or consumer gate is introduced. Stronger local rules remain binding. Future generic builders/evidence/recovery/acceptance tooling now belongs to v0.3.0. Historical audit records below/above retain their scoped identities and limitations.

| Rule | Provenance class | Semantic delta | Canonical owner |
| --- | --- | --- | --- |
| DEV-FOUNDATION | NEW generic decision / reference implementation | Explicit machine identity/toolchain/dependency/exclusion inventory and bounded static checks | DEVELOPMENT_RULES.md |
| REL-DATA-CONTRACT | NEW generic contract, synthesis of existing safety principles | Explicit mode/owner/recovery/backup declarations without implementing engines | MIGRATION_AND_RELEASE_POLICY.md |
| SEC-FOUNDATION | NEW generic contract + minimal reference | Auth/session/authorization/logging applicability and bounded generated-ID events | SECURITY_BASELINE.md |
| TEST-CLASSES | NEW generic classification/reference harness | Explicit six classes, timeout/state/network declarations, sanitized bounded unittest execution | TESTING_AND_EVIDENCE.md |

No claim is made that historical source already had this exact schema, harness or templates. Earlier 73/73 bounded evidence remains baseline evidence, not proof of the expanded candidate.

## v0.2.2 FINAL portable collaboration provenance

WF-PORTABLE and GOV-PLAN-AUTHORITY are D NEW generic decisions from the explicitly authorized Supervisor-controlled capability, not unchanged source extraction. Existing bounded CURRENT, source truth, truthful evidence, handoff and external-roadmap permissiveness are reused under their established owners. The new requirements are portable packets, no hidden shared-session dependency, declared-versus-directly-verified planning revisions and a single repository projection. SUPERVISOR_PACKET.template.md and AGENTS.template.md are supporting forms; no consumer-specific plan, external tool brand, provider, database or business workflow is imported. No protected AI approval or transport implementation is inferred.

The maintainer-only `tests/test_portable_packet_rehearsal.py` is a reproducible synthetic two-process protocol rehearsal. It is not a distributed standard member, live two-AI acceptance, sender authentication or external planning-service evidence.

## 0.2.3 FINAL STD-TEST-01

The optional cooperative unittest job/evidence adapter is new generic reference infrastructure implementing existing WF-SCOPE/TEST-REPORT/TEST-IDENTITY semantics; not unchanged extraction of a source project's executor. Source scoping/state/selection are project-owned configuration. No new canonical policy owner, protected approval power or mandatory external runner is introduced. Raw-output suppression and cooperative test-boundary cancellation are explicit implementation limits; no live multi-AI/production/service acceptance is inferred.

## 0.2.4 FINAL — STD-REL-01

The optional staged-candidate Git adapter is new generic reference infrastructure under existing REL-ARTIFACT, WF-SCOPE, TEST-IDENTITY and EXEC-MUTATION owners, not extracted historical executor behavior. Local gates/lifecycle/message/approval applicability stay project-owned; no new invariant IDs, mandatory consumer files, human authentication or delegated approval authority. Strict scope/config/evidence binding, private index/CAS and unsupported hook/signing handling are adapter restrictions, not universal policy changes.

## 0.2.5 DRAFT — STD-REL-02

The committed-blob preview adapter and stateless HTTP reference validator are new generic reference infrastructure implementing existing WF-SCOPE/REL-ARTIFACT/TEST-IDENTITY/EXEC-MUTATION isolation, authorization and evidence boundaries. They are not unchanged extraction of a historical executor. Committed profile, separate PREVIEW record, trusted single-process/stdlib-only support, bounded evidence/output suppression and source snapshots are optional adapter contracts, not new invariant policy owners or protected approval powers. No consumer requirements, production acceptance or general deployment/sandbox engine are claimed.

## 0.2.5 FINAL closure review

Owner authorizes bounded correction and finalization after exact candidate review. Portable drive/metadata/device-alias rejection closes an implementation path-boundary defect, not a new policy owner or protected power. Prior DRAFT packet/evidence remains historical; corrected final input hashes and real owner decision are recorded separately in docs/packets/STD-REL-02-CLOSURE.md. Reference committed fixtures prove the optional adapter, not real publication/production acceptance or a mandatory consumer runtime.
