# Stage 1 reconciliation — new-policy register

Audit-only, not consumer invariant policy. Decision authority: repository owner's explicit STAGE 1 RECONCILIATION request (2026-09-26), including D1–D4 and the accepted/revise/local decisions. No future-direction note was used. These are conscious standard decisions, not an assertion of semantically unchanged extraction.

Classification: A direct, B generalized, C synthesis, D new, E contradiction/regression, F unproven/ambiguous. Prior full audit N01–N30 is reconciled below. Scope/obligation/evidence changes remain visible; source-practice details are in PROVENANCE.

| ID | Final owner | Origin/change class | Before → final semantics | Decision / boundary |
| --- | --- | --- | --- | --- |
| N01 | TEST-FORMAL | D / broader | Risk/contract-based release suites → every configured formal release gate required | ACCEPT NEW — explicit D1; docs-only excluded |
| N02 | TEST-APPLICABILITY | D | Consistency/product QA → affected-doc links/facts/invariant checks | ACCEPT NEW — bounded affected scope |
| N03 | TEST-GUARDS | D / revised | Blanket guard-disable ban removed; no bypassed guard acceptance, controlled doubles valid | REVISED — protects acceptance without banning isolation |
| N04 | TEST-REPORT / TEST-IDENTITY | D / broader corrected | All-test pre/post burden removed; formal exact evidence versus routine context/counts | REVISED — preserves formal proof and local requirements |
| N05 | TEST-CLOSURE | B / broader bounded | Formal projection generalized only to pointer/state-changing closure | REVISED — existing applicable automatic gates preserved |
| N06 | TEST-CLOSURE | D/E / weaker corrected | Undefined small-project manual waiver removed | REVISED — D2 four conditions; never replace applicable automated gate |
| N07 | TEST-SCREENSHOT | F / clarified | Vague material-UI trigger removed | REVISED — explicit local trigger and evidence coverage |
| N08 | WF-COMMANDS | B / narrower local protocol | Source user-observed full suite is not inherited generic default | ACCEPT NEW — stronger local protocol retained |
| N09 | DEV-BOUNDARY | D | Shared service cannot absorb consumer business authorization | ACCEPT NEW — initial user scope + explicit reconciliation |
| N10 | DEV-REMOTE | B/C / broader bounded | Domain retry/idempotency generalized to applicable external side effects | REVISED — contract limits, ambiguous unsafe retry prohibited |
| N11 | DEV-LICENSE | B / broader | Frontend/vendor review generalized to all third-party dependencies | ACCEPT NEW — budgets/stronger local rejection remain local |
| N12 | GOV-OWNERS / GOV-STATE | D/B | New local profile owner; optional external scope authority | ACCEPT NEW — source external authority stays project-local |
| N13 | GOV-OWNERS | B / narrower projection | Source JSON release facts generalized to optional state projection | ACCEPT NEW — does not demote existing local release metadata |
| N14 | GOV-STATE / catalog template | B / generalized | Small generic implementation statuses plus richer independent verification states | REVISED — no flattening configured/connection/operation/field acceptance |
| N15 | REL-METADATA | C/D | Independent standard/app versions and non-release doc checkpoints | ACCEPT NEW — local application policy preserved |
| N16 | REL-MIGRATION | D / source-practice tension | Absolute published migration edit ban replaced by immutable default and authorized emergency | REVISED — D4 rationale, successor impossibility, compatibility, identities, recovery and history |
| N17 | UI-APPLY / UI-MAPPING | B / narrower local constraints | Fixed source brands/stack/adapter counts not imported | KEEP LOCAL — preserve stronger local acceptance contracts |
| N18 | UI-LIST | E / weaker corrected | Unqualified should-filter wording removed | REVISED — declared task trigger; no declaration means PENDING; stronger local MUST retained |
| N19 | ADP-INTEGRITY / ADP-UPGRADE | D | Version, pin, reviewed copies/upgrades and portable companion snapshot | ACCEPT NEW — requested standard-product mechanism, not extraction |
| N20 | TEST-IDENTITY / REL-ARTIFACT | B / weaker corrected | Short generic identity replaced by minimum formal contract including applicable modes/policy | REVISED — stronger snapshot/marker/attestation contracts not weakened |
| N21 | ADP-EXCEPT / registry | D | Exceptions protected by stable owner/eligibility and exact narrow block drift | REVISED — D3 core, real rule, metadata/date, no tooling/registry drift |
| N22 | consumer profile / execution | D / local | Documentation closure and historical lint debt are scoped local acceptance | KEEP LOCAL — no formal app-release waiver |
| N23 | GOV-OWNERS / GOV-PRECEDENCE | F / ownership defect | Rule IDs, canonical details and six-level precedence | REVISED — summaries defer; conflict is defect |
| N24 | STANDARD_ADOPTION_HISTORY / ADP-UPGRADE | E / corrected | Standards history removed from routine product roadmap logging | REVISED — dedicated owner; roadmap only actual product changes |
| N25 | README / reports / ADP-STRUCTURE | E/F / corrected | Hash PASS no longer means READY or human semantic approval | REVISED — prior bytes DRAFT/RC; final readiness separately validated |
| N26 | EXTRACTION_MATRIX / PROVENANCE | F / corrected | Navigation document had business-only label yet informed generic UI | REVISED — only generic route/access principle, no domain navigation imported |
| N27 | check_standard / ADP-STRUCTURE | D/E | Fixed distribution/invariant/project-owned inventories, registry/exception checks | REVISED — documented integrity/structure/recorded approval boundaries |
| N28 | check_docs / README | D/F | Bounded supported-link, placeholder and historical lexical scan (superseded by N35) | REVISED — exact structural scope; earlier vocabulary branch removed by N35; no factual correctness claim |
| N29 | ADP-INTEGRITY / consumer profile | F / portability defect | Unversioned sibling dependency removed | REVISED — complete content-pinned companion snapshot and copied checkers |
| N30 | consumer state/architecture/catalog | E / factual | Unsupported lifecycle/permanence claims corrected against current source | REVISED — current source wins; not future implementation |

No high-impact Stage 1 reconciliation decision remained pending at that checkpoint; subsequent unreleased candidate scope is separately recorded below. Structural exception tooling cannot authenticate a human approval or detect arbitrary semantic evasion inside an approved waivable block: ADP-EXCEPT requires human review against the protected core. Existing local gates survive adoption. New mechanisms are accepted because they serve the requested standard product; removed accidental breadth/permissions are recorded rather than hidden.

## v0.1.1 authorized scope extension

N31 / EXEC-FACADE, EXEC-DISPATCH: NEW generic facade vocabulary, argv routing and portable profile, explicitly authorized by v0.1.1 request; source run.sh practice generalized, capability absent from 0.1.0. N32 / EXEC-READONLY, EXEC-MUTATION: NEW explicit side-effect boundary, correcting observed bootstrap/version-status hazards rather than inheriting them. N33 / EXEC-ADOPTION: NEW executable identity/static enforcement and compatibility transition. N34: NEW stdlib day-zero health/base validation reference; no business framework. actor-exclusive dependency mutation is rejected as unproven, not silently introduced. Release delta remains an artifact operation. User-observed full-suite/stronger release tooling stays local. These are deliberate new capabilities, not a retroactive claim about 0.1.0.

## N35 — product-independent genericity correction

The current candidate removes the checker’s built-in source/consumer/business/provider denylist. Option 1: generic docs checks cover supported inline links, non-template placeholders and JSON syntax only, explicitly report vocabulary/project neutrality NOT ASSESSED, and never infer lexical policy from a release manifest. Extraction/release neutrality is a separate audit using temporary externally supplied terms. Tests use synthetic source/consumer/entity names. Exact historical extraction evidence is exported outside the current repository; neutral provenance and historical checkpoint summaries retain decision distinctions. No published historical release is rewritten; no version bump is implied by this pre-release correction.

## Final bounded split — N36–N40

Owner authority: explicit FINAL BOUNDED-SPLIT PATCH request. N36 / EXEC-DELIVERY: D new generic A/B/transition/profile/bootstrap policy, informed by B historical application delivery; prior actor-exclusive dependency conclusion was narrowly about resolver authority and misleading when applied to application ZIP delivery. N37 / REL-APPLY-STATE: D new NON-WAIVABLE external state/artifact boundary. The owner says mutable transient snapshots MUST NOT pollute source; this patch chooses enforceable core rather than automatic legacy exceptions. Genuine version-controlled installer code/fixtures are source, not mutable apply state. Preserve historical bytes until authorized migration; a truthful PENDING consumer is preferable to waiving this accepted default. This deliberately differs from the audit's optional ordinary-waiver proposal; no legacy exception is granted.

N38 / SEC-ENV: B existing secret protection + D checked-in env contract/schema/ignore enforcement. N39 / EXEC-RUNTIME: D explicit runtime/IPv4/network/health contract and native/optional Docker reference, preserving existing stdlib health. N40 / deferred scope: B reusable operational patterns, C interfaces, D/E local assumptions and G new safe applier/full-builder design are listed in OPERATIONAL_TOOLING_SCOPE; none implemented in v0.1.1. No consumer adoption/roadmap semantics or source project's runtime changes are accepted by this patch.

## v0.2.0 continuation — owner-approved NEW foundation decisions

The unreleased v0.1.1 candidate is superseded before publication, with its implementation preserved and expanded. Published 0.1.0 remains immutable. DEV-FOUNDATION (toolchain/exclusions), REL-DATA-CONTRACT (DB/persistence/backup/migration applicability), SEC-FOUNDATION (authentication/observability) and TEST-CLASSES (isolated/live dimensions) are NEW generic rules accepted by the owner continuation request, not unchanged extraction. Local data/release/security practices motivate them; the fixed schema, license/ops templates and bounded reference harness are new generic/reference implementations. No universal PostgreSQL, identity provider, business model or consumer gate is introduced. Stronger local rules remain binding. Future generic builders/evidence/recovery/acceptance tooling now belongs to v0.3.0. Historical audit records below/above retain their scoped identities and limitations.

| Rule | Provenance class | Semantic delta | Canonical owner |
| --- | --- | --- | --- |
| DEV-FOUNDATION | NEW generic decision / reference implementation | Explicit machine identity/toolchain/dependency/exclusion inventory and bounded static checks | DEVELOPMENT_RULES.md |
| REL-DATA-CONTRACT | NEW generic contract, synthesis of existing safety principles | Explicit mode/owner/recovery/backup declarations without implementing engines | MIGRATION_AND_RELEASE_POLICY.md |
| SEC-FOUNDATION | NEW generic contract + minimal reference | Auth/session/authorization/logging applicability and bounded generated-ID events | SECURITY_BASELINE.md |
| TEST-CLASSES | NEW generic classification/reference harness | Explicit six classes, timeout/state/network declarations, sanitized bounded unittest execution | TESTING_AND_EVIDENCE.md |

No claim is made that historical source already had this exact schema, harness or templates. Earlier 73/73 bounded evidence remains baseline evidence, not proof of the expanded candidate.

## v0.2.2 FINAL — portable Supervisor/coding-agent decisions

| Decision | Canonical owner | Class and semantic delta | Boundary |
| --- | --- | --- | --- |
| N41 / WF-PORTABLE | AGENT_WORKFLOW.md | D NEW generic account/session-independent packet and reconstructability contract; existing WF-SCOPE/WF-CLOSURE supply bounded execution and closure separation | Non-waivable; template is transport only, no sender authentication or new approval authority |
| N42 / GOV-PLAN-AUTHORITY | DOCUMENT_GOVERNANCE.md | D NEW explicit external planning declaration/direct-verification distinction and repository projection reconciliation | Non-waivable; EXECUTION_PLAN remains sole live pointer, external artifact is not technical truth |

Supporting project templates add references and honest PENDING states without making their fields second policy authorities. The optional AGENTS template is a reading map. No consumer, roadmap, tooling backend or published version is changed by this candidate.
