#!/usr/bin/env python3
"""Inspect/replay captured task inputs and verify stored trial file integrity offline."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SKILLS={'ai-native-sdlc-skills',*('sdlc-'+s for s in ('plan','design','build','test','deploy','maintain'))}

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def child(root,path):
    if not isinstance(path,str) or not path or Path(path).is_absolute() or '\\' in path or ':' in path:
        raise ValueError('Expected a confined relative file path')
    result=root/path
    if result.is_symlink() or not result.resolve().is_relative_to(root.resolve()) or not result.is_file():
        raise ValueError('Missing or escaping record file: '+path)
    return result

def records(root=ROOT):
    base=Path(root)/'evals/recorded'
    return [(p.parent,json.loads(p.read_text(encoding='utf-8'))) for p in sorted(base.glob('*/record.json'))]

def verify(root=ROOT,require_current=False):
    root=Path(root);items=records(root);errors=[];summary=[];seen=set();coverage=set()
    if not items:errors.append('No captured trials found')
    for folder,item in items:
        label=item.get('id',folder.name) if isinstance(item,dict) else folder.name
        try:
            if not isinstance(item,dict) or type(item.get('schema_version')) is not int or item['schema_version']!=1:raise ValueError('Unknown trial schema')
            if not isinstance(label,str) or label!=folder.name or label in seen:raise ValueError('Missing, mismatched or duplicate trial ID')
            seen.add(label)
            skill=item.get('skill')
            if skill not in SKILLS:raise ValueError('Unknown skill')
            coverage.add(skill)
            for kind in ('task','response'):
                file=child(folder,item.get(kind+'_file'))
                if not file.read_text(encoding='utf-8').strip():raise ValueError('Empty '+kind)
                if item.get(kind+'_sha256')!=sha(file):raise ValueError('Changed '+kind+' bytes')
            provenance=item.get('provenance')
            if not isinstance(provenance,dict) or not provenance.get('runner') or not provenance.get('classification') or 'model_deployment_identifier' not in provenance or not provenance.get('model_identifier_status'):
                raise ValueError('Missing provenance or model-identifier disclosure')
            inspected=item.get('inspected_files')
            if not isinstance(inspected,list) or not inspected:raise ValueError('Missing inspected source references')
            current=True
            for source in inspected:
                if not isinstance(source,dict) or not re.fullmatch('[0-9a-f]{64}',str(source.get('sha256',''))):raise ValueError('Malformed source reference')
                file=child(root,source.get('path'))
                current=current and sha(file)==source['sha256']
            if require_current and not current:raise ValueError('Inspected source changed; capture a new trial')
            review=item.get('author_review')
            if not isinstance(review,dict) or not isinstance(review.get('observations'),list) or not review['observations'] or not all(isinstance(x,str) and x.strip() for x in review['observations']) or not isinstance(review.get('limits'),str) or not review['limits'].strip():
                raise ValueError('Missing review observations or scope limits')
            summary.append({'id':label,'skill':skill,'source_matches_current':current,'classification':provenance['classification']})
        except (OSError,ValueError,KeyError,TypeError) as exc:errors.append(f'{label}: {exc}')
    if coverage!=SKILLS:errors.append('Captured trials do not cover the seven shipped skills')
    return {'valid':not errors,'trials':summary,'findings':errors,'boundary':'File integrity and disclosed provenance only. Captures and author judgments are not authenticated; no benchmark score is computed.'}

def prompt(trial_id,client='codex',root=ROOT):
    matches=[(folder,r) for folder,r in records(root) if r.get('id')==trial_id]
    if len(matches)!=1:raise ValueError('Unknown trial ID')
    folder,item=matches[0];text=child(folder,item['task_file']).read_text(encoding='utf-8')
    # Retain the task; replace only historical skill filesystem references for replay.
    text=re.sub(r'/workspace/projects/ai-native-sdlc-skills/(?:skills/[^/]+/)?SKILL\.md','the selected skill',text)
    invocation='/'+item['skill'] if client=='claude' else '$'+item['skill']
    return invocation+'\n\n'+text

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    check=sub.add_parser('verify');check.add_argument('--require-current',action='store_true')
    show=sub.add_parser('prompt');show.add_argument('id');show.add_argument('--client',choices=['claude','codex'],default='codex')
    a=p.parse_args(argv)
    try:
        if a.command=='prompt':print(prompt(a.id,a.client));return 0
        result=verify(require_current=a.require_current);print(json.dumps(result,indent=2));return 0 if result['valid'] else 1
    except (OSError,ValueError,KeyError,TypeError) as exc:print('Error: '+str(exc),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
