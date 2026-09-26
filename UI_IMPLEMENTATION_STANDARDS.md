# UI implementation standards

## UI-APPLY: Applicable surfaces and established patterns

Apply to actual new/changed user-visible surfaces. The profile records surfaces, framework, supported themes and QA capabilities. Reuse established templates/components/design language; prefer existing patterns. No imported brand, framework, CSS prefix, adapter count or global redesign is mandated. Preserve stronger local UI contracts; adoption must not silently weaken them. Unchanged documentation-only work may record UI QA NOT APPLICABLE.

## UI-ACCESS: Presentation and route semantics

Keep presentation separate from domain/security decisions; SEC-AUTHZ owns backend authorization. Preserve routes, deep links, interaction and permission semantics unless the authorized contract changes them. Check hierarchy, spacing, labels/errors, empty/loading/disabled states, keyboard/focus, accessible status text beyond color, responsive layout and supported themes.

## UI-LIST: Status-filter applicability

A new or changed status-bearing operational list requires a validated server-scoped status filter when the local profile/contract identifies filtering as applicable to its task. The profile must declare the trigger before acceptance; if such a list is changed without a declaration, applicability is PENDING rather than silently optional. Preserve any stronger existing first-release filter mandate. Applicable filters use allowed values, preserve/clear selection, explain empty results and never widen access. A justified NOT APPLICABLE records the surface and rationale.

## UI-MAPPING: Implementation and QA mapping

Map touched routes to templates/components, services and acceptance evidence. Keep dependencies local/pinned where the project contract requires and retain license notices under DEV-LICENSE. TEST-SCREENSHOT owns browser/static evidence distinctions and triggers. Absent tools or template fields are not implementation/evidence claims.
