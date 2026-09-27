# {{PROJECT_NAME}} handoff

As of {{DATE}}. Resume from current local working tree, preserving unrelated modifications. Read `PROJECT_PROFILE.md`, `PROJECT_STATE.md`, `EXECUTION_PLAN.md`, `standard-adoption.json` and `AGENT_WORKFLOW.md`; verify facts against source.

- Current version/source and architecture: {{SOURCE_BACKED_SUMMARY}}.
- CURRENT/NEXT and last closed checkpoint: {{PLAN_REFERENCE}}.
- Known debt/risks and missing evidence: {{CURRENT_LIMITATIONS}}.
- Next governance checkpoint: {{AUTHORIZED_NEXT_CHECKPOINT_OR_PENDING}}.
- Verification evidence and safe commands: {{PROFILE_AND_EVIDENCE_REFERENCE}}.
- Latest assignment, investigation, checkpoint or closure-candidate packet IDs and durable locations: {{LATEST_PACKET_REFERENCES_OR_PENDING}}.
- Latest actual authorized decision, scope, authority channel/reference and remaining authorized work: {{DECISION_AND_REMAINING_SCOPE_OR_PENDING}}.
- Exact safe resumption step and stop/review triggers for a new account/session: {{SAFE_RESUMPTION_STEP_AND_TRIGGERS}}.

This handoff summarizes EXECUTION_PLAN.md; it does not own CURRENT/NEXT or authorize NEXT. A packet or remembered conversation cannot replace source/plan inspection. If the decision cannot be verified through the approved channel, report PENDING and continue only independently safe work.

For another machine/account, transfer sanitized full required source plus exact identity, lockfiles and governance. Do not transfer secrets, runtime data, backups or generated logs; provision test credentials independently. An upgrade delta alone is not a full-source handoff. Never infer release/deployment approval from a handoff document.

## Delivery mode and receiving bootstrap

Record source-backed Mode A direct worktree, Mode B external versioned full/delta APPLICATION delivery, or B-to-A transition. Work/iWork is an optional historical producer example, not dependency authority. A delta delivery is not a self-contained full account-transfer handoff. Mode B receiver needs a separately available apply_package.sh/bootstrap bundle and its validation/preservation/recovery instructions before installed ./run.sh can run. Declare external package-apply and release/handoff roots; preserve historical debt explicitly. Third-party dependency install/resolution is separate from applying application ZIP bytes.
