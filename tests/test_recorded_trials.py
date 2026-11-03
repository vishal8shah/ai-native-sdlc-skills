import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(name):
    spec=importlib.util.spec_from_file_location('packet_'+name,ROOT/'scripts'/f'{name}.py')
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
trials=load('trials');worked=load('worked_example');s=load('sdlc')

class TrialPacketTests(unittest.TestCase):
    def copy(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);root=Path(temp.name)/'repo'
        shutil.copytree(ROOT,root,ignore=shutil.ignore_patterns('.git','__pycache__'));return root
    def test_all_seven_captured_trials_match_current_source(self):
        result=trials.verify(require_current=True);self.assertTrue(result['valid']);self.assertEqual(len(result['trials']),7)
    def test_changed_response_is_detected(self):
        root=self.copy();p=root/'evals/recorded/DEMO-301/response.md';p.write_text(p.read_text(encoding='utf-8')+'\nEdited response.\n', encoding='utf-8')
        self.assertTrue(any('Changed response' in x for x in trials.verify(root)['findings']))
    def test_missing_model_disclosure_is_detected(self):
        root=self.copy();p=root/'evals/recorded/DEMO-301/record.json';item=json.loads(p.read_text(encoding='utf-8'));item['provenance'].pop('model_deployment_identifier');p.write_text(json.dumps(item), encoding='utf-8')
        self.assertFalse(trials.verify(root)['valid'])
    def test_changed_skill_requires_new_trial_when_requested(self):
        root=self.copy();p=root/'skills/sdlc-build/SKILL.md';p.write_text(p.read_text(encoding='utf-8')+'\nChanged instruction.\n', encoding='utf-8')
        self.assertTrue(trials.verify(root)['valid']);self.assertFalse(trials.verify(root,True)['valid'])
    def test_replay_prompt_omits_recorded_response(self):
        text=trials.prompt('DEMO-301');self.assertTrue(text.startswith('$sdlc-build\n'))
        self.assertNotIn('Ran 4 tests',text);self.assertNotIn('/workspace/projects/',text)
    def test_boolean_schema_version_is_rejected(self):
        root=self.copy();p=root/'evals/recorded/DEMO-301/record.json';item=json.loads(p.read_text(encoding='utf-8'));item['schema_version']=True;p.write_text(json.dumps(item), encoding='utf-8')
        self.assertFalse(trials.verify(root)['valid'])

class WorkedPacketTests(unittest.TestCase):
    def test_six_stage_worked_example_runs_actual_tests_and_binds_files(self):
        with tempfile.TemporaryDirectory() as t:
            folder=Path(t)/'run';result=worked.build_example(folder)
            self.assertTrue(result['valid']);self.assertEqual(result['actual_test_exit_code'],0)
            self.assertEqual(result['record_mode'],'synthetic');self.assertEqual(result['evidence_summary']['local_files_verified'],6)
            self.assertEqual(result['evidence_summary']['local_file_references_verified'],36)
            self.assertIn('Ran 4 tests',(folder/'evidence/unittest.txt').read_text(encoding='utf-8'))
            (folder/'implementation/request_validation.py').write_text('Changed implementation.\n', encoding='utf-8')
            self.assertFalse(s.check_run(folder,require_accepted=True)['valid'])
    def test_skipped_application_suite_cannot_produce_accepted_packet(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as t:
            repo=Path(t)/'repo';shutil.copytree(ROOT,repo,ignore=shutil.ignore_patterns('.git','__pycache__'))
            p=repo/'examples/worked-change/blueprint/test_request_validation.py'
            p.write_text(p.read_text(encoding='utf-8').replace('class RequestIsValidTests','@unittest.skip("synthetic unavailable environment")\nclass RequestIsValidTests'), encoding='utf-8')
            output=Path(t)/'run'
            with patch.object(worked,'ROOT',repo):
                with self.assertRaises(ValueError):worked.build_example(output)
            data=s.load_run(output)
            self.assertTrue(all(x['status']=='draft' for x in data['stages'].values()))
            report=json.loads((output/'evidence/test-report.json').read_text(encoding='utf-8'))
            self.assertEqual(report['skipped'],4);self.assertFalse(report['verified'])
    def test_worked_example_refuses_existing_output(self):
        with tempfile.TemporaryDirectory() as t:
            folder=Path(t)/'run';folder.mkdir()
            with self.assertRaises(FileExistsError):worked.build_example(folder)
