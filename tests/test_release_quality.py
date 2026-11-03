import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
def module(name):
    spec=importlib.util.spec_from_file_location('quality_'+name,ROOT/'scripts'/f'{name}.py')
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result
v=module('validate_repo');s=module('sdlc');installer=module('install');demo=module('demo')

class SchemaRegressions(unittest.TestCase):
    def copy(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        root=Path(temp.name)/'repo';shutil.copytree(ROOT,root,ignore=shutil.ignore_patterns('.git','__pycache__'))
        return root
    def test_invalid_ui_yaml_is_rejected(self):
        root=self.copy();(root/'agents/openai.yaml').write_text('invalid: [ $ai-native-sdlc-skills')
        self.assertTrue(any('interface' in e for e in v.validate(root)))
    def test_duplicate_ui_keys_are_rejected(self):
        with self.assertRaises(ValueError):v.ui_metadata('interface:\n  display_name: "A"\n  display_name: "B"')
    def test_malformed_frontmatter_string_is_rejected(self):
        with self.assertRaises(ValueError):v.frontmatter('---\nname: example\ndescription: "broken\n---\n')
    def test_missing_eval_prompt_is_rejected(self):
        root=self.copy();p=root/'evals/cases.json';cases=json.loads(p.read_text());cases[0].pop('prompt');p.write_text(json.dumps(cases))
        self.assertTrue(any('prompt' in e for e in v.validate(root)))
    def test_empty_eval_rubric_is_rejected(self):
        root=self.copy();p=root/'evals/cases.json';cases=json.loads(p.read_text());cases[0]['rubric']=[''];p.write_text(json.dumps(cases))
        self.assertTrue(any('rubric' in e for e in v.validate(root)))
    def test_unknown_eval_input_is_rejected(self):
        root=self.copy();p=root/'evals/cases.json';cases=json.loads(p.read_text());cases[0]['input']='missing.md';p.write_text(json.dumps(cases))
        self.assertTrue(any('Missing local' in e for e in v.validate(root)))
    def test_links_cannot_escape_repository(self):
        root=self.copy();(root/'outside.md').write_text('[outside](../README.md)')
        self.assertTrue(any('escapes repository' in e for e in v.validate(root)))
    def test_absent_catalog_is_reported_without_traceback(self):
        root=self.copy();(root/'evals/cases.json').unlink()
        self.assertTrue(any('Evaluation catalog' in e for e in v.validate(root)))

class InstallerRegressions(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.project=Path(self.temp.name)/'project';self.project.mkdir()
    def test_router_omits_repository_only_tools(self):
        installer.install(self.project,'codex',installer.NAME,True)
        scripts=self.project/'.agents/skills'/installer.NAME/'scripts'
        self.assertEqual({p.name for p in scripts.iterdir()},{'sdlc.py','install.py'})
    def test_stage_copy_failure_exposes_no_installed_skills(self):
        with patch.object(installer.shutil,'copy2',side_effect=OSError('synthetic copy failure')):
            with self.assertRaises(OSError):installer.install(self.project,'codex',apply=True)
        base=self.project/'.agents/skills'
        self.assertEqual(list(base.iterdir()),[])
    def test_publish_failure_rolls_back_owned_new_directories(self):
        original=Path.rename
        def fail_second(path,target):
            if path.name=='sdlc-plan':raise OSError('synthetic rename failure')
            return original(path,target)
        with patch.object(Path,'rename',fail_second):
            with self.assertRaises(OSError):installer.install(self.project,'codex',apply=True)
        self.assertEqual(list((self.project/'.agents/skills').iterdir()),[])

class EvidenceRegressions(unittest.TestCase):
    def test_empty_accepted_document_cannot_pass_structure(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)/'run';s.init_run(root,'Example','DEMO-001','Reviewer')
            (root/'intent.md').write_text('Status: ACCEPTED\n')
            s.snapshot(root,'plan');data=s.load_run(root)
            data['stages']['plan'].update(status='accepted',evidence=['synthetic-evidence'],decision={'owner':'Reviewer','reference':'synthetic/decision','timestamp':'2026-11-03T11:00:00+11:00'})
            s.save_run(root,data);result=s.check_run(root,'plan',True)
            self.assertFalse(result['valid']);self.assertTrue(any('missing or empty section' in x for x in result['findings']))
    def test_demo_covers_wrong_expectation_fix_and_stale_evidence(self):
        result=demo.run_demo()
        self.assertTrue(result['demo_verified']);self.assertTrue(result['generated_test_passed'])
        self.assertEqual(result['original_acceptance']['failed'],4);self.assertEqual(result['corrected_acceptance']['passed'],7)
        self.assertTrue(result['lineage']['before_valid']);self.assertFalse(result['lineage']['after_valid'])
    def test_demo_keeps_requested_run(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)/'run';demo.run_demo(root)
            self.assertTrue((root/'run.json').is_file())
            with self.assertRaises(FileExistsError):demo.run_demo(root)

if __name__=='__main__':unittest.main()
