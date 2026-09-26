"""Bounded parser/scope regression checks in synthetic temporary directories."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import check_docs


class DocsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def put(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def test_supported_space_title_percent_and_anchor_links(self):
        self.put("a file.md", "target")
        self.put("README.md", '[space](<a file.md> "title") [encoded](a%20file.md#heading)')
        errors, _ = check_docs.check(self.root)
        self.assertEqual(errors, [])

    def test_missing_link_names_file_and_rule(self):
        self.put("README.md", "[broken](missing.md)")
        errors, _ = check_docs.check(self.root)
        self.assertIn("README.md: TEST-APPLICABILITY", errors[0])

    def test_code_images_reference_external_and_heading_out_of_scope(self):
        self.put(
            "README.md",
            "```md\n[code](absent.md)\n```\n`[inline](absent.md)`\n"
            "![image](absent.png)\n[ref][x]\n[x]: absent.md\n"
            "[external](https://example.invalid) [anchor](#absent)",
        )
        self.assertEqual(check_docs.check(self.root)[0], [])

    def test_nested_markdown_and_json_placeholders(self):
        self.put("docs/a.md", "{{nested_1}}")
        self.put("docs/state.json", '{"value":"{{nested_2}}"}')
        self.assertEqual(len(check_docs.check(self.root)[0]), 2)

    def test_template_placeholders_allowed(self):
        self.put("state.template.json", '{"value":"{{name}}"}')
        self.put("docs/a.template.md", "{{name}}")
        self.assertEqual(check_docs.check(self.root)[0], [])

    def test_hidden_and_runtime_vendor_paths_excluded(self):
        for name in (".hidden/x.md", "data/x.md", "vendor/x.md", "build/x.md"):
            self.put(name, "[broken](absent) {{name}}")
        self.assertEqual(check_docs.check(self.root)[0], [])

    def test_normal_consumer_has_no_vocabulary_policy(self):
        self.put("README.md", "SourceProductAlpha ConsumerProductBeta BusinessEntityExample")
        errors, scope = check_docs.check(self.root)
        self.assertEqual(errors, [])
        self.assertEqual(scope, {"markdown": 1, "json": 0})

    def test_release_manifest_does_not_enable_a_vocabulary_policy(self):
        self.put("tool.py", 'name = "SourceProductAlpha"')
        self.put("README.md", "ConsumerProductBeta BusinessEntityExample")
        self.put("standard-release.json", json.dumps({"files": {"tool.py": "fixture"}}))
        errors, scope = check_docs.check(self.root)
        self.assertEqual(errors, [])
        self.assertEqual(scope, {"markdown": 1, "json": 1})

    def test_explicit_affected_files_scope(self):
        self.put("changed.md", "okay")
        self.put("unchanged.md", "[broken](missing)")
        self.assertEqual(check_docs.check(self.root, ["changed.md"])[0], [])
        with self.assertRaisesRegex(ValueError, "unsupported/missing"):
            check_docs.check(self.root, ["../escape.md"])


if __name__ == "__main__":
    unittest.main()
