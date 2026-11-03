#!/usr/bin/env python3
"""Regenerate the README diagrams from the runnable synthetic demo; stdlib only."""
import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def render():
    spec=importlib.util.spec_from_file_location('asset_demo',ROOT/'scripts/demo.py');demo=importlib.util.module_from_spec(spec);spec.loader.exec_module(demo)
    result=demo.run_demo();original=result['original_acceptance'];fixed=result['corrected_acceptance']
    directory=ROOT/'docs/assets';directory.mkdir(parents=True,exist_ok=True)
    hero='''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="430" viewBox="0 0 1200 430" role="img" aria-labelledby="title desc">
<title id="title">AI-Native SDLC Skills: from intent to evidence</title><desc id="desc">Seven reusable skills connect a problem, a change, independent checks and a reviewable decision. Local demo and helper scripts need no API key.</desc>
<rect width="1200" height="430" rx="24" fill="#102c33"/><circle cx="1120" cy="60" r="170" fill="#173d43"/>
<g font-family="Arial, Helvetica, sans-serif"><text x="60" y="62" fill="#93cfbf" font-size="20" letter-spacing="3">AI-NATIVE SDLC SKILLS</text>
<text x="56" y="145" fill="#f3f7ef" font-size="68" font-weight="700">From intent to evidence.</text>
<text x="60" y="193" fill="#bfd5d1" font-size="27">A repeatable delivery loop for humans and coding agents.</text>
<g font-size="25" fill="#edf5ef" text-anchor="middle"><rect x="60" y="235" width="220" height="64" rx="12" fill="#23554e"/><text x="170" y="276">Clear intent</text>
<rect x="340" y="235" width="220" height="64" rx="12" fill="#23554e"/><text x="450" y="276">Bounded change</text>
<rect x="620" y="235" width="220" height="64" rx="12" fill="#23554e"/><text x="730" y="276">Independent checks</text>
<rect x="900" y="235" width="240" height="64" rx="12" fill="#23554e"/><text x="1020" y="276">Reviewable decision</text></g>
<g fill="none" stroke="#8dc9b7" stroke-width="3"><path d="M292 267H327m-9-8 9 8-9 8M572 267H607m-9-8 9 8-9 8M852 267H887m-9-8 9 8-9 8"/></g>
<text x="60" y="370" fill="#d3e7dc" font-size="25">7 portable skills</text><text x="343" y="370" fill="#d3e7dc" font-size="25">Claude Code + Codex</text><text x="720" y="370" fill="#d3e7dc" font-size="25">MIT licensed</text><text x="965" y="370" fill="#d3e7dc" font-size="25">Runnable demo</text></g></svg>'''
    diagram=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="460" viewBox="0 0 1200 460" role="img" aria-labelledby="title desc">
<title id="title">Green tests can encode the wrong requirement</title><desc id="desc">Synthetic demo: the original implementation passes its misleading generated test but passes only {original['passed']} of 7 independent acceptance checks. The corrected implementation passes {fixed['passed']} of 7. Changing the requirement after a content snapshot is detected.</desc>
<rect width="1200" height="460" rx="24" fill="#f0f4ed"/>
<g font-family="Arial, Helvetica, sans-serif" fill="#173b36"><text x="50" y="58" font-size="21" letter-spacing="2">THE GREEN-TEST TRAP / SYNTHETIC DEMO</text>
<text x="50" y="111" font-size="38" font-weight="700">The test can agree with the bug.</text>
<text x="50" y="151" font-size="24">Requirement: reject blank or whitespace-only justification.</text>
<text x="50" y="214" font-size="25">Original implementation</text><text x="970" y="214" font-size="30" font-weight="700">{original['passed']} / 7 pass</text>
<rect x="50" y="232" width="1080" height="31" rx="5" fill="#dce4d7"/><rect x="50" y="232" width="{1080*original['passed']/7:.2f}" height="31" rx="5" fill="#c58c3c"/>
<text x="50" y="312" font-size="25">Corrected implementation</text><text x="970" y="312" font-size="30" font-weight="700">{fixed['passed']} / 7 pass</text>
<rect x="50" y="330" width="1080" height="31" rx="5" fill="#20745a"/>
<text x="50" y="415" font-size="23">Independent expectations catch {original['failed']} misses. Changed evidence also invalidates the snapshot.</text></g></svg>'''
    (directory/'hero.svg').write_text(hero,encoding='utf-8');(directory/'demo.svg').write_text(diagram,encoding='utf-8')
    return result
if __name__=='__main__':
    render();print('Regenerated docs/assets/hero.svg and demo.svg from the synthetic demo')
