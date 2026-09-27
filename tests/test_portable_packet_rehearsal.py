"""Maintainer-only, synthetic two-process rehearsal of portable artifact transfer.

This checks reconstructability, not AI reasoning, sender authentication, external
service access, human approval, or consumer runtime acceptance.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


STANDARD = Path(__file__).resolve().parents[1]
STANDARD_RECORDS = (
    "AGENT_WORKFLOW.md",
    "DOCUMENT_GOVERNANCE.md",
    "TESTING_AND_EVIDENCE.md",
    "MIGRATION_AND_RELEASE_POLICY.md",
    "ADOPTION.md",
    "standard-release.json",
)

CODING_SESSION = r'''
import hashlib, json, sys
from pathlib import Path

root = Path(sys.argv[1])
def read(name): return (root / name).read_text()
def fields(name):
    return dict(line.split(': ', 1) for line in read(name).splitlines() if ': ' in line)

for name in ('AGENT_WORKFLOW.md', 'DOCUMENT_GOVERNANCE.md',
             'TESTING_AND_EVIDENCE.md', 'MIGRATION_AND_RELEASE_POLICY.md',
             'ADOPTION.md', 'standard-release.json', 'PROJECT_PROFILE.md',
             'EXECUTION_PLAN.md', 'PROJECT_STATE.md', 'HANDOFF.md',
             'assignment.packet.md'):
    read(name)
assert '## WF-PORTABLE:' in read('AGENT_WORKFLOW.md')
assert '## GOV-PLAN-AUTHORITY:' in read('DOCUMENT_GOVERNANCE.md')
profile = fields('PROJECT_PROFILE.md')
plan = fields('EXECUTION_PLAN.md')
state = fields('PROJECT_STATE.md')
handoff = fields('HANDOFF.md')
packet = fields('assignment.packet.md')
assert plan['CURRENT'] == 'UNIT-A IN PROGRESS'
assert plan['NEXT'] == 'UNIT-B NOT STARTED'
assert packet['Work-unit'] == 'UNIT-A'
assert packet['Plan pointer'] == plan['CURRENT']
assert handoff['Latest packet'] == packet['Packet ID']
assert packet['Source HEAD'] == state['HEAD']
manifest = json.loads(read('standard-release.json'))
assert packet['Standard version/status'] == manifest['version'] + ' ' + manifest['status']
assert packet['Standard hash'] == hashlib.sha256(
    (root / 'standard-release.json').read_bytes()).hexdigest()
assert packet['Planning locator'] == profile['Planning locator']
assert packet['Planning declaration'] == profile['Declared revision']
for key in ('Packet kind', 'Packet ID', 'Project', 'Timestamp', 'Issuer role',
            'Decision authority', 'Uncommitted diff', 'Authorized scope',
            'Exclusions', 'Dependencies', 'Direct verification',
            'Projection revision', 'Acceptance gates', 'Observations',
            'Assertions', 'Evidence', 'Decisions authorized',
            'Unresolved question', 'Requested next decision',
            'Safe work while waiting', 'Redaction'):
    assert packet[key]

external = root / profile['Planning locator']
if external.is_file():
    content = external.read_bytes()
    digest = hashlib.sha256(content).hexdigest()
    assert digest == profile['Direct evidence SHA-256']
    revision = dict(line.split(': ', 1) for line in content.decode().splitlines())['revision']
    assert revision == profile['Last directly verified revision']
    status = 'MATCHED' if revision == plan['Projection revision'] else 'DISCREPANCY'
else:
    assert profile['Direct evidence SHA-256'] == 'PENDING: source inaccessible'
    assert profile['Last directly verified revision'] == 'PENDING: source inaccessible'
    revision = None
    status = 'UNVERIFIED'
assert status == plan['Reconciliation']
permitted = {
    'MATCHED': 'ROUTINE_IMPLEMENTATION_WITHIN_AUTHORIZED_UNIT',
    'UNVERIFIED': 'INDEPENDENT_SAFE_INSPECTION_ONLY',
    'DISCREPANCY': 'HOLD_SCOPE_CHANGE; SAFE_INSPECTION_ONLY',
}[status]
report = {
    'packet_kind': 'investigation report and closure candidate',
    'packet_id': 'REPORT-001', 'work_unit': packet['Work-unit'],
    'source_head': state['HEAD'], 'planning_status': status,
    'verified_revision': revision, 'permitted_work': permitted,
    'evidence': 'synthetic artifact-only reconstruction; runtime PENDING',
    'closure': 'REQUEST_REVIEW', 'current_transition': 'NONE',
    'next_authorization': 'NONE', 'protected_authorization': 'NONE',
    'supervisor_ai_approval_power': False,
}
(root / 'returned.report.json').write_text(json.dumps(report, sort_keys=True))
print(json.dumps({'planning_status': status, 'permitted_work': permitted}))
'''

SUPERVISOR_SESSION = r'''
import hashlib, json, sys
from pathlib import Path

root = Path(sys.argv[1])
def read(name): return (root / name).read_text()
def fields(name):
    return dict(line.split(': ', 1) for line in read(name).splitlines() if ': ' in line)

for name in ('AGENT_WORKFLOW.md', 'DOCUMENT_GOVERNANCE.md',
             'TESTING_AND_EVIDENCE.md', 'MIGRATION_AND_RELEASE_POLICY.md',
             'ADOPTION.md', 'standard-release.json', 'PROJECT_PROFILE.md',
             'EXECUTION_PLAN.md', 'PROJECT_STATE.md', 'HANDOFF.md',
             'assignment.packet.md'):
    read(name)
profile = fields('PROJECT_PROFILE.md')
plan = fields('EXECUTION_PLAN.md')
packet = fields('assignment.packet.md')
report = json.loads(read('returned.report.json'))
assert report['work_unit'] == packet['Work-unit']
assert report['source_head'] == fields('PROJECT_STATE.md')['HEAD']
manifest = json.loads(read('standard-release.json'))
assert packet['Standard version/status'] == manifest['version'] + ' ' + manifest['status']
assert packet['Standard hash'] == hashlib.sha256(
    (root / 'standard-release.json').read_bytes()).hexdigest()
assert plan['CURRENT'] == 'UNIT-A IN PROGRESS'
assert plan['NEXT'] == 'UNIT-B NOT STARTED'
external = root / profile['Planning locator']
if external.is_file():
    content = external.read_bytes()
    assert hashlib.sha256(content).hexdigest() == profile['Direct evidence SHA-256']
    revision = dict(line.split(': ', 1) for line in content.decode().splitlines())['revision']
    status = 'MATCHED' if revision == plan['Projection revision'] else 'DISCREPANCY'
else:
    assert profile['Direct evidence SHA-256'] == 'PENDING: source inaccessible'
    status = 'UNVERIFIED'
assert report['planning_status'] == status == plan['Reconciliation']
assert report['closure'] == 'REQUEST_REVIEW'
assert report['current_transition'] == 'NONE'
assert report['next_authorization'] == 'NONE'
assert report['protected_authorization'] == 'NONE'
assert report['supervisor_ai_approval_power'] is False
assert 'runtime PENDING' in report['evidence']
print(json.dumps({'review': 'REVIEW_REQUIRED', 'planning_status': status,
                  'current': plan['CURRENT'], 'next': plan['NEXT'],
                  'protected_authority': 'OWNER_REQUIRED'}))
'''


class PortablePacketRehearsal(unittest.TestCase):
    def rehearse(self, external_revision: str | None, expected: str) -> None:
        with tempfile.TemporaryDirectory(prefix="portable-packet-rehearsal-") as tmp:
            root = Path(tmp)
            for name in STANDARD_RECORDS:
                (root / name).write_bytes((STANDARD / name).read_bytes())
            source_hash = hashlib.sha256((root / "standard-release.json").read_bytes()).hexdigest()
            manifest = json.loads((root / "standard-release.json").read_text())
            if external_revision is None:
                direct_revision = "PENDING: source inaccessible"
                direct_hash = "PENDING: source inaccessible"
            else:
                content = f"revision: {external_revision}\n".encode()
                (root / "external-plan.txt").write_bytes(content)
                direct_revision = external_revision
                direct_hash = hashlib.sha256(content).hexdigest()
            (root / "PROJECT_PROFILE.md").write_text(
                "Planning authority: synthetic external source\n"
                "Planning locator: external-plan.txt\n"
                "Declared revision: r7\n"
                f"Last directly verified revision: {direct_revision}\n"
                f"Direct evidence SHA-256: {direct_hash}\n"
                "Approval channel: synthetic owner record; protected actions excluded\n"
            )
            (root / "EXECUTION_PLAN.md").write_text(
                "CURRENT: UNIT-A IN PROGRESS\nNEXT: UNIT-B NOT STARTED\n"
                "Projection revision: r7\n"
                f"Reconciliation: {expected}\n"
            )
            (root / "PROJECT_STATE.md").write_text(
                "HEAD: synthetic-head-001\nValidation: PENDING\n"
            )
            (root / "HANDOFF.md").write_text(
                "Latest packet: ASSIGN-001\n"
                "Safe resumption: inspect UNIT-A and its source before acting\n"
            )
            (root / "assignment.packet.md").write_text(
                "Packet kind: Assignment / handoff\nPacket ID: ASSIGN-001\n"
                "Project: synthetic-portable-fixture\nWork-unit: UNIT-A\n"
                "Timestamp: 2026-09-27T00:00:00Z\n"
                "Issuer role: Supervisor recommendation, not owner approval\n"
                "Decision authority: synthetic owner; no protected action authorized\n"
                f"Standard version/status: {manifest['version']} {manifest['status']}\n"
                f"Standard hash: {source_hash}\nSource HEAD: synthetic-head-001\n"
                "Uncommitted diff: NONE\nPlan pointer: UNIT-A IN PROGRESS\n"
                "Authorized scope: inspect and perform routine UNIT-A work only when verified\n"
                "Exclusions: no NEXT, closure, commit, release or production\n"
                "Dependencies: NONE in this synthetic fixture\n"
                "Planning locator: external-plan.txt\n"
                "Planning declaration: r7\n"
                f"Direct verification: {direct_revision}; SHA-256 {direct_hash}\n"
                "Projection revision: r7\n"
                "Acceptance gates: project contract PENDING\n"
                "Observations: synthetic local records only; no runtime action\n"
                "Assertions: no live acceptance or external service access claimed\n"
                "Evidence: source state above; runtime PENDING\n"
                "Decisions authorized: bounded synthetic UNIT-A task only\n"
                "Unresolved question: closure evidence and owner review\n"
                "Requested next decision: review after real gates\n"
                "Safe work while waiting: independent read-only inspection\n"
                "Redaction: no secrets or personal data\n"
            )
            args = (str(root),)
            agent = subprocess.run(
                [sys.executable, "-I", "-S", "-c", CODING_SESSION, *args],
                cwd=root, env={}, capture_output=True, text=True, check=True,
            )
            supervisor = subprocess.run(
                [sys.executable, "-I", "-S", "-c", SUPERVISOR_SESSION, *args],
                cwd=root, env={}, capture_output=True, text=True, check=True,
            )
            agent_result = json.loads(agent.stdout)
            supervisor_result = json.loads(supervisor.stdout)
            self.assertEqual(agent_result["planning_status"], expected)
            self.assertEqual(supervisor_result["planning_status"], expected)
            self.assertEqual(supervisor_result["review"], "REVIEW_REQUIRED")
            self.assertEqual(supervisor_result["current"], "UNIT-A IN PROGRESS")
            self.assertEqual(supervisor_result["next"], "UNIT-B NOT STARTED")
            self.assertEqual(supervisor_result["protected_authority"], "OWNER_REQUIRED")
            expected_work = {
                "MATCHED": "ROUTINE_IMPLEMENTATION_WITHIN_AUTHORIZED_UNIT",
                "UNVERIFIED": "INDEPENDENT_SAFE_INSPECTION_ONLY",
                "DISCREPANCY": "HOLD_SCOPE_CHANGE; SAFE_INSPECTION_ONLY",
            }
            self.assertEqual(agent_result["permitted_work"], expected_work[expected])

    def test_declared_but_inaccessible(self) -> None:
        self.rehearse(None, "UNVERIFIED")

    def test_directly_verified_matching_revision(self) -> None:
        self.rehearse("r7", "MATCHED")

    def test_verified_revision_disagrees_with_projection(self) -> None:
        self.rehearse("r8", "DISCREPANCY")


if __name__ == "__main__":
    unittest.main()
