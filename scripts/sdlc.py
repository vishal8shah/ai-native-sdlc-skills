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

class ValidationError(ValueError):
    pass

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def stamp_time() -> str:
    return datetime.now(timezone.utc).isoformat()

def confined(root: Path, value: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError('Artifact path must be a nonempty relative string')
    p = Path(value)
    if p.is_absolute() or '..' in p.parts or '\\' in value or ':' in value:
        raise ValidationError('Artifact paths must stay inside the run folder')
    target = root / p
    if target.is_symlink():
        raise ValidationError('Artifact symlinks are not supported')
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
        if not isinstance(data.get(key), str) or not data[key].strip():
            raise ValidationError(f'Missing metadata: {key}')
    if data.get('profile') not in ('generic', 'servicenow'):
        raise ValidationError('Unknown profile')
    if not isinstance(data.get('stages'), dict) or set(data['stages']) != set(STAGES):
        raise ValidationError('Run must contain exactly the six known stages')
    for stage in STAGES:
        value = data['stages'][stage]
        if not isinstance(value, dict) or value.get('status') not in STATUSES:
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
             profile: str = 'generic') -> dict:
    for label, value in [('title', title), ('record_id', record_id), ('owner', owner), ('system_of_record', system_of_record)]:
        if not isinstance(value, str) or not value.strip():
            raise ValidationError(f'{label} must not be blank')
    if profile not in ('generic', 'servicenow'):
        raise ValidationError('Unknown profile')
    # Read sources before creating output; no partial output for missing templates.
    templates = {s: (ROOT / 'skills' / f'sdlc-{s}' / 'assets' / 'output-template.md').read_text(encoding='utf-8') for s in STAGES}
    folder.mkdir(parents=True, exist_ok=False)
    data = {'schema_version': 1, 'created_at': stamp_time(), 'title': title,
            'record_id': record_id, 'owner': owner, 'system_of_record': system_of_record,
            'profile': profile, 'stages': {}}
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
    findings = []
    for stage in STAGES[:STAGES.index(through)+1]:
        record = data['stages'][stage]
        status = record['status']
        path = confined(folder, record['artifact'])
        if require_accepted and status != 'accepted':
            findings.append(f'{stage}: actual acceptance record is required')
        if status not in ('ready_for_review', 'accepted'):
            continue
        text = path.read_text(encoding='utf-8')
        header = re.search(r'^Status:\s*(\S+)\s*$', text, re.MULTILINE)
        if not header or header.group(1).lower() != status:
            findings.append(f'{stage}: Markdown and manifest statuses disagree')
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
        if not isinstance(evidence, list) or not evidence or any(not isinstance(v, str) or not v.strip() for v in evidence):
            findings.append(f'{stage}: evidence must be a list of nonempty references')
    return {'valid': not findings, 'record_id': data['record_id'], 'through': through,
            'findings': findings, 'boundary': 'Local structure and content lineage only; approvals are not authenticated.'}

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
    snap = subs.add_parser('snapshot'); snap.add_argument('run', type=Path); snap.add_argument('--stage', choices=STAGES, required=True)
    check = subs.add_parser('check-run'); check.add_argument('run', type=Path); check.add_argument('--through', choices=STAGES, default='maintain'); check.add_argument('--require-accepted', action='store_true')
    meas = subs.add_parser('measure'); meas.add_argument('csv', type=Path); meas.add_argument('--hour-rate', type=float, required=True); meas.add_argument('--setup-hours', type=float, default=0); meas.add_argument('--ai-cost', type=float, default=0)
    args = parser.parse_args(argv)
    try:
        if args.command == 'init-run':
            data = init_run(args.output, args.title, args.record_id, args.owner, args.system_of_record, args.profile)
            result = {'created': str(args.output), 'record_id': data['record_id'], 'status': 'draft'}
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
