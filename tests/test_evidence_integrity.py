import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def module(name):
    spec=importlib.util.spec_from_file_location('integrity_'+name,ROOT/'scripts'/f'{name}.py')
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
s=module('sdlc');v=module('validate_repo')

class DiscoveryMetadataTests(unittest.TestCase):
    def test_description_requires_a_quoted_string(self):
        for raw in ('null','false','123','yes'):
            with self.subTest(raw=raw),self.assertRaises(ValueError):
                v.frontmatter(f'---\nname: example\ndescription: {raw}\n---\n')
    def test_blank_description_is_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)/'repo';shutil.copytree(ROOT,root,ignore=shutil.ignore_patterns('.git','__pycache__'))
            p=root/'SKILL.md';p.write_text(p.read_text(encoding='utf-8').replace(p.read_text(encoding='utf-8').splitlines()[2],'description: " "'), encoding='utf-8')
            self.assertTrue(any('description length' in e for e in v.validate(root)))
    def test_ui_invocation_suffix_does_not_match(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)/'repo';shutil.copytree(ROOT,root,ignore=shutil.ignore_patterns('.git','__pycache__'))
            p=root/'agents/openai.yaml';p.write_text(p.read_text(encoding='utf-8').replace('$ai-native-sdlc-skills','$ai-native-sdlc-skills-NONEXISTENT'), encoding='utf-8')
            self.assertTrue(any('wrong skill' in e for e in v.validate(root)))

class EvidenceIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)/'run'
        s.init_run(self.root,'Example','ID-1','Reviewer')
        self.document='# Synthetic intent\nStatus: READY_FOR_REVIEW\nRecord ID: ID-1\nSource of truth: Existing work item and change records\nAccountable owner: Reviewer\n'
        self.document+=''.join(f'\n## {title}\nSynthetic fixture.\n' for title in s.SECTIONS['plan'])
        (self.root/'intent.md').write_text(self.document, encoding='utf-8')
        d=s.load_run(self.root);d['stages']['plan'].update(status='ready_for_review',evidence=['synthetic-input'])
        s.save_run(self.root,d);s.snapshot(self.root,'plan')
    def test_commented_document_is_not_ready(self):
        p=self.root/'intent.md';p.write_text('<!--\n'+self.document+'\n-->', encoding='utf-8')
        s.snapshot(self.root,'plan');self.assertFalse(s.check_run(self.root,'plan')['valid'])
    def test_fenced_document_is_not_ready(self):
        for fence in ('```','~~~~','  ```markdown'):
            with self.subTest(fence=fence):
                closing='~~~~' if fence=='~~~~' else '```'
                (self.root/'intent.md').write_text(fence+'\n'+self.document+'\n'+closing, encoding='utf-8')
                s.snapshot(self.root,'plan');self.assertFalse(s.check_run(self.root,'plan')['valid'])
    def test_comment_syntax_inside_code_does_not_hide_real_document(self):
        p=self.root/'intent.md';p.write_text('```html\n<!-- literal unclosed marker\n```\n'+self.document, encoding='utf-8')
        s.snapshot(self.root,'plan');self.assertTrue(s.check_run(self.root,'plan')['valid'])
    def test_symlink_ancestor_cannot_alias_run_metadata(self):
        try:(self.root/'alias').symlink_to(self.root,target_is_directory=True)
        except (OSError,NotImplementedError):self.skipTest('Symlinks unavailable')
        with self.assertRaises(s.ValidationError):s.attach_evidence(self.root,'plan','alias/run.json')
    def test_fenced_content_can_satisfy_section_body(self):
        p=self.root/'intent.md';p.write_text(self.document.replace('## Desired outcome\nSynthetic fixture.','## Desired outcome\n```text\nNonblank values succeed.\n```'), encoding='utf-8')
        s.snapshot(self.root,'plan');self.assertTrue(s.check_run(self.root,'plan')['valid'])
    def test_html_literal_inside_inline_code_is_not_raw_html(self):
        p=self.root/'intent.md';p.write_text(self.document+'\nThe literal field tag is `<request>`.\n', encoding='utf-8')
        s.snapshot(self.root,'plan');self.assertTrue(s.check_run(self.root,'plan')['valid'])
    def test_real_document_may_include_examples(self):
        p=self.root/'intent.md';p.write_text(self.document+'\n```\nStatus: DRAFT\n```\n<!-- non-authoritative note -->', encoding='utf-8')
        s.snapshot(self.root,'plan');self.assertTrue(s.check_run(self.root,'plan')['valid'])
    def test_raw_html_in_checked_document_is_rejected(self):
        p=self.root/'intent.md';p.write_text('<div hidden>\n'+self.document+'\n</div>', encoding='utf-8')
        s.snapshot(self.root,'plan');self.assertTrue(any('raw HTML' in x for x in s.check_run(self.root,'plan')['findings']))
    def attach(self):
        (self.root/'implementation.py').write_text('value = 1\n', encoding='utf-8')
        s.attach_evidence(self.root,'plan','implementation.py')
    def test_attached_file_is_verified(self):
        self.attach();r=s.check_run(self.root,'plan')
        self.assertTrue(r['valid']);self.assertEqual(r['evidence_summary']['local_files_verified'],1)
    def test_changed_attached_file_fails(self):
        self.attach();(self.root/'implementation.py').write_text('value = 2\n', encoding='utf-8')
        self.assertTrue(any('Local evidence changed' in x for x in s.check_run(self.root,'plan')['findings']))
    def test_deleted_attached_file_fails(self):
        self.attach();(self.root/'implementation.py').unlink()
        self.assertFalse(s.check_run(self.root,'plan')['valid'])
    def test_snapshot_does_not_bless_changed_attachment(self):
        self.attach();(self.root/'implementation.py').write_text('changed\n', encoding='utf-8');s.snapshot(self.root,'plan')
        self.assertFalse(s.check_run(self.root,'plan')['valid'])
    def test_reference_strings_are_explicitly_unverified(self):
        r=s.check_run(self.root,'plan');self.assertTrue(r['valid'])
        self.assertEqual(r['evidence_summary']['external_references_unverified'],1)
        self.assertTrue(any('not fetched or verified' in x for x in r['warnings']))
    def test_attach_rejects_path_escape(self):
        with self.assertRaises(s.ValidationError):s.attach_evidence(self.root,'plan','../outside.py')
    def test_attach_rejects_metadata_self_reference(self):
        for path in ('run.json','./run.json'):
            with self.subTest(path=path),self.assertRaises(s.ValidationError):s.attach_evidence(self.root,'plan',path)
    def test_repeated_attach_replaces_same_path(self):
        self.attach();s.attach_evidence(self.root,'plan','implementation.py')
        d=s.load_run(self.root);self.assertEqual(len(d['stages']['plan']['evidence']),2)
    def test_accepted_stage_refuses_new_attachment(self):
        self.attach();d=s.load_run(self.root);d['stages']['plan']['status']='accepted';s.save_run(self.root,d)
        with self.assertRaises(s.ValidationError):s.attach_evidence(self.root,'plan','implementation.py')

class IdentityTests(unittest.TestCase):
    def test_initialization_normalizes_edge_whitespace(self):
        with tempfile.TemporaryDirectory() as t:
            r=s.init_run(Path(t)/'run',' Example ',' ID-1 ',' Reviewer ',' Records ')
            self.assertEqual((r['title'],r['record_id'],r['owner'],r['system_of_record']),('Example','ID-1','Reviewer','Records'))
    def test_load_normalizes_legacy_edge_whitespace(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)/'run';d=s.init_run(root,'Example','ID','Reviewer');d['owner']=' Reviewer ';s.save_run(root,d)
            self.assertEqual(s.load_run(root)['owner'],'Reviewer')
    def test_single_line_identity_rejects_controls(self):
        for value in ('Line\nbreak','Line\rbreak','Name\u2028break','Name\x00'):
            with self.subTest(value=value),self.assertRaises(s.ValidationError):s.identity(value,'owner')
    def test_synthetic_mode_is_explicit(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)/'run';s.init_run(root,'Example','ID','Reviewer',record_mode='synthetic');r=s.check_run(root)
            self.assertEqual(r['record_mode'],'synthetic');self.assertTrue(any('Synthetic run' in x for x in r['warnings']))

if __name__=='__main__':unittest.main()
