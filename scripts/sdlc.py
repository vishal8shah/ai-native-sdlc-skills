#!/usr/bin/env python3
"""Local delivery record helpers. No network, model calls or approval authority."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import re
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGES = ('plan', 'design', 'build', 'test', 'deploy', 'maintain')
ARTIFACTS = dict(zip(STAGES, ('intent.md', 'spec.md', 'plan.md', 'test-evidence.md', 'release.md', 'lessons.md')))
STATUSES = {'draft', 'ready_for_review', 'accepted', 'blocked'}
SECTIONS = {
    'plan': ('Problem and evidence','Desired outcome','Scope and exclusions','Acceptance examples','Constraints and unknowns','Decision and next step'),
    'design': ('Current system and verified context','Options and selected design','Acceptance traceability','Data, access and failure behavior','Policies and conflicts','Open questions and decision'),
    'build': ('Verified environment and components','Implementation order and proof','Risks, dependencies and rollback','Actual change','Checks actually run','Deviations and next decision'),
    'test': ('Coverage and actual results','Failures and corrections','Unrun checks and limits','Evidence review and next decision'),
    'deploy': ('Change and user impact','Review findings and actual test evidence','Required approvals','Release and rollback procedure','Monitoring and stop conditions','Decision and execution'),
    'maintain': ('Observations and alternative hypotheses','Action, authority and observed outcome','Regression or context improvement','Next intent or disposition','Measurement limits'),
}


class ValidationError(ValueError):
    pass

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def stamp_time() -> str:
    return datetime.now(timezone.utc).isoformat()

def identity(value, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f'{label} must be a nonempty string')
    if any(ord(c)<32 or 127<=ord(c)<=159 or c in '\u2028\u2029' for c in value):
        raise ValidationError(f'{label} must be single-line text without control characters')
    return value.strip()

def visible_markdown(text: str) -> str:
    """Read the supported Markdown structure outside comments and fenced blocks."""
    output=[];fence=None;comment=False
    for line in text.splitlines():
        if fence:
            marker=re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$',line)
            if marker and marker[1][0]==fence[0] and len(marker[1])>=fence[1] and not marker[2].strip():
                fence=None;output.append('')
            else:
                output.append('[fenced content]' if line.strip() else '')
            continue
        parts=[];position=0
        while position<len(line):
            if comment:
                end=line.find('-->',position)
                if end<0:break
                comment=False;position=end+3
            else:
                start=line.find('<!--',position)
                if start<0:parts.append(line[position:]);break
                parts.append(line[position:start]);comment=True;position=start+4
        visible=''.join(parts)
        marker=re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$',visible)
        if marker:
            fence=(marker[1][0],len(marker[1]));output.append('')
        else:output.append(visible)
    return '\n'.join(output)

def confined(root: Path, value: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError('Artifact path must be a nonempty relative string')
    p = Path(value)
    if p.is_absolute() or '..' in p.parts or '\\' in value or ':' in value:
        raise ValidationError('Artifact paths must stay inside the run folder')
    target = root / p
    cursor=root
    for part in p.parts:
        cursor=cursor/part
        if cursor.is_symlink():
            raise ValidationError('File symlinks and symlink ancestors are not supported')
    resolved = target.resolve()
    if root.resolve() not in resolved.parents:
        raise ValidationError('Artifact path escapes the run folder')
    if not target.is_file():
        raise ValidationError(f'Missing artifact: {value}')
    return target

def load_run(folder: Path) -> dict:
    metadata = folder / 'run.json'
    if metadata.is_symlink():
        raise ValidationError('run.json must not be a symlink')
    data = json.loads(metadata.read_text(encoding='utf-8'))
    if not isinstance(data, dict) or type(data.get('schema_version')) is not int or data['schema_version'] != 1:
        raise ValidationError('Unsupported run schema')
    for key in ('title', 'record_id', 'owner', 'system_of_record'):
        data[key]=identity(data.get(key),key)
    if data.get('record_mode','working') not in ('working','synthetic'):
        raise ValidationError('Unknown record_mode')
    if data.get('profile') not in ('generic', 'servicenow'):
        raise ValidationError('Unknown profile')
    if not isinstance(data.get('stages'), dict) or set(data['stages']) != set(STAGES):
        raise ValidationError('Run must contain exactly the six known stages')
    for stage in STAGES:
        value = data['stages'][stage]
        if not isinstance(value, dict) or not isinstance(value.get('status'),str) or value['status'] not in STATUSES:
            raise ValidationError(f'{stage}: invalid stage or status')
        if value.get('artifact') != ARTIFACTS[stage]:
            raise ValidationError(f'{stage}: expected artifact {ARTIFACTS[stage]}')
        confined(folder, value['artifact'])
    return data

def save_run(folder: Path, data: dict) -> None:
    path = folder / 'run.json'
    if path.is_symlink():
        raise ValidationError('run.json must not be a symlink')
    temp = folder / '.run.json.pending'
    if temp.exists() or temp.is_symlink():
        raise ValidationError('Pending metadata file already exists; inspect it before retrying')
    with temp.open('x', encoding='utf-8') as handle:
        json.dump(data, handle, indent=2)
        handle.write('\n')
    temp.replace(path)

def init_run(folder: Path, title: str, record_id: str, owner: str,
             system_of_record: str = 'Existing work item and change records',
             profile: str = 'generic', record_mode: str = 'working') -> dict:
    title=identity(title,'title');record_id=identity(record_id,'record_id')
    owner=identity(owner,'owner');system_of_record=identity(system_of_record,'system_of_record')
    if record_mode not in ('working','synthetic'):
        raise ValidationError('Unknown record_mode')
    if profile not in ('generic', 'servicenow'):
        raise ValidationError('Unknown profile')
    # Read sources before creating output; no partial output for missing templates.
    templates = {s: (ROOT / 'skills' / f'sdlc-{s}' / 'assets' / 'output-template.md').read_text(encoding='utf-8') for s in STAGES}
    folder.mkdir(parents=True, exist_ok=False)
    data = {'schema_version': 1, 'created_at': stamp_time(), 'title': title,
            'record_id': record_id, 'owner': owner, 'system_of_record': system_of_record,
            'profile': profile, 'record_mode': record_mode, 'stages': {}}
    # Keep user-provided values in JSON; templates remain explicit drafts.
    for stage in STAGES:
        (folder / ARTIFACTS[stage]).write_text(templates[stage], encoding='utf-8')
        data['stages'][stage] = {'artifact': ARTIFACTS[stage], 'status': 'draft',
                                'artifact_sha256': None, 'upstream_sha256': {},
                                'decision': None, 'evidence': []}
    save_run(folder, data)
    return data

def snapshot(folder: Path, stage: str) -> dict:
    if stage not in STAGES:
        raise ValidationError('Unknown stage')
    data = load_run(folder)
    record = data['stages'][stage]
    if record['status'] == 'accepted':
        raise ValidationError('Accepted records cannot be re-snapshotted; reopen as draft and obtain a new real decision')
    record['artifact_sha256'] = digest(confined(folder, record['artifact']))
    record['upstream_sha256'] = {s: digest(confined(folder, ARTIFACTS[s])) for s in STAGES[:STAGES.index(stage)]}
    record['snapshotted_at'] = stamp_time()
    record['decision'] = None
    save_run(folder, data)
    return record

def attach_evidence(folder: Path, stage: str, relative_path: str) -> dict:
    if stage not in STAGES:
        raise ValidationError('Unknown stage')
    data=load_run(folder);record=data['stages'][stage]
    if record['status']=='accepted':
        raise ValidationError('Reopen an accepted stage before attaching new evidence')
    if relative_path in ('run.json','.run.json.pending'):
        raise ValidationError('Evidence cannot reference mutable run metadata')
    path=confined(folder,relative_path)
    canonical=path.relative_to(folder).as_posix()
    if canonical in ('run.json','.run.json.pending'):
        raise ValidationError('Evidence cannot reference mutable run metadata')
    value={'kind':'local_file','path':canonical,'sha256':digest(path)}
    evidence=record.get('evidence')
    if not isinstance(evidence,list):
        raise ValidationError('Evidence must be a list')
    record['evidence']=[x for x in evidence if not (isinstance(x,dict) and x.get('kind')=='local_file' and x.get('path')==value['path'])]+[value]
    record['decision']=None
    save_run(folder,data)
    return value

def decision_valid(value) -> bool:
    if not isinstance(value, dict):
        return False
    if not all(isinstance(value.get(k), str) and value[k].strip() for k in ('owner', 'reference', 'timestamp')):
        return False
    try:
        dt = datetime.fromisoformat(value['timestamp'].replace('Z', '+00:00'))
        return dt.tzinfo is not None and dt.utcoffset() is not None
    except ValueError:
        return False

def check_run(folder: Path, through: str = 'maintain', require_accepted: bool = False) -> dict:
    if through not in STAGES:
        raise ValidationError('Unknown stage')
    data = load_run(folder)
    findings = [];warnings=[];local_verified=0;local_paths=set();external_unverified=0
    if data.get('record_mode')=='synthetic':
        warnings.append('Synthetic run: acceptance decisions are demonstration metadata, not real approvals.')
    for stage in STAGES[:STAGES.index(through)+1]:
        record = data['stages'][stage]
        status = record['status']
        path = confined(folder, record['artifact'])
        if require_accepted and status != 'accepted':
            findings.append(f'{stage}: actual acceptance record is required')
        if status not in ('ready_for_review', 'accepted'):
            continue
        text = visible_markdown(path.read_text(encoding='utf-8'))
        html_checked=re.sub(r'(`+)(.*?)\1','[inline code]',text,flags=re.S)
        if re.search(r'</?[A-Za-z][A-Za-z0-9]*(?:\s[^>]*|/?)>',html_checked):
            findings.append(f'{stage}: raw HTML is unsupported in checked artifact content')
        header = re.search(r'^Status:\s*(\S+)\s*$', text, re.MULTILINE)
        if not header or header.group(1).lower() != status:
            findings.append(f'{stage}: Markdown and manifest statuses disagree')
        for label,key in [('Record ID','record_id'),('Source of truth','system_of_record'),('Accountable owner','owner')]:
            field = re.search(r'^'+re.escape(label)+r':[ \t]*(.+)$',text,re.MULTILINE)
            if not field or field.group(1).strip() != data[key]:
                findings.append(f'{stage}: missing or mismatched {label}')
        blocks = re.split(r'^##[ \t]+(.+?)[ \t]*$',text,flags=re.MULTILINE)
        sections = {blocks[i].strip(): blocks[i+1].strip() for i in range(1,len(blocks)-1,2)}
        for title in SECTIONS[stage]:
            body = re.sub(r'<!--.*?-->','',sections.get(title,''),flags=re.S).strip()
            if not body:
                findings.append(f'{stage}: missing or empty section {title}')
        if '[required' in text.lower():
            findings.append(f'{stage}: unfilled required template fields')
        if not record.get('artifact_sha256') or digest(path) != record['artifact_sha256']:
            findings.append(f'{stage}: missing or stale artifact snapshot')
        earlier = STAGES[:STAGES.index(stage)]
        hashes = record.get('upstream_sha256')
        if not isinstance(hashes, dict) or set(hashes) != set(earlier):
            findings.append(f'{stage}: incomplete upstream snapshot')
        else:
            for previous in earlier:
                if hashes[previous] != digest(confined(folder, ARTIFACTS[previous])):
                    findings.append(f'{stage}: upstream {previous} changed; review the impact')
                if data['stages'][previous]['status'] != 'accepted':
                    findings.append(f'{stage}: upstream {previous} is not accepted')
        if status == 'accepted' and not decision_valid(record.get('decision')):
            findings.append(f'{stage}: missing decision owner, external reference or timezone-aware timestamp')
        evidence = record.get('evidence')
        if not isinstance(evidence, list) or not evidence:
            findings.append(f'{stage}: evidence must contain at least one reference')
            continue
        seen=set()
        for reference in evidence:
            if isinstance(reference,str) and reference.strip():
                external_unverified+=1
            elif isinstance(reference,dict) and reference.get('kind')=='local_file':
                try:
                    if set(reference)!={'kind','path','sha256'}:
                        raise ValidationError('local_file evidence requires kind, path and sha256 only')
                    if reference['path'] in ('run.json','.run.json.pending'):
                        raise ValidationError('Evidence cannot reference mutable run metadata')
                    if not isinstance(reference['sha256'],str) or not re.fullmatch(r'[0-9a-f]{64}',reference['sha256']):
                        raise ValidationError('Invalid evidence SHA-256')
                    local=confined(folder,reference['path'])
                    canonical=local.relative_to(folder).as_posix()
                    if canonical in ('run.json','.run.json.pending'):
                        raise ValidationError('Evidence cannot reference mutable run metadata')
                    if canonical in seen:raise ValidationError('Duplicate local evidence path')
                    seen.add(canonical)
                    if digest(local)!=reference['sha256']:
                        raise ValidationError('Local evidence changed: '+canonical)
                    local_verified+=1;local_paths.add(canonical)
                except (OSError,ValueError,TypeError) as exc:
                    findings.append(f'{stage}: {exc}')
            else:
                findings.append(f'{stage}: unsupported or empty evidence reference')
    if external_unverified:
        warnings.append(f'{external_unverified} external reference(s) are recorded but not fetched or verified.')
    return {'valid': not findings, 'record_id': data['record_id'], 'through': through,
            'record_mode':data.get('record_mode','working'),
            'findings': findings, 'warnings':warnings,
            'evidence_summary':{'local_files_verified':len(local_paths),'local_file_references_verified':local_verified,'external_references_unverified':external_unverified},
            'boundary': 'Local artifact and registered-file freshness only; external references and approvals are not authenticated.'}

MEASURES = ('baseline_elapsed_h', 'pilot_elapsed_h', 'baseline_staff_min', 'pilot_staff_min',
            'baseline_rework', 'pilot_rework', 'baseline_defects', 'pilot_defects')

def nonnegative(value: float, label: str) -> float:
    if not math.isfinite(value) or value < 0:
        raise ValidationError(f'{label} must be finite and nonnegative')
    return value

def measure(path: Path, hour_rate: float, setup_hours: float = 0, ai_cost: float = 0) -> dict:
    for label, v in [('hour_rate', hour_rate), ('setup_hours', setup_hours), ('ai_cost', ai_cost)]:
        nonnegative(v, label)
    rows = []
    with path.open(newline='', encoding='utf-8-sig') as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or not set(MEASURES).issubset(reader.fieldnames):
            raise ValidationError('CSV is missing required measurement columns')
        if len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValidationError('CSV contains duplicate column names')
        for index, raw in enumerate(reader, 2):
            if None in raw:
                raise ValidationError(f'CSV row {index}: extra values')
            row = {}
            for key in MEASURES:
                text = raw.get(key)
                if text is None or not text.strip():
                    raise ValidationError(f'CSV row {index}: missing {key}')
                try:
                    val = float(text)
                except ValueError as exc:
                    raise ValidationError(f'CSV row {index}: invalid {key}') from exc
                nonnegative(val, f'row {index} {key}')
                if key.endswith('_h') and val <= 0:
                    raise ValidationError(f'CSV row {index}: elapsed hours must be positive')
                if key.endswith(('rework', 'defects')) and not val.is_integer():
                    raise ValidationError(f'CSV row {index}: counts must be whole numbers')
                row[key] = val
            rows.append(row)
    if not rows:
        raise ValidationError('CSV has no complete observations')
    saved_h = sum(r['baseline_staff_min']-r['pilot_staff_min'] for r in rows)/60
    result = {'pairs': len(rows), 'median_elapsed_reduction_pct': statistics.median(100*(1-r['pilot_elapsed_h']/r['baseline_elapsed_h']) for r in rows),
              'staff_hours_saved': saved_h,
              'rework_difference': sum(r['pilot_rework']-r['baseline_rework'] for r in rows),
              'defect_difference': sum(r['pilot_defects']-r['baseline_defects'] for r in rows),
              'net_capacity_value_aud': saved_h*hour_rate-setup_hours*hour_rate-ai_cost,
              'limits': 'Matched observations are directional, not causal proof. Capacity value is not guaranteed cash savings.'}
    for key, value in result.items():
        if isinstance(value, (int, float)) and not math.isfinite(value):
            raise ValidationError('Numeric overflow; reduce measurement magnitudes')
    return result

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='command', required=True)
    init = subs.add_parser('init-run')
    init.add_argument('--output', type=Path, required=True)
    for name in ('title', 'record-id', 'owner'):
        init.add_argument('--'+name, required=True)
    init.add_argument('--system-of-record', default='Existing work item and change records')
    init.add_argument('--profile', choices=['generic', 'servicenow'], default='generic')
    init.add_argument('--synthetic',action='store_true',help='Mark demonstration decisions as synthetic')
    attach=subs.add_parser('attach-evidence');attach.add_argument('run',type=Path);attach.add_argument('--stage',choices=STAGES,required=True);attach.add_argument('--file',required=True,help='Existing file path relative to the run folder')
    snap = subs.add_parser('snapshot'); snap.add_argument('run', type=Path); snap.add_argument('--stage', choices=STAGES, required=True)
    check = subs.add_parser('check-run'); check.add_argument('run', type=Path); check.add_argument('--through', choices=STAGES, default='maintain'); check.add_argument('--require-accepted', action='store_true')
    meas = subs.add_parser('measure'); meas.add_argument('csv', type=Path); meas.add_argument('--hour-rate', type=float, required=True); meas.add_argument('--setup-hours', type=float, default=0); meas.add_argument('--ai-cost', type=float, default=0)
    args = parser.parse_args(argv)
    try:
        if args.command == 'init-run':
            data = init_run(args.output, args.title, args.record_id, args.owner, args.system_of_record, args.profile,'synthetic' if args.synthetic else 'working')
            result = {'created': str(args.output), 'record_id': data['record_id'], 'status': 'draft'}
        elif args.command == 'attach-evidence':
            result=attach_evidence(args.run,args.stage,args.file)
        elif args.command == 'snapshot':
            result = snapshot(args.run, args.stage)
        elif args.command == 'check-run':
            result = check_run(args.run, args.through, args.require_accepted)
        else:
            result = measure(args.csv, args.hour_rate, args.setup_hours, args.ai_cost)
        print(json.dumps(result, indent=2, allow_nan=False))
        return 1 if result.get('valid') is False else 0
    except (OSError, ValueError, TypeError, KeyError, OverflowError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
