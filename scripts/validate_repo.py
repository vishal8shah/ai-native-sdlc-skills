#!/usr/bin/env python3
"""Validate this repository's documented, constrained metadata schemas offline."""
import ast
import json
import re
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
NAME='ai-native-sdlc-skills'

def nonempty(value):
    return isinstance(value,str) and bool(value.strip())

def frontmatter(text):
    match=re.match(r'\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)',text,re.S)
    if not match:raise ValueError('Missing YAML frontmatter delimiters')
    values={}
    for line in match.group(1).splitlines():
        m=re.fullmatch(r'([a-z_]+):\s+(.+)',line)
        if not m or m[1] in values:raise ValueError('Use unique, one-line metadata fields')
        key,raw=m.groups()
        if raw.startswith('"'):
            value=json.loads(raw)
        elif re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',raw):
            value=raw
        else:raise ValueError('Use a plain hyphenated name or a JSON-quoted string')
        if not isinstance(value,str):raise ValueError('Metadata values must be strings')
        values[key]=value
    return values

def ui_metadata(text):
    # A deliberate YAML subset: interface plus three double-quoted string fields.
    lines=[line for line in text.splitlines() if line.strip()]
    if not lines or lines[0]!='interface:':raise ValueError('Expected interface mapping')
    values={}
    for line in lines[1:]:
        m=re.fullmatch(r'  ([a-z_]+): (".*")',line)
        if not m or m[1] in values:raise ValueError('Expected unique interface string fields')
        value=json.loads(m[2])
        if not nonempty(value):raise ValueError('UI fields must be nonempty strings')
        values[m[1]]=value
    if set(values)!={'display_name','short_description','default_prompt'}:
        raise ValueError('Expected display_name, short_description and default_prompt')
    if not 25<=len(values['short_description'])<=64:
        raise ValueError('short_description must have 25 to 64 characters')
    return values

def local_target(root,file,target):
    if re.match(r'^[a-z][a-z0-9+.-]*:',target,re.I) or target.startswith('#'):return None
    p=(file.parent/target.split('#')[0]).resolve()
    if not p.is_relative_to(root.resolve()):raise ValueError('Local reference escapes repository')
    if not p.exists():raise ValueError('Missing local reference '+target)
    return p

def validate(root=ROOT):
    errors=[];root=Path(root)
    skills=[root/'SKILL.md',*sorted((root/'skills').glob('*/SKILL.md'))]
    if len(skills)!=7:errors.append('Expected router plus six stage skills')
    names=[]
    for file in skills:
        try:
            text=file.read_text(encoding='utf-8');values=frontmatter(text)
            if set(values)!={'name','description'}:raise ValueError('Expected name and description only')
            name=values['name'];names.append(name)
            expected=NAME if file==root/'SKILL.md' else file.parent.name
            if name!=expected or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',name) or len(name)>64:
                raise ValueError('Invalid or mismatched skill name')
            if not 1<=len(values['description'])<=1024:raise ValueError('Invalid description length')
            if len(text.splitlines())>500:raise ValueError('Keep SKILL.md under 500 lines')
            if 'TODO' in text:raise ValueError('Unfinished initializer placeholder')
            values=ui_metadata((file.parent/'agents/openai.yaml').read_text(encoding='utf-8'))
            if f'${name}' not in values['default_prompt']:raise ValueError('Default prompt names the wrong skill')
        except (OSError,ValueError,TypeError) as exc:errors.append(f'{file.relative_to(root)}: {exc}')
    if len(names)!=len(set(names)):errors.append('Duplicate skill names')
    for file in root.rglob('*.md'):
        text=file.read_text(encoding='utf-8')
        targets=re.findall(r'\[[^\]]+\]\(([^)]+)\)',text)+re.findall(r'(?:src|href)="([^"]+)"',text)
        for target in targets:
            try:local_target(root,file,target)
            except ValueError as exc:errors.append(f'{file.relative_to(root)}: {exc}')
    for file in root.rglob('*.py'):
        try:ast.parse(file.read_text(encoding='utf-8'),filename=str(file))
        except SyntaxError as exc:errors.append(str(exc))
    try:
        cases=json.loads((root/'evals/cases.json').read_text(encoding='utf-8'))
        if not isinstance(cases,list) or not cases:raise ValueError('Expected nonempty evaluation list')
        ids=[]
        for case in cases:
            if not isinstance(case,dict):raise ValueError('Every evaluation must be an object')
            if not all(nonempty(case.get(k)) for k in ('id','skill','prompt')):
                raise ValueError('Evaluation requires nonempty id, skill and prompt')
            if case['skill'] not in names:raise ValueError('Evaluation names an unknown skill')
            rubric=case.get('rubric')
            if not isinstance(rubric,list) or not rubric or not all(nonempty(x) for x in rubric):
                raise ValueError('Evaluation requires nonempty rubric strings')
            if 'input' in case:
                if not nonempty(case['input']):raise ValueError('Evaluation input must be a nonempty path')
                target=local_target(root,root/'README.md',case['input'])
                if target is None or not target.is_file():raise ValueError('Evaluation input must be a local file')
            ids.append(case['id'])
        if len(ids)!=len(set(ids)):raise ValueError('Duplicate evaluation IDs')
    except (OSError,ValueError,KeyError,TypeError) as exc:errors.append('Evaluation catalog: '+str(exc))
    return errors

if __name__=='__main__':
    errors=validate()
    print('\n'.join(errors) if errors else 'PASS: 7 skill schemas, UI metadata schemas, relative file links, evaluation schema and Python syntax')
    sys.exit(bool(errors))
