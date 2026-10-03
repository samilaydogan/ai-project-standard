"""Synthetic foundation coherence and bounded reference enforcement; no external services."""

import contextlib
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import foundation_contract as contract
import project_runner
import reference_tests
from health_scaffold import Handler
import check_standard


def compose_available():
    return bool(shutil.which('docker')) and subprocess.run(
        ['docker', 'compose', 'version'], capture_output=True, timeout=5, check=False).returncode == 0


class FoundationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'source'
        self.source = Path(__file__).resolve().parents[1]
        for name in check_standard.DISTRIBUTION:
            # No test engine or Docker daemon is invoked while setting up fixtures.
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(self.source / name, target)
        self.profile = json.loads((self.root / 'execution-profile.json').read_text())
        self.f = self.profile['foundation']

    def load(self):
        (self.root / 'execution-profile.json').write_text(json.dumps(self.profile))
        return project_runner.load(self.root)

    def reject(self, expression):
        with self.assertRaisesRegex(ValueError, expression):
            self.load()

    def embedded(self):
        self.f['database'].update(database_mode='embedded', database_engine='sqlite', data_root='database-data',
                                  test_isolation='temporary-synthetic', name='synthetic.db')
        self.f['persistent_data']['database_data_root'] = 'database-data'
        self.profile['runtime']['storage'].update(status='READY', data_roots=['database-data'])

    def secret(self, key):
        self.profile['runtime']['environment']['optional_env_keys'].append(key)
        self.profile['runtime']['environment']['secret_env_keys'].append(key)
        with (self.root / '.env.example').open('a') as output:
            output.write(key + '=\n')

    def docker_db(self):
        self.profile = json.loads((self.root / 'execution-profile.docker.json').read_text())
        self.f = self.profile['foundation']
        self.secret('DB_PASSWORD')
        self.profile['runtime']['environment']['optional_env_keys'].append('DB_USER')
        with (self.root / '.env.example').open('a') as output:
            output.write('DB_USER=synthetic\n')
        self.f['database'].update(database_mode='container', database_engine='postgres', host='database',
            host_port=5433, listen_port=5432, name='synthetic', user_env_key='DB_USER', password_env_key='DB_PASSWORD',
            compose_service='database', data_root='volume:dbstate', health_command=['db-health'], test_isolation='isolated-container')
        self.f['persistent_data']['database_data_root'] = 'volume:dbstate'
        self.profile['runtime']['storage'].update(status='READY', volume_roots=['dbstate'])
        compose = json.loads((self.root / 'compose.yaml').read_text())
        compose['services']['database'] = {'x-foundation-role':'database', 'image':'synthetic-db:fixture',
            'environment':{'DB_USER':'${DB_USER}', 'DB_PASSWORD':'${DB_PASSWORD:?required}'},
            'healthcheck':{'test':['CMD','db-health']}, 'volumes':['dbstate:/data'], 'ports':['127.0.0.1:5433:5432']}
        compose['volumes'] = {'dbstate':{}}
        (self.root / 'compose.yaml').write_text(json.dumps(compose))
        return compose

    def parameterized_db(self):
        compose = self.docker_db()
        self.f['database']['host_port_env_key'] = 'DB_PORT'
        self.profile['runtime']['environment']['optional_env_keys'].append('DB_PORT')
        with (self.root / '.env.example').open('a') as output:
            output.write('DB_PORT=5433\n')
        compose['services']['database']['ports'] = ['127.0.0.1:${DB_PORT:-5433}:5432']
        (self.root / 'compose.yaml').write_text(json.dumps(compose))
        return compose

    def test_explicit_stateless_default(self):
        self.load()
        self.assertEqual(contract.validate(self.root, self.profile), [])
        for section in ('database','background_jobs','authentication'):
            self.assertEqual(self.f[section].get('mode', self.f[section].get('database_mode')), 'none')

    def test_missing_significant_family_rejected(self):
        del self.f['database']
        self.reject('foundation fixed schema')

    def test_unknown_significant_family_rejected(self):
        self.f['guessed_engine'] = 'automatic'
        self.reject('foundation fixed schema')

    def test_application_version_is_independent(self):
        self.load()
        self.assertNotEqual(self.f['identity']['application_version'], (self.root / 'VERSION').read_text().strip())

    def test_manifest_hash_requires_explicit_review(self):
        with (self.root / 'pyproject.toml').open('a') as output:
            output.write('# mutation\n')
        self.reject('manifest hash mismatch')

    def test_identity_version_mismatch(self):
        self.f['identity']['application_version'] = '8.0.0'
        self.reject('application version source mismatch')

    def test_no_dependency_claim_not_implicit(self):
        path = self.root / 'pyproject.toml'
        path.write_text(path.read_text().replace('dependencies = []', 'dependencies = ["synthetic-dependency"]'))
        self.f['toolchain']['manifest_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        self.reject('no-dependency claim')

    def test_missing_frozen_lock(self):
        self.f['toolchain']['lock_policy'] = 'FROZEN_LOCK'
        self.reject('frozen lock missing')

    def test_npm_adapter_not_python_only(self):
        payload = {'name':'project-scaffold','version':'0.0.0','engines':{'node':'>=20'},'dependencies':{},'devDependencies':{}}
        path = self.root / 'package.json'
        path.write_text(json.dumps(payload))
        self.f['identity']['version_source'] = 'package.json'
        self.f['toolchain'].update(language='javascript', runtime='node', runtime_version_range='>=20',
            dependency_manifest_path='package.json', manifest_format='npm', manifest_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        self.load()

    def test_frozen_lock_binding_mismatch(self):
        lock = self.root / 'uv.lock'
        lock.write_text('requires-python=">=3.11"\n[[package]]\nname="project-scaffold"\nversion="0.0.0"\n')
        self.f['toolchain'].update(lockfile_path='uv.lock',lockfile_format='uv',lock_policy='FROZEN_LOCK',
                                  lockfile_sha256=hashlib.sha256(lock.read_bytes()).hexdigest(),lock_binding_manifest_sha256='0'*64)
        self.reject('lock review binding')
        self.f['toolchain']['lock_binding_manifest_sha256'] = self.f['toolchain']['manifest_sha256']
        self.load()
        lock.write_text(lock.read_text() + '# changed\n')
        self.reject('lock hash mismatch')

    def test_database_none_not_silent_engine(self):
        self.f['database']['database_engine'] = 'postgres'
        self.reject('no-DB engine')

    def test_embedded_sqlite_positive_exclusion(self):
        self.embedded()
        self.load()

    def test_embedded_wrong_engine(self):
        self.embedded()
        self.f['database']['database_engine'] = 'postgres'
        self.reject('embedded DB engine')

    def test_data_root_requires_exclusion(self):
        self.embedded()
        self.f['database']['data_root'] = 'retained-private'
        self.f['persistent_data']['database_data_root'] = 'retained-private'
        self.profile['runtime']['storage']['data_roots'] = ['retained-private']
        self.reject('lacks unified source exclusion')

    def test_source_ancestor_not_data_root(self):
        self.embedded()
        self.f['database']['data_root'] = '..'
        self.reject('cannot contain source')

    def test_runtime_storage_matches_foundation(self):
        self.embedded()
        self.profile['runtime']['storage']['data_roots'] = ['data']
        self.reject('storage lists differ')

    def test_database_data_owner_matches(self):
        self.embedded()
        self.f['persistent_data']['database_data_root'] = 'data'
        self.reject('database data owner mismatch')

    def test_container_db_positive_without_execution(self):
        self.docker_db()
        self.load()

    def test_container_db_volume_mismatch(self):
        compose = self.docker_db()
        compose['services']['database']['volumes'] = ['elsewhere:/data']
        (self.root / 'compose.yaml').write_text(json.dumps(compose))
        self.reject('named volume coherence|Compose rendering failed')

    def test_container_db_password_never_literal(self):
        compose = self.docker_db()
        compose['services']['database']['environment']['DB_PASSWORD'] = 'synthetic-forbidden'
        (self.root / 'compose.yaml').write_text(json.dumps(compose))
        self.reject('no literal/default DB password')

    def test_container_db_health_mismatch(self):
        compose = self.docker_db()
        compose['services']['database']['healthcheck']['test'] = ['NONE']
        (self.root / 'compose.yaml').write_text(json.dumps(compose))
        self.reject('DB service health')

    def test_external_db_cannot_keep_local_service(self):
        self.docker_db()
        self.f['database'].update(database_mode='external',compose_service=contract.NA,data_root=contract.NA,listen_port=contract.NA)
        self.f['persistent_data']['database_data_root'] = contract.NA
        self.profile['runtime']['storage'].update(status='NOT APPLICABLE', volume_roots=[])
        self.reject('external DB cannot define')

    def test_database_secret_declaration(self):
        self.docker_db()
        self.profile['runtime']['environment']['secret_env_keys'].remove('DB_PASSWORD')
        self.reject('classified|DB password')

    def test_automatic_down_migration_forbidden(self):
        self.f['migration']['automatic_down_migration'] = True
        self.reject('no automatic down')

    def test_source_behind_must_fail_closed(self):
        self.f['migration']['source_behind_database_fail_closed'] = False
        self.reject('source-behind fails closed')

    def test_required_migration_backup_absent(self):
        self.embedded()
        self.f['migration']['backup_required_before_migration'] = True
        self.reject('migration requires absent backup')

    def test_pending_migration_is_debt(self):
        self.embedded()
        self.f['migration']['applicability'] = 'PENDING'
        self.load()
        self.assertIn('migration applicability pending',contract.validate(self.root,self.profile))

    def backup(self):
        self.f['backup'].update(applicability='APPLICABLE',scope=['source'],root='../private-backups',
                               verify_command='NOT_IMPLEMENTED',restore_command='NOT_IMPLEMENTED',retention='PENDING')

    def test_backup_no_engine_reports_debt(self):
        self.backup()
        self.load()
        self.assertIn('backup restore_command not implemented', contract.validate(self.root,self.profile))

    def test_backup_inside_source_rejected(self):
        self.backup()
        self.f['backup']['root'] = 'backups'
        self.reject('backup root outside source')

    def test_restore_readonly_cannot_hide_mutation(self):
        self.backup()
        self.f['backup']['restore_command'] = 'health'
        self.reject('backup restore_command mutability')

    def test_restore_confirmation_nonwaivable(self):
        self.f['backup']['restore_confirmation_required'] = False
        self.reject('backup integrity/restore safety')

    def test_backup_scope_without_database(self):
        self.backup()
        self.f['backup']['scope'] = ['database']
        self.reject('scope without DB')

    def test_git_exclusion_gap_rejected(self):
        path = self.root / '.gitignore'
        path.write_text(path.read_text().replace('database-data/\n',''))
        self.reject('Git exclusion missing database-data')

    def test_docker_exclusion_gap_rejected(self):
        path = self.root / '.dockerignore'
        path.write_text(path.read_text()+'\n!backups/\n!backups/probe\n')
        self.reject('Docker nested exclusion missing backups')

    def test_exclusion_targets_cannot_drift(self):
        path = self.root / 'source-exclusions.json'
        policy = json.loads(path.read_text())
        policy['rules'][0]['targets'].remove('handoff')
        path.write_text(json.dumps(policy))
        self.reject('all source targets')

    def test_new_consumer_editable_root_lock_version_coherence(self):
        manifest = self.root / 'pyproject.toml'
        manifest.write_text(manifest.read_text().replace('version = "0.0.0"', 'version = "0.1.0"'))
        self.f['identity']['application_version'] = '0.1.0'
        self.f['toolchain']['manifest_sha256'] = hashlib.sha256(manifest.read_bytes()).hexdigest()
        lock = self.root / 'uv.lock'
        dependency = '\n[[package]]\nname="synthetic-dependency"\nversion="7.1.2"\nsource={registry="https://example.invalid"}\n'
        lock.write_text('requires-python=">=3.11"\n[[package]]\nname="project-scaffold"\nversion="0.1.0"\nsource={editable="."}\n' + dependency)
        self.f['toolchain'].update(lockfile_path='uv.lock', lockfile_format='uv', lock_policy='FROZEN_LOCK',
            lockfile_sha256=hashlib.sha256(lock.read_bytes()).hexdigest(),
            lock_binding_manifest_sha256=self.f['toolchain']['manifest_sha256'])
        before = lock.read_bytes()
        contract.consumer_identity(self.load(), new_consumer=True)
        self.assertEqual(before, lock.read_bytes())
        # Reviewed hashes alone cannot turn wrong editable-root metadata into coherence.
        lock.write_text(lock.read_text().replace('version="0.1.0"', 'version="0.0.0"'))
        self.f['toolchain']['lockfile_sha256'] = hashlib.sha256(lock.read_bytes()).hexdigest()
        self.reject('lock project identity mismatch')
        self.assertTrue(lock.read_text().endswith(dependency))

    def test_metadata_all_targets_and_no_cleanup(self):
        policy = json.loads((self.root / 'source-exclusions.json').read_text())
        rule = next(row for row in policy['rules'] if row['path'] == '.DS_Store')
        self.assertEqual(rule['category'], 'os_metadata')
        self.assertEqual(set(rule['targets']), contract.TARGETS)
        for name in ('.DS_Store', 'scripts/.DS_Store', 'nested/deeper/.DS_Store'):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'synthetic metadata')
            self.assertTrue(contract.excluded(name, policy))
            self.assertTrue(contract.ignored(name, (self.root / '.gitignore').read_text()))
            self.assertTrue(contract.ignored(name, (self.root / '.dockerignore').read_text()))
        self.load()
        profile_before = (self.root / 'execution-profile.json').read_bytes()
        before = {str(p.relative_to(self.root)): (p.read_bytes(), p.stat().st_mode)
                  for p in self.root.rglob('*') if p.is_file()}
        result = subprocess.run([str(self.root / 'run.sh'), 'doctor'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        after = {str(p.relative_to(self.root)): (p.read_bytes(), p.stat().st_mode)
                 for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before, after)
        self.assertEqual(profile_before, (self.root / 'execution-profile.json').read_bytes())

    def test_missing_metadata_rule_rejected(self):
        path = self.root / 'source-exclusions.json'
        policy = json.loads(path.read_text())
        policy['rules'] = [row for row in policy['rules'] if row['path'] != '.DS_Store']
        path.write_text(json.dumps(policy))
        self.reject('canonical .DS_Store exclusion missing')

    def test_each_metadata_target_is_required(self):
        path = self.root / 'source-exclusions.json'
        policy = json.loads(path.read_text())
        rule = next(row for row in policy['rules'] if row['path'] == '.DS_Store')
        for target in contract.TARGETS:
            with self.subTest(target=target):
                rule['targets'] = sorted(contract.TARGETS - {target})
                path.write_text(json.dumps(policy))
                self.reject('all source targets')

    def test_metadata_exception_cannot_readmit(self):
        path = self.root / 'source-exclusions.json'
        policy = json.loads(path.read_text())
        for name in ('.DS_Store', 'nested/.DS_Store'):
            policy['source_exceptions'] = ['.env.example', name]
            path.write_text(json.dumps(policy))
            self.assertTrue(contract.excluded(name, policy))
            self.reject('OS metadata source exception forbidden')

    def test_existing_cache_metadata_category_compatible(self):
        path = self.root / 'source-exclusions.json'
        policy = json.loads(path.read_text())
        next(row for row in policy['rules'] if row['path'] == '.DS_Store')['category'] = 'cache'
        path.write_text(json.dumps(policy))
        self.load()

    def test_docker_metadata_recursion_and_late_inclusions_rejected(self):
        path = self.root / '.dockerignore'
        original = path.read_text()
        for invalid in (original.replace('**/.DS_Store', ''), original + '\n!scripts/.DS_Store\n'):
            path.write_text(invalid)
            self.reject('Docker root/recursive .DS_Store patterns')

    def test_worker_without_entry_rejected(self):
        self.f['background_jobs'].update(mode='worker',persistence_dependency='PENDING',retry_idempotency_owner='project')
        self.reject('worker entry required')

    def test_auth_cannot_own_business_authorization(self):
        self.f['authentication']['authorization_owner'] = 'provider'
        self.reject('authorization boundary')

    def test_external_auth_explicit_session(self):
        self.f['authentication'].update(mode='external', integration_class='oidc',session_owner='project')
        self.load()

    def test_logging_redaction_boundary(self):
        self.f['observability']['redaction'] = 'log-everything'
        self.reject('redaction boundary')

    def test_missing_test_class_rejected(self):
        del self.f['testing']['classes']['screenshot_qa']
        self.reject('test classes fixed schema')

    def test_synthetic_cannot_enable_live_network(self):
        self.f['testing']['classes']['unit']['network'] = 'explicit-live'
        self.reject('live network class isolation')

    def test_unbounded_timeout_rejected(self):
        self.f['testing']['classes']['unit']['timeout_seconds'] = 0
        self.reject('bounded test timeout')

    def test_mock_not_live_acceptance(self):
        self.f['testing']['mock_is_live'] = True
        self.reject('test truth')

    def test_license_unknown_reports_pending(self):
        self.f['third_party']['review_status'] = 'PENDING'
        self.load()
        self.assertIn('license review pending', contract.validate(self.root,self.profile))

    def test_bundled_assets_not_reference_only(self):
        self.f['third_party']['bundled_assets'] = ['synthetic-asset']
        self.reject('bundled assets cannot be reference-only')

    def test_missing_operational_doc_rejected(self):
        (self.root / 'INSTALLATION.md').unlink()
        self.reject('missing file INSTALLATION')

    def test_secret_environment_not_inherited_and_timeout_bounded(self):
        with patch.dict(os.environ, {'PRODUCTION_TOKEN':'synthetic-private','HTTPS_PROXY':'synthetic-proxy'}):
            with patch.object(reference_tests.subprocess, 'run') as run:
                run.return_value.returncode = 17
                self.assertEqual(reference_tests.main(),17)
                kwargs = run.call_args.kwargs
                self.assertNotIn('PRODUCTION_TOKEN', kwargs['env'])
                self.assertNotIn('HTTPS_PROXY', kwargs['env'])
                self.assertEqual(kwargs['timeout'], reference_tests.TIMEOUT_SECONDS)
                self.assertTrue(kwargs['env']['PYTHONPATH'].startswith(kwargs['env']['HOME']))
                self.assertFalse(Path(kwargs['env']['HOME']).exists())  # temp state cleaned after child completion

    def test_timeout_is_failure_not_pass(self):
        with patch.object(reference_tests.subprocess,'run',side_effect=subprocess.TimeoutExpired('synthetic',reference_tests.TIMEOUT_SECONDS)):
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(reference_tests.main(),124)

    def test_canonical_test_timeouts_share_a_bounded_policy(self):
        formal = json.loads((self.root / 'test-control-profile.json').read_text())
        classes = self.f['testing']['classes']
        self.assertEqual(reference_tests.TIMEOUT_SECONDS, 360)
        self.assertEqual(formal['timeout_seconds'], reference_tests.TIMEOUT_SECONDS)
        self.assertEqual(classes['unit']['timeout_seconds'], reference_tests.TIMEOUT_SECONDS)
        self.assertEqual(classes['isolated_acceptance']['timeout_seconds'], reference_tests.TIMEOUT_SECONDS)

    def test_reference_guard_denies_external_before_dns(self):
        argv=[sys.executable,'-B','-c',"import test_network_guard,socket;socket.getaddrinfo('example.invalid',443)"]
        result=subprocess.run(argv,env={**os.environ,'PYTHONPATH':str(self.source/'scripts')},capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('deny non-loopback',result.stderr)

    def test_reference_logs_never_use_raw_request(self):
        handler = object.__new__(Handler)
        handler.response_status = 404
        handler.path = '/private?token=synthetic-secret'
        out = io.StringIO()
        with contextlib.redirect_stderr(out):
            handler.log_message('caller-controlled-secret %s', 'synthetic-secret')
        record = json.loads(out.getvalue())
        self.assertEqual(set(record),{'event','request_id','status'})
        self.assertNotIn('synthetic-secret',out.getvalue())
        self.assertTrue(record['request_id'])

    def test_status_unavailable_never_starts_service(self):
        import scaffold_status
        with patch.object(sys,'argv',['status']),patch.object(scaffold_status.urllib.request,'build_opener') as opener:
            opener.return_value.open.side_effect = OSError('synthetic unavailable')
            with contextlib.redirect_stdout(io.StringIO()) as out:
                self.assertEqual(scaffold_status.main(),3)
            self.assertIn('PENDING',out.getvalue())

    def test_container_database_ports_coherent(self):
        compose = self.docker_db()
        compose['services']['database']['ports'] = ['127.0.0.1:9999:5432']
        (self.root / 'compose.yaml').write_text(json.dumps(compose))
        self.reject('DB Compose port coherence')

    @unittest.skipUnless(compose_available(), 'Docker Compose CLI unavailable')
    def test_inactive_database_profile_cannot_pass_from_raw_source(self):
        compose = self.docker_db()
        compose['services']['database']['profiles'] = ['optional']
        (self.root / 'compose.yaml').write_text(json.dumps(compose))
        with patch.dict(os.environ, {'COMPOSE_PROFILES': 'optional'}):
            self.reject('effective DB Compose service missing')

    def test_inactive_database_profile_requires_compose(self):
        compose = self.docker_db()
        compose['services']['database']['profiles'] = ['optional']
        (self.root / 'compose.yaml').write_text(json.dumps(compose))
        with patch.object(project_runner.shutil, 'which', return_value=None):
            with self.assertRaises(project_runner.ComposeUnavailable):
                self.load()

    @unittest.skipUnless(compose_available(), 'Docker Compose CLI unavailable')
    def test_parameterized_host_port_default_and_override(self):
        self.parameterized_db()
        self.load()
        docker = self.profile['runtime']['docker']
        values = project_runner.env_contract(self.root, self.profile['runtime']['environment'])
        for supplied, expected in (('', 5433), ('5434', 5434)):
            with self.subTest(supplied=supplied):
                effective = project_runner.compose_render(self.root, docker, env_values=values,
                    secrets={'DB_PASSWORD'}, override={'DB_PORT': supplied})
                self.assertEqual(effective['name'], 'project-scaffold')
                self.assertEqual(project_runner.rendered_ports(effective['services']['database']),
                                 [('127.0.0.1', expected, 5432)])

    @unittest.skipUnless(compose_available(), 'Docker Compose CLI unavailable')
    def test_parameterized_port_mismatches_fail_closed(self):
        base = self.parameterized_db()
        for defect, binding, expected in (
            ('default', '127.0.0.1:${DB_PORT:-5440}:5432', 'source/default'),
            ('environment', '127.0.0.1:${OTHER_PORT:-5433}:5432', 'source/default'),
            ('target', '127.0.0.1:${DB_PORT:-5433}:5434', 'source/default'),
        ):
            with self.subTest(defect=defect):
                compose = copy.deepcopy(base)
                compose['services']['database']['ports'] = [binding]
                (self.root / 'compose.yaml').write_text(json.dumps(compose))
                self.reject(expected)
        compose = copy.deepcopy(base)
        compose['services']['database']['ports'].append('127.0.0.1:5440:5432')
        (self.root / 'compose.yaml').write_text(json.dumps(compose))
        self.reject('source/default')
        (self.root / 'compose.yaml').write_text(json.dumps(base))
        self.profile['runtime']['environment']['optional_env_keys'].remove('DB_PORT')
        self.reject('example inventory differs')

    def test_parameterized_source_cannot_claim_fixed_profile(self):
        self.parameterized_db()
        del self.f['database']['host_port_env_key']
        self.reject('DB Compose port coherence')

    def test_parameterized_port_render_failure_is_not_a_pass(self):
        self.parameterized_db()
        with patch.object(project_runner.subprocess, 'run', side_effect=[
            subprocess.CompletedProcess([], 0, 'Docker Compose version test', ''),
            subprocess.CompletedProcess([], 1, '', '')]):
            self.reject('Compose rendering failed')

    def test_home_relative_database_bind_fails_before_machine_resolution(self):
        compose = self.docker_db()
        for source in ('~/db', '~otheruser/db', '${DATA_ROOT:-~/db}'):
            with self.subTest(source=source):
                changed = copy.deepcopy(compose)
                changed['services']['database']['volumes'].append(source + ':/cache')
                (self.root / 'compose.yaml').write_text(json.dumps(changed))
                for home in ('machine-a', 'machine-b'):
                    with patch.dict(os.environ, {'HOME': str(Path(self.temp.name) / home)}):
                        self.reject('HOME-relative Compose path')

    @unittest.skipUnless(compose_available(), 'Docker Compose CLI unavailable')
    def test_yaml_home_relative_bind_fails_before_machine_resolution(self):
        self.parameterized_db()
        (self.root / 'compose.yaml').write_text('''name: project-scaffold
services:
  scaffold:
    image: python:3.11-slim
  database:
    image: postgres:17-alpine
    volumes:
      - ~/db:/data
''')
        self.reject('HOME-relative Compose path')

    @unittest.skipUnless(compose_available(), 'Docker Compose CLI unavailable')
    def test_project_relative_database_bind_is_supported(self):
        compose = self.docker_db()
        self.f['database']['data_root'] = './data'
        self.f['persistent_data']['database_data_root'] = './data'
        self.profile['runtime']['storage'].update(data_roots=['./data'], volume_roots=[])
        compose['services']['database']['volumes'] = ['./data:/data']
        (self.root / 'compose.yaml').write_text(json.dumps(compose))
        self.load()
        absolute = str(self.root / 'data')
        self.f['database']['data_root'] = absolute
        self.f['persistent_data']['database_data_root'] = absolute
        self.profile['runtime']['storage']['data_roots'] = [absolute]
        compose['services']['database']['volumes'] = [absolute + ':/data']
        (self.root / 'compose.yaml').write_text(json.dumps(compose))
        self.load()

    @unittest.skipUnless(compose_available(), 'Docker Compose CLI unavailable')
    def test_project_relative_yaml_database_bind_is_supported(self):
        self.docker_db()
        self.f['database']['data_root'] = './data'
        self.f['persistent_data']['database_data_root'] = './data'
        self.profile['runtime']['storage'].update(data_roots=['./data'], volume_roots=[])
        (self.root / 'compose.yaml').write_text('''name: project-scaffold
services:
  scaffold:
    image: python:3.11-slim
    ports: ["127.0.0.1:8080:8080"]
    environment:
      APP_CONTAINER_LISTEN_HOST: "0.0.0.0"
      APP_CONTAINER_PORT: "8080"
      APP_HEALTH_PATH: "/health"
    healthcheck:
      test: ["CMD", "python3", "-c", "print('/health')"]
  database:
    image: postgres:17-alpine
    x-foundation-role: database
    ports: ["127.0.0.1:5433:5432"]
    environment:
      DB_USER: "${DB_USER}"
      DB_PASSWORD: "${DB_PASSWORD:?required}"
    healthcheck:
      test: ["CMD", "db-health"]
    volumes: ["./data:/data"]
''')
        self.load()

    def test_fixed_json_with_unresolved_interpolation_requires_compose(self):
        compose = self.docker_db()
        compose['services']['database']['environment']['POSTGRES_DB'] = '${UNDECLARED_VALUE}'
        (self.root / 'compose.yaml').write_text(json.dumps(compose))
        with patch.object(project_runner.shutil, 'which', return_value=None):
            with self.assertRaises(project_runner.ComposeUnavailable):
                self.load()

    @unittest.skipUnless(compose_available(), 'Docker Compose CLI unavailable')
    def test_fixed_json_undefined_malformed_and_private_env_fail(self):
        original = self.docker_db()
        (self.root / '.env').write_text('UNDECLARED_VALUE=hidden-local-value\n')
        for value, expected in (('${UNDECLARED_VALUE}', 'diagnostics'),
                                ('${UNDECLARED_VALUE', 'rendering failed')):
            with self.subTest(value=value):
                compose = copy.deepcopy(original)
                compose['services']['database']['environment']['POSTGRES_DB'] = value
                (self.root / 'compose.yaml').write_text(json.dumps(compose))
                with patch.dict(os.environ, {'UNDECLARED_VALUE': 'hidden-caller-value'}):
                    self.reject(expected)

    @unittest.skipUnless(compose_available(), 'Docker Compose CLI unavailable')
    def test_json_and_yaml_undefined_interpolation_classify_equally(self):
        self.docker_db()
        docker = self.profile['runtime']['docker']
        values = project_runner.env_contract(self.root, self.profile['runtime']['environment'])
        for source in (
            json.dumps({'name': 'project-scaffold', 'services': {'scaffold': {
                'image': 'alpine', 'environment': {'POSTGRES_DB': '${UNDECLARED_VALUE}'}}}}),
            'name: project-scaffold\nservices:\n  scaffold:\n    image: alpine\n'
            '    environment:\n      POSTGRES_DB: "${UNDECLARED_VALUE}"\n',
        ):
            with self.subTest(serialization=source[:1]):
                (self.root / 'compose.yaml').write_text(source)
                with self.assertRaisesRegex(ValueError, 'diagnostics'):
                    project_runner.compose_render(self.root, docker, env_values=values, secrets={'DB_PASSWORD'})

    @unittest.skipUnless(compose_available(), 'Docker Compose CLI unavailable')
    def test_undefined_and_malformed_interpolation_fail_closed(self):
        original = self.parameterized_db()
        for value, expected in (('${UNDECLARED_VALUE}', 'diagnostics'),
                                ('${UNDECLARED_VALUE', 'rendering failed')):
            with self.subTest(value=value):
                compose = copy.deepcopy(original)
                compose['services']['database']['environment']['POSTGRES_DB'] = value
                (self.root / 'compose.yaml').write_text(json.dumps(compose))
                self.reject(expected)

    @unittest.skipUnless(compose_available(), 'Docker Compose CLI unavailable')
    def test_missing_required_database_value_is_not_accepted(self):
        compose = self.parameterized_db()
        compose['services']['database']['environment']['POSTGRES_DB'] = '${MISSING_DB_NAME}'
        (self.root / 'compose.yaml').write_text(json.dumps(compose))
        self.reject('diagnostics')

    @unittest.skipUnless(compose_available(), 'Docker Compose CLI unavailable')
    def test_private_dotenv_cannot_satisfy_undeclared_interpolation(self):
        compose = self.parameterized_db()
        (self.root / '.env').write_text('UNDECLARED_VALUE=hidden-local-value\n')
        compose['services']['database']['environment']['POSTGRES_DB'] = '${UNDECLARED_VALUE}'
        (self.root / 'compose.yaml').write_text(json.dumps(compose))
        self.reject('diagnostics')

    @unittest.skipUnless(compose_available(), 'Docker Compose CLI unavailable')
    def test_caller_environment_cannot_satisfy_undeclared_interpolation(self):
        compose = self.parameterized_db()
        compose['services']['database']['environment']['POSTGRES_DB'] = '${UNDECLARED_VALUE}'
        (self.root / 'compose.yaml').write_text(json.dumps(compose))
        with patch.dict(os.environ, {'UNDECLARED_VALUE': 'hidden-caller-value'}):
            self.reject('diagnostics')

    @unittest.skipUnless(compose_available(), 'Docker Compose CLI unavailable')
    def test_tool_environment_is_not_implicit_compose_authority(self):
        compose = self.parameterized_db()
        for variable in ('HOME', 'CI_RANDOM_DB_NAME'):
            with self.subTest(variable=variable):
                changed = copy.deepcopy(compose)
                changed['services']['database']['environment']['POSTGRES_DB'] = '${' + variable + '}'
                (self.root / 'compose.yaml').write_text(json.dumps(changed))
                with patch.dict(os.environ, {variable: 'machine-specific-value'}):
                    self.reject('Compose tool environment is not interpolation authority' if variable == 'HOME'
                                else 'diagnostics')

    def test_fixed_port_source_also_rejects_implicit_tool_input(self):
        compose = self.docker_db()
        compose['services']['database']['environment']['POSTGRES_DB'] = '${HOME}'
        (self.root / 'compose.yaml').write_text(json.dumps(compose))
        self.reject('Compose tool environment is not interpolation authority')

    def test_escaped_tool_name_is_literal_not_interpolation(self):
        compose = self.docker_db()
        compose['services']['database']['environment']['LITERAL_NAME'] = '$$HOME'
        (self.root / 'compose.yaml').write_text(json.dumps(compose))
        self.load()
        compose['services']['database']['environment']['LITERAL_NAME'] = '$$${HOME}'
        (self.root / 'compose.yaml').write_text(json.dumps(compose))
        self.reject('Compose tool environment is not interpolation authority')

    @unittest.skipUnless(compose_available(), 'Docker Compose CLI unavailable')
    def test_declared_home_cannot_become_compose_tool_input(self):
        compose = self.parameterized_db()
        self.profile['runtime']['environment']['optional_env_keys'].append('HOME')
        with (self.root / '.env.example').open('a') as output:
            output.write('HOME=declared-compose-value\n')
        compose['services']['database']['environment']['POSTGRES_DB'] = '${HOME}'
        (self.root / 'compose.yaml').write_text(json.dumps(compose))
        self.reject('Compose tool environment is not interpolation authority')

    @unittest.skipUnless(compose_available(), 'Docker Compose CLI unavailable')
    def test_declared_values_override_caller_environment(self):
        compose = self.parameterized_db()
        compose['services']['database']['environment']['DB_USER'] = '${DB_USER}'
        (self.root / 'compose.yaml').write_text(json.dumps(compose))
        with patch.dict(os.environ, {'DB_USER': 'wrong-caller-value'}):
            self.load()
            effective = project_runner.compose_render(self.root, self.profile['runtime']['docker'],
                env_values=project_runner.env_contract(self.root, self.profile['runtime']['environment']),
                secrets={'DB_PASSWORD'})
        self.assertEqual(effective['services']['database']['environment']['DB_USER'], 'synthetic')

    @unittest.skipUnless(compose_available(), 'Docker Compose CLI unavailable')
    def test_different_tool_homes_produce_same_verified_model(self):
        self.parameterized_db()
        original_plugin = Path.home() / '.docker' / 'cli-plugins' / 'docker-compose'
        models = []
        for name in ('machine-a', 'machine-b'):
            home = Path(self.temp.name) / name
            home.mkdir()
            if original_plugin.is_file():
                plugin = home / '.docker' / 'cli-plugins' / 'docker-compose'
                plugin.parent.mkdir(parents=True)
                plugin.symlink_to(original_plugin.resolve())
            with patch.dict(os.environ, {'HOME': str(home)}):
                self.load()
                models.append(project_runner.compose_render(
                    self.root, self.profile['runtime']['docker'],
                    env_values=project_runner.env_contract(self.root, self.profile['runtime']['environment']),
                    secrets={'DB_PASSWORD'}))
        self.assertEqual(models[0], models[1])

    @unittest.skipUnless(compose_available(), 'Docker Compose CLI unavailable')
    def test_explicit_service_env_file_is_not_a_verified_input(self):
        compose = self.parameterized_db()
        for service_name in ('database', 'scaffold'):
            for file_name in ('.env', '/dev/null', 'missing-local.env'):
                with self.subTest(service=service_name, env_file=file_name):
                    changed = copy.deepcopy(compose)
                    changed['services'][service_name]['env_file'] = file_name
                    (self.root / 'compose.yaml').write_text(json.dumps(changed))
                    self.reject('Compose service env_file')
        changed = copy.deepcopy(compose)
        changed['services']['database']['env_file'] = '.env'
        changed['services']['database']['command'] = ['db-server', '--from-env-file']
        (self.root / 'compose.yaml').write_text(json.dumps(changed))
        self.reject('Compose service env_file')

    @unittest.skipUnless(compose_available(), 'Docker Compose CLI unavailable')
    def test_yaml_source_rejects_tool_interpolation_and_env_file(self):
        self.parameterized_db()
        base = '''name: project-scaffold
services:
  scaffold:
    image: python:3.11-slim
  database:
    image: postgres:17-alpine
    x-foundation-role: database
    environment:
      POSTGRES_DB: "${HOME}"
'''
        (self.root / 'compose.yaml').write_text(base)
        self.reject('Compose tool environment is not interpolation authority')
        (self.root / 'compose.yaml').write_text(base.replace('    environment:\n      POSTGRES_DB: "${HOME}"',
                                                             '    env_file: /dev/null'))
        self.reject('Compose service env_file')

    @unittest.skipUnless(compose_available(), 'Docker Compose CLI unavailable')
    def test_legitimate_unrelated_default_interpolation_is_accepted(self):
        compose = self.parameterized_db()
        compose['services']['database']['environment']['OPTIONAL_MODE'] = '${OPTIONAL_MODE-default}'
        (self.root / 'compose.yaml').write_text(json.dumps(compose))
        self.load()

    @unittest.skipUnless(compose_available(), 'Docker Compose CLI unavailable')
    def test_host_port_override_cannot_change_database_environment(self):
        compose = self.parameterized_db()
        compose['services']['database']['environment']['POSTGRES_DB'] = '${DB_PORT:-5433}'
        (self.root / 'compose.yaml').write_text(json.dumps(compose))
        self.reject('foundation identity drift')

    @unittest.skipUnless(compose_available(), 'Docker Compose CLI unavailable')
    def test_host_port_override_cannot_change_database_command(self):
        compose = self.parameterized_db()
        compose['services']['database']['command'] = ['db-server', '--mode=${DB_PORT:-5433}']
        (self.root / 'compose.yaml').write_text(json.dumps(compose))
        self.reject('foundation identity drift')

    @unittest.skipUnless(compose_available(), 'Docker Compose CLI unavailable')
    def test_host_port_override_cannot_change_database_service_identity(self):
        compose = self.parameterized_db()
        compose['services']['database']['hostname'] = 'db-${DB_PORT:-5433}'
        (self.root / 'compose.yaml').write_text(json.dumps(compose))
        self.reject('foundation identity drift')

    def test_compose_unavailable_is_pending_not_pass(self):
        self.parameterized_db()
        with patch.object(project_runner.shutil, 'which', return_value=None):
            with self.assertRaisesRegex(project_runner.ComposeUnavailable, 'verification unavailable'):
                self.load()

    @unittest.skipUnless(compose_available(), 'Docker Compose CLI unavailable')
    def test_parameterized_port_example_mismatch_fails(self):
        self.parameterized_db()
        path = self.root / '.env.example'
        path.write_text(path.read_text().replace('DB_PORT=5433', 'DB_PORT=5440'))
        self.reject('example/default')

    @unittest.skipUnless(compose_available(), 'Docker Compose CLI unavailable')
    def test_operationhub_style_port_is_configurable_without_changing_target(self):
        compose = self.parameterized_db()
        self.f['database']['host_port'] = 15432
        self.f['database']['host_port_env_key'] = 'OPERATION_HUB_DB_PORT'
        keys = self.profile['runtime']['environment']['optional_env_keys']
        keys[keys.index('DB_PORT')] = 'OPERATION_HUB_DB_PORT'
        example = self.root / '.env.example'
        example.write_text(example.read_text().replace('DB_PORT=5433', 'OPERATION_HUB_DB_PORT=15432'))
        compose['services']['database']['ports'] = ['127.0.0.1:${OPERATION_HUB_DB_PORT:-15432}:5432']
        (self.root / 'compose.yaml').write_text(json.dumps(compose))
        self.load()
        docker = self.profile['runtime']['docker']
        values = project_runner.env_contract(self.root, self.profile['runtime']['environment'])
        for supplied, expected in (('', 15432), ('15433', 15433)):
            effective = project_runner.compose_render(self.root, docker, env_values=values,
                secrets={'DB_PASSWORD'}, override={'OPERATION_HUB_DB_PORT': supplied})
            self.assertEqual(project_runner.rendered_ports(effective['services']['database']),
                             [('127.0.0.1', expected, 5432)])

    @unittest.skipUnless(compose_available(), 'Docker Compose CLI unavailable')
    def test_parameterized_database_in_ordinary_yaml(self):
        self.parameterized_db()
        self.profile['runtime']['docker']['compose_project_name'] = 'source'
        (self.root / 'compose.yaml').write_text('''services:
  scaffold:
    image: python:3.11-slim
    ports:
      - "${APP_BIND_HOST:-127.0.0.1}:${APP_HOST_PORT:-8080}:${APP_CONTAINER_PORT:-8080}"
    environment:
      APP_CONTAINER_LISTEN_HOST: "${APP_CONTAINER_LISTEN_HOST:-0.0.0.0}"
      APP_CONTAINER_PORT: "${APP_CONTAINER_PORT:-8080}"
      APP_HEALTH_PATH: "${APP_HEALTH_PATH:-/health}"
    healthcheck:
      test: ["CMD", "python3", "-c", "print('/health')"]
  database:
    image: postgres:17-alpine
    x-foundation-role: database
    ports:
      - "127.0.0.1:${DB_PORT:-5433}:5432"
    environment:
      DB_USER: "${DB_USER}"
      DB_PASSWORD: "${DB_PASSWORD:?required}"
    healthcheck:
      test: ["CMD", "db-health"]
    volumes:
      - dbstate:/data
volumes:
  dbstate: {}
''')
        self.load()

    def test_unpublished_database_port_supported(self):
        compose = self.docker_db()
        self.f['database']['host_port'] = contract.NA
        del compose['services']['database']['ports']
        (self.root / 'compose.yaml').write_text(json.dumps(compose))
        self.load()

    def test_pending_license_rows_never_approved(self):
        self.f['third_party']['review_status'] = 'APPROVED'
        self.reject('license row cannot be approved')

    def test_safe_example_must_be_git_source_exception(self):
        path = self.root / '.gitignore'
        path.write_text(path.read_text().replace('!.env.example', ''))
        self.reject('safe environment example must not be Git excluded')

    def test_guard_denies_external_datagram(self):
        argv=[sys.executable,'-B','-c', "import test_network_guard,socket;socket.socket(socket.AF_INET,socket.SOCK_DGRAM).sendto(b'fixture',('192.0.2.1',9))"]
        result=subprocess.run(argv,env={**os.environ,'PYTHONPATH':str(self.source/'scripts')},capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('deny non-loopback',result.stderr)

    def test_nested_secret_and_cache_exclusions(self):
        policy = json.loads((self.root / 'source-exclusions.json').read_text())
        for name in ('nested/.env', 'scripts/__pycache__/module.pyc', 'nested/node_modules/pkg/file', 'nested/backups/private'):
            self.assertTrue(contract.excluded(name, policy), name)
            self.assertTrue(contract.ignored(name, (self.root / '.gitignore').read_text()), name)
            self.assertTrue(contract.ignored(name, (self.root / '.dockerignore').read_text()), name)
        self.assertFalse(contract.excluded('.env.example', policy))

    def test_new_safety_rules_nonwaivable(self):
        registry = json.loads((self.root/'POLICY_RULES.json').read_text())
        for rid in ('DEV-FOUNDATION','REL-DATA-CONTRACT','SEC-FOUNDATION','TEST-CLASSES'):
            self.assertIn(rid,check_standard.CORE)
            self.assertFalse(registry['rules'][rid]['waivable'])


if __name__ == '__main__':
    unittest.main()
