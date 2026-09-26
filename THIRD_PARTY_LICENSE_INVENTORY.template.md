# {{PROJECT_NAME}} third-party license inventory

This reference declares no third-party package dependency and bundles no third-party binary or asset. Runtime and image selections below are references, not redistributed content or legal approval. Unknown/conditional/PENDING decisions never mean approved; review actual version, upstream license evidence, commercial use and redistribution/OEM/SaaS constraints before application redistribution or deployment. No invented license or cost approval is implied by a checker PASS.

| Dependency/asset | Version | Purpose | Source | License | Commercial-use constraints | Redistribution/OEM/SaaS constraints | Cost/licensing risk | Bundled | Decision | Evidence/reference |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Python runtime / standard library | >=3.11 (exact runtime selected by consumer) | Native health/test reference | Upstream runtime selected by project owner | PENDING exact distribution review | PENDING | PENDING | PENDING | No | REFERENCE_ONLY | pyproject.toml runtime range; no license approval |
| Optional container base | python:3.11-slim (tag, not immutable digest) | Optional health example | Upstream image selected by project owner | PENDING exact image/component inventory | PENDING | PENDING | PENDING | No | REFERENCE_ONLY | Dockerfile.scaffold; runtime/redistribution review pending |

Inventory review status REFERENCE_ONLY means there is no bundled asset to approve. A consumer adding dependencies, images or assets must list their exact identity and disposition; bundled/conditional items need explicit review. The static checker verifies inventory shape and declared review state, not license correctness. Standard artifact approval is distinct from application deployment and third-party redistribution approval.

## Instantiation record

Declare actual owners, command mappings, modes, paths, applicability, evidence and unresolved debt: {{PROJECT_LOCAL_DECISIONS_OR_PENDING}}. Replace reference facts with current source-backed facts before acceptance.
