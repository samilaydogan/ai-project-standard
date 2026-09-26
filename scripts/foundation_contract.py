"""Fixed language-neutral foundation declarations; static reads only, no engines."""

from __future__ import annotations

import fnmatch
import hashlib
import json
import re
import tomllib
from pathlib import Path

NA = "NOT_APPLICABLE"
PENDING = {"PENDING", "NOT_CONFIGURED", "NOT_IMPLEMENTED"}
SECTIONS = {"identity", "toolchain", "database", "migration", "persistent_data", "hygiene",
            "backup", "background_jobs", "authentication", "observability", "testing",
            "third_party", "ui", "local_stronger_rules", "operations"}
STATUS = {"APPLICABLE", NA, "PENDING", "NOT_CONFIGURED"}
TARGETS = {"git", "docker", "release", "fingerprint", "handoff"}


def require(ok, message):
    if not ok:
        raise ValueError(f"FOUNDATION: {message}")


def shape(value, keys, label):
    require(isinstance(value, dict) and set(value) == set(keys), f"{label} fixed schema")


def text(value, label):
    require(isinstance(value, str) and value.strip() and "\0" not in value, f"{label} declaration")
    return value


def file(root, name):
    from project_runner import local_file
    return local_file(root, name)


def json_file(root, name):
    def unique(pairs):
        out = {}
        for key, value in pairs:
            require(key not in out, f"{name} duplicate key")
            out[key] = value
        return out
    value = json.loads(file(root, name).read_text(), object_pairs_hook=unique)
    require(isinstance(value, dict), f"{name} object required")
    return value


def unavailable(row, except_keys=()):
    require(all(value == NA for key, value in row.items() if key not in except_keys),
            "inapplicable family fields must be NOT_APPLICABLE")


def command(config, name, label, mutating=None, permit_pending=True):
    if permit_pending and name in PENDING:
        return False
    require(isinstance(name, str) and name in config["commands"], f"{label} command mapping")
    row = config["commands"][name]
    require(row["status"] == "READY" and row["argv"], f"{label} configured command required")
    if mutating is not None:
        require(row["mutability"] == ("mutating" if mutating else "read-only"), f"{label} mutability")
    return True


def external(root, name, label):
    text(name, label)
    require(name not in PENDING | {NA} and "$" not in name and "\\" not in name, f"{label} external root")
    path = Path(name).expanduser()
    path = path if path.is_absolute() else root / path
    resolved = path.resolve()
    require(not resolved.is_relative_to(root.resolve()) and not root.resolve().is_relative_to(resolved),
            f"{label} outside source (not ancestor), including symlinks")


def matches(path, pattern):
    # Bounded contract: relative paths; basename globs at any depth; directory subtrees.
    if pattern.endswith('/'):
        directory = pattern.rstrip('/')
        return path.startswith(directory + '/') or '/' + directory + '/' in '/' + path
    return fnmatch.fnmatch(path, pattern) or ('/' not in pattern and any(
        fnmatch.fnmatch(part, pattern) for part in Path(path).parts))


def excluded(path, policy):
    return path not in policy["source_exceptions"] and any(matches(path, r["path"]) for r in policy["rules"])


def ignored(path, patterns):
    result = False
    for pattern in patterns.splitlines():
        pattern = pattern.strip()
        if not pattern or pattern.startswith('#'):
            continue
        negative = pattern.startswith('!')
        pattern = pattern.lstrip('!').lstrip('/')
        if matches(path, pattern):
            result = not negative
    return result


def hygiene(root, row, runtime):
    shape(row, {"policy_path", "gitignore_path", "dockerignore_path"}, "hygiene")
    policy = json_file(root, row["policy_path"])
    shape(policy, {"schema_version", "source_exceptions", "rules"}, "exclusion policy")
    require(type(policy["schema_version"]) is int and policy["schema_version"] == 1, "exclusion schema")
    require(isinstance(policy["source_exceptions"], list) and
            all(isinstance(v, str) for v in policy["source_exceptions"]), "source exception inventory")
    require(isinstance(policy["rules"], list) and bool(policy["rules"]), "exclusion rules required")
    git = file(root, row["gitignore_path"]).read_text()
    docker = file(root, row["dockerignore_path"]).read_text() if row["dockerignore_path"] != NA else None
    if runtime["runtime_mode"] in {"docker", "hybrid"}:
        require(docker is not None, "Docker build exclusions required")
    seen = set()
    for item in policy["rules"]:
        shape(item, {"path", "category", "targets"}, "exclusion rule")
        path = text(item["path"], "exclusion pattern")
        require(not Path(path).is_absolute() and '..' not in Path(path).parts and path not in seen,
                "unsafe/duplicate exclusion pattern")
        seen.add(path)
        require(item["category"] in {"secrets", "cache", "runtime", "database", "backup", "apply", "test", "build"},
                "exclusion category")
        require(isinstance(item["targets"], list) and set(item["targets"]) == TARGETS and
                len(item["targets"]) == len(TARGETS), "single policy must cover all source targets")
        probe = path.replace('*', 'private-probe').rstrip('/') + ('/probe' if path.endswith('/') else '')
        if probe in policy["source_exceptions"]:
            continue
        require(ignored(probe, git), f"Git exclusion missing {path}")
        if '/' not in path.rstrip('/'):
            require(ignored('nested/' + probe, git), f'Git nested exclusion missing {path}')
            if docker is not None:
                require(ignored('nested/' + probe, docker), f'Docker nested exclusion missing {path}')
        if docker is not None:
            require(ignored(probe, docker), f"Docker exclusion missing {path}")
    env = runtime["environment"]
    require(excluded(env["env_path"], policy), "runtime env missing from release/fingerprint/handoff exclusion")
    require(env["env_example_path"] in policy["source_exceptions"], "safe environment example source exception")
    require(not ignored(env["env_example_path"], git), "safe environment example must not be Git excluded")
    return policy


def data_root(root, value, label, policy):
    text(value, label)
    if value.startswith('volume:'):
        require(re.fullmatch(r"volume:[a-z][a-z0-9_-]*", value), f"{label} named volume")
        return
    require(value not in PENDING | {NA} and '$' not in value, f"{label} concrete data root")
    path = Path(value).expanduser()
    path = path if path.is_absolute() else root / path
    resolved = path.resolve()
    require(resolved != root.resolve() and not root.resolve().is_relative_to(resolved), f"{label} cannot contain source")
    if resolved.is_relative_to(root.resolve()):
        rel = resolved.relative_to(root.resolve()).as_posix()
        require(excluded(rel + '/probe', policy) or excluded(rel, policy), f"{label} lacks unified source exclusion")


def validate(root, config):
    f = config["foundation"]
    shape(f, SECTIONS, "foundation")
    debt = []
    runtime = config["runtime"]
    env = runtime["environment"]
    keys = set(env["required_env_keys"] + env["optional_env_keys"])
    secrets = set(env["secret_env_keys"])
    def env_key(value, label, secret=False):
        require(value in keys and (not secret or value in secrets), f"{label} environment/secret declaration")
    identity = f["identity"]
    shape(identity, {"project_name", "project_slug", "application_version", "version_source"}, "identity")
    text(identity["project_name"], "project_name")
    require(isinstance(identity["project_slug"], str) and re.fullmatch(r"[a-z][a-z0-9-]*", identity["project_slug"]), "project_slug")
    text(identity["application_version"], "application version")
    version_path = file(root, identity["version_source"])
    if version_path.suffix == '.toml':
        observed_version = tomllib.loads(version_path.read_text()).get('project', {}).get('version')
    elif version_path.suffix == '.json':
        observed_version = json_file(root, identity['version_source']).get('version')
    else:
        observed_version = version_path.read_text().strip()
    require(observed_version == identity['application_version'], 'application version source mismatch')
    tool = f["toolchain"]
    shape(tool, {"language", "runtime", "runtime_version_range", "dependency_manifest_path", "manifest_format",
                 "manifest_sha256", "lockfile_path", "lockfile_format", "lockfile_sha256",
                 "lock_binding_manifest_sha256", "lock_policy", "build_system", "test_runner", "lint_runner",
                 "application_entrypoint", "execution_facade"}, "toolchain")
    for k in ("language", "runtime", "runtime_version_range", "build_system", "test_runner", "lint_runner"):
        text(tool[k], k)
    require(tool["execution_facade"] == config["facade"], "toolchain facade mismatch")
    file(root, tool["application_entrypoint"])
    manifest_path = file(root, tool["dependency_manifest_path"])
    digest = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    require(tool["manifest_sha256"] == digest, "dependency manifest hash mismatch; explicit review required")
    require(tool["manifest_format"] in {"pep621", "npm", "declared"}, "manifest format")
    deps = None
    if tool["manifest_format"] == "pep621":
        project = tomllib.loads(manifest_path.read_text()).get('project', {})
        require(project.get('name') == identity["project_slug"] and project.get('version') == identity["application_version"],
                "manifest project name/version coherence")
        require(project.get('requires-python') == tool["runtime_version_range"], "manifest runtime range coherence")
        deps = project.get('dependencies', [])
    elif tool["manifest_format"] == "npm":
        project = json_file(root, tool["dependency_manifest_path"])
        require(project.get('name') == identity["project_slug"] and project.get('version') == identity["application_version"],
                "manifest project name/version coherence")
        require(project.get('engines', {}).get('node') == tool["runtime_version_range"], "manifest runtime range coherence")
        deps = {**project.get('dependencies', {}), **project.get('devDependencies', {})}
    require(tool["lock_policy"] in {"NO_THIRD_PARTY_DEPENDENCIES", "PROJECT_DECLARED_NO_LOCK", "FROZEN_LOCK"}, "lock policy")
    if tool["lockfile_path"] == NA:
        require(tool["lockfile_format"] == 'none' and tool["lockfile_sha256"] == NA and tool["lock_binding_manifest_sha256"] == NA,
                "inapplicable lock fields")
        require(tool["lock_policy"] != "FROZEN_LOCK", "frozen lock missing")
        if tool["lock_policy"] == "NO_THIRD_PARTY_DEPENDENCIES":
            require(deps is not None and not deps and not project.get('optional-dependencies') and not project.get('optionalDependencies'), "no-dependency claim conflicts with manifest")
        else:
            debt.append('project-declared no-lock policy requires local review')
    else:
        require(tool["lock_policy"] == "FROZEN_LOCK" and tool["lockfile_format"] in {"uv", "package-lock", "declared"}, "lock format/policy")
        lock_path = file(root, tool["lockfile_path"])
        require(hashlib.sha256(lock_path.read_bytes()).hexdigest() == tool["lockfile_sha256"], "lock hash mismatch")
        require(tool["lock_binding_manifest_sha256"] == digest, "lock review binding differs from manifest")
        if tool["lockfile_format"] == "uv":
            lock = tomllib.loads(lock_path.read_text())
            require(lock.get('requires-python') == tool["runtime_version_range"], "lock runtime range mismatch")
            require(any(p.get('name') == identity["project_slug"] and p.get('version') == identity["application_version"]
                        for p in lock.get('package', [])), "lock project identity mismatch")
        elif tool["lockfile_format"] == "package-lock":
            lock = json_file(root, tool["lockfile_path"])
            require(lock.get('name') == identity["project_slug"] and lock.get('version') == identity["application_version"], "lock project identity mismatch")
            require(all(lock.get('packages', {}).get('', {}).get(kind, {}) == project.get(kind, {}) for kind in ('dependencies', 'devDependencies', 'optionalDependencies')), "lock dependency map mismatch")
    policy = hygiene(root, f["hygiene"], runtime)
    db = f["database"]
    shape(db, {"database_mode", "database_engine", "host", "host_port", "listen_port", "name", "user_env_key",
               "password_env_key", "connection_env_key", "data_root", "compose_service", "health_command",
               "required_at_day_zero", "test_isolation"}, "database")
    mode = db["database_mode"]
    require(mode in {"none", "embedded", "container", "external"}, "database_mode")
    require(db["database_engine"] in {"none", "sqlite", "postgres", "mysql", "project_defined"}, "database_engine")
    require(type(db["required_at_day_zero"]) is bool, "database_required_at_day_zero")
    if mode == 'none':
        require(db["database_engine"] == 'none' and db["required_at_day_zero"] is False, "no-DB engine/required coherence")
        unavailable(db, {"database_mode", "database_engine", "required_at_day_zero"})
    else:
        require(db["database_engine"] != 'none' and db["test_isolation"] in {'temporary-synthetic', 'isolated-container', 'explicit-external-test'}, "stateful DB/test isolation")
        if db["connection_env_key"] != NA:
            env_key(db["connection_env_key"], 'DB connection')
        if mode == 'embedded':
            require(db["database_engine"] in {'sqlite', 'project_defined'}, "embedded DB engine")
            unavailable(db, {"database_mode", "database_engine", "data_root", "connection_env_key", "required_at_day_zero", "test_isolation", "name"})
            data_root(root, db["data_root"], 'embedded DB data', policy)
        else:
            text(db['host'], 'database host')
            text(db['name'], 'database name')
            require(db['host_port'] == NA and mode == 'container' or type(db['host_port']) is int and 1 <= db['host_port'] <= 65535, 'database host port')
            env_key(db['user_env_key'], 'DB user')
            env_key(db['password_env_key'], 'DB password', secret=True)
            require(isinstance(db['health_command'], list) and db['health_command'] and all(isinstance(x,str) and x for x in db['health_command']), 'DB health argv')
            if mode == 'container':
                require(runtime['runtime_mode'] in {'docker','hybrid'}, 'container DB requires Docker applicability')
                require(type(db['listen_port']) is int and 1 <= db['listen_port'] <= 65535, 'DB listen port')
                compose = json_file(root, runtime['docker']['compose_file'])
                service = compose.get('services', {}).get(db['compose_service'])
                require(isinstance(service, dict) and db['compose_service'] != runtime['docker']['primary_service'], 'DB service coherence')
                require(db['host'] in {db['compose_service'], service.get('hostname')}, 'DB host/service coherence')
                ports = service.get('ports', [])
                if db['host_port'] == NA:
                    require(not ports, 'unpublished DB cannot expose host port')
                else:
                    require(ports == [f"{runtime['network']['bind_host']}:{db['host_port']}:{db['listen_port']}"], 'DB Compose port coherence')
                require(service.get('x-foundation-role') == 'database', 'DB Compose role declaration')
                require(service.get('healthcheck', {}).get('test') == ['CMD', *db['health_command']], 'DB service health coherence')
                environment = service.get('environment', {})
                require(isinstance(environment, dict) and db['password_env_key'] in environment and db['user_env_key'] in environment, 'DB Compose env mapping')
                require(environment[db['password_env_key']] in {None, '${'+db['password_env_key']+'}', '${'+db['password_env_key']+':?required}'}, 'no literal/default DB password')
                data_root(root, db['data_root'], 'DB data', policy)
                require(service.get('volumes'), 'DB persistent volume required')
                if db['data_root'].startswith('volume:'):
                    volume = db['data_root'][7:]
                    require(volume in compose.get('volumes', {}) and any(isinstance(v,str) and v.startswith(volume+':') for v in service['volumes']), 'DB named volume coherence')
                else:
                    require(any(isinstance(v,str) and v.startswith(db['data_root']+':') for v in service['volumes']), 'DB bind volume coherence')
            else:
                require(db['compose_service'] == NA and db['data_root'] == NA and db['listen_port'] == NA, 'external DB has no local service/data/listen port')
                if runtime['docker']['status'] == 'READY':
                    compose = json_file(root, runtime['docker']['compose_file'])
                    require(not any('database' in s.get('x-foundation-role','') for s in compose.get('services',{}).values()), 'external DB cannot define local DB service')
    migration = f['migration']
    shape(migration, {'applicability','strategy','command','preflight_command','schema_version_source','current_version','target_version',
                      'automatic_down_migration','source_behind_database_fail_closed','backup_required_before_migration',
                      'recovery_strategy','recovery_command','documentation_path'}, 'migration')
    file(root, migration['documentation_path'])
    require(migration['applicability'] in STATUS, 'migration applicability')
    require(migration['automatic_down_migration'] is False and migration['source_behind_database_fail_closed'] is True, 'no automatic down/source-behind fails closed')
    require(type(migration['backup_required_before_migration']) is bool, 'migration backup requirement')
    if migration['applicability'] == NA:
        unavailable(migration, {'applicability','automatic_down_migration','source_behind_database_fail_closed','backup_required_before_migration','documentation_path'})
    elif migration['applicability'] in PENDING:
        require(mode != 'none', 'no-DB migration coherence')
        debt.append('migration applicability pending')
        for k in ('strategy','command','preflight_command','schema_version_source','current_version','target_version','recovery_strategy','recovery_command'):
            text(migration[k], k)
    else:
        require(mode != 'none' and migration['strategy'] == 'forward-idempotent', 'stateful forward/idempotent migration')
        for k in ('command','preflight_command','recovery_command'):
            if not command(config, migration[k], 'migration '+k, mutating=k!='preflight_command'):
                debt.append('migration '+k+' not implemented')
        if migration['schema_version_source'] in PENDING:
            debt.append('schema version source pending')
        else:
            file(root, migration['schema_version_source'])
        for k in ('current_version','target_version','recovery_strategy'):
            text(migration[k], k)
    data = f['persistent_data']
    shape(data, {'runtime_data_root','database_data_root','blob_storage_mode','blob_root','retention','quota_bytes','upload_limit_bytes'}, 'persistent_data')
    require(data['database_data_root'] == db['data_root'], 'database data owner mismatch')
    require(data['blob_storage_mode'] in {'none','local','object_store','external','project_defined'}, 'blob storage mode')
    if data['runtime_data_root'] != NA:
        data_root(root, data['runtime_data_root'], 'runtime data', policy)
    if data['blob_storage_mode'] == 'local':
        data_root(root, data['blob_root'], 'local blob data', policy)
    else:
        require(data['blob_root'] == NA, 'non-local blob root must be NOT_APPLICABLE')
    for k in ('quota_bytes','upload_limit_bytes'):
        require(data[k] in {NA, 'PENDING'} or (type(data[k]) is int and data[k]>0), k+' applicability/limit')
    text(data['retention'], 'data retention')
    declared_roots = {value for value in (data['runtime_data_root'], data['database_data_root'], data['blob_root']) if value != NA}
    declared_data = {x for x in declared_roots if not x.startswith('volume:')}
    declared_volumes = {x[7:] for x in declared_roots if x.startswith('volume:')}
    require(set(runtime['storage']['data_roots']) == declared_data and set(runtime['storage']['volume_roots']) == declared_volumes,
            'runtime storage lists differ from foundation data roots')
    if declared_roots:
        require(runtime['storage']['status'] == 'READY', 'persistent storage availability')
    backup = f['backup']
    shape(backup, {'applicability','scope','root','integrity_metadata_required','verify_command','restore_command',
                   'restore_confirmation_required','pre_restore_backup','retention','key_preservation','rationale'}, 'backup')
    require(backup['applicability'] in STATUS, 'backup applicability')
    require(isinstance(backup['scope'], list) and set(backup['scope']) <= {'source','database','runtime_data','blob_data','configuration'}, 'backup scope')
    require(all(backup[k] is True for k in ('integrity_metadata_required','restore_confirmation_required','pre_restore_backup')), 'backup integrity/restore safety')
    require(backup['key_preservation'] == 'required-if-encrypted', 'decryption key preservation')
    text(backup['rationale'], 'backup rationale')
    if backup['applicability'] == NA:
        require(not backup['scope'] and backup['root'] == NA and backup['verify_command'] == NA and backup['restore_command'] == NA and backup['retention'] == NA, 'inapplicable backup fields')
        require(not migration['backup_required_before_migration'], 'migration requires absent backup')
    elif backup['applicability'] in PENDING:
        debt.append('backup applicability pending')
        if backup['root'] not in PENDING | {NA}:
            external(root, backup['root'], 'pending backup root')
    else:
        require(backup['scope'], 'backup scope required')
        external(root, backup['root'], 'backup root')
        for k in ('verify_command','restore_command'):
            if not command(config, backup[k], 'backup '+k, mutating=k=='restore_command'):
                debt.append('backup '+k+' not implemented')
        text(backup['retention'], 'backup retention')
    require('database' not in backup['scope'] or mode != 'none', 'backup database scope without DB')
    require('runtime_data' not in backup['scope'] or data['runtime_data_root'] != NA, 'backup runtime scope without data')
    require('blob_data' not in backup['scope'] or data['blob_storage_mode'] != 'none', 'backup blob scope without data')
    if migration['backup_required_before_migration']:
        require(backup['applicability'] != NA and 'database' in backup['scope'], 'migration backup database scope required')
    jobs = f['background_jobs']
    shape(jobs, {'mode','command','compose_service','persistence_dependency','retry_idempotency_owner','health_command'}, 'background jobs')
    require(jobs['mode'] in {'none','in_process','worker','external','project_defined'}, 'background jobs mode')
    if jobs['mode'] == 'none':
        unavailable(jobs, {'mode'})
    else:
        for k in ('persistence_dependency','retry_idempotency_owner'):
            text(jobs[k], k)
        if jobs['command'] != NA:
            if not command(config,jobs['command'],'worker',mutating=True):debt.append('worker command pending')
        if jobs['compose_service'] != NA:
            require(runtime['docker']['status']=='READY' and jobs['compose_service'] in json_file(root,runtime['docker']['compose_file']).get('services',{}), 'worker service applicability')
        require(jobs['mode'] not in {'worker'} or jobs['command'] != NA or jobs['compose_service'] != NA, 'worker entry required')
        if jobs['health_command'] != NA and not command(config,jobs['health_command'],'worker health',mutating=False):debt.append('worker health pending')
    auth = f['authentication']
    shape(auth, {'mode','integration_class','callback_url_env_key','public_url_env_key','session_owner','authorization_owner'}, 'authentication')
    require(auth['mode'] in {'none','external','project_defined'} and auth['authorization_owner']=='project', 'authentication/business authorization boundary')
    if auth['mode']=='none':
        unavailable(auth, {'mode','authorization_owner'})
    else:
        text(auth['integration_class'],'generic integration class');text(auth['session_owner'],'session owner')
        for k in ('callback_url_env_key','public_url_env_key'):
            if auth[k]!=NA:env_key(auth[k],k)
    obs=f['observability']
    shape(obs, {'logging_format','logging_strategy','correlation','redaction','health_command','readiness_command','log_destination','retention'}, 'observability')
    for k,v in obs.items():text(v,'observability '+k)
    require(obs['redaction']=='no-headers-query-body-or-personal-data','redaction boundary')
    for k in ('health_command','readiness_command'):
        command(config,obs[k],k,mutating=False,permit_pending=False)
    tests=f['testing']
    shape(tests, {'classes','production_credentials','skip_is_pass','mock_is_live','stale_on_identity_change'}, 'testing')
    require(tests['production_credentials']=='forbidden' and tests['skip_is_pass'] is False and tests['mock_is_live'] is False and tests['stale_on_identity_change'] is True, 'test truth/safety/staleness')
    shape(tests['classes'], {'unit','integration','isolated_acceptance','live_acceptance','e2e','screenshot_qa'}, 'test classes')
    for cls,row in tests['classes'].items():
        shape(row, {'status','command','timeout_seconds','network','state'}, 'test class '+cls)
        require(row['status'] in STATUS, 'test class status')
        if row['status']==NA:
            unavailable(row, {'status'})
        elif row['status'] in PENDING:
            debt.append('test class '+cls+' pending')
        else:
            command(config,row['command'],'test class '+cls,permit_pending=False)
            require(type(row['timeout_seconds']) is int and 1<=row['timeout_seconds']<=86400, 'bounded test timeout')
            require(row['network'] in ({'explicit-live'} if cls=='live_acceptance' else {'disabled','loopback-only'}), 'live network class isolation')
            require(row['state']=='temporary-synthetic' or cls=='live_acceptance' and row['state']=='explicit-authorized-live','test state isolation')
    third=f['third_party']
    shape(third, {'inventory_path','review_status','bundled_assets','rationale'}, 'third party')
    license_text=file(root,third['inventory_path']).read_text()
    require(third['review_status'] in {'APPROVED','PENDING','NOT_CONFIGURED','REFERENCE_ONLY'},'license review status')
    require(isinstance(third['bundled_assets'],list) and all(isinstance(x,str) and x for x in third['bundled_assets']), 'bundled assets inventory')
    text(third['rationale'],'license rationale')
    require(third['review_status']!='REFERENCE_ONLY' or not third['bundled_assets'],'bundled assets cannot be reference-only')
    for word in ('dependency/asset','version','purpose','source','license','commercial','redistribution','cost','bundled','decision','evidence'):
        require(word in license_text.lower(), 'third-party inventory missing '+word)
    if third['review_status'] == 'APPROVED':
        table_rows = [line.lower() for line in license_text.splitlines() if line.strip().startswith('|')]
        require(len(table_rows) > 2, 'approved inventory requires item evidence')
        require(not any(re.search(r'\b(pending|unknown|conditional|reference_only)\b', line) for line in table_rows[2:]),
                'unknown/conditional license row cannot be approved')
    if third['review_status'] in PENDING:debt.append('license review pending')
    ui=f['ui'];shape(ui,{'applicability','rationale'},'UI')
    require(ui['applicability'] in STATUS,'UI applicability');text(ui['rationale'],'UI rationale')
    stronger=f['local_stronger_rules'];shape(stronger,{'references','rationale'},'local stronger rules')
    require(isinstance(stronger['references'],list),'stronger rule references')
    for name in stronger['references']:file(root,name)
    text(stronger['rationale'],'stronger rules rationale')
    ops=f['operations'];shape(ops,{'installation_doc','recovery_doc','runbook_doc'},'operations')
    for name in ops.values():file(root,name)
    return sorted(set(debt))
