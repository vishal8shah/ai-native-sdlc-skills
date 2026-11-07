import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import verify_skill_release as preflight
sys.path.pop(0)


class SkillReleasePreflightTests(unittest.TestCase):
    def test_changed_manifest_stops_before_gh(self):
        original_install = preflight.install

        def corrupt_after_install(project, client, apply):
            original_install(project, client, apply=apply)
            manifest = project / '.agents/skills/sdlc-test/SKILL.md'
            manifest.write_bytes(manifest.read_bytes() + b'\nModified evidence.\n')

        error = io.StringIO()
        with patch.object(preflight.shutil, 'which', return_value='gh'), \
             patch.object(preflight, 'install', side_effect=corrupt_after_install), \
             patch.object(preflight.subprocess, 'run') as run, \
             contextlib.redirect_stderr(error):
            self.assertEqual(preflight.main([]), 2)
        self.assertIn('differs from source: sdlc-test', error.getvalue())
        run.assert_not_called()

    def test_missing_manifest_names_the_skill(self):
        with tempfile.TemporaryDirectory() as work:
            project = Path(work)
            preflight.install(project, 'codex', apply=True)
            skills = project / '.agents/skills'
            (skills / 'sdlc-plan/SKILL.md').unlink()
            with self.assertRaisesRegex(ValueError, 'Missing installed skill manifest: sdlc-plan'):
                preflight.verify_manifests(skills)

    def test_missing_gh_exits_before_install(self):
        error = io.StringIO()
        with patch.object(preflight.shutil, 'which', return_value=None), \
             patch.object(preflight, 'install') as install, \
             contextlib.redirect_stderr(error):
            self.assertEqual(preflight.main([]), 2)
        self.assertIn('GitHub CLI (gh) is required', error.getvalue())
        install.assert_not_called()

    def test_gh_error_propagates_and_temporary_layout_is_removed(self):
        paths = []

        def fail_gh(args):
            self.assertEqual(args[:-1], ['gh', 'skill', 'publish', '--dry-run'])
            layout = Path(args[-1])
            self.assertEqual(len(list(layout.glob('skills/*/SKILL.md'))), 7)
            paths.append(layout.parent)
            return subprocess.CompletedProcess(args, 1)

        with patch.object(preflight.shutil, 'which', return_value='gh'), \
             patch.object(preflight.subprocess, 'run', side_effect=fail_gh), \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(preflight.main([]), 1)
        self.assertEqual(len(paths), 1)
        self.assertFalse(paths[0].exists())
