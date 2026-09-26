# Security, secrets and logging baseline

## SEC-SECRETS: Credentials and retained keys

Keep credentials/signing/encryption keys outside source, release artifacts, public UI and test evidence. Use protected runtime storage, restrictive permissions and safe writes. Protect backups separately and preserve keys needed to decrypt existing records. Never silently regenerate missing keys over encrypted data. Hash nonrecoverable verifiers, encrypt recoverable credentials and compare secrets safely according to purpose.

## SEC-AUTHZ: Required security guards

Required authentication/authorization fails closed on missing, malformed, unsupported, stale or mismatched inputs. Apply relevant checks on the server on every read/write; navigation is not authorization. Validate inputs and allowed callback/destination targets before side effects. Use least privilege, expiration, replay/revocation/binding controls required by the source contract. Browser mutations require appropriate CSRF protection, sessions appropriate cookie/server validation and deployment TLS settings. Development defaults are not production proof. Missing controls remain explicit debt; adoption does not implement them.

## SEC-LOGGING: Curated evidence and personal data

Use bounded safe error codes/counts/identifiers. Do not emit raw credential headers, callback codes, tokens, personal profiles, secret-bearing queries or raw external bodies in evidence/logs. Restrict retained personal data to documented purposes and protection/retention boundaries. Redaction alone does not protect stored profiles. Report actual audit/log coverage; model timestamps or append-only conventions do not prove tamper resistance.

## SEC-SAFETY: External and persistent-data boundaries

Ordinary development tests use isolated synthetic data and mocked transports, without production credentials, inherited secret environment files, live identity-provider calls or shared persistent database mutations. Separate authorized live acceptance must name safe credentials/environment, scope and data boundaries. Mocks prove local protocol behavior only. Never infer live acceptance or production approval from them. These boundaries cannot be waived by a standard exception.
