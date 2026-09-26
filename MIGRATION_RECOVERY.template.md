# {{PROJECT_NAME}} migration and recovery

The reference has database_mode=none, migration=NOT_APPLICABLE and backup=NOT_APPLICABLE; there is no retained application data. These are explicit day-zero choices, not a universal architecture. Migration, restore and backup commands are NOT_APPLICABLE and no engine is bundled.

A stateful adaptation must declare embedded/container/external mode and engine, current/target schema source, isolated test DB, forward-idempotent command and read-only preflight. Source behind DB fails closed. automatic_down_migration stays false; destructive down migrations are never automatic. Published migrations remain immutable under REL-MIGRATION; emergency reconciliation requires the documented authorized recovery procedure.

Before migration, evaluate DB/data/source/config compatibility together and declare whether a verified backup is required. Record identity/hash, preflight/current/target and real command/count/exit evidence. A missing required backup or pending recovery path prevents that operational acceptance. DB passwords are symbolic secret env declarations, not committed examples.

Document partial-failure detection, safe retry/idempotency owner, recovery checkpoint and escalation. An explicit destructive restore requires confirmation, integrity metadata, compatibility review, a pre-restore safety backup and secure retention of decryption keys. A backup belongs outside source and is never a sanitized handoff. Verify restoration into isolated state; never drill on shared/production data without explicit authorization. NOT_IMPLEMENTED/PENDING commands must never be described as successful recovery. A project-local procedure supplies concrete commands, retention and owners; v0.3.0 may supply generic helpers later.

## Instantiation record

Declare actual owners, command mappings, modes, paths, applicability, evidence and unresolved debt: {{PROJECT_LOCAL_DECISIONS_OR_PENDING}}. Replace reference facts with current source-backed facts before acceptance.
