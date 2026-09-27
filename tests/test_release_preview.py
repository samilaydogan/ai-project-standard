"""Committed-preview acceptance in disposable repositories, including actual HTTP."""
from __future__ import annotations
import importlib.util
import json
import os
import subprocess
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('bounded_preview', SOURCE / 'scripts/release_preview.py')
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)

VALIDATOR = '''import os,json
from pathlib import Path
root=Path.cwd()
assert not (root/'.git').exists()
assert not (root/'untracked.txt').exists()
assert not (root/'.env').exists()
assert (root/'tracked.txt').read_text()=='committed'
assert 'SECRET_TEST_TOKEN' not in os.environ
assert 'HTTP_PROXY' not in os.environ
assert Path(os.environ['HOME']).parent!=root
print('SECRET_OUTPUT_MUST_NOT_LEAK')
Path(os.environ['PREVIEW_RESULT_PATH']).write_text(json.dumps({'nonce':os.environ['PREVIEW_NONCE'],'startup':True,'health':True,'stop':True}))
'''


class ReleasePreviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='preview-fixture-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / 'source'
        self.root.mkdir()
        self.g('init', '-b', 'synthetic-branch')
        self.g('config', 'user.name', 'Fixture Owner')
        self.g('config', 'user.email', 'fixture@example.invalid')
        self.g('config', 'commit.gpgsign', 'false')
        self.cfg = json.loads((SOURCE / 'release-preview-profile.json').read_text())
        self.cfg.update(entrypoint='validate.py', prerequisites=[])
        self.save('release-preview-profile.json', self.cfg)
        self.save('standard-release.json', {'version': '1.2.3'})
        self.save('source-exclusions.json', json.loads((SOURCE / 'source-exclusions.json').read_text()))
        (self.root / 'VERSION').write_text('1.2.3\n')
        (self.root / 'tracked.txt').write_text('committed')
        (self.root / 'validate.py').write_text(VALIDATOR)
        (self.root / '.gitignore').write_text('.env\n')
        self.commit()
        self.approval_path = self.base / 'approval.json'
        self.approve()

    def g(self, *args):
        return p.git(self.root, *args).decode().strip()

    def save(self, name, value):
        (self.root / name).parent.mkdir(parents=True, exist_ok=True)
        (self.root / name).write_text(json.dumps(value))

    def commit(self):
        self.g('add', '.')
        self.g('commit', '-m', 'Commit isolated synthetic preview source')
        self.head = self.g('rev-parse', 'HEAD')

    def approve(self):
        self.ident, _, _ = p.identity(self.root, self.head, 'UNIT-P')
        self.approval = {'schema_version': 1, 'kind': 'PREVIEW', 'status': 'APPROVED', 'role': 'human_owner',
                         'reference': 'SYNTHETIC-PREVIEW-DECISION', 'identity_sha256': p.binding(self.ident),
                         'expires_at': time.time() + 3600}
        self.write_approval()

    def write_approval(self):
        self.approval_path.write_text(json.dumps(self.approval))

    def run_preview(self):
        return p.execute(self.root, self.head, 'UNIT-P', self.approval_path,
                         p.sha(self.approval_path.read_bytes()), 'SYNTHETIC-PREVIEW-DECISION')

    def replace_validator(self, content):
        (self.root / 'validate.py').write_text(content)
        self.commit()
        self.approve()

    def test_committed_exact_identity_isolated_completion_and_source_nonmutation(self):
        before = p.source_state(self.root)
        result, code = self.run_preview()
        self.assertEqual((result['status'], code), ('PASS', 0))
        self.assertEqual(result['identity']['tree'], self.g('rev-parse', 'HEAD^{tree}'))
        self.assertEqual(result['before'], before)
        self.assertEqual(result['after'], before)
        self.assertEqual(result['cleanup'], 'PASS')
        self.assertEqual(result['output'], 'SUPPRESSED')
        self.assertNotIn('SECRET_OUTPUT', json.dumps(result))
        self.assertFalse(self.g('tag'))
        self.assertFalse(self.g('remote'))

    def test_dirty_staged_untracked_and_ignored_never_contaminate_preview(self):
        (self.root / 'tracked.txt').write_text('dirty worktree')
        self.g('add', 'tracked.txt')
        (self.root / 'validate.py').write_text('raise RuntimeError("MUTABLE_SOURCE_EXECUTED")')
        (self.root / 'untracked.txt').write_text('unrelated')
        (self.root / '.env').write_text('SECRET=private')
        before = p.source_state(self.root)
        with patch.dict(os.environ, SECRET_TEST_TOKEN='private', HTTP_PROXY='http://invalid'):
            result, code = self.run_preview()
        self.assertEqual(code, 0)
        self.assertEqual(result['after'], before)
        self.assertEqual((self.root / '.env').read_text(), 'SECRET=private')

    def test_readonly_identity_preflight_do_not_mutate(self):
        before = p.source_state(self.root)
        for _ in range(2):
            p.identity(self.root, self.head, 'UNIT-P')
            p.preflight(self.root, self.head, 'UNIT-P', self.approval_path)
        self.assertEqual(before, p.source_state(self.root))

    def test_repeated_preview_new_isolation_no_stale_output(self):
        first, c1 = self.run_preview()
        second, c2 = self.run_preview()
        self.assertEqual((c1, c2), (0, 0))
        self.assertEqual(first['identity'], second['identity'])
        self.assertEqual(first['after'], second['after'])
        self.assertEqual(second['cleanup'], 'PASS')

    def test_wrong_and_missing_commit_rejected(self):
        for head in ('0' * 40, self.head[:12], 'main', 'HEAD'):
            with self.subTest(head=head), self.assertRaises(ValueError):
                p.identity(self.root, head, 'UNIT-P')

    def test_source_head_changed_after_approval_rejected(self):
        old = self.head
        (self.root / 'tracked.txt').write_text('new commit')
        self.commit()
        with self.assertRaises(ValueError):
            p.preflight(self.root, old, 'UNIT-P', self.approval_path)
        with self.assertRaises(ValueError):
            self.run_preview()

    def test_wrong_unit_and_stale_profile_rejected(self):
        with self.assertRaises(ValueError):
            p.preflight(self.root, self.head, 'UNIT-Q', self.approval_path)
        self.cfg['args'] = ['different']
        self.save('release-preview-profile.json', self.cfg)
        self.commit()
        with self.assertRaises(ValueError):
            self.run_preview()

    def test_commit_permission_is_not_preview_permission(self):
        for key, value in [('kind', 'COMMIT'), ('status', 'PENDING'), ('role', 'supervisor_ai')]:
            old = self.approval[key]
            self.approval[key] = value
            self.write_approval()
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.run_preview()
            self.approval[key] = old

    def test_missing_expired_malformed_approval_rejected(self):
        for value in ({}, {'schema_version': 1}, dict(self.approval, expires_at=time.time() - 1),
                      dict(self.approval, expires_at=float('nan'))):
            self.approval_path.write_text(json.dumps(value))
            with self.subTest(value=value), self.assertRaises((ValueError, KeyError)):
                self.run_preview()
        self.approval_path.unlink()
        with self.assertRaises(ValueError):
            p.preflight(self.root, self.head, 'UNIT-P', self.approval_path)

    def test_operator_confirmation_and_actual_reference_required(self):
        for confirm, reference in [('wrong', 'SYNTHETIC-PREVIEW-DECISION'), (p.sha(self.approval_path.read_bytes()), 'wrong')]:
            with self.assertRaises(ValueError):
                p.execute(self.root, self.head, 'UNIT-P', self.approval_path, confirm, reference)

    def test_missing_and_unsupported_prerequisites_rejected(self):
        for changes in ({'prerequisites': ['missing.py']}, {'adapter': 'docker'}, {'entrypoint': '../outside.py'},
                        {'timeout_seconds': 0}, {'entrypoint': 'installer.sh'}):
            self.save('release-preview-profile.json', dict(self.cfg, **changes))
            self.commit()
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                p.identity(self.root, self.head, 'UNIT-P')

    def test_symlink_and_published_secret_rejected(self):
        (self.root / 'link').symlink_to('tracked.txt')
        self.commit()
        with self.assertRaises(ValueError):
            p.identity(self.root, self.head, 'UNIT-P')
        (self.root / 'link').unlink()
        (self.root / '.env').write_text('private')
        self.g('add', '-f', '.env')
        self.commit()
        with self.assertRaises(ValueError):
            p.identity(self.root, self.head, 'UNIT-P')

    def test_nested_runtime_exclusion_and_nonwaivable_metadata_rejected(self):
        policy = json.loads((self.root / 'source-exclusions.json').read_text())
        policy['rules'].append({'path': 'private/runtime/', 'category': 'runtime',
                                'targets': ['git', 'docker', 'release', 'fingerprint', 'handoff']})
        self.save('source-exclusions.json', policy)
        (self.root / 'private/runtime').mkdir(parents=True)
        (self.root / 'private/runtime/state.json').write_text('synthetic runtime')
        self.commit()
        with self.assertRaisesRegex(ValueError, 'excluded'):
            p.identity(self.root, self.head, 'UNIT-P')
        (self.root / 'private/runtime/state.json').unlink()
        policy['source_exceptions'].append('.DS_Store')
        self.save('source-exclusions.json', policy)
        (self.root / '.DS_Store').write_text('synthetic metadata')
        self.commit()
        with self.assertRaisesRegex(ValueError, 'non-waivable'):
            p.identity(self.root, self.head, 'UNIT-P')
        (self.root / '.DS_Store').unlink()
        policy['source_exceptions'].append('.env')
        self.save('source-exclusions.json', policy)
        (self.root / '.env').write_text('synthetic credential')
        self.g('add', '-f', '.env')
        self.commit()
        with self.assertRaisesRegex(ValueError, 'credential'):
            p.identity(self.root, self.head, 'UNIT-P')

    def test_portable_paths_reject_drive_metadata_and_device_aliases(self):
        for name in ('C:/escape.py', 'a:b.py', '.GIT/config', 'folder./file', 'NUL/data',
                     'folder/COM1.txt', 'LPT².txt', '../escape', 'a\\escape'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                p.relative(name)
        self.assertEqual(p.relative('docs/valid-file.md'), 'docs/valid-file.md')

    def test_case_normalization_collisions_and_sensitive_aliases_rejected(self):
        for pair in (('Scripts/one.py', 'scripts/two.py'), ('A.py', 'a.py'), ('é.py', 'e\u0301.py')):
            listing = b''.join(('100644 blob ' + '0' * 40 + '\t' + name + '\0').encode() for name in pair)
            with self.subTest(pair=pair), patch.object(p, 'git', return_value=listing), self.assertRaisesRegex(ValueError, 'collision'):
                p.objects(self.root, self.head)
        for name in ('.ENV', '.ds_store'):
            target = self.root / name
            target.write_text('synthetic alias')
            self.g('add', '-f', name)
            self.commit()
            with self.subTest(name=name), self.assertRaises(ValueError):
                p.identity(self.root, self.head, 'UNIT-P')
            target.unlink()
            self.commit()

    def test_detached_and_wrong_repository_root_rejected(self):
        with self.assertRaises(ValueError):
            p.identity(self.root.parent, self.head, 'UNIT-P')
        self.g('checkout', '--detach', self.head)
        with self.assertRaises(ValueError):
            p.identity(self.root, self.head, 'UNIT-P')

    def test_child_failure_no_raw_output_no_pass_and_cleanup(self):
        self.replace_validator("print('SECRET_OUTPUT'); raise RuntimeError('PRIVATE_ERROR')")
        before = p.source_state(self.root)
        result, code = self.run_preview()
        self.assertEqual((result['status'], code), ('FAIL', 1))
        self.assertEqual(result['health'], 'NOT ASSESSED')
        self.assertEqual(result['cleanup'], 'PASS')
        self.assertEqual(result['after'], before)
        self.assertNotIn('PRIVATE_ERROR', json.dumps(result))

    def test_exit_zero_missing_report_cannot_pass(self):
        self.replace_validator('pass')
        result, code = self.run_preview()
        self.assertEqual((result['status'], code), ('FAIL', 1))

    def test_stale_nonce_false_or_malformed_evidence_cannot_pass(self):
        variants = ['[]', 'None', "{'nonce':'stale','startup':True,'health':True,'stop':True}",
                    "{'nonce':os.environ['PREVIEW_NONCE'],'startup':True,'health':False,'stop':True}",
                    "{'nonce':os.environ['PREVIEW_NONCE'],'startup':1,'health':1,'stop':1}"]
        for value in variants:
            self.replace_validator("import os,json\nfrom pathlib import Path\nPath(os.environ['PREVIEW_RESULT_PATH']).write_text(json.dumps(" + value + '))')
            with self.subTest(value=value):
                result, code = self.run_preview()
                self.assertEqual(code, 1)
                self.assertEqual(result['cleanup'], 'PASS')

    def test_timeout_truthful_failure_and_cleanup(self):
        self.cfg['timeout_seconds'] = 1
        self.save('release-preview-profile.json', self.cfg)
        self.replace_validator('import time; time.sleep(60)')
        result, code = self.run_preview()
        self.assertEqual((result['status'], code), ('TIMED_OUT', 1))
        self.assertEqual(result['cleanup'], 'PASS')
        self.assertTrue(result['source_unchanged'])

    def test_source_race_before_launch_rejected(self):
        real = p.source_state
        calls = []
        def race(root):
            calls.append(1)
            if len(calls) == 2:
                (root / 'tracked.txt').write_text('concurrent change')
            return real(root)
        with patch.object(p, 'source_state', side_effect=race), self.assertRaises(ValueError):
            self.run_preview()

    def test_approval_race_before_launch_rejected(self):
        real = p.preflight
        calls = []
        def race(*args):
            calls.append(1)
            if len(calls) == 2:
                self.approval['reference'] = 'CHANGED-OWNER-REFERENCE'
                self.write_approval()
            return real(*args)
        with patch.object(p, 'preflight', side_effect=race), self.assertRaises(ValueError):
            self.run_preview()

    def test_actual_committed_reference_http_startup_health_stop(self):
        for name in ('scripts/preview_health.py', 'scripts/health_scaffold.py'):
            (self.root / name).parent.mkdir(parents=True, exist_ok=True)
            (self.root / name).write_bytes((SOURCE / name).read_bytes())
        self.save('release-preview-profile.json', json.loads((SOURCE / 'release-preview-profile.json').read_text()))
        self.commit()
        self.approve()
        result, code = self.run_preview()
        self.assertEqual(code, 0, result)
        self.assertEqual([result[k] for k in ('startup', 'health', 'stop')], ['PASS'] * 3)
        self.assertTrue(result['source_unchanged'])
        self.assertEqual(result['cleanup'], 'PASS')

    def test_temporary_root_inside_source_is_rejected_without_creation(self):
        before = p.source_state(self.root)
        with patch.object(p.tempfile, 'gettempdir', return_value=str(self.root)), self.assertRaises(ValueError):
            self.run_preview()
        self.assertEqual(before, p.source_state(self.root))
        self.assertFalse(list(self.root.glob('committed-preview-*')))

    def test_postexecution_concurrent_source_change_is_failure_and_preserved(self):
        real = p.subprocess.run
        def writer(argv, **kwargs):
            result = real(argv, **kwargs)
            if 'validate.py' in str(argv):
                (self.root / 'tracked.txt').write_text('external concurrent writer')
            return result
        with patch.object(p.subprocess, 'run', side_effect=writer):
            result, code = self.run_preview()
        self.assertEqual(code, 1)
        self.assertFalse(result['source_unchanged'])
        self.assertEqual(result['health'], 'PASS')
        self.assertEqual(result['cleanup'], 'PASS')
        self.assertEqual((self.root / 'tracked.txt').read_text(), 'external concurrent writer')

    def test_cli_fresh_process_explicit_preview_authorized_and_redacted(self):
        before = p.source_state(self.root)
        child = subprocess.run([os.sys.executable, '-B', str(SOURCE / 'scripts/release_preview.py'), 'run',
                                '--root', str(self.root), '--commit', self.head, '--work-unit', 'UNIT-P',
                                '--approval', str(self.approval_path), '--owner-confirmed', p.sha(self.approval_path.read_bytes()),
                                '--authorization-reference', 'SYNTHETIC-PREVIEW-DECISION'], capture_output=True, check=False)
        self.assertEqual(child.returncode, 0, child.stdout)
        result = json.loads(child.stdout)
        self.assertEqual(result['status'], 'PASS')
        self.assertNotIn(b'SECRET_OUTPUT', child.stdout + child.stderr)
        self.assertEqual(before, p.source_state(self.root))

    def test_cli_missing_approval_pending_no_source_mutation(self):
        before = p.source_state(self.root)
        child = subprocess.run([os.sys.executable, '-B', str(SOURCE / 'scripts/release_preview.py'), 'preflight',
                                '--root', str(self.root), '--commit', self.head, '--work-unit', 'UNIT-P'],
                               capture_output=True, check=False)
        self.assertEqual(child.returncode, 3)
        self.assertEqual(json.loads(child.stdout)['status'], 'PENDING')
        self.assertEqual(before, p.source_state(self.root))


if __name__ == '__main__':
    unittest.main()
