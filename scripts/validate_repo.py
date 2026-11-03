#!/usr/bin/env python3
"""Validate this repository's constrained skill format, links and Python syntax."""
import ast
import json
import re
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
NAME='ai-native-sdlc-skills'

def validate(root=ROOT):
    errors=[]
    skills=[root/'SKILL.md',*sorted((root/'skills').glob('*/SKILL.md'))]
    if len(skills)!=7:
        errors.append('Expected router plus six stage skills')
    names=[]
    for file in skills:
        text=file.read_text(encoding='utf-8')
        parts=text.split('---',2)
        if len(parts)!=3 or parts[0].strip():
            errors.append(f'{file}: invalid frontmatter');continue
        values={}
        for line in parts[1].strip().splitlines():
            if ':' not in line:
                errors.append(f'{file}: invalid metadata line');continue
            k,v=line.split(':',1);values[k.strip()]=v.strip().strip('"')
        if set(values)!={'name','description'}:
            errors.append(f'{file}: expected name and description only')
        name=values.get('name','');names.append(name)
        expected=NAME if file==root/'SKILL.md' else file.parent.name
        if name!=expected or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',name) or len(name)>64:
            errors.append(f'{file}: invalid name')
        if not 1<=len(values.get('description',''))<=1024:
            errors.append(f'{file}: invalid description')
        if len(text.splitlines())>500:
            errors.append(f'{file}: skill too long')
        if 'TODO' in text:
            errors.append(f'{file}: unfinished initializer placeholder')
        metadata=file.parent/'agents'/'openai.yaml'
        if not metadata.is_file() or f'${name}' not in metadata.read_text():
            errors.append(f'{file}: missing or stale UI metadata')
    if len(names)!=len(set(names)):
        errors.append('Duplicate skill names')
    for file in root.rglob('*.md'):
        for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)',file.read_text(encoding='utf-8')):
            if re.match(r'^[a-z]+:',target) or target.startswith('#'):
                continue
            if not (file.parent/target.split('#')[0]).exists():
                errors.append(f'{file}: missing linked file {target}')
    for file in root.rglob('*.py'):
        try:ast.parse(file.read_text(encoding='utf-8'),filename=str(file))
        except SyntaxError as exc:errors.append(str(exc))
    cases=json.loads((root/'evals'/'cases.json').read_text())
    if len({c['id'] for c in cases})!=len(cases):errors.append('Duplicate eval IDs')
    for case in cases:
        if case['skill'] not in names or not case.get('rubric'):errors.append('Invalid evaluation case')
        if case.get('input') and not (root/case['input']).is_file():errors.append('Missing evaluation input')
    return errors
if __name__=='__main__':
    errors=validate()
    print('\n'.join(errors) if errors else 'PASS: 7 skills, UI metadata, local links, evaluation cases and Python syntax')
    sys.exit(bool(errors))
