# Portable Supervisor / coding-agent packet (supporting template)

Instantiate one form below for one bounded task. The envelope travels unchanged by manual copy/paste, file transfer or future routing; transport does not change authority. Carry a bounded decision/evidence subset and references to durable project records accessible to the receiver, rather than copying full project state. Canonical behavior belongs to [AGENT_WORKFLOW.md](AGENT_WORKFLOW.md), planning truth to [DOCUMENT_GOVERNANCE.md](DOCUMENT_GOVERNANCE.md), and evidence/closure to [TESTING_AND_EVIDENCE.md](TESTING_AND_EVIDENCE.md). This packet is not self-authenticating, a second CURRENT/NEXT owner, or proof of a human decision. Verify protected-action authorization through the project's approved channel. Do not include secrets, personal data or raw credential-bearing logs.

## Common envelope — complete for every form

| Field | Instance value or explicit PENDING / NOT APPLICABLE with reason |
| --- | --- |
| Packet kind and unique packet ID | {{KIND_AND_ID}} |
| Project; stable work-unit/task ID; date/time with zone | {{PROJECT_TASK_TIME}} |
| Issuing role; actual decision authority and verifiable reference | {{ROLE_AUTHORITY_REFERENCE}} |
| Active standard version/status and release-manifest hash; adopted pin where applicable | {{STANDARD_IDENTITY_OR_REASON}} |
| Repository/branch/HEAD; relevant worktree/index/diff identity | {{SOURCE_AND_UNCOMMITTED_IDENTITY}} |
| Single live EXECUTION_PLAN.md CURRENT/NEXT reference | {{PLAN_REFERENCE_NOT_NEW_POINTER}} |
| Planning authority type/locator, owner and declared revision | {{PLANNING_DECLARATION}} |
| Directly verified planning revision, evidence/date or access limit | {{VERIFICATION_STATUS_AND_LIMIT}} |
| Projection revision, reconciliation status and known discrepancy | {{PROJECTION_STATUS}} |
| Authorized goal, boundaries, explicit exclusions and dependencies | {{BOUNDED_SCOPE}} |
| Applicable acceptance, security, compatibility and closure gates | {{GATES_AND_APPLICABILITY}} |
| Decisions already authorized, with scope and authority reference | {{PRIOR_DECISIONS_OR_NONE}} |
| Observations with evidence locations and required identity/hashes | {{OBSERVATIONS_AND_EVIDENCE}} |
| Assertions/inferences and their limits, separate from observations | {{ASSERTIONS_AND_LIMITS}} |
| Unresolved questions and requested next decision/action | {{QUESTIONS_AND_REQUEST}} |
| Safe work permitted while awaiting review; stop conditions | {{SAFE_CONTINUATION_OR_NONE}} |

## Form A — assignment / handoff

- Assigned CURRENT/task and independently checkable acceptance: {{ASSIGNMENT}}.
- Starting repository/source identity and applicable local commands: {{STARTING_CONTEXT}}.
- Authorized implementation actions versus actions needing a later decision: {{AUTHORITY_BOUNDARY}}.
- Receiving session reconstruction: read pinned policy, profile, execution plan, state, handoff, source/diff and this packet; report any mismatch before dependent work.

## Form B — bounded investigation request or report

- Question and investigation limit; permitted read-only or disposable checks: {{QUESTION_AND_SCOPE}}.
- Observed facts, exact commands/contexts/results and evidence: {{INVESTIGATION_EVIDENCE}}.
- Candidate explanations or recommendations, explicitly distinguished from facts: {{INTERPRETATION}}.
- Decision sought; no implementation or pointer advance unless separately authorized: {{DECISION_REQUEST}}.

## Form C — meaningful Supervisor checkpoint

- Trigger (material architecture, roadmap, security, compatibility, evidence or scope issue): {{TRIGGER}}.
- Work safely completed, protected source/diff identity and applicable checks: {{CHECKPOINT_FACTS}}.
- Options and consequences; unresolved gate; safe continuation while waiting: {{OPTIONS_AND_SAFE_STEP}}.
- Supervisor recommendation versus actual authorized owner decision: {{RECOMMENDATION_AND_AUTHORITY}}.

## Form D — closure candidate

- CURRENT acceptance criterion → exact evidence/status/limitation: {{CRITERIA_MATRIX}}.
- Projected versus actual source, state, dependencies and pointer transition: {{PROJECTED_ACTUAL}}.
- Test/identity/skip, migration/release/external/production gates as applicable: {{GATE_RESULTS}}.
- Remaining debt and any PENDING/NOT APPLICABLE rationale: {{REMAINING_LIMITS}}.
- Request for closure review and separately required protected-action decisions: {{REVIEW_REQUEST}}.

A closure candidate does not mark CURRENT CLOSED, start NEXT, approve semantic adoption, authorize commit/tag/push/release or grant production authority. Record an actual authorized decision and run the applicable existing closure contract before updating the single live execution plan.
