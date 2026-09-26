"""Bounded integrity/structure checker; recorded approval is not runtime acceptance."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import UTC, date, datetime
from pathlib import Path

INVARIANTS = frozenset(
    {
        "AGENT_WORKFLOW.md",
        "DEVELOPMENT_RULES.md",
        "DOCUMENT_GOVERNANCE.md",
        "SECURITY_BASELINE.md",
        "TESTING_AND_EVIDENCE.md",
        "MIGRATION_AND_RELEASE_POLICY.md",
        "UI_IMPLEMENTATION_STANDARDS.md",
        "ADOPTION.md",
        "POLICY_RULES.json",
        "scripts/check_standard.py",
        "scripts/check_docs.py",
    }
)
PROJECT_DOCUMENTS = frozenset(
    {
        "PROJECT_PROFILE.md",
        "PROJECT_STATE.md",
        "EXECUTION_PLAN.md",
        "CAPABILITY_CATALOG.md",
        "ROADMAP_CHANGELOG.md",
        "HANDOFF.md",
        "STANDARD_ADOPTION_HISTORY.md",
    }
)
DISTRIBUTION = INVARIANTS | frozenset(
    {
        "README.md",
        "VERSION",
        "CHANGELOG.md",
        "PROJECT_PROFILE.template.md",
        "PROJECT_STATE.template.md",
        "PROJECT_STATE.template.json",
        "EXECUTION_PLAN.template.md",
        "CAPABILITY_CATALOG.template.md",
        "ROADMAP_CHANGELOG.template.md",
        "HANDOFF.template.md",
        "STANDARD_ADOPTION_HISTORY.template.md",
        "standard-adoption.template.json",
        "scripts/generate_release.py",
        "tests/test_check_standard.py",
        "tests/test_check_docs.py",
    }
)
OWNER_PREFIXES = {
    "WF": "AGENT_WORKFLOW.md",
    "DEV": "DEVELOPMENT_RULES.md",
    "GOV": "DOCUMENT_GOVERNANCE.md",
    "SEC": "SECURITY_BASELINE.md",
    "TEST": "TESTING_AND_EVIDENCE.md",
    "REL": "MIGRATION_AND_RELEASE_POLICY.md",
    "UI": "UI_IMPLEMENTATION_STANDARDS.md",
    "ADP": "ADOPTION.md",
}
CORE = frozenset(
    {
        "WF-PRESERVE",
        "WF-SCOPE",
        "WF-CLOSURE",
        "DEV-CHANGE",
        "DEV-HYGIENE",
        "DEV-BOUNDARY",
        "GOV-TRUTH",
        "GOV-OWNERS",
        "GOV-PRECEDENCE",
        "SEC-SECRETS",
        "SEC-AUTHZ",
        "SEC-LOGGING",
        "SEC-SAFETY",
        "TEST-FORMAL",
        "TEST-GUARDS",
        "TEST-REPORT",
        "TEST-IDENTITY",
        "TEST-CLOSURE",
        "REL-METADATA",
        "REL-MIGRATION",
        "REL-RECOVERY",
        "REL-ARTIFACT",
        "REL-PRODUCTION",
        "UI-ACCESS",
        "ADP-INTEGRITY",
        "ADP-STRUCTURE",
        "ADP-EXCEPT",
        "ADP-UPGRADE",
    }
)
RULE_HEADING = re.compile(r"^## ([A-Z]+-[A-Z0-9-]+):[^\n]*$", re.MULTILINE)
HASH = re.compile(r"[0-9a-f]{64}")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def member(root: Path, name: str) -> Path:
    require(isinstance(name, str) and bool(name), "ADP-INTEGRITY: empty/non-string path")
    relative = Path(name)
    require(
        not relative.is_absolute()
        and ".." not in relative.parts
        and relative.as_posix() == name
        and name != ".",
        f"ADP-INTEGRITY: unsafe path {name}",
    )
    path = root
    for part in relative.parts:
        path = path / part
        require(not path.is_symlink(), f"ADP-INTEGRITY: symlink member {name}")
    require(
        path.resolve().is_relative_to(root.resolve()) and path.is_file(),
        f"ADP-INTEGRITY: missing/unsafe member {name}",
    )
    return path


def read_json(path: Path) -> dict:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f"ADP-STRUCTURE: duplicate JSON key {key}")
            result[key] = value
        return result

    value = json.loads(path.read_text(), object_pairs_hook=unique)
    require(isinstance(value, dict), f"ADP-STRUCTURE: object required {path.name}")
    return value


def string(value, label: str) -> str:
    require(isinstance(value, str) and bool(value.strip()), f"ADP-STRUCTURE: missing {label}")
    return value


def hash_value(value, label: str) -> str:
    require(
        isinstance(value, str) and HASH.fullmatch(value) is not None,
        f"ADP-INTEGRITY: invalid SHA-256 {label}",
    )
    return value


def names(value, label: str) -> set[str]:
    require(
        isinstance(value, list) and all(isinstance(x, str) for x in value),
        f"ADP-STRUCTURE: invalid {label}",
    )
    require(len(value) == len(set(value)), f"ADP-STRUCTURE: duplicate {label}")
    return set(value)


def rule_blocks(text: str) -> tuple[str, dict[str, str]]:
    matches = list(RULE_HEADING.finditer(text))
    require(bool(matches), "ADP-EXCEPT: no canonical rule blocks")
    result = {}
    for index, match in enumerate(matches):
        rid = match.group(1)
        require(rid not in result, f"GOV-OWNERS: duplicate heading {rid}")
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        result[rid] = text[match.start() : end]
    return text[: matches[0].start()], result


def check_release(standard: Path) -> tuple[dict, dict]:
    release = read_json(member(standard, "standard-release.json"))
    require(
        release.get("schema_version") == 2 and release.get("standard") == "ai-project-standard",
        "ADP-INTEGRITY: unsupported release contract",
    )
    require(release.get("status") in {"DRAFT", "RC", "FINAL"}, "ADP-INTEGRITY: release status")
    require(
        release.get("version") == member(standard, "VERSION").read_text().strip(),
        "ADP-INTEGRITY: version mismatch",
    )
    require(
        names(release.get("invariants"), "release invariants") == INVARIANTS,
        "ADP-INTEGRITY: required invariant set mismatch",
    )
    files = release.get("files")
    require(
        isinstance(files, dict) and set(files) == DISTRIBUTION,
        "ADP-INTEGRITY: required distribution set mismatch",
    )
    for name, expected in files.items():
        hash_value(expected, name)
        require(digest(member(standard, name)) == expected, f"ADP-INTEGRITY: standard drift {name}")
    registry = read_json(member(standard, "POLICY_RULES.json"))
    require(registry.get("schema_version") == 1, "GOV-OWNERS: registry schema")
    require(
        names(registry.get("invariants"), "registry invariants") == INVARIANTS,
        "GOV-OWNERS: registry invariants mismatch",
    )
    require(
        names(registry.get("distribution_files"), "registry distribution") == DISTRIBUTION,
        "GOV-OWNERS: registry distribution mismatch",
    )
    require(
        names(registry.get("required_project_owned"), "registry project documents")
        == PROJECT_DOCUMENTS,
        "GOV-OWNERS: required documents mismatch",
    )
    rules = registry.get("rules")
    require(isinstance(rules, dict) and set(rules) >= CORE, "GOV-OWNERS: missing core rules")
    actual = {}
    for owner in OWNER_PREFIXES.values():
        _, blocks = rule_blocks(member(standard, owner).read_text())
        for rid in blocks:
            require(rid not in actual, f"GOV-OWNERS: duplicate global rule {rid}")
            actual[rid] = owner
    require(set(rules) == set(actual), "GOV-OWNERS: registry/heading mismatch")
    for rid, row in rules.items():
        require(
            isinstance(row, dict) and set(row) == {"owner", "waivable"},
            f"GOV-OWNERS: invalid metadata {rid}",
        )
        require(
            row["owner"] == actual[rid] == OWNER_PREFIXES.get(rid.split("-")[0]),
            f"GOV-OWNERS: owner mismatch {rid}",
        )
        require(isinstance(row["waivable"], bool), f"ADP-EXCEPT: eligibility type {rid}")
        require(rid not in CORE or row["waivable"] is False, f"ADP-EXCEPT: core is waivable {rid}")
    return release, registry


def check(standard: Path, consumer: Path | None = None) -> dict:
    release, registry = check_release(standard)
    result = {
        "integrity": "PASS",
        "release_status": release["status"],
        "structure": None,
        "semantic": "NOT ASSESSED",
        "runtime_release": "NOT ASSESSED",
    }
    if consumer is None:
        return result
    adoption = read_json(member(consumer, "standard-adoption.json"))
    require(
        adoption.get("schema_version") == 2 and adoption.get("standard") == "ai-project-standard",
        "ADP-STRUCTURE: unsupported consumer contract",
    )
    require(adoption.get("version") == release["version"], "ADP-INTEGRITY: version pin mismatch")
    pin = hash_value(adoption.get("release_manifest_sha256"), "release pin")
    require(
        pin == digest(member(standard, "standard-release.json")),
        "ADP-INTEGRITY: release pin mismatch",
    )
    string(adoption.get("source_reference"), "source_reference")
    require(
        date.fromisoformat(string(adoption.get("adopted_on"), "adopted_on"))
        <= datetime.now(UTC).date(),
        "ADP-STRUCTURE: future adoption date",
    )
    invariants = adoption.get("invariants")
    require(
        isinstance(invariants, dict) and set(invariants) == INVARIANTS,
        "ADP-STRUCTURE: required consumer invariant set mismatch",
    )
    owned = names(adoption.get("project_owned"), "project_owned")
    require(
        owned >= PROJECT_DOCUMENTS and not (owned & INVARIANTS),
        "ADP-STRUCTURE: missing required project-owned document or invariant collision",
    )
    for name in owned:
        member(consumer, name)
    exceptions = adoption.get("exceptions")
    require(isinstance(exceptions, list), "ADP-EXCEPT: exceptions must be a list")
    ids, rule_ids, drift = set(), set(), {}
    required = {
        "id",
        "rule",
        "path",
        "scope",
        "reason",
        "risk",
        "compensating_control",
        "approved_by",
        "approved_on",
        "review_on",
        "status",
    }
    for row in exceptions:
        require(
            isinstance(row, dict)
            and required <= set(row)
            and set(row) <= required | {"expected_sha256"},
            "ADP-EXCEPT: exception schema",
        )
        for field in required:
            string(row[field], f"exception.{field}")
        rid = row["rule"]
        require(row["id"] not in ids and rid not in rule_ids, "ADP-EXCEPT: duplicate id/rule")
        ids.add(row["id"])
        rule_ids.add(rid)
        require(rid in registry["rules"], f"ADP-EXCEPT: unknown rule {rid}")
        metadata = registry["rules"][rid]
        require(metadata["waivable"], f"ADP-EXCEPT: non-waivable rule {rid}")
        require(row["path"] == metadata["owner"], f"ADP-EXCEPT: owner mismatch {rid}")
        require(row["status"] == "APPROVED", f"ADP-EXCEPT: unapproved {rid}")
        approval = date.fromisoformat(row["approved_on"])
        review = date.fromisoformat(row["review_on"])
        require(
            approval <= datetime.now(UTC).date() <= review,
            f"ADP-EXCEPT: expired/future approval {rid}",
        )
        if "expected_sha256" in row:
            hash_value(row["expected_sha256"], f"exception.{rid}")
            drift.setdefault(row["path"], {})[rid] = row["expected_sha256"]
    for name in sorted(INVARIANTS):
        expected = release["files"][name]
        require(invariants[name] == expected, f"ADP-INTEGRITY: invariant pin mismatch {name}")
        actual_path = member(consumer, name)
        actual_hash = digest(actual_path)
        if actual_hash == expected:
            require(name not in drift, f"ADP-EXCEPT: unnecessary drift exception {name}")
            continue
        permitted = drift.get(name, {})
        require(
            bool(permitted) and all(value == actual_hash for value in permitted.values()),
            f"ADP-INTEGRITY: unauthorized drift {name}",
        )
        require(name.endswith(".md"), f"ADP-EXCEPT: tooling/registry drift prohibited {name}")
        old_header, old_blocks = rule_blocks(member(standard, name).read_text())
        new_header, new_blocks = rule_blocks(actual_path.read_text())
        require(
            old_header == new_header and set(old_blocks) == set(new_blocks),
            f"ADP-EXCEPT: structural drift {name}",
        )
        changed = {rid for rid in old_blocks if old_blocks[rid] != new_blocks[rid]}
        require(changed == set(permitted), f"ADP-EXCEPT: unapproved block drift {name}")
    acceptance = adoption.get("semantic_acceptance")
    require(
        isinstance(acceptance, dict) and acceptance.get("status") in {"PENDING", "APPROVED"},
        "ADP-STRUCTURE: semantic acceptance record missing/invalid",
    )
    if acceptance["status"] == "APPROVED":
        require(release["status"] == "FINAL", "ADP-STRUCTURE: approval requires FINAL content")
        for key in ("approved_by", "approved_on", "decision_reference", "scope", "evidence"):
            string(acceptance.get(key), f"semantic_acceptance.{key}")
        require(
            date.fromisoformat(acceptance["approved_on"]) <= datetime.now(UTC).date(),
            "ADP-STRUCTURE: future semantic approval",
        )
        require(
            acceptance.get("reviewed_release_manifest_sha256") == pin,
            "ADP-INTEGRITY: stale semantic approval pin",
        )
        require(acceptance["evidence"] in owned, "ADP-STRUCTURE: semantic evidence not owned")
        member(consumer, acceptance["evidence"])
    result.update(structure="PASS", semantic=acceptance["status"])
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--standard", type=Path)
    parser.add_argument("--consumer", type=Path)
    parser.add_argument("--require-semantic", action="store_true")
    args = parser.parse_args()
    try:
        consumer = args.consumer
        standard = args.standard
        if standard is None:
            consumer = consumer or Path.cwd()
            adoption = read_json(member(consumer, "standard-adoption.json"))
            version = string(adoption.get("version"), "version")
            require(
                re.fullmatch(r"\d+\.\d+\.\d+", version) is not None,
                "ADP-INTEGRITY: unsafe snapshot version",
            )
            standard = consumer / ".project-standard" / version
        result = check(standard, consumer)
        print(f"INTEGRITY PASS; standard content {result['release_status']}")
        if result["structure"]:
            print("ADOPTION STRUCTURE PASS")
        print(
            f"SEMANTIC ACCEPTANCE {result['semantic']} "
            "(record only; no authority/evidence authentication)"
        )
        print("RUNTIME/RELEASE ACCEPTANCE NOT ASSESSED")
        if args.require_semantic:
            require(result["semantic"] == "APPROVED", "ADP-STRUCTURE: semantic acceptance pending")
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        print(f"FAIL: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
