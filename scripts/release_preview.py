"""Trusted stdlib preview adapter; committed blobs only, no approval authentication."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import uuid
import unicodedata
from pathlib import Path, PurePosixPath


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def binding(value):
    return sha(json.dumps(value, sort_keys=True, separators=(',', ':')).encode())


def decode(data):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            need(key not in result, 'PENDING: duplicate key')
            result[key] = value
        return result
    return json.loads(data, object_pairs_hook=unique)


def git(root, *args):
    env = {k: os.environ[k] for k in ('PATH', 'HOME', 'LANG', 'LC_CTYPE') if k in os.environ}
    env.update(GIT_OPTIONAL_LOCKS='0', GIT_TERMINAL_PROMPT='0', GIT_NO_REPLACE_OBJECTS='1')
    p = subprocess.run(['git', '-c', 'core.fsmonitor=false', '-C', str(root), *args], env=env, stdout=subprocess.PIPE,
                       stderr=subprocess.DEVNULL, timeout=30, check=False)
    need(p.returncode == 0, 'PENDING: Git object/state unavailable')
    return p.stdout


def relative(name):
    need(isinstance(name, str) and name and '\\' not in name and ':' not in name, 'PENDING: unsafe member')
    p = PurePosixPath(name)
    need(not p.is_absolute() and all(x.lower() not in ('.', '..', '.git') and x.rstrip(' .') == x for x in p.parts)
         and p.as_posix() == name, 'PENDING: unsafe member')
    reserved = {'con', 'prn', 'aux', 'nul', 'conin$', 'conout$'} | {f'{prefix}{n}' for prefix in ('com', 'lpt') for n in '123456789¹²³'}
    need(all(x.split('.')[0].lower() not in reserved for x in p.parts), 'PENDING: reserved platform member')
    return name


def objects(root, commit):
    entries = {}
    aliases = {}
    for raw in git(root, 'ls-tree', '-rz', '--full-tree', commit).split(b'\0'):
        if not raw:
            continue
        meta, name = raw.split(b'\t', 1)
        mode, kind, oid = meta.decode().split()
        name = relative(name.decode())
        parts = PurePosixPath(name).parts
        for n in range(1, len(parts) + 1):
            prefix = '/'.join(parts[:n])
            alias = unicodedata.normalize('NFC', prefix).casefold()
            need(alias not in aliases or aliases[alias] == prefix, 'PENDING: platform path collision')
            aliases[alias] = prefix
        need(kind == 'blob' and mode in ('100644', '100755'), 'NOT CONFIGURED: symlink/submodule/special member')
        entries[name] = (mode, oid)
    need(entries, 'PENDING: empty committed tree')
    need(len(entries) <= 10000, 'NOT CONFIGURED: bounded member limit')
    return entries


def blob(root, entries, name):
    relative(name)
    need(name in entries, 'NOT CONFIGURED: missing committed prerequisite')
    need(int(git(root, 'cat-file', '-s', entries[name][1])) <= 16 * 1024 * 1024, 'NOT CONFIGURED: bounded blob limit')
    return git(root, 'cat-file', 'blob', entries[name][1])


def identity(root, commit, unit):
    need(re.fullmatch(r'[0-9a-f]{40}', commit or ''), 'PENDING: full commit SHA required')
    need(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,79}', unit or ''), 'PENDING: work-unit identity')
    need(git(root, 'rev-parse', '--show-toplevel').decode().strip() == str(root), 'PENDING: repository root mismatch')
    need(git(root, 'rev-parse', 'HEAD').decode().strip() == commit, 'PENDING: source HEAD mismatch')
    ref = git(root, 'symbolic-ref', '-q', 'HEAD').decode().strip()
    need(ref.startswith('refs/heads/'), 'PENDING: detached source')
    entries = objects(root, commit)
    cfg_raw = blob(root, entries, 'release-preview-profile.json')
    cfg = decode(cfg_raw)
    need(set(cfg) == {'schema_version', 'adapter', 'entrypoint', 'args', 'timeout_seconds', 'prerequisites', 'version_path', 'standard_path'},
         'NOT CONFIGURED: preview profile schema')
    need(type(cfg['schema_version']) is int and cfg['schema_version'] == 1 and cfg['adapter'] == 'trusted-stdlib-python-validation', 'NOT CONFIGURED: preview adapter')
    relative(cfg['entrypoint'])
    need(cfg['entrypoint'].endswith('.py'), 'NOT CONFIGURED: Python entrypoint required')
    need(isinstance(cfg['args'], list) and all(isinstance(x, str) and '\0' not in x for x in cfg['args']), 'NOT CONFIGURED: literal args')
    need(type(cfg['timeout_seconds']) is int and 1 <= cfg['timeout_seconds'] <= 180, 'NOT CONFIGURED: timeout')
    need(isinstance(cfg['prerequisites'], list) and all(isinstance(n, str) for n in cfg['prerequisites']), 'NOT CONFIGURED: prerequisites')
    for name in [cfg['entrypoint'], *cfg['prerequisites']]:
        blob(root, entries, name)
    version = blob(root, entries, cfg['version_path']).decode().strip()
    standard_raw = blob(root, entries, cfg['standard_path'])
    standard = decode(standard_raw)
    need(standard.get('version') == version, 'PENDING: committed version mismatch')
    # Do not import tracked credentials/runtime/cache history into a preview.
    policy = decode(blob(root, entries, 'source-exclusions.json'))
    from fnmatch import fnmatchcase
    need(set(policy) == {'schema_version', 'rules', 'source_exceptions'} and type(policy['schema_version']) is int
         and policy['schema_version'] == 1 and isinstance(policy['rules'], list) and policy['rules']
         and isinstance(policy['source_exceptions'], list), 'PENDING: exclusion contract')
    for name in entries:
        need(not any(part.casefold() == '.ds_store' for part in PurePosixPath(name).parts), 'PENDING: non-waivable OS metadata')
        need(not any(part.casefold() == '.env' for part in PurePosixPath(name).parts), 'PENDING: runtime credential environment')
        for rule in policy['rules']:
            pat = rule['path'].rstrip('/')
            relative(pat)
            matches = (name.startswith(pat + '/') or '/' + pat + '/' in '/' + name) if rule['path'].endswith('/') else (
                fnmatchcase(name, pat) or ('/' not in pat and any(fnmatchcase(p, pat) for p in PurePosixPath(name).parts)))
            need(not matches or name in policy['source_exceptions'], 'PENDING: excluded committed source member')
    return {'schema_version': 1, 'repository_sha256': sha(str(root).encode()), 'commit': commit,
            'tree': git(root, 'rev-parse', commit + '^{tree}').decode().strip(), 'ref': ref,
            'work_unit': unit, 'profile_sha256': sha(cfg_raw), 'version': version,
            'standard_sha256': sha(standard_raw), 'adapter_sha256': sha(Path(__file__).read_bytes()),
            'runtime': sys.version, 'runtime_executable_sha256': sha(Path(sys.executable).read_bytes())}, cfg, entries


def source_state(root):
    inventory = {}
    names = set(git(root, 'ls-files', '-z', '--cached', '--others').split(b'\0')) - {b''}
    for raw in sorted(names):
        name = relative(raw.decode())
        p = root / name
        alias = next((q for q in (p, *p.parents) if q != root and q.is_relative_to(root) and q.is_symlink()), None)
        if alias is not None:
            inventory[name] = {'link': sha(os.readlink(alias).encode())}
        elif p.is_symlink():
            inventory[name] = {'link': sha(os.readlink(p).encode())}
        elif p.is_file():
            inventory[name] = {'sha256': sha(p.read_bytes()), 'mode': p.stat().st_mode & 0o777}
        else:
            inventory[name] = {'missing_or_special': True}
    index = Path(git(root, 'rev-parse', '--git-path', 'index').decode().strip())
    if not index.is_absolute():
        index = root / index
    return {'head': git(root, 'rev-parse', 'HEAD').decode().strip(),
            'refs_sha256': sha(git(root, 'show-ref')), 'index_sha256': sha(index.read_bytes()),
            'inventory_sha256': binding(inventory)}


def preflight(root, commit, unit, approval_path):
    ident, cfg, entries = identity(root, commit, unit)
    need(approval_path.is_file() and not approval_path.is_symlink() and not approval_path.resolve().is_relative_to(root),
         'PENDING: external preview approval required')
    raw = approval_path.read_bytes()
    approval = decode(raw)
    need(set(approval) == {'schema_version', 'kind', 'status', 'role', 'reference', 'identity_sha256', 'expires_at'}, 'PENDING: preview approval schema')
    need(type(approval['schema_version']) is int and approval['schema_version'] == 1 and approval['kind'] == 'PREVIEW' and approval['status'] == 'APPROVED'
         and approval['role'] == 'human_owner', 'PENDING: separate preview decision required')
    need(approval['identity_sha256'] == binding(ident), 'PENDING: stale/mismatched preview decision')
    need(isinstance(approval['reference'], str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,119}', approval['reference']), 'PENDING: decision reference')
    need(type(approval['expires_at']) in (int, float) and time.time() < approval['expires_at'] <= time.time() + 86400,
         'PENDING: expired/unbounded preview decision')
    return ident, cfg, entries, approval, sha(raw)


def execute(root, commit, unit, approval_path, confirmed, reference):
    before = source_state(root)
    ident, cfg, entries, approval, ahash = preflight(root, commit, unit, approval_path)
    need(confirmed == ahash and reference == approval['reference'], 'PENDING: operator must confirm actual owner channel')
    result = {'status': 'FAIL', 'identity': ident, 'approval_sha256': ahash,
              'authority': 'RECORD_NOT_HUMAN_AUTHENTICATION', 'before': before,
              'startup': 'NOT ASSESSED', 'health': 'NOT ASSESSED', 'stop': 'NOT ASSESSED',
              'child_exit': None, 'cleanup': 'PENDING', 'retention': 'NONE', 'output': 'SUPPRESSED'}
    temp_root = Path(tempfile.gettempdir()).resolve()
    need(temp_root.is_dir() and not temp_root.is_relative_to(root), 'PENDING: temporary storage must be outside source')
    with tempfile.TemporaryDirectory(prefix='committed-preview-', dir=temp_root) as temp:
        base = Path(temp)
        base.chmod(0o700)
        source = base / 'source'
        source.mkdir()
        total = 0
        for name, (mode, oid) in entries.items():
            p = source / name
            p.parent.mkdir(parents=True, exist_ok=True)
            data = blob(root, entries, name)
            total += len(data)
            need(total <= 64 * 1024 * 1024, 'NOT CONFIGURED: bounded tree limit')
            p.write_bytes(data)
            p.chmod(0o755 if mode == '100755' else 0o644)
        # Recheck after extraction, before starting trusted code.
        need(source_state(root) == before and identity(root, commit, unit)[0] == ident, 'PENDING: source race')
        preflight(root, commit, unit, approval_path)
        need(sha(approval_path.read_bytes()) == ahash, 'PENDING: approval race')
        home = base / 'home'
        home.mkdir()
        state = base / 'state'
        state.mkdir()
        report = state / 'result.json'
        nonce = uuid.uuid4().hex
        env = {'HOME': str(home), 'TMPDIR': str(state), 'LANG': 'C.UTF-8',
               'PREVIEW_RESULT_PATH': str(report), 'PREVIEW_NONCE': nonce}
        try:
            child = subprocess.run([sys.executable, '-I', '-S', '-B', str(source / cfg['entrypoint']), *cfg['args']],
                                   cwd=source, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL, timeout=cfg['timeout_seconds'], check=False)
            result['child_exit'] = child.returncode
            if report.is_file() and not report.is_symlink() and report.stat().st_size <= 4096:
                evidence = decode(report.read_bytes())
                if isinstance(evidence, dict) and set(evidence) == {'nonce', 'startup', 'health', 'stop'} and evidence['nonce'] == nonce:
                    for key in ('startup', 'health', 'stop'):
                        result[key] = 'PASS' if evidence[key] is True else 'FAIL'
            result['status'] = 'PASS' if child.returncode == 0 and all(result[k] == 'PASS' for k in ('startup', 'health', 'stop')) else 'FAIL'
        except subprocess.TimeoutExpired:
            result['status'] = 'TIMED_OUT'
        except (ValueError, OSError):
            result['status'] = 'FAIL'
    result['cleanup'] = 'PASS' if not base.exists() else 'FAIL'
    result['after'] = source_state(root)
    result['source_unchanged'] = result['after'] == before
    if not result['source_unchanged'] or result['cleanup'] != 'PASS':
        result['status'] = 'FAIL'
    return result, 0 if result['status'] == 'PASS' else 1


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['identity', 'preflight', 'run'])
    p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument('--commit', required=True)
    p.add_argument('--work-unit', required=True)
    p.add_argument('--approval', type=Path)
    p.add_argument('--owner-confirmed')
    p.add_argument('--authorization-reference')
    a = p.parse_args()
    try:
        root = a.root.resolve()
        if a.action == 'identity':
            result, _, _ = identity(root, a.commit, a.work_unit)
            result = {'status': 'IDENTIFIED', 'identity': result, 'identity_sha256': binding(result)}
            code = 0
        else:
            need(a.approval is not None, 'PENDING: separate preview approval required')
            if a.action == 'preflight':
                ident, _, _, _, _ = preflight(root, a.commit, a.work_unit, a.approval)
                result, code = {'status': 'ELIGIBLE', 'identity': ident, 'authority': 'RECORD_NOT_HUMAN_AUTHENTICATION'}, 0
            else:
                result, code = execute(root, a.commit, a.work_unit, a.approval, a.owner_confirmed, a.authorization_reference)
    except (ValueError, OSError, KeyError, TypeError, AttributeError, subprocess.SubprocessError):
        result, code = {'status': 'PENDING', 'reason': 'IDENTITY_CONFIG_AUTHORIZATION_OR_STATE_UNPROVEN'}, 3
    print(json.dumps(result, sort_keys=True))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
