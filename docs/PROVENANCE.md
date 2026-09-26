# Reconciled provenance and distribution inventory

Audit-only. Primary practice authority is current local `/Users/samil/Documents/GitHub/ai-operation-hub`, main HEAD `367b78141ec10f8e7636c778254991f7495c307f` plus preserved L/112 working-tree changes. Source facts for the first consumer come only from current local ai-auth-hub. Source filenames and domain names here are provenance, never generic product assumptions. No future-direction input or business code/tool implementation was copied.

The initial extraction matrix records file-level candidates, not proof of rule-level semantic equivalence. Full semantic audit found broadened/narrowed/new rules; [NEW_POLICY_REGISTER.md](NEW_POLICY_REGISTER.md) records all reconciled N01–N30 decisions. New standard-product mechanisms were explicitly requested; detailed policy decisions are explicitly approved by the reconciliation request. A/B/C are extraction/generalization/synthesis; D new; E corrected regression; F ambiguity corrected.

| Stable rule / canonical owner | Source file + location | Provenance | Semantic scope/obligation/evidence difference |
| --- | --- | --- | --- |
| WF-PRESERVE / AGENT_WORKFLOW.md | AGENT_WORKFLOW.md:7,11,19,25,29–31,41–55,107,119,125; HANDOFF.md transfer sections | B/C | Preserved principle; generic parameters/implementation names removed; no new obligation |
| WF-SCOPE / AGENT_WORKFLOW.md | AGENT_WORKFLOW.md:7,11,19,25,29–31,41–55,107,119,125; HANDOFF.md transfer sections | B/C | Preserved principle; generic parameters/implementation names removed; no new obligation |
| WF-COMMANDS / AGENT_WORKFLOW.md | AGENT_WORKFLOW.md:7,11,19,25,29–31,41–55,107,119,125; HANDOFF.md transfer sections | B/C | N08 — see final decision register |
| WF-CLOSURE / AGENT_WORKFLOW.md | AGENT_WORKFLOW.md:7,11,19,25,29–31,41–55,107,119,125; HANDOFF.md transfer sections | B/C | Preserved principle; generic parameters/implementation names removed; no new obligation |
| WF-HANDOFF / AGENT_WORKFLOW.md | AGENT_WORKFLOW.md:7,11,19,25,29–31,41–55,107,119,125; HANDOFF.md transfer sections | B/C | Preserved principle; generic parameters/implementation names removed; no new obligation |
| DEV-BOUNDARY / DEVELOPMENT_RULES.md | DEVELOPMENT_RULES.md:18,24–28,42,87,89; AGENT_WORKFLOW.md:69–72,97,103,112; THIRD_PARTY_LICENSE_INVENTORY.md:3–21 | B/C | N09 — see final decision register |
| DEV-CHANGE / DEVELOPMENT_RULES.md | DEVELOPMENT_RULES.md:18,24–28,42,87,89; AGENT_WORKFLOW.md:69–72,97,103,112; THIRD_PARTY_LICENSE_INVENTORY.md:3–21 | B/C | Preserved principle; generic parameters/implementation names removed; no new obligation |
| DEV-REMOTE / DEVELOPMENT_RULES.md | DEVELOPMENT_RULES.md:18,24–28,42,87,89; AGENT_WORKFLOW.md:69–72,97,103,112; THIRD_PARTY_LICENSE_INVENTORY.md:3–21 | B/C | N10 — see final decision register |
| DEV-HYGIENE / DEVELOPMENT_RULES.md | DEVELOPMENT_RULES.md:18,24–28,42,87,89; AGENT_WORKFLOW.md:69–72,97,103,112; THIRD_PARTY_LICENSE_INVENTORY.md:3–21 | B/C | Preserved principle; generic parameters/implementation names removed; no new obligation |
| DEV-LICENSE / DEVELOPMENT_RULES.md | DEVELOPMENT_RULES.md:18,24–28,42,87,89; AGENT_WORKFLOW.md:69–72,97,103,112; THIRD_PARTY_LICENSE_INVENTORY.md:3–21 | B/C | N11 — see final decision register |
| GOV-TRUTH / DOCUMENT_GOVERNANCE.md | docs/governance/DOCUMENT_GOVERNANCE.md:5–24; docs/governance/CAPABILITY_CATALOG_POLICY.md:3–9 | B/C | Preserved principle; generic parameters/implementation names removed; no new obligation |
| GOV-OWNERS / DOCUMENT_GOVERNANCE.md | docs/governance/DOCUMENT_GOVERNANCE.md:5–24; docs/governance/CAPABILITY_CATALOG_POLICY.md:3–9 | B/C | N12, N13, N23 — see final decision register |
| GOV-PRECEDENCE / DOCUMENT_GOVERNANCE.md | docs/governance/DOCUMENT_GOVERNANCE.md:5–24; docs/governance/CAPABILITY_CATALOG_POLICY.md:3–9 | D; source ownership inspired | N23 — see final decision register |
| GOV-STATE / DOCUMENT_GOVERNANCE.md | docs/governance/DOCUMENT_GOVERNANCE.md:5–24; docs/governance/CAPABILITY_CATALOG_POLICY.md:3–9 | B/C | N12, N14 — see final decision register |
| SEC-SECRETS / SECURITY_BASELINE.md | docs/SECURITY.md:7–27,31–45; DEVELOPMENT_RULES.md:18,42,87,89; pre-production privacy/security sources | B/C | Preserved principle; generic parameters/implementation names removed; no new obligation |
| SEC-AUTHZ / SECURITY_BASELINE.md | docs/SECURITY.md:7–27,31–45; DEVELOPMENT_RULES.md:18,42,87,89; pre-production privacy/security sources | B/C | Preserved principle; generic parameters/implementation names removed; no new obligation |
| SEC-LOGGING / SECURITY_BASELINE.md | docs/SECURITY.md:7–27,31–45; DEVELOPMENT_RULES.md:18,42,87,89; pre-production privacy/security sources | B/C | Preserved principle; generic parameters/implementation names removed; no new obligation |
| SEC-SAFETY / SECURITY_BASELINE.md | docs/SECURITY.md:7–27,31–45; DEVELOPMENT_RULES.md:18,42,87,89; pre-production privacy/security sources | B/C | Preserved principle; generic parameters/implementation names removed; no new obligation |
| TEST-APPLICABILITY / TESTING_AND_EVIDENCE.md | AGENT_WORKFLOW.md:25,29–33,41–55,109,137; DEVELOPMENT_RULES.md:24–28,42; scripts/release_source_fingerprint.py:69–117; scripts/projected_closure_gate.py:252–415; screenshot-qa/manifest.json:3–29 | B/C | N02 — see final decision register |
| TEST-FORMAL / TESTING_AND_EVIDENCE.md | AGENT_WORKFLOW.md:25,29–33,41–55,109,137; DEVELOPMENT_RULES.md:24–28,42; scripts/release_source_fingerprint.py:69–117; scripts/projected_closure_gate.py:252–415; screenshot-qa/manifest.json:3–29 | D (explicit D1) | N01 — see final decision register |
| TEST-GUARDS / TESTING_AND_EVIDENCE.md | AGENT_WORKFLOW.md:25,29–33,41–55,109,137; DEVELOPMENT_RULES.md:24–28,42; scripts/release_source_fingerprint.py:69–117; scripts/projected_closure_gate.py:252–415; screenshot-qa/manifest.json:3–29 | B/C | N03 — see final decision register |
| TEST-REPORT / TESTING_AND_EVIDENCE.md | AGENT_WORKFLOW.md:25,29–33,41–55,109,137; DEVELOPMENT_RULES.md:24–28,42; scripts/release_source_fingerprint.py:69–117; scripts/projected_closure_gate.py:252–415; screenshot-qa/manifest.json:3–29 | B/C | N04 — see final decision register |
| TEST-IDENTITY / TESTING_AND_EVIDENCE.md | AGENT_WORKFLOW.md:25,29–33,41–55,109,137; DEVELOPMENT_RULES.md:24–28,42; scripts/release_source_fingerprint.py:69–117; scripts/projected_closure_gate.py:252–415; screenshot-qa/manifest.json:3–29 | B/C | N04, N20 — see final decision register |
| TEST-CLOSURE / TESTING_AND_EVIDENCE.md | AGENT_WORKFLOW.md:25,29–33,41–55,109,137; DEVELOPMENT_RULES.md:24–28,42; scripts/release_source_fingerprint.py:69–117; scripts/projected_closure_gate.py:252–415; screenshot-qa/manifest.json:3–29 | B/C | N05, N06 — see final decision register |
| TEST-SCREENSHOT / TESTING_AND_EVIDENCE.md | AGENT_WORKFLOW.md:25,29–33,41–55,109,137; DEVELOPMENT_RULES.md:24–28,42; scripts/release_source_fingerprint.py:69–117; scripts/projected_closure_gate.py:252–415; screenshot-qa/manifest.json:3–29 | B/C | N07 — see final decision register |
| REL-METADATA / MIGRATION_AND_RELEASE_POLICY.md | docs/MIGRATION_RECOVERY.md:3–21; docs/STORAGE_MIGRATION_RUNBOOK.md:3 and validation/cutover; AGENT_WORKFLOW.md:47,51,87–115; scripts/release_baseline.py; scripts/release_candidate.py; scripts/release_attestation.py | B/C | N15 — see final decision register |
| REL-MIGRATION / MIGRATION_AND_RELEASE_POLICY.md | docs/MIGRATION_RECOVERY.md:3–21; docs/STORAGE_MIGRATION_RUNBOOK.md:3 and validation/cutover; AGENT_WORKFLOW.md:47,51,87–115; scripts/release_baseline.py; scripts/release_candidate.py; scripts/release_attestation.py | B + D (D4); source RELEASE_0.6.0.md:34 historical correction counterexample | N16 — see final decision register |
| REL-RECOVERY / MIGRATION_AND_RELEASE_POLICY.md | docs/MIGRATION_RECOVERY.md:3–21; docs/STORAGE_MIGRATION_RUNBOOK.md:3 and validation/cutover; AGENT_WORKFLOW.md:47,51,87–115; scripts/release_baseline.py; scripts/release_candidate.py; scripts/release_attestation.py | B/C | Preserved principle; generic parameters/implementation names removed; no new obligation |
| REL-ARTIFACT / MIGRATION_AND_RELEASE_POLICY.md | docs/MIGRATION_RECOVERY.md:3–21; docs/STORAGE_MIGRATION_RUNBOOK.md:3 and validation/cutover; AGENT_WORKFLOW.md:47,51,87–115; scripts/release_baseline.py; scripts/release_candidate.py; scripts/release_attestation.py | B/C | N20 — see final decision register |
| REL-PRODUCTION / MIGRATION_AND_RELEASE_POLICY.md | docs/MIGRATION_RECOVERY.md:3–21; docs/STORAGE_MIGRATION_RUNBOOK.md:3 and validation/cutover; AGENT_WORKFLOW.md:47,51,87–115; scripts/release_baseline.py; scripts/release_candidate.py; scripts/release_attestation.py | B/C | Preserved principle; generic parameters/implementation names removed; no new obligation |
| UI-APPLY / UI_IMPLEMENTATION_STANDARDS.md | docs/governance/UI_IMPLEMENTATION_STANDARD.md; docs/UI_LIST_STANDARD.md:3–9; docs/governance/NAVIGATION_INFORMATION_ARCHITECTURE.md route/access principle only | B/C | N17 — see final decision register |
| UI-ACCESS / UI_IMPLEMENTATION_STANDARDS.md | docs/governance/UI_IMPLEMENTATION_STANDARD.md; docs/UI_LIST_STANDARD.md:3–9; docs/governance/NAVIGATION_INFORMATION_ARCHITECTURE.md route/access principle only | B/C | Preserved principle; generic parameters/implementation names removed; no new obligation |
| UI-LIST / UI_IMPLEMENTATION_STANDARDS.md | docs/governance/UI_IMPLEMENTATION_STANDARD.md; docs/UI_LIST_STANDARD.md:3–9; docs/governance/NAVIGATION_INFORMATION_ARCHITECTURE.md route/access principle only | B/C | N18 — see final decision register |
| UI-MAPPING / UI_IMPLEMENTATION_STANDARDS.md | docs/governance/UI_IMPLEMENTATION_STANDARD.md; docs/UI_LIST_STANDARD.md:3–9; docs/governance/NAVIGATION_INFORMATION_ARCHITECTURE.md route/access principle only | B/C | N17 — see final decision register |
| ADP-INTEGRITY / ADOPTION.md | New standard-product mechanism requested by initial Stage 1 prompt:135–144,175–189; fingerprint/governance inspired, no source tooling copied | D | N19, N29 — see final decision register |
| ADP-STRUCTURE / ADOPTION.md | New standard-product mechanism requested by initial Stage 1 prompt:135–144,175–189; fingerprint/governance inspired, no source tooling copied | D | N25, N27 — see final decision register |
| ADP-EXCEPT / ADOPTION.md | New standard-product mechanism requested by initial Stage 1 prompt:135–144,175–189; fingerprint/governance inspired, no source tooling copied | D | N21 — see final decision register |
| ADP-UPGRADE / ADOPTION.md | New standard-product mechanism requested by initial Stage 1 prompt:135–144,175–189; fingerprint/governance inspired, no source tooling copied | D | N19, N24 — see final decision register |

| Other artifact | Source / construction | Consumer treatment |
| --- | --- | --- |
| README / VERSION / CHANGELOG | New standard-product distribution/readiness/version contract; source process separation inspired | Companion snapshot; no app version implication |
| PROJECT_PROFILE.template.md | New local-command/applicability owner, source README/AW/DG inspired | Required project-owned instantiation |
| EXECUTION_PLAN.template.md | Source EXECUTION_PLAN CURRENT/NEXT/contract/dependencies | Instantiate without product/history |
| PROJECT_STATE.template.md | Source PROJECT_STATE metadata/source/evidence/debt | Required fact owner |
| PROJECT_STATE.template.json | Source JSON inspired; explicitly new optional projection scope | Optional; preserve stronger local metadata owners |
| CAPABILITY_CATALOG.template.md | Source catalog/continuity; generic minimum + preserved local verification dimensions | Required source-backed instantiation |
| ROADMAP_CHANGELOG.template.md | DG:20–24 and roadmap revision history | Only product scope/order/dependency/exit changes |
| HANDOFF.template.md | Source HANDOFF full-source preservation/transfer | Required project-owned resumption summary |
| STANDARD_ADOPTION_HISTORY.template.md | New N24 owner | Required adoption/exception/upgrade history |
| standard-adoption.template.json | New schema-2 structure, pin, exception and semantic record | Required consumer manifest |
| POLICY_RULES.json | New lightweight ID/owner/eligibility and inventory registry | Invariant, no policy DSL |
| scripts/check_standard.py | New stdlib implementation, fingerprint/path safety inspired | Invariant; bounded integrity/structure/record validation |
| scripts/check_docs.py | New bounded quality implementation, initial user quality requirements | Invariant; declared lexical/parser coverage |
| scripts/generate_release.py | New deterministic fixed-inventory manifest generator | Companion tooling; no publishing/approval |
| tests/test_check_standard.py, tests/test_check_docs.py | New isolated positive/negative enforcement regression fixtures | Companion validation; no app/runtime tests |
| standard-release.json | Generated schema-2 hashes for 26 files and 11 invariants; excludes itself/audits | Consumer pins exact final SHA-256 |
| docs/EXTRACTION_MATRIX.md | Historical candidate inventory, classification correction note | Audit-only |
| docs/NEW_POLICY_REGISTER.md | Full audit findings + explicit user reconciliation decisions | Audit-only |
| docs/STAGE1_REPORT.md | Historical initial report, superseded readiness claim | Audit-only |
| docs/RECONCILIATION_VALIDATION.md | Final validation/gate evidence | Audit-only |
| docs/evidence/protected-summary.json | Historical initial before/after evidence | Audit-only; original DS metadata qualification retained |

No source-local roadmap authority, stack/adapter count, user-observed runner, legal approval, business model or richer provider acceptance state becomes a generic mandate. Stronger local contracts remain local. Candidate identity/evidence separation preserves source practice; the lightweight standard does not claim to implement the source's release workflow.
