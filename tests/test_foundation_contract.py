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
        self.reject('named volume coherence')

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
                self.assertEqual(kwargs['timeout'],180)
                self.assertTrue(kwargs['env']['PYTHONPATH'].startswith(kwargs['env']['HOME']))
                self.assertFalse(Path(kwargs['env']['HOME']).exists())  # temp state cleaned after child completion

    def test_timeout_is_failure_not_pass(self):
        with patch.object(reference_tests.subprocess,'run',side_effect=subprocess.TimeoutExpired('synthetic',180)):
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(reference_tests.main(),124)

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
