#!/usr/bin/env python3
"""Generate a complete synthetic delivery packet with real local test execution."""
from __future__ import annotations
import argparse
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def delivery():
    spec=importlib.util.spec_from_file_location('worked_delivery',ROOT/'scripts/sdlc.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def build_example(folder):
    folder=Path(folder);s=delivery();blueprint=ROOT/'examples/worked-change/blueprint'
    s.init_run(folder,'Synthetic request validation','DEMO-WORKED-001','Demo reviewer',
               system_of_record='Synthetic local worked example',record_mode='synthetic')
    for directory in ('inputs','implementation','evidence'):(folder/directory).mkdir()
    shutil.copy2(blueprint/'request.md',folder/'inputs/request.md')
    for name in ('request_validation.py','test_request_validation.py'):
        shutil.copy2(blueprint/name,folder/'implementation'/name)
    runner="""import json,sys,unittest
class ObservedResult(unittest.TextTestResult):
    def startTest(self,test):
        super().startTest(test);self.executed_ids.append(test.id())
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs);self.executed_ids=[]
suite=unittest.defaultTestLoader.discover(sys.argv[1],pattern='test_request_validation.py')
result=unittest.TextTestRunner(verbosity=2,resultclass=ObservedResult).run(suite)
required={
 'test_request_validation.RequestIsValidTests.test_missing_justification',
 'test_request_validation.RequestIsValidTests.test_empty_and_whitespace_only_justification',
 'test_request_validation.RequestIsValidTests.test_nonblank_justification',
 'test_request_validation.RequestIsValidTests.test_non_string_input'}
report={'tests_run':result.testsRun,'executed_test_ids':result.executed_ids,
 'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),
 'expected_failures':len(result.expectedFailures),'unexpected_successes':len(result.unexpectedSuccesses),
 'all_required_methods_executed':required.issubset(result.executed_ids)}
report['verified']=bool(result.wasSuccessful() and report['all_required_methods_executed'] and not report['skipped'] and not report['expected_failures'] and not report['unexpected_successes'])
with open(sys.argv[2],'w',encoding='utf-8') as output:json.dump(report,output,indent=2)
sys.exit(0 if report['verified'] else 1)
"""
    command=[sys.executable,'-B','-c',runner,str(folder/'implementation'),str(folder/'evidence/test-report.json')]
    result=subprocess.run(command,capture_output=True,text=True,timeout=30)
    (folder/'evidence/unittest.txt').write_text(result.stdout+result.stderr,encoding='utf-8')
    context={'synthetic':True,'generated_at':datetime.now(timezone.utc).isoformat(),
             'python_version':sys.version.split()[0],'command':command,'exit_code':result.returncode,
             'scope':'Real local unit tests. No client discovery, external service or production release.'}
    (folder/'evidence/execution.json').write_text(json.dumps(context,indent=2)+'\n',encoding='utf-8')
    if result.returncode:
        raise ValueError('Actual tests failed; logs retained and stages remain drafts')
    source_digest=s.digest(folder/'implementation/request_validation.py')
    bodies={
      'plan':[
       'Synthetic input: inputs/request.md. No real incident or customer record is used.',
       'Provide request_is_valid(value=None) with the exact behaviors in the supplied synthetic request.',
       'One local function. Exclude network calls, production changes, integrations and data mutation.',
       'AC-01 omitted/None reject; AC-02 Python whitespace-only strings reject; AC-03 nonblank strings accept; AC-04 non-string input rejects.',
       'Whitespace is defined by Python str.strip(). This is not a claim to detect every visually empty Unicode string.',
       'All owner decisions in this packet are simulated solely to demonstrate record structure.'],
      'design':[
       'Local Python standard library environment; no web framework, platform fields or database are assumed.',
       'Use isinstance(value, str) and bool(value.strip()); this preserves type checks and handles the specified whitespace definition.',
       'AC-01 through AC-04 map to the four test methods in implementation/test_request_validation.py.',
       'Inputs are inspected only. Non-string input returns False; no source record is modified.',
       'Synthetic scenario only. No organization policy or exception has been approved.',
       'Conceptual design represented by a simulated owner record; no real organizational design decision occurred.'],
      'build':[
       'implementation/request_validation.py and implementation/test_request_validation.py were copied from the captured DEMO-301 implementation.',
       'Create the bounded function, execute the four unit methods, retain the actual output, and bind source/results as evidence.',
       'The example is local and disposable. Rollback means discarding the generated example, not a production recovery operation.',
       'Actual local implementation SHA-256: '+source_digest+'. This is the generated candidate, not a deployed version.',
       'Executed: '+ ' '.join(command)+'. Actual exit code: 0. Literal output: evidence/unittest.txt.',
       'No external implementation or production action. Owner acceptance records are simulated.'],
      'test':[
       'Four real unittest methods cover AC-01 through AC-04. Exact tested source and test files are bound by SHA-256; raw output is retained.',
       'The captured local verification returned exit 0. No code or expectations were altered to obtain that outcome.',
       'No real Claude/Codex discovery, ServiceNow instance, integration, load or production test was run.',
       'Local results are observed. The owner decision is explicitly simulated and grants no real release authority.'],
      'deploy':[
       'This packet concerns only a synthetic local function. No user-facing service is changed.',
       'Candidate source, test code and actual execution log are local evidence attachments. Results do not establish production readiness.',
       'SIMULATED ONLY: Demo reviewer metadata demonstrates the required record shape. There is no authenticated approval.',
       'No release procedure is executed. Production transport, actual rollback and rehearsal are out of scope.',
       'Only local unit outcomes were observed. No production baseline, monitoring window or recovery is claimed.',
       'Decision: simulated packet acceptance for the walkthrough. Execution: NOT EXECUTED. No deployment is authorized by this example.'],
      'maintain':[
       'Observed outcome: the local unit suite passed against the registered candidate. No operational incident occurred.',
       'Only local test execution occurred. There is no service remediation, user benefit or recovery measurement.',
       'Keep the whitespace/type cases as regressions; add a new case only when its expected behavior is independently justified.',
       'Use a real authoritative work item and real decisions for any actual product change; this packet is a synthetic teaching example.',
       'No productivity, cost saving, production reliability or model benchmark can be inferred from these tests.']}
    for stage in s.STAGES:
        text=f'# Synthetic worked example: {stage}\nStatus: ACCEPTED\nRecord ID: DEMO-WORKED-001\nSource of truth: Synthetic local worked example\nAccountable owner: Demo reviewer\n\nSYNTHETIC DECISIONS ONLY. Actual local test execution is recorded separately.\n'
        text+=''.join(f'\n## {title}\n{body}\n' for title,body in zip(s.SECTIONS[stage],bodies[stage]))
        (folder/s.ARTIFACTS[stage]).write_text(text,encoding='utf-8')
        for path in ('inputs/request.md','implementation/request_validation.py','implementation/test_request_validation.py','evidence/unittest.txt','evidence/execution.json','evidence/test-report.json'):
            s.attach_evidence(folder,stage,path)
        s.snapshot(folder,stage)
        data=s.load_run(folder)
        data['stages'][stage].update(status='accepted',decision={'owner':'SIMULATED Demo reviewer','reference':'synthetic://DEMO-WORKED-001/'+stage,'timestamp':datetime.now(timezone.utc).isoformat()})
        s.save_run(folder,data)
    checked=s.check_run(folder,require_accepted=True)
    return {'valid':checked['valid'],'record_mode':'synthetic','actual_test_exit_code':result.returncode,
            'evidence_summary':checked['evidence_summary'],'warnings':checked['warnings'],'findings':checked['findings'],
            'boundary':'Synthetic decision metadata; real local unit execution. No external approval or release occurred.'}

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,help='Retain the packet in a NEW directory')
    a=p.parse_args(argv)
    try:
        if a.output:result=build_example(a.output);result['retained_at']=str(a.output)
        else:
            with tempfile.TemporaryDirectory(prefix='sdlc-worked-') as t:result=build_example(Path(t)/'run')
            result['files_retained']=False
        print(json.dumps(result,indent=2));return 0 if result['valid'] else 1
    except (OSError,ValueError,subprocess.TimeoutExpired) as exc:print('Error: '+str(exc),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
