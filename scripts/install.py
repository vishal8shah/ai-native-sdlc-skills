#!/usr/bin/env python3
"""Copy new, reviewed skills into an existing local project; dry-run by default."""
from __future__ import annotations
import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME = 'ai-native-sdlc-skills'
STAGES = ('sdlc-plan','sdlc-design','sdlc-build','sdlc-test','sdlc-deploy','sdlc-maintain')
ROOT_FILES = ('SKILL.md', 'agents', 'scripts', 'references', 'skills')

def install(project: Path, client: str, only: str | None = None, apply: bool = False) -> dict:
    project = project.resolve()
    if not project.is_dir():
        raise ValueError('Destination project must already be a directory')
    if client not in ('claude', 'codex'):
        raise ValueError('Unknown client')
    if only is not None and only not in (NAME, *STAGES):
        raise ValueError('Unknown skill')
    base = project / ('.claude' if client == 'claude' else '.agents') / 'skills'
    if base.resolve() != base or base.is_symlink():
        raise ValueError('Destination skills path must not contain symlinks')
    names = [only] if only else [NAME, *STAGES]
    plans = [(n, ROOT if n == NAME else ROOT/'skills'/n, base/n) for n in names]
    for name, source, dest in plans:
        if dest.exists() or dest.is_symlink():
            raise ValueError(f'Refusing to overwrite existing skill: {name}')
        if not (source/'SKILL.md').is_file():
            raise ValueError(f'Missing source skill: {name}')
        if source.resolve() == dest.resolve() or source.resolve() in dest.resolve().parents:
            raise ValueError('Destination must not be inside the source skill')
        roots = [source/f for f in ROOT_FILES] if name == NAME else [source]
        for scan in roots:
            if scan.is_symlink() or (scan.is_dir() and any(p.is_symlink() for p in scan.rglob('*'))):
                raise ValueError('Skill source must not contain symlinks')
    if apply:
        base.mkdir(parents=True, exist_ok=True)
        for name, source, dest in plans:
            if name == NAME:
                dest.mkdir()
                for item in ROOT_FILES:
                    src=source/item
                    if src.is_dir():
                        shutil.copytree(src,dest/item,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
                    else:
                        shutil.copy2(src,dest/item)
            else:
                shutil.copytree(source,dest,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    return {'applied': apply, 'client': client, 'skills': [{'name':n,'destination':str(d)} for n,s,d in plans]}

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--client',required=True,choices=['claude','codex'])
    parser.add_argument('--project',type=Path,required=True)
    parser.add_argument('--only',choices=[NAME,*STAGES])
    parser.add_argument('--apply',action='store_true')
    a=parser.parse_args(argv)
    try:
        print(json.dumps(install(a.project,a.client,a.only,a.apply),indent=2))
        return 0
    except (OSError,ValueError) as exc:
        print(f'Error: {exc}',file=sys.stderr)
        return 2
if __name__=='__main__':
    raise SystemExit(main())
