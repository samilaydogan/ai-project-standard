"""Optional validated staged-candidate commit adapter; records never grant authority."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

ID = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,79}')
HEX = re.compile(r'[0-9a-f]{64}')


def need(ok, rule):
    if not ok:
        raise ValueError(rule)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def binding(value):
    return sha(json.dumps(value, sort_keys=True, separators=(',', ':')).encode())


def read(path):
    need(path.is_file() and not path.is_symlink(), 'MISSING_UNSAFE_RECORD')
    def unique(pairs):
        result = {}
        for k, v in pairs:
            need(k not in result, 'DUPLICATE_RECORD_KEY')
            result[k] = v
        return result
    return json.loads(path.read_text(), object_pairs_hook=unique)


def environment():
    # Drop inherited GIT_* directives, credentials/proxies and command injection.
    env = {k: os.environ[k] for k in ('PATH', 'HOME', 'LANG', 'LC_CTYPE', 'TMPDIR') if k in os.environ}
    env.update(GIT_OPTIONAL_LOCKS='0', GIT_TERMINAL_PROMPT='0')
    return env


def git(root, *args, input=None, env=None):
    p = subprocess.run(['git', '--no-pager', '-C', str(root), *args], input=input,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       env=environment() if env is None else env, timeout=30, check=False)
    need(p.returncode == 0, 'GIT_COMMAND_FAILED')
    return p.stdout


def relative(root, name):
    need(isinstance(name, str), 'INVALID_PATH')
    p = Path(name)
    need(not p.is_absolute() and p.parts and '..' not in p.parts and '.git' not in p.parts, 'INVALID_PATH')
    target = root
    for part in p.parts:
        target /= part
        need(not target.is_symlink(), 'SOURCE_SYMLINK_UNSUPPORTED')
    return target


def external(root, name):
    p = Path(name).expanduser()
    if not p.is_absolute():
        p = root / p
    need(all(not q.is_symlink() for q in (p, *p.parents)), 'EXTERNAL_SYMLINK')
    p = p.resolve()
    need(not p.is_relative_to(root) and not root.is_relative_to(p), 'EXTERNAL_ROOT_OVERLAP')
    return p


def profile(root):
    cfg = read(root / 'release-commit-profile.json')
    need(set(cfg) == {'schema_version', 'state_root', 'version_path', 'lifecycle_path', 'allowed_states',
                     'required_gates', 'test_gates', 'required_approvals', 'message_pattern'} and cfg['schema_version'] == 1,
         'NOT_CONFIGURED_PROFILE')
    need(isinstance(cfg['required_gates'], list) and cfg['required_gates']
         and len(set(cfg['required_gates'])) == len(cfg['required_gates'])
         and all(isinstance(x, str) and ID.fullmatch(x) for x in cfg['required_gates']), 'INVALID_GATES')
    need(isinstance(cfg['test_gates'], list) and cfg['test_gates']
         and set(cfg['test_gates']) <= set(cfg['required_gates']), 'INVALID_TEST_GATES')
    need(isinstance(cfg['required_approvals'], list) and 'COMMIT' in cfg['required_approvals']
         and len(set(cfg['required_approvals'])) == len(cfg['required_approvals'])
         and set(cfg['required_approvals']) <= {'COMMIT', 'SEMANTIC', 'CLOSURE'}, 'INVALID_APPROVAL_REQUIREMENTS')
    need(isinstance(cfg['allowed_states'], list) and cfg['allowed_states']
         and set(cfg['allowed_states']) <= {'DRAFT', 'RC', 'FINAL'}, 'INVALID_LIFECYCLE')
    need(isinstance(cfg['message_pattern'], str) and len(cfg['message_pattern']) <= 200, 'INVALID_MESSAGE_CONTRACT')
    re.compile(cfg['message_pattern'])
    return cfg, external(root, cfg['state_root'])


def state(root):
    head = git(root, 'rev-parse', 'HEAD').decode().strip()
    branch = git(root, 'symbolic-ref', '--quiet', 'HEAD').decode().strip()
    need(branch.startswith('refs/heads/'), 'DETACHED_OR_INVALID_BRANCH')
    index_path = Path(git(root, 'rev-parse', '--path-format=absolute', '--git-path', 'index').decode().strip())
    need(index_path.is_file() and not index_path.is_symlink(), 'INVALID_INDEX')
    return {'head': head, 'branch': branch, 'index_sha256': sha(index_path.read_bytes())}, index_path


def snapshot(root, work_unit, files, message):
    cfg, _ = profile(root)
    policy_environment(root)
    need(isinstance(work_unit, str) and ID.fullmatch(work_unit), 'INVALID_WORK_UNIT')
    need(isinstance(files, list) and files and len(set(files)) == len(files), 'INVALID_SCOPE')
    need(isinstance(message, str) and '\x00' not in message and len(message) <= 500
         and re.fullmatch(cfg['message_pattern'], message), 'INVALID_COMMIT_MESSAGE')
    need(Path(git(root, 'rev-parse', '--show-toplevel').decode().strip()).resolve() == root, 'WRONG_REPOSITORY_ROOT')
    before, _ = state(root)
    # No conflict, partial staging, unexpected nonignored file or unrelated staged scope.
    need(not git(root, 'ls-files', '--unmerged', '-z'), 'UNMERGED_INDEX')
    entries = git(root, 'ls-files', '--stage', '-z')
    need(all(e.split(b'\t', 1)[0].split()[0] in (b'100644', b'100755')
             for e in entries.split(b'\0') if e), 'UNSUPPORTED_INDEX_MEMBER')
    need(not git(root, 'ls-files', '--others', '--exclude-standard', '-z'), 'UNEXPECTED_UNTRACKED')
    need(not git(root, 'diff', '--no-ext-diff', '--no-textconv', '--name-only', '-z'), 'UNSTAGED_DRIFT')
    staged = git(root, 'diff', '--cached', '--no-ext-diff', '--no-textconv', '--no-renames', '--name-only', '-z').decode().split('\0')[:-1]
    need(set(staged) == set(files), 'STAGED_SCOPE_MISMATCH')
    # Reject operation states rather than continuing/changing a merge/rebase/cherry-pick.
    for name in ('MERGE_HEAD', 'CHERRY_PICK_HEAD', 'REVERT_HEAD', 'rebase-merge', 'rebase-apply', 'sequencer'):
        p = Path(git(root, 'rev-parse', '--path-format=absolute', '--git-path', name).decode().strip())
        need(not p.exists(), 'GIT_OPERATION_IN_PROGRESS')
    members = {}
    for entry in entries.split(b'\0'):
        if not entry:
            continue
        meta, raw_name = entry.split(b'\t', 1)
        mode, oid, stage = meta.decode().split()
        need(stage == '0' and mode in ('100644', '100755'), 'UNSUPPORTED_INDEX_MEMBER')
        name = raw_name.decode()
        p = relative(root, name)
        need(p.is_file(), 'MISSING_SOURCE_MEMBER')
        members[name] = {'sha256': sha(p.read_bytes()), 'mode': p.stat().st_mode & 0o777}
    for name in files:
        relative(root, name)  # Deletions can be absent, but paths remain bounded.
    version = relative(root, cfg['version_path']).read_text().strip()
    lifecycle = read(relative(root, cfg['lifecycle_path']))['status']
    need(version and lifecycle in cfg['allowed_states'], 'CANDIDATE_LIFECYCLE_REJECTED')
    return {'schema_version': 1, 'work_unit': work_unit, **before, 'files': sorted(files), 'message': message,
            'repository_sha256': sha(str(root).encode()),
            'git_config_sha256': sha(git(root, 'config', '--null', '--list', '--show-origin')),
            'git_executable_sha256': sha(Path(shutil.which('git')).read_bytes()),
            'version': version, 'lifecycle': lifecycle, 'members': dict(sorted(members.items())),
            'staged_entries_sha256': sha(entries), 'profile_sha256': sha((root / 'release-commit-profile.json').read_bytes()),
            'adapter_sha256': sha(Path(__file__).read_bytes())}


def policy_environment(root):
    def option(name):
        p = subprocess.run(['git', '-C', str(root), 'config', '--get', name], env=environment(),
                           capture_output=True, timeout=30, check=False)
        need(p.returncode in (0, 1), 'INVALID_GIT_CONFIGURATION')
        return p.stdout.decode().strip()
    need(not option('core.hooksPath'), 'CUSTOM_HOOKS_NOT_CONFIGURED')
    need(not option('core.fsmonitor'), 'FSMONITOR_NOT_CONFIGURED')
    keys = git(root, 'config', '--name-only', '--list').decode().lower().splitlines()
    names = git(root, 'ls-files', '-z')
    # Merely installed global filters (e.g. unused LFS) are not executed. Inspect
    # effective staged AND worktree attributes before diagnostics can clean files.
    for cached in ([], ['--cached']):
        attrs = git(root, 'check-attr', *cached, '-z', '--stdin', 'filter', input=names).decode().split('\0')
        for i in range(0, len(attrs) - 1, 3):
            value = attrs[i + 2].lower()
            need(value in ('unspecified', 'unset') or not any(k.startswith('filter.' + value + '.') for k in keys),
                 'EXTERNAL_GIT_HELPERS_UNSUPPORTED')
    hooks = Path(git(root, 'rev-parse', '--path-format=absolute', '--git-path', 'hooks').decode().strip())
    if hooks.exists():
        need(not hooks.is_symlink(), 'HOOKS_UNSUPPORTED')
        need(not any(p.is_symlink() or (p.is_file() and os.access(p, os.X_OK) and not p.name.endswith('.sample'))
                     for p in hooks.iterdir()), 'ACTIVE_HOOKS_UNSUPPORTED')
    need(option('commit.gpgsign').lower() not in ('true', 'yes', 'on', '1'), 'SIGNING_NOT_CONFIGURED')
    for name in ('user.name', 'user.email'):
        need(bool(option(name)), 'COMMIT_IDENTITY_NOT_CONFIGURED')


def records(root, candidate_path, evidence_path, approval_path, work_unit):
    cfg, storage = profile(root)
    paths = [external(root, str(p)) for p in (candidate_path, evidence_path, approval_path)]
    candidate, evidence, approval = map(read, paths)
    need(candidate['work_unit'] == work_unit, 'WRONG_WORK_UNIT')
    candidate_id = binding(candidate)
    need(set(evidence) == {'schema_version', 'candidate_sha256', 'work_unit', 'gates'}
         and evidence['schema_version'] == 1 and evidence['candidate_sha256'] == candidate_id
         and evidence['work_unit'] == work_unit, 'STALE_VALIDATION')
    need(set(evidence['gates']) == set(cfg['required_gates']), 'MISSING_REQUIRED_GATE')
    for name, gate in evidence['gates'].items():
        need(set(gate) == {'status', 'exit', 'command', 'runtime', 'passed', 'failed', 'skipped'}
             and gate['status'] == 'PASS' and type(gate['exit']) is int and gate['exit'] == 0
             and all(type(gate[k]) is int and gate[k] >= 0 for k in ('passed', 'failed', 'skipped'))
             and gate['failed'] == gate['skipped'] == 0
             and isinstance(gate['command'], str) and bool(gate['command'])
             and isinstance(gate['runtime'], str) and bool(gate['runtime']), 'UNVERIFIED_GATE')
        need(name not in cfg['test_gates'] or gate['passed'] > 0, 'EMPTY_TEST_GATE')
    need(set(approval) == {'schema_version', 'candidate_sha256', 'evidence_sha256', 'work_unit', 'decisions'}
         and approval['schema_version'] == 1 and approval['candidate_sha256'] == candidate_id
         and approval['evidence_sha256'] == sha(paths[1].read_bytes()) and approval['work_unit'] == work_unit,
         'STALE_APPROVAL')
    need(set(approval['decisions']) == set(cfg['required_approvals']), 'MISSING_APPROVAL')
    for decision in approval['decisions'].values():
        need(set(decision) == {'status', 'role', 'reference', 'reviewed_candidate_sha256', 'expires_at'}
             and decision['status'] == 'APPROVED' and decision['role'] == 'human_owner'
             and isinstance(decision['reference'], str) and ID.fullmatch(decision['reference'])
             and decision['reviewed_candidate_sha256'] == candidate_id
             and type(decision['expires_at']) in (int, float) and math.isfinite(decision['expires_at'])
             and time.time() < decision['expires_at'], 'UNVERIFIED_APPROVAL')
    return candidate, candidate_id, sha(paths[2].read_bytes()), approval, storage


def preflight(root, candidate_path, evidence_path, approval_path, work_unit):
    candidate, candidate_id, approval_id, approval, storage = records(root, candidate_path, evidence_path, approval_path, work_unit)
    current = snapshot(root, work_unit, candidate['files'], candidate['message'])
    need(current == candidate, 'STALE_CANDIDATE_SOURCE_HEAD_INDEX')
    policy_environment(root)
    return {'status': 'ELIGIBLE', 'candidate_sha256': candidate_id, 'approval_sha256': approval_id,
            'authority': 'RECORDS_NOT_AUTHENTICATED; OWNER_CHANNEL_CONFIRMATION_REQUIRED'}, candidate, approval, storage


def atomic(path, value):
    need(not path.exists() and not path.is_symlink(), 'RECEIPT_ALREADY_EXISTS')
    with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, delete=False) as f:
        temp = Path(f.name)
        json.dump(value, f, sort_keys=True)
        f.write('\n')
    os.replace(temp, path)


def execute(root, candidate_path, evidence_path, approval_path, work_unit, owner_confirmed, authorization_reference):
    # The calling actor must have verified the real human channel. This explicit
    # assertion is neither a digital signature nor a substitute for that decision.
    candidate, cid, aid, approval, storage = records(root, candidate_path, evidence_path, approval_path, work_unit)
    need(owner_confirmed == aid and authorization_reference == approval['decisions']['COMMIT']['reference'],
         'OWNER_CHANNEL_CONFIRMATION_REQUIRED')
    receipt_path = storage / (cid + '.json')
    if receipt_path.exists():
        policy_environment(root)
        need(sha(git(root, 'config', '--null', '--list', '--show-origin')) == candidate['git_config_sha256'],
             'POST_COMMIT_CONFIGURATION_DRIFT')
        receipt = read(receipt_path)
        current, _ = state(root)
        need(receipt['candidate_sha256'] == cid and receipt['approval_sha256'] == aid
             and receipt['status'] == 'COMMITTED' and current == receipt['after'], 'PRIOR_ATTEMPT_REQUIRES_REVIEW')
        need(not git(root, 'status', '--porcelain', '--untracked-files=normal'), 'POST_COMMIT_DRIFT')
        return {**receipt, 'status': 'ALREADY_COMMITTED'}, 0
    result, candidate, approval, storage = preflight(root, candidate_path, evidence_path, approval_path, work_unit)
    storage.mkdir(mode=0o700, parents=True, exist_ok=True)
    need(storage.stat().st_mode & 0o077 == 0, 'STATE_ROOT_NOT_PRIVATE')
    before, index = state(root)
    lock = index.with_name(index.name + '.lock')
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    os.close(fd)
    commit = None
    attempt_code = 3
    try:
        # Cooperating Git index writers are excluded; repeat identity/record checks
        # after lock acquisition. Use a private index, not automatic staging.
        again, _, _, _ = preflight(root, candidate_path, evidence_path, approval_path, work_unit)
        need(again == result, 'APPROVAL_CHANGED_DURING_PREFLIGHT')
        with tempfile.TemporaryDirectory(prefix='commit-index-', dir=storage) as tmp:
            private_index = Path(tmp) / 'index'
            shutil.copyfile(index, private_index)
            env = environment()
            env['GIT_INDEX_FILE'] = str(private_index)
            tree = git(root, 'write-tree', env=env).decode().strip()
            commit = git(root, 'commit-tree', tree, '-p', candidate['head'], input=(candidate['message']+'\n').encode(), env=env).decode().strip()
            # Recheck source, approvals and branch after object creation; CAS uses
            # the approved parent and can never replace an unexpectedly advanced ref.
            again, _, _, _ = preflight(root, candidate_path, evidence_path, approval_path, work_unit)
            need(again == result, 'APPROVAL_CHANGED_DURING_COMMIT')
            git(root, 'update-ref', '-m', 'validated candidate commit', candidate['branch'], commit, candidate['head'])
            attempt_code = 0
    except Exception:
        # Object/ref/index changes must be observed even on failure. No rollback.
        attempt_code = 3
    finally:
        lock.unlink()
    after, _ = state(root)
    actual_tree = git(root, 'rev-parse', 'HEAD^{tree}').decode().strip()
    actual_parent = git(root, 'rev-parse', 'HEAD^').decode().strip() if after['head'] != before['head'] else None
    success = (attempt_code == 0 and after['head'] == commit and after['branch'] == before['branch']
               and after['index_sha256'] == before['index_sha256'] and actual_parent == candidate['head']
               and actual_tree == tree and not git(root, 'status', '--porcelain', '--untracked-files=normal'))
    receipt = {'status': 'COMMITTED' if success else 'ATTEMPT_REQUIRES_REVIEW', 'candidate_sha256': cid,
               'approval_sha256': aid, 'before': before, 'after': after, 'commit_object': commit,
               'attempt_exit': attempt_code, 'authority': 'NO_CLOSURE_NEXT_PUBLICATION_OR_PRODUCTION_AUTHORITY'}
    atomic(receipt_path, receipt)
    return receipt, 0 if success else 3


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('operation', choices=('identity', 'preflight', 'commit'))
    p.add_argument('--work-unit', required=True)
    p.add_argument('--candidate', type=Path)
    p.add_argument('--evidence', type=Path)
    p.add_argument('--approval', type=Path)
    p.add_argument('--file', action='append', default=[])
    p.add_argument('--message')
    p.add_argument('--owner-confirmed')
    p.add_argument('--authorization-reference')
    args = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        if args.operation == 'identity':
            value = snapshot(root, args.work_unit, args.file, args.message)
            output = {'status': 'IDENTITY_ONLY', 'candidate_sha256': binding(value), 'candidate': value}
            code = 0
        elif args.operation == 'preflight':
            output, _, _, _ = preflight(root, args.candidate, args.evidence, args.approval, args.work_unit)
            code = 0
        else:
            output, code = execute(root, args.candidate, args.evidence, args.approval, args.work_unit,
                                   args.owner_confirmed, args.authorization_reference)
        print(json.dumps(output, sort_keys=True))
        return code
    except Exception:
        # Never echo Git output/config/user identity/raw paths or exception text.
        try:
            actual, _ = state(root)
        except Exception:
            actual = None
        print(json.dumps({'status': 'PENDING', 'eligible': False, 'actual': actual,
                          'reason': 'UNPROVEN_PRECONDITION; INSPECT_LOCAL_CONTRACT'}))
        return 3


if __name__ == '__main__':
    raise SystemExit(main())
