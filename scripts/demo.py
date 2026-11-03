#!/usr/bin/env python3
"""Run a deterministic, synthetic example of why green tests need valid expectations."""
from __future__ import annotations
import argparse
import importlib.util
import json
import sys
import tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

def run_demo(output=None):
    fixture=load('demo_fixture',ROOT/'demo/justification.py')
    delivery=load('delivery_helper',ROOT/'scripts/sdlc.py')
    def inspect(folder):
        delivery.init_run(folder,'Synthetic request validation','DEMO-001','Demo reviewer',profile='servicenow')
        data=delivery.load_run(folder)
        text='# Synthetic intent\nStatus: READY_FOR_REVIEW\nRecord ID: DEMO-001\nSource of truth: Existing work item and change records\nAccountable owner: Demo reviewer\n'
        text+=''.join(f'\n## {title}\nSynthetic demo fixture; reject blank justification.\n' for title in delivery.SECTIONS['plan'])
        artifact=folder/'intent.md';artifact.write_text(text,encoding='utf-8')
        data['stages']['plan'].update(status='ready_for_review',evidence=['synthetic-fixture:DEMO-001'])
        delivery.save_run(folder,data);delivery.snapshot(folder,'plan')
        before=delivery.check_run(folder,'plan')
        artifact.write_text(text+'\nRequirement changed after the snapshot.\n',encoding='utf-8')
        after=delivery.check_run(folder,'plan')
        return {'before_valid':before['valid'],'after_valid':after['valid'],'findings':after['findings']}
    if output is not None:
        lineage=inspect(Path(output))
    else:
        with tempfile.TemporaryDirectory(prefix='sdlc-demo-') as temporary:
            lineage=inspect(Path(temporary)/'run')
    original=fixture.acceptance(fixture.unsafe)
    fixed=fixture.acceptance(fixture.corrected)
    result={'synthetic':True,'generated_test_passed':fixture.unsafe('   ') is True,'original_acceptance':original,'corrected_acceptance':fixed,'lineage':lineage}
    result['demo_verified']=result['generated_test_passed'] and original['failed']>0 and fixed['failed']==0 and lineage['before_valid'] and not lineage['after_valid']
    return result

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json',action='store_true');parser.add_argument('--output',type=Path,help='Retain the synthetic run in a NEW folder')
    args=parser.parse_args(argv)
    try:
        result=run_demo(args.output)
        if args.json:print(json.dumps(result,indent=2))
        else:
            print('AI-NATIVE SDLC / SYNTHETIC DEMO\n')
            print('1. A generated test expects whitespace to be accepted: PASS')
            print(f"   Independent acceptance checks: {result['original_acceptance']['passed']}/7 passed; {result['original_acceptance']['failed']} failed")
            print('   The test and implementation agree. The requirement disagrees.\n')
            print(f"2. Correct the behavior: {result['corrected_acceptance']['passed']}/7 acceptance checks pass\n")
            print('3. Snapshot the evidence, then edit the requirement: STALE RECORD DETECTED')
            print('   '+ '; '.join(result['lineage']['findings']))
            print('\nLocal checks verify records and covered behavior; they do not grant release authority.')
            if args.output:print('\nRetained synthetic run: '+str(args.output))
        return 0 if result['demo_verified'] else 1
    except (OSError,ValueError,TypeError) as exc:
        print('Error: '+str(exc),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
