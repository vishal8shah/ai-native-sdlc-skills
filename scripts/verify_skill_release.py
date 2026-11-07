#!/usr/bin/env python3
"""Run GitHub CLI's dry run against a fresh installation of this toolkit."""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from install import NAME, ROOT, STAGES, install


def verify_manifests(installed: Path) -> None:
    """Check each top-level installed manifest against its canonical source."""
    expected = {NAME: ROOT / 'SKILL.md'}
    expected.update({name: ROOT / 'skills' / name / 'SKILL.md' for name in STAGES})
    for name, source in expected.items():
        manifest = installed / name / 'SKILL.md'
        if not manifest.is_file():
            raise ValueError(f'Missing installed skill manifest: {name}')
        if manifest.read_bytes() != source.read_bytes():
            raise ValueError(f'Installed skill manifest differs from source: {name}')

    unexpected = {path.parent.name for path in installed.glob('*/SKILL.md')} - expected.keys()
    if unexpected:
        raise ValueError('Unexpected installed skill manifests: ' + ', '.join(sorted(unexpected)))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    gh = shutil.which('gh')
    if gh is None:
        print('Error: GitHub CLI (gh) is required for this preflight.', file=sys.stderr)
        return 2

    try:
        with TemporaryDirectory(prefix='sdlc-release-preflight-') as work:
            root = Path(work)
            project = root / 'project'
            project.mkdir()
            install(project, 'codex', apply=True)
            layout = root / 'layout'
            layout.mkdir()
            installed = layout / 'skills'
            (project / '.agents' / 'skills').rename(installed)
            verify_manifests(installed)
            print(f'PASS: {len(STAGES) + 1} installed skill manifests match source bytes.', flush=True)
            print('Running gh skill publish --dry-run on the installer layout.', flush=True)
            return subprocess.run([gh, 'skill', 'publish', '--dry-run', str(layout)]).returncode
    except (OSError, ValueError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
