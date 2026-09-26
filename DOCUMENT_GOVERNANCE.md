# Document governance

## GOV-TRUTH: Source truth and honest status

Explicit user authorization defines task scope. Current source, configuration contracts, migration definitions and actual release metadata establish technical truth. Documents cannot override implementation. Future-direction/design notes express intent until source/evidence supports them. Never fabricate approval, PASS, evidence, capabilities or historical closure. Missing facts remain PENDING/TBD; resolve material contradictions before dependent work.

## GOV-OWNERS: Canonical ownership

| Owner | Normative responsibility |
| --- | --- |
| AGENT_WORKFLOW.md | Execution sequencing, bounded work, closure orchestration summaries |
| DEVELOPMENT_RULES.md | Code, compatibility, data and repository engineering |
| DOCUMENT_GOVERNANCE.md | Ownership, precedence, facts versus policy |
| SECURITY_BASELINE.md | Secrets/environment contract, security/authentication controls, logging/privacy-security |
| TESTING_AND_EVIDENCE.md | Testing applicability, identity, closure and screenshot evidence |
| MIGRATION_AND_RELEASE_POLICY.md | Schema/migration, external apply/artifact state and release/production lifecycle |
| UI_IMPLEMENTATION_STANDARDS.md | Generic UI implementation and QA applicability |
| EXECUTION_FACADE.md | Public facade, delivery/runtime/profile/network contracts, diagnostics, mutation boundaries and transition |
| ADOPTION.md | Standard pin, adoption, upgrades and exceptions |
| PROJECT_PROFILE.md | Local commands/applicability, stronger policies and local protocols |

POLICY_RULES.json records stable rule ID, canonical owner and waiver eligibility; the owner text defines the rule. It is a registry, not a policy language.

Project fact owners: EXECUTION_PLAN.md owns the single live CURRENT/NEXT, dependencies and acceptance; PROJECT_STATE.md owns current implementation/metadata/debt; optional PROJECT_STATE.json projects the same facts; CAPABILITY_CATALOG.md owns source-backed capabilities; HANDOFF.md summarizes resumption/transfer; STANDARD_ADOPTION_HISTORY.md owns standard review/adoption/upgrade history; standard-adoption.json owns pin, exceptions and recorded semantic acceptance. ROADMAP_CHANGELOG.md records actual product scope/order/dependency/exit changes, not every standards upgrade. Audit/history records are evidence, not policy authorities.

## GOV-PRECEDENCE: Policy precedence

Apply, in order: (1) non-waivable standard core; (2) invariant canonical rule owner; (3) approved narrow exception to a waivable rule; (4) project-profile strengthening/applicability; (5) project-owned execution/state docs; (6) historical/audit records. An authorized exception modifies only its named waivable rule and never the core. Profiles may strengthen rules and select explicitly permitted applicability, but cannot silently weaken invariants. Source truth remains technical fact, not proof of policy compliance. When invariant summaries conflict, the canonical owner wins; the conflict is a standard defect requiring correction before dependent work. A stronger existing local gate remains in force unless separately and explicitly reconciled without weakening the core.

## GOV-STATE: State and verification dimensions

Choose one product roadmap authority in PROJECT_PROFILE.md; an external roadmap is optional. Avoid competing live pointers. Update state/catalog/handoff when relevant source/evidence changes. Minimum implementation vocabulary: IMPLEMENTED = bounded source behavior exists; PARTIAL = incomplete behavior exists; NOT STARTED = absent implementation; PENDING = unknown decision/evidence. Implementation status does not imply configuration, connection verification, operation testing, field acceptance or production approval. Projects may add these independent dimensions and richer local statuses, documenting meanings/evidence in profile/catalog. Keep them distinct from execution NOT STARTED/IN PROGRESS/CLOSED and validation PASS/FAIL/PENDING/NOT APPLICABLE.
