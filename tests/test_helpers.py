import importlib.util
import json
import math
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def module(name):
 spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/f'{name}.py')
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
s=module('sdlc');installer=module('install');validator=module('validate_repo')

class RunTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
  self.path=Path(self.temp.name)/'run'
  s.init_run(self.path,'Example','DEMO-001','Reviewer')
 def read(self):return json.loads((self.path/'run.json').read_text())
 def write(self,data):(self.path/'run.json').write_text(json.dumps(data))
 def complete(self,stage):
  (self.path/s.ARTIFACTS[stage]).write_text(f'# {stage}\nStatus: ACCEPTED\nObserved evidence for synthetic test.\n')
  s.snapshot(self.path,stage)
  data=self.read();data['stages'][stage].update(status='accepted',evidence=['synthetic-test-evidence'],decision={'owner':'Reviewer','reference':'external/decision/1','timestamp':'2026-11-03T10:00:00+11:00'});self.write(data)
 def test_drafts_are_structurally_valid(self):self.assertTrue(s.check_run(self.path)['valid'])
 def test_drafts_are_not_accepted(self):self.assertFalse(s.check_run(self.path,require_accepted=True)['valid'])
 def test_init_refuses_overwrite(self):
  before=(self.path/'run.json').read_bytes()
  with self.assertRaises(FileExistsError):s.init_run(self.path,'Other','OTHER','Other')
  self.assertEqual(before,(self.path/'run.json').read_bytes())
 def test_acceptance_requires_actual_decision_metadata(self):
  self.complete('plan');d=self.read();d['stages']['plan']['decision']=None;self.write(d)
  self.assertFalse(s.check_run(self.path,'plan')['valid'])
 def test_complete_plan_passes_local_checks(self):
  self.complete('plan');self.assertTrue(s.check_run(self.path,'plan',True)['valid'])
 def test_changed_artifact_fails(self):
  self.complete('plan');(self.path/'intent.md').write_text('# New\nStatus: ACCEPTED\n')
  self.assertFalse(s.check_run(self.path,'plan')['valid'])
 def test_upstream_change_invalidates_downstream(self):
  self.complete('plan');self.complete('design');(self.path/'intent.md').write_text('# Edited\nStatus: ACCEPTED\n')
  self.assertTrue(any('upstream plan changed' in f for f in s.check_run(self.path,'design')['findings']))
 def test_accepted_record_cannot_be_resnapshotted(self):
  self.complete('plan')
  with self.assertRaises(s.ValidationError):s.snapshot(self.path,'plan')
 def test_snapshot_clears_old_decision(self):
  self.complete('plan');d=self.read();d['stages']['plan']['status']='draft';self.write(d)
  s.snapshot(self.path,'plan');self.assertIsNone(self.read()['stages']['plan']['decision'])
 def test_mismatched_status_fails(self):
  self.complete('plan');(self.path/'intent.md').write_text('# Example\nStatus: DRAFT\n')
  d=self.read();d['stages']['plan']['artifact_sha256']=s.digest(self.path/'intent.md');self.write(d)
  self.assertTrue(any('statuses disagree' in f for f in s.check_run(self.path,'plan')['findings']))
 def test_placeholders_fail_review(self):
  s.snapshot(self.path,'plan');d=self.read();d['stages']['plan']['status']='ready_for_review';self.write(d)
  self.assertFalse(s.check_run(self.path,'plan')['valid'])
 def test_evidence_is_required(self):
  self.complete('plan');d=self.read();d['stages']['plan']['evidence']=[];self.write(d)
  self.assertFalse(s.check_run(self.path,'plan')['valid'])
 def test_naive_timestamp_fails(self):
  self.assertFalse(s.decision_valid({'owner':'Reviewer','reference':'ID','timestamp':'2026-11-03T10:00:00'}))
 def test_unknown_stage_and_path_traversal_fail(self):
  with self.assertRaises(s.ValidationError):s.snapshot(self.path,'unknown')
  with self.assertRaises(s.ValidationError):s.confined(self.path,'../secret')
  with self.assertRaises(s.ValidationError):s.confined(self.path,'C:\\secret')
 def test_artifact_symlink_rejected(self):
  target=self.path/'intent.md';target.unlink();outside=Path(self.temp.name)/'outside.md';outside.write_text('outside')
  try:target.symlink_to(outside)
  except (OSError,NotImplementedError):self.skipTest('Symlinks unavailable')
  with self.assertRaises(s.ValidationError):s.load_run(self.path)

class MeasurementTests(unittest.TestCase):
 def test_synthetic_example_calculation(self):
  r=s.measure(ROOT/'examples/pilot-measurements.csv',140,1,10)
  self.assertEqual(r['pairs'],5);self.assertAlmostEqual(r['median_elapsed_reduction_pct'],30)
  self.assertEqual(r['staff_hours_saved'],2.5);self.assertEqual(r['net_capacity_value_aud'],200)
 def csv(self,row):
  t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);p=Path(t.name)/'input.csv'
  p.write_text(','.join(s.MEASURES)+'\n'+row+'\n');return p
 def test_incomplete_row_rejected(self):
  with self.assertRaises(s.ValidationError):s.measure(self.csv('10,,120,90,0,0,0,0'),140)
 def test_zero_elapsed_rejected(self):
  with self.assertRaises(s.ValidationError):s.measure(self.csv('0,10,120,90,0,0,0,0'),140)
 def test_nonfinite_rejected(self):
  for value in ('nan','inf','-1'):
   with self.subTest(value=value),self.assertRaises(s.ValidationError):s.measure(self.csv(f'10,{value},120,90,0,0,0,0'),140)
 def test_fractional_counts_rejected(self):
  with self.assertRaises(s.ValidationError):s.measure(self.csv('10,8,120,90,0.5,0,0,0'),140)
 def test_negative_savings_preserved(self):
  r=s.measure(self.csv('10,20,60,120,0,1,0,1'),140)
  self.assertEqual(r['median_elapsed_reduction_pct'],-100);self.assertEqual(r['net_capacity_value_aud'],-140)
 def test_nonfinite_costs_rejected(self):
  with self.assertRaises(s.ValidationError):s.measure(ROOT/'examples/pilot-measurements.csv',math.inf)

class InstallTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.project=Path(self.temp.name)/'project';self.project.mkdir()
 def test_dry_run_does_not_write(self):
  result=installer.install(self.project,'claude');self.assertFalse(result['applied']);self.assertFalse((self.project/'.claude').exists())
 def test_independent_stage_installs(self):
  installer.install(self.project,'codex','sdlc-test',True)
  p=self.project/'.agents/skills/sdlc-test'
  self.assertTrue((p/'SKILL.md').is_file());self.assertTrue((p/'assets/output-template.md').is_file())
 def test_bundle_installs_with_runtime_resources(self):
  installer.install(self.project,'claude',apply=True)
  p=self.project/'.claude/skills/ai-native-sdlc-skills'
  self.assertTrue((p/'scripts/sdlc.py').is_file());self.assertTrue((p/'skills/sdlc-plan/assets/output-template.md').is_file())
  self.assertFalse((p/'README.md').exists())
 def test_overwrite_is_refused(self):
  installer.install(self.project,'claude','sdlc-plan',True)
  with self.assertRaises(ValueError):installer.install(self.project,'claude','sdlc-plan',True)
 def test_repository_validates(self):self.assertEqual(validator.validate(ROOT),[])

if __name__=='__main__':unittest.main()
