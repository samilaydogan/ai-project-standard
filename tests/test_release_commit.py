"""Commit acceptance exclusively in disposable Git repositories, no real ref writes."""
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

spec = importlib.util.spec_from_file_location('bounded_release_commit', Path(__file__).resolve().parents[1] / 'scripts/release_commit.py')
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)


class ReleaseCommitTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='commit-control-')
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.root = self.base / 'source'
        self.root.mkdir()
        self.cfg = {'schema_version': 1, 'state_root': str(self.base / 'state'), 'version_path': 'VERSION',
                    'lifecycle_path': 'lifecycle.json', 'allowed_states': ['DRAFT', 'FINAL'],
                    'required_gates': ['full', 'docs'], 'test_gates': ['full'], 'required_approvals': ['COMMIT', 'SEMANTIC'],
                    'message_pattern': '[A-Z][^\\n]{9,199}'}
        self.save('release-commit-profile.json', self.cfg)
        (self.root / 'VERSION').write_text('1.2.3\n')
        self.save('lifecycle.json', {'status': 'DRAFT'})
        (self.root / 'code.txt').write_text('baseline\n')
        self.g('init', '-b', 'fixture-main')
        self.g('config', 'user.name', 'Synthetic Owner')
        self.g('config', 'user.email', 'fixture@example.invalid')
        self.g('config', 'commit.gpgsign', 'false')
        self.g('add', '.')
        self.g('commit', '-m', 'Initial synthetic fixture')
        (self.root / 'code.txt').write_text('validated change\n')
        self.g('add', 'code.txt')
        self.paths = [self.base / n for n in ('candidate.json', 'evidence.json', 'approval.json')]
        self.prepare()

    def g(self, *args):
        return c.git(self.root, *args).decode().strip()

    def save(self, name, value):
        (self.root / name).write_text(json.dumps(value))

    def prepare(self):
        self.candidate = c.snapshot(self.root, 'UNIT-A', ['code.txt'], 'Finalize validated synthetic candidate')
        cid = c.binding(self.candidate)
        self.evidence = {'schema_version': 1, 'candidate_sha256': cid, 'work_unit': 'UNIT-A',
                         'gates': {n: {'status': 'PASS', 'exit': 0, 'command': 'synthetic ' + n,
                                      'runtime': 'stdlib isolated fixture', 'passed': 1, 'failed': 0, 'skipped': 0}
                                   for n in self.cfg['required_gates']}}
        self.paths[0].write_text(json.dumps(self.candidate))
        self.paths[1].write_text(json.dumps(self.evidence))
        self.approval = {'schema_version': 1, 'candidate_sha256': cid, 'evidence_sha256': c.sha(self.paths[1].read_bytes()),
                         'work_unit': 'UNIT-A', 'decisions': {n: {'status': 'APPROVED', 'role': 'human_owner',
                         'reference': 'SYNTHETIC-OWNER-DECISION', 'reviewed_candidate_sha256': cid,
                         'expires_at': time.time() + 3600} for n in self.cfg['required_approvals']}}
        self.write_approval()

    def write_approval(self):
        self.paths[2].write_text(json.dumps(self.approval))

    def invoke(self):
        return c.execute(self.root, *self.paths, 'UNIT-A', c.sha(self.paths[2].read_bytes()), 'SYNTHETIC-OWNER-DECISION')

    def preflight(self):
        return c.preflight(self.root, *self.paths, 'UNIT-A')

    def test_validated_authorized_commit_exact_tree_parent_index_no_side_effects(self):
        before, _ = c.state(self.root)
        expected = self.g('diff', '--cached')
        refs = self.g('show-ref')
        result, code = self.invoke()
        self.assertEqual((result['status'], code), ('COMMITTED', 0))
        self.assertEqual(result['after']['index_sha256'], before['index_sha256'])
        self.assertEqual(self.g('rev-parse', 'HEAD^'), before['head'])
        self.assertEqual(self.g('diff', 'HEAD^', 'HEAD'), expected)
        self.assertFalse(self.g('status', '--porcelain'))
        self.assertFalse(self.g('tag'))
        self.assertFalse(self.g('remote'))
        self.assertEqual(len(refs.splitlines()), len(self.g('show-ref').splitlines()))

    def test_preflight_is_read_only_and_not_authority(self):
        before, index = c.state(self.root)
        original = index.read_bytes()
        for _ in range(2):
            result, _, _, _ = self.preflight()
            self.assertEqual(result['status'], 'ELIGIBLE')
            self.assertIn('NOT_AUTHENTICATED', result['authority'])
        self.assertEqual(c.state(self.root)[0], before)
        self.assertEqual(index.read_bytes(), original)
        self.assertFalse((self.base / 'state').exists())

    def test_no_stage_untracked_or_unrelated_files(self):
        for kind in ('untracked', 'staged'):
            p = self.root / 'unrelated.txt'
            p.write_text('unrelated')
            if kind == 'staged':
                self.g('add', p.name)
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                self.invoke()
            self.assertEqual(p.read_text(), 'unrelated')
            if kind == 'untracked':
                p.unlink()
        self.assertIn('unrelated.txt', self.g('diff', '--cached', '--name-only'))

    def test_changed_bytes_after_validation_rejected(self):
        (self.root / 'code.txt').write_text('later change')
        with self.assertRaises(ValueError):
            self.invoke()
        self.assertEqual(self.g('rev-parse', 'HEAD'), self.candidate['head'])

    def test_changed_staging_after_approval_rejected(self):
        (self.root / 'code.txt').write_text('later staged change')
        self.g('add', 'code.txt')
        with self.assertRaises(ValueError):
            self.invoke()

    def test_missing_semantic_and_commit_decisions_rejected(self):
        for name in ('SEMANTIC', 'COMMIT'):
            original = self.approval['decisions'].pop(name)
            self.write_approval()
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'MISSING_APPROVAL'):
                self.invoke()
            self.approval['decisions'][name] = original

    def test_supervisor_role_or_pending_is_not_owner_approval(self):
        for key, value in (('role', 'ai_supervisor'), ('status', 'PENDING')):
            original = self.approval['decisions']['COMMIT'][key]
            self.approval['decisions']['COMMIT'][key] = value
            self.write_approval()
            with self.assertRaisesRegex(ValueError, 'UNVERIFIED_APPROVAL'):
                self.invoke()
            self.approval['decisions']['COMMIT'][key] = original

    def test_expired_or_wrong_hash_approval_rejected(self):
        self.approval['decisions']['COMMIT']['expires_at'] = time.time() - 1
        self.write_approval()
        with self.assertRaises(ValueError):
            self.invoke()
        self.approval['candidate_sha256'] = '0' * 64
        self.write_approval()
        with self.assertRaisesRegex(ValueError, 'STALE_APPROVAL'):
            self.invoke()

    def test_explicit_owner_channel_confirmation_required(self):
        for confirm, ref in ((None, None), ('wrong', 'SYNTHETIC-OWNER-DECISION'), (c.sha(self.paths[2].read_bytes()), 'wrong')):
            with self.subTest(confirm=confirm), self.assertRaisesRegex(ValueError, 'OWNER_CHANNEL'):
                c.execute(self.root, *self.paths, 'UNIT-A', confirm, ref)

    def test_wrong_work_unit_and_head_rejected(self):
        with self.assertRaisesRegex(ValueError, 'WRONG_WORK_UNIT'):
            c.preflight(self.root, *self.paths, 'UNIT-B')
        self.g('update-ref', 'refs/heads/other', self.candidate['head'])
        self.g('symbolic-ref', 'HEAD', 'refs/heads/other')
        with self.assertRaisesRegex(ValueError, 'STALE_CANDIDATE'):
            self.invoke()

    def test_detached_head_and_operation_state_rejected(self):
        self.g('checkout', '--detach')
        with self.assertRaises(ValueError):
            self.invoke()
        self.g('checkout', 'fixture-main')
        (self.root / '.git' / 'MERGE_HEAD').write_text(self.candidate['head'])
        with self.assertRaisesRegex(ValueError, 'GIT_OPERATION_IN_PROGRESS'):
            self.invoke()

    def test_missing_failed_skipped_validation_rejected(self):
        for key, value in (('status', 'PENDING'), ('exit', 1), ('skipped', 1)):
            self.evidence['gates']['full'][key] = value
            self.paths[1].write_text(json.dumps(self.evidence))
            with self.assertRaisesRegex(ValueError, 'UNVERIFIED_GATE'):
                self.invoke()
            self.evidence['gates']['full'][key] = {'status': 'PASS', 'exit': 0, 'skipped': 0}[key]
        del self.evidence['gates']['full']
        self.paths[1].write_text(json.dumps(self.evidence))
        with self.assertRaisesRegex(ValueError, 'MISSING_REQUIRED_GATE'):
            self.invoke()

    def test_empty_test_gate_and_changed_git_config_hold(self):
        self.evidence['gates']['full']['passed'] = 0
        self.paths[1].write_text(json.dumps(self.evidence))
        with self.assertRaisesRegex(ValueError, 'EMPTY_TEST_GATE'):
            self.invoke()
        self.prepare()
        self.g('config', 'user.name', 'Changed author')
        with self.assertRaisesRegex(ValueError, 'STALE_CANDIDATE'):
            self.invoke()

    def test_changed_evidence_rejects_previously_approved_record(self):
        self.evidence['gates']['docs']['command'] = 'different actual check'
        self.paths[1].write_text(json.dumps(self.evidence))
        with self.assertRaisesRegex(ValueError, 'STALE_APPROVAL'):
            self.invoke()

    def test_repeat_success_is_nondestructive_and_later_drift_holds(self):
        first, _ = self.invoke()
        before = self.g('rev-parse', 'HEAD')
        second, code = self.invoke()
        self.assertEqual((second['status'], code), ('ALREADY_COMMITTED', 0))
        self.assertEqual(first['after'], second['after'])
        self.assertEqual(self.g('rev-parse', 'HEAD'), before)
        (self.root / 'code.txt').write_text('post-commit drift')
        with self.assertRaises(ValueError):
            self.invoke()

    def test_hooks_and_signing_require_another_accepted_adapter(self):
        hook = self.root / '.git' / 'hooks' / 'pre-commit'
        hook.write_text('#!/bin/sh\ntouch forbidden-side-effect\nexit 1\n')
        hook.chmod(0o755)
        with self.assertRaisesRegex(ValueError, 'HOOKS_UNSUPPORTED'):
            self.invoke()
        self.assertFalse((self.root / 'forbidden-side-effect').exists())
        hook.unlink()
        self.g('config', 'commit.gpgsign', 'true')
        with self.assertRaisesRegex(ValueError, 'SIGNING_NOT_CONFIGURED'):
            self.invoke()

    def test_repeat_rechecks_git_environment_before_status(self):
        self.invoke()
        marker = self.base / 'forbidden-repeat-helper'
        self.g('config', 'core.fsmonitor', 'touch ' + str(marker))
        with patch.object(c, 'git', wraps=c.git) as calls:
            with self.assertRaisesRegex(ValueError, 'FSMONITOR_NOT_CONFIGURED'):
                self.invoke()
        self.assertFalse(any(call.args[1] == 'status' for call in calls.call_args_list))
        self.assertFalse(marker.exists())
        self.g('config', '--unset', 'core.fsmonitor')
        self.g('config', 'user.name', 'Changed after commit')
        with self.assertRaisesRegex(ValueError, 'POST_COMMIT_CONFIGURATION_DRIFT'):
            self.invoke()

    def test_custom_hook_path_is_not_silently_bypassed(self):
        self.g('config', 'core.hooksPath', '/unsupported/hooks')
        with self.assertRaisesRegex(ValueError, 'CUSTOM_HOOKS'):
            self.invoke()

    def test_commit_tree_failure_reports_actual_head_index(self):
        real = c.git
        def fail(root, *args, **kw):
            if args[0] == 'commit-tree':
                raise ValueError('simulated failure secret never reported')
            return real(root, *args, **kw)
        before = c.state(self.root)[0]
        with patch.object(c, 'git', side_effect=fail):
            result, code = self.invoke()
        self.assertEqual((result['status'], code), ('ATTEMPT_REQUIRES_REVIEW', 3))
        self.assertEqual(result['after'], before)
        self.assertFalse((self.root / '.git' / 'index.lock').exists())
        with self.assertRaisesRegex(ValueError, 'PRIOR_ATTEMPT'):
            self.invoke()

    def test_nonzero_after_ref_update_reports_changed_actual_head(self):
        real = c.git
        def fail(root, *args, **kw):
            value = real(root, *args, **kw)
            if args[0] == 'update-ref':
                raise ValueError('reported failure after mutation')
            return value
        with patch.object(c, 'git', side_effect=fail):
            result, code = self.invoke()
        self.assertEqual(code, 3)
        self.assertNotEqual(result['before']['head'], result['after']['head'])
        self.assertEqual(result['commit_object'], self.g('rev-parse', 'HEAD'))
        self.assertEqual(result['status'], 'ATTEMPT_REQUIRES_REVIEW')

    def test_ref_race_cannot_overwrite_concurrent_commit(self):
        real = c.git
        other = []
        def race(root, *args, **kw):
            if args[0] == 'update-ref':
                tree = real(root, 'rev-parse', 'HEAD^{tree}').decode().strip()
                new = real(root, 'commit-tree', tree, '-p', self.candidate['head'], input=b'Concurrent unrelated commit\n').decode().strip()
                real(root, 'update-ref', self.candidate['branch'], new, self.candidate['head'])
                other.append(new)
            return real(root, *args, **kw)
        with patch.object(c, 'git', side_effect=race):
            result, code = self.invoke()
        self.assertEqual(code, 3)
        self.assertEqual(result['after']['head'], other[0])
        self.assertEqual(self.g('rev-parse', 'HEAD'), other[0])

    def test_index_lock_busy_is_preserved(self):
        lock = self.root / '.git' / 'index.lock'
        lock.write_text('another writer')
        with self.assertRaises(FileExistsError):
            self.invoke()
        self.assertEqual(lock.read_text(), 'another writer')

    def test_source_storage_overlap_rejected(self):
        self.cfg['state_root'] = str(self.root / 'state')
        self.save('release-commit-profile.json', self.cfg)
        with self.assertRaisesRegex(ValueError, 'OVERLAP'):
            self.prepare()

    def test_symlink_and_submodule_index_members_rejected(self):
        (self.root / 'linked').symlink_to('code.txt')
        self.g('add', 'linked')
        with self.assertRaisesRegex(ValueError, 'UNSUPPORTED_INDEX_MEMBER'):
            c.snapshot(self.root, 'UNIT-A', ['code.txt', 'linked'], 'Finalize synthetic candidate')
        self.g('update-index', '--force-remove', 'linked')
        (self.root / 'linked').unlink()
        self.g('update-index', '--add', '--cacheinfo', '160000,' + self.candidate['head'] + ',module')
        with self.assertRaisesRegex(ValueError, 'UNSUPPORTED_INDEX_MEMBER'):
            c.snapshot(self.root, 'UNIT-A', ['code.txt', 'module'], 'Finalize synthetic candidate')

    def test_readonly_identity_rejects_external_git_helpers_before_execution(self):
        marker = self.base / 'forbidden-helper-execution'
        self.g('config', 'filter.unsafe.clean', 'touch ' + str(marker))
        (self.root / '.gitattributes').write_text('code.txt filter=unsafe\n')
        # No git add here: Git's own refresh could run the helper before the adapter.
        with self.assertRaisesRegex(ValueError, 'EXTERNAL_GIT_HELPERS'):
            c.snapshot(self.root, 'UNIT-A', ['code.txt'], 'Finalize synthetic candidate')
        self.assertFalse(marker.exists())

    def test_unsafe_message_and_lifecycle_not_approval(self):
        with self.assertRaisesRegex(ValueError, 'INVALID_COMMIT_MESSAGE'):
            c.snapshot(self.root, 'UNIT-A', ['code.txt'], 'bad\nmessage')
        self.save('lifecycle.json', {'status': 'READY'})
        self.g('add', 'lifecycle.json')
        with self.assertRaises(ValueError):
            c.snapshot(self.root, 'UNIT-A', ['code.txt', 'lifecycle.json'], 'Finalize synthetic candidate')

    def test_source_race_during_object_creation_holds_without_ref_change(self):
        real = c.git
        def race(root, *args, **kw):
            result = real(root, *args, **kw)
            if args[0] == 'commit-tree':
                (self.root / 'code.txt').write_text('changed during commit')
            return result
        with patch.object(c, 'git', side_effect=race):
            result, code = self.invoke()
        self.assertEqual(code, 3)
        self.assertEqual(result['after']['head'], self.candidate['head'])
        self.assertIsNotNone(result['commit_object'])

    def test_cli_fresh_process_authorized_commit(self):
        scripts = self.root / 'scripts'
        scripts.mkdir()
        (scripts / 'release_commit.py').write_bytes(Path(c.__file__).read_bytes())
        self.g('add', 'scripts/release_commit.py')
        self.g('commit', '-m', 'Prepare isolated CLI adapter fixture')
        (self.root / 'code.txt').write_text('CLI validated candidate')
        self.g('add', 'code.txt')
        self.prepare()
        args = [os.sys.executable, '-B', str(scripts / 'release_commit.py'), 'commit', '--work-unit', 'UNIT-A',
                '--candidate', str(self.paths[0]), '--evidence', str(self.paths[1]), '--approval', str(self.paths[2]),
                '--owner-confirmed', c.sha(self.paths[2].read_bytes()), '--authorization-reference', 'SYNTHETIC-OWNER-DECISION']
        p = subprocess.run(args, capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stdout)
        result = json.loads(p.stdout)
        self.assertEqual(result['status'], 'COMMITTED')
        self.assertEqual(result['after']['head'], self.g('rev-parse', 'HEAD'))
        p = subprocess.run(args, capture_output=True, text=True)
        self.assertEqual((p.returncode, json.loads(p.stdout)['status']), (0, 'ALREADY_COMMITTED'))

    def test_cli_fresh_process_missing_approval_is_redacted_and_no_commit(self):
        scripts = self.root / 'scripts'
        scripts.mkdir()
        (scripts / 'release_commit.py').write_bytes(Path(c.__file__).read_bytes())
        self.g('add', 'scripts/release_commit.py')
        p = subprocess.run([os.sys.executable, '-B', str(scripts / 'release_commit.py'), 'commit',
                            '--work-unit', 'UNIT-A'], capture_output=True, text=True)
        self.assertEqual(p.returncode, 3)
        report = json.loads(p.stdout)
        self.assertEqual(report['actual']['head'], self.candidate['head'])
        self.assertNotIn('Synthetic Owner', p.stdout+p.stderr)
        self.assertEqual(report['status'], 'PENDING')


if __name__ == '__main__':
    unittest.main()
