# {{PROJECT_NAME}} handoff

As of {{DATE}}. Resume from current local working tree, preserving unrelated modifications. Read `PROJECT_PROFILE.md`, `PROJECT_STATE.md`, `EXECUTION_PLAN.md`, `standard-adoption.json` and `AGENT_WORKFLOW.md`; verify facts against source.

- Current version/source and architecture: {{SOURCE_BACKED_SUMMARY}}.
- CURRENT/NEXT and last closed checkpoint: {{PLAN_REFERENCE}}.
- Known debt/risks and missing evidence: {{CURRENT_LIMITATIONS}}.
- Next governance checkpoint: {{AUTHORIZED_NEXT_CHECKPOINT_OR_PENDING}}.
- Verification evidence and safe commands: {{PROFILE_AND_EVIDENCE_REFERENCE}}.

For another machine/account, transfer sanitized full required source plus exact identity, lockfiles and governance. Do not transfer secrets, runtime data, backups or generated logs; provision test credentials independently. An upgrade delta alone is not a full-source handoff. Never infer release/deployment approval from a handoff document.
