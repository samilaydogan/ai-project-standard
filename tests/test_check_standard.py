"""Synthetic isolated integrity/waiver/approval regression cases; no runtime imports."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import check_standard as checker
import generate_release


class StandardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.standard = self.root / "standard"
        source = Path(__file__).resolve().parents[1]
        for name in checker.DISTRIBUTION:
            target = self.standard / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source / name, target)
        self.write_release()
        self.consumer = self.root / "consumer"
        for name in checker.INVARIANTS:
            target = self.consumer / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(self.standard / name, target)
        for name in checker.PROJECT_DOCUMENTS | {"docs/evidence.md", ".env.example", ".dockerignore", "pyproject.toml"}:
            target = self.consumer / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("Synthetic fixture, not real acceptance.\n")
        for name in (
            '.dockerignore',
            'pyproject.toml',
            'source-exclusions.json',
            'scripts/foundation_contract.py',
            'scripts/reference_tests.py',
            'scripts/test_controls.py',
            'scripts/release_commit.py',
            'release-commit-profile.json',
            'test-control-profile.json',
            'scripts/test_network_guard.py',
            'scripts/scaffold_status.py',
            'INSTALLATION.md',
            'MIGRATION_RECOVERY.md',
            'OPERATIONS_RUNBOOK.md',
            'THIRD_PARTY_LICENSE_INVENTORY.md',
            ".env.example",
            ".gitignore",
            "run.sh",
            "execution-profile.json",
            "scripts/health_scaffold.py",
            "scripts/scaffold_lint.py",
        ):
            target = self.consumer / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source / name, target)
        (self.consumer / "PROJECT_PROFILE.md").write_text(
            "execution-profile.json EXECUTION_FACADE.md\n"
        )
        self.application_version("0.1.0")
        self.adoption = {
            "schema_version": 2,
            "standard": "ai-project-standard",
            "version": (self.standard / "VERSION").read_text().strip(),
            "adopted_on": "2026-01-01",
            "source_reference": "synthetic isolated content snapshot",
            "release_manifest_sha256": checker.digest(self.standard / "standard-release.json"),
            "invariants": {
                name: checker.digest(self.standard / name) for name in checker.INVARIANTS
            },
            "project_owned": sorted(checker.PROJECT_DOCUMENTS | {"docs/evidence.md", ".env.example", ".dockerignore", "pyproject.toml"}),
            "exceptions": [],
            "semantic_acceptance": {"status": "PENDING"},
        }
        self.save()

    def application_version(self, version):
        """Explicit disposable consumer instantiation, never a production mutator."""
        path = self.consumer / 'pyproject.toml'
        import re
        path.write_text(re.sub(r'version = "[^"]+"', f'version = "{version}"', path.read_text()))
        profile_path = self.consumer / 'execution-profile.json'
        profile = json.loads(profile_path.read_text())
        profile['foundation']['identity']['application_version'] = version
        profile['foundation']['toolchain']['manifest_sha256'] = checker.digest(path)
        profile_path.write_text(json.dumps(profile))

    def test_new_consumer_is_coherent_and_check_is_readonly(self):
        before = {str(p.relative_to(self.consumer)): (p.read_bytes(), p.stat().st_mode)
                  for p in self.consumer.rglob('*') if p.is_file()}
        self.assertEqual(checker.check(self.standard, self.consumer, new_consumer=True)['structure'], 'PASS')
        profile = json.loads((self.consumer / 'execution-profile.json').read_text())
        self.assertEqual(profile['foundation']['identity']['application_version'], '0.1.0')
        self.assertNotEqual('0.1.0', (self.standard / 'VERSION').read_text().strip())
        after = {str(p.relative_to(self.consumer)): (p.read_bytes(), p.stat().st_mode)
                 for p in self.consumer.rglob('*') if p.is_file()}
        self.assertEqual(before, after)

    def test_reference_zero_cannot_leak_into_real_consumer(self):
        self.application_version('0.0.0')
        self.rejected('real consumer cannot retain internal/reference')

    def test_existing_consumer_upgrade_preserves_version(self):
        self.application_version('2.7.9')
        before = (self.consumer / 'pyproject.toml').read_bytes()
        self.assertEqual(checker.check(self.standard, self.consumer)['structure'], 'PASS')
        self.assertEqual(before, (self.consumer / 'pyproject.toml').read_bytes())
        with self.assertRaisesRegex(ValueError, 'new consumer must initialize'):
            checker.check(self.standard, self.consumer, new_consumer=True)
        self.assertEqual(before, (self.consumer / 'pyproject.toml').read_bytes())

    def test_new_consumer_cli_and_missing_context(self):
        argv = [sys.executable, '-B', str(self.standard / 'scripts/check_standard.py'),
                '--standard', str(self.standard), '--new-consumer']
        result = subprocess.run(argv + ['--consumer', str(self.consumer)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout)
        result = subprocess.run(argv, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn('requires consumer context', result.stdout)

    def test_task_permission_does_not_initialize_approval(self):
        template = json.loads((self.standard / 'standard-adoption.template.json').read_text())
        self.assertEqual(template['semantic_acceptance'], {'status': 'PENDING'})
        (self.consumer / 'docs/evidence.md').write_text('Synthetic implementation authorized; result presented for review. No human decision yet.\n')
        self.assertEqual(checker.check(self.standard, self.consumer)['semantic'], 'PENDING')
        self.adoption['semantic_acceptance'] = {'status': 'APPROVED', 'decision_reference': 'implementation task'}
        self.rejected('semantic_acceptance.approved_by')

    def test_os_metadata_release_member_rejected(self):
        name = '.DS_Store'
        (self.standard / name).write_bytes(b'synthetic finder metadata')
        release_path = self.standard / 'standard-release.json'
        release = json.loads(release_path.read_text())
        release['files'][name] = checker.digest(self.standard / name)
        release_path.write_text(json.dumps(release))
        with patch.object(checker, 'DISTRIBUTION', checker.DISTRIBUTION | {name}):
            with self.assertRaisesRegex(ValueError, 'excluded release member .DS_Store'):
                checker.check_release(self.standard)

    def write_release(self):
        (self.standard / "standard-release.json").write_text(
            json.dumps(generate_release.payload(self.standard, "FINAL"), indent=2) + "\n"
        )

    def save(self):
        (self.consumer / "standard-adoption.json").write_text(json.dumps(self.adoption))

    def exception(self, rid="WF-COMMANDS"):
        registry = json.loads((self.standard / "POLICY_RULES.json").read_text())
        return {
            "id": "fixture-exception",
            "rule": rid,
            "path": registry["rules"][rid]["owner"],
            "scope": "synthetic isolated check",
            "reason": "fixture reason",
            "risk": "fixture risk",
            "compensating_control": "fixture control",
            "approved_by": "Synthetic fixture authority",
            "approved_on": "2026-01-01",
            "review_on": "2099-01-01",
            "status": "APPROVED",
        }

    def rejected(self, message=None):
        self.save()
        with self.assertRaisesRegex(ValueError, message or "ADP-|GOV-"):
            checker.check(self.standard, self.consumer)

    def test_valid_structure_is_not_semantic_approval(self):
        result = checker.check(self.standard, self.consumer)
        self.assertEqual(result["structure"], "PASS")
        self.assertEqual(result["semantic"], "PENDING")
        self.assertEqual(result["runtime_release"], "NOT ASSESSED")

    def test_portable_forms_are_distributed_but_not_policy_or_required_project_files(self):
        for name in ("AGENTS.template.md", "SUPERVISOR_PACKET.template.md"):
            self.assertIn(name, checker.DISTRIBUTION)
            self.assertNotIn(name, checker.INVARIANTS)
            self.assertNotIn(name, checker.PROJECT_DOCUMENTS)
        self.assertNotIn("AGENTS.md", checker.PROJECT_DOCUMENTS)
        self.assertEqual(checker.check(self.standard, self.consumer)["structure"], "PASS")

    def test_missing_portable_form_fails_distribution_integrity(self):
        (self.standard / "SUPERVISOR_PACKET.template.md").unlink()
        self.rejected("missing/unsafe member SUPERVISOR_PACKET.template.md")

    def test_portable_authority_rules_cannot_be_waived(self):
        for rid, owner in (("WF-PORTABLE", "AGENT_WORKFLOW.md"),
                           ("GOV-PLAN-AUTHORITY", "DOCUMENT_GOVERNANCE.md")):
            with self.subTest(rule=rid):
                registry = json.loads((self.standard / "POLICY_RULES.json").read_text())
                self.assertEqual(registry["rules"][rid], {"owner": owner, "waivable": False})
                self.adoption["exceptions"] = [self.exception(rid)]
                self.rejected("non-waivable")

    def test_nonexecutable_consumer_facade(self):
        (self.consumer / "run.sh").chmod(0o644)
        self.rejected("facade not executable")

    def test_readonly_package_mapping_rejected(self):
        path = self.consumer / "execution-profile.json"
        profile = json.loads(path.read_text())
        profile["commands"]["apply-package"] = {
            "status": "READY",
            "mutability": "read-only",
            "argv": ["python3", "-c", "print('must never execute')"],
            "prerequisites": [],
        }
        path.write_text(json.dumps(profile))
        self.rejected("must be mutating")

    def test_missing_execution_baseline(self):
        path = self.consumer / "execution-profile.json"
        profile = json.loads(path.read_text())
        del profile["commands"]["doctor"]
        path.write_text(json.dumps(profile))
        self.rejected("missing baseline")

    def test_compatibility_removal_boundary_required(self):
        path = self.consumer / "execution-profile.json"
        profile = json.loads(path.read_text())
        profile["compatibility_launchers"] = [{"path": "run.sh", "removal_boundary": ""}]
        path.write_text(json.dumps(profile))
        self.rejected("compatibility schema")

    def test_unconfigured_base_test_is_rejected(self):
        path = self.consumer / "execution-profile.json"
        profile = json.loads(path.read_text())
        profile["commands"]["test"].update(status="NOT CONFIGURED", argv=[])
        path.write_text(json.dumps(profile))
        self.rejected("configured base validation")

    def test_exact_maintainer_evidence_is_not_distributed(self):
        evidence = self.standard / "maintainer-only" / "source-evidence.json"
        evidence.parent.mkdir()
        evidence.write_text('{"source": "SourceProductAlpha"}')
        release = generate_release.payload(self.standard, "FINAL")
        self.assertNotIn("maintainer-only/source-evidence.json", release["files"])
        self.assertNotIn("maintainer-only/source-evidence.json", release["invariants"])
        self.assertTrue(all(not name.startswith("docs/") for name in release["files"]))

    def test_missing_pin(self):
        del self.adoption["release_manifest_sha256"]
        self.rejected("invalid SHA-256")

    def test_wrong_pin(self):
        self.adoption["release_manifest_sha256"] = "0" * 64
        self.rejected("release pin mismatch")

    def test_wrong_version(self):
        self.adoption["version"] = "99.0.0"
        self.rejected("version pin mismatch")

    def test_missing_invariant(self):
        del self.adoption["invariants"]["ADOPTION.md"]
        self.rejected("invariant set mismatch")

    def test_missing_required_document_inventory(self):
        self.adoption["project_owned"].remove("PROJECT_PROFILE.md")
        self.rejected("required project-owned")

    def test_missing_required_document_bytes(self):
        (self.consumer / "PROJECT_PROFILE.md").unlink()
        self.rejected("missing/unsafe")

    def test_nonwaivable_core_exceptions(self):
        for rid in sorted(checker.CORE):
            with self.subTest(rule=rid):
                self.adoption["exceptions"] = [self.exception(rid)]
                self.rejected("non-waivable")

    def test_unknown_rule(self):
        row = self.exception()
        row["rule"] = "WF-NOTREAL"
        self.adoption["exceptions"] = [row]
        self.rejected("unknown rule")

    def test_wrong_rule_owner(self):
        row = self.exception()
        row["path"] = "DEVELOPMENT_RULES.md"
        self.adoption["exceptions"] = [row]
        self.rejected("owner mismatch")

    def test_expired_exception(self):
        row = self.exception()
        row["review_on"] = "2026-01-01"
        self.adoption["exceptions"] = [row]
        self.rejected("expired/future")

    def test_unapproved_exception(self):
        row = self.exception()
        row["status"] = "PENDING"
        self.adoption["exceptions"] = [row]
        self.rejected("unapproved")

    def test_duplicate_exception(self):
        row = self.exception()
        self.adoption["exceptions"] = [row, row]
        self.rejected("duplicate")

    def test_allowed_narrow_block_drift(self):
        target = self.consumer / "AGENT_WORKFLOW.md"
        target.write_text(
            target.read_text().replace("await terminal evidence", "await fixture evidence")
        )
        row = self.exception()
        row["expected_sha256"] = checker.digest(target)
        self.adoption["exceptions"] = [row]
        self.save()
        self.assertEqual(checker.check(self.standard, self.consumer)["structure"], "PASS")

    def test_waivable_exception_cannot_hide_core_drift(self):
        target = self.consumer / "AGENT_WORKFLOW.md"
        text = target.read_text().replace("await terminal evidence", "await fixture evidence")
        target.write_text(
            text.replace("Do not begin NEXT automatically.", "Begin NEXT automatically.")
        )
        row = self.exception()
        row["expected_sha256"] = checker.digest(target)
        self.adoption["exceptions"] = [row]
        self.rejected("unapproved block drift")

    def test_tooling_drift(self):
        target = self.consumer / "scripts/check_standard.py"
        target.write_text(target.read_text() + "\n# altered synthetic tooling\n")
        self.rejected("unauthorized drift")

    def test_incomplete_release_inventory_even_if_repinned(self):
        path = self.standard / "standard-release.json"
        release = json.loads(path.read_text())
        del release["files"]["README.md"]
        path.write_text(json.dumps(release))
        self.adoption["release_manifest_sha256"] = checker.digest(path)
        self.rejected("distribution set mismatch")

    def test_registry_cannot_make_core_waivable(self):
        path = self.standard / "POLICY_RULES.json"
        registry = json.loads(path.read_text())
        registry["rules"]["SEC-SAFETY"]["waivable"] = True
        path.write_text(json.dumps(registry))
        self.write_release()
        self.rejected("core is waivable")

    def test_parent_symlink_member(self):
        external = self.root / "external"
        external.mkdir()
        (external / "item.md").write_text("fixture")
        (self.consumer / "linked").symlink_to(external, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            checker.member(self.consumer, "linked/item.md")

    def test_absolute_and_traversal_paths(self):
        for name in ("../item.md", "/item.md"):
            with self.assertRaisesRegex(ValueError, "unsafe path"):
                checker.member(self.consumer, name)

    def test_duplicate_json_keys(self):
        (self.consumer / "standard-adoption.json").write_text(
            '{"schema_version":2,"schema_version":2}'
        )
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            checker.check(self.standard, self.consumer)

    def test_approved_record_requires_current_pin_and_evidence(self):
        self.adoption["semantic_acceptance"] = {
            "status": "APPROVED",
            "approved_by": "Synthetic human owner (fixture only)",
            "approved_on": "2026-01-01",
            "decision_reference": "Synthetic post-result human instruction: commit reviewed exact-hash result",
            "scope": "synthetic fixture only",
            "evidence": "docs/evidence.md",
            "reviewed_release_manifest_sha256": self.adoption["release_manifest_sha256"],
        }
        self.save()
        self.assertEqual(checker.check(self.standard, self.consumer)["semantic"], "APPROVED")
        self.adoption["semantic_acceptance"]["reviewed_release_manifest_sha256"] = "0" * 64
        self.rejected("stale semantic")

    def test_portable_default_without_sibling(self):
        snapshot = self.consumer / ".project-standard" / self.adoption["version"]
        shutil.copytree(self.standard, snapshot)
        result = subprocess.run(
            [sys.executable, "-B", "scripts/check_standard.py"],
            cwd=self.consumer,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("SEMANTIC ACCEPTANCE PENDING", result.stdout)
        result = subprocess.run(
            [sys.executable, "-B", "scripts/check_standard.py", "--require-semantic"],
            cwd=self.consumer,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 1)


if __name__ == "__main__":
    unittest.main()
