#!/usr/bin/env python3
"""Archive safety and canonical-manifest assertion regressions; no model calls."""

import copy
import importlib.util
import json
import stat
import tempfile
import unittest
import zipfile
from pathlib import Path

spec = importlib.util.spec_from_file_location("packager", Path(__file__).with_name("package-engineering-skills.py"))
packager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(packager)


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # The actual downloaded canonical schema is provided explicitly.
        import os
        cls.schema = json.loads(Path(os.environ["ENGINEERING_PLUGIN_SCHEMA"]).read_text())
        cls.expected = packager.source_members()

    def archive(self, entries=None, mode=stat.S_IFREG | 0o644):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        path = Path(temp.name) / "test.zip"
        with zipfile.ZipFile(path, "w") as archive:
            for name, data in (entries or list(self.expected.items())):
                item = zipfile.ZipInfo(name)
                item.create_system = 3
                item.external_attr = mode << 16
                archive.writestr(item, data)
        return path

    def test_valid_archive_is_read_back_and_matched(self):
        result = packager.audit_archive(self.archive(), self.expected, self.schema)
        self.assertEqual(result["state"], "READY_FOR_UPLOAD")
        self.assertEqual(len(result["members"]), 4)

    def test_traversal_rejected(self):
        archive = self.archive(list(self.expected.items()) + [("../outside", b"x")])
        with self.assertRaisesRegex(ValueError, "Unsafe ZIP"):
            packager.audit_archive(archive, self.expected, self.schema)

    def test_symlink_rejected(self):
        with self.assertRaisesRegex(ValueError, "regular"):
            packager.audit_archive(self.archive(mode=stat.S_IFLNK | 0o777), self.expected, self.schema)

    def test_extra_or_missing_member_rejected(self):
        for entries in [list(self.expected.items())[:-1], list(self.expected.items()) + [("extra", b"x")]]:
            with self.subTest(entries=len(entries)), self.assertRaisesRegex(ValueError, "Unexpected or missing"):
                packager.audit_archive(self.archive(entries), self.expected, self.schema)

    def test_modified_skill_rejected(self):
        entries = [(name, data + b"changed" if name.endswith("SKILL.md") else data)
                   for name, data in self.expected.items()]
        with self.assertRaisesRegex(ValueError, "Source-byte mismatch"):
            packager.audit_archive(self.archive(entries), self.expected, self.schema)

    def test_duplicate_member_rejected(self):
        entries = list(self.expected.items()) + [next(iter(self.expected.items()))]
        with self.assertWarns(UserWarning):
            archive = self.archive(entries)
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            packager.audit_archive(archive, self.expected, self.schema)

    def test_canonical_schema_rejects_unknown_root_fields_and_wrong_types(self):
        manifest = json.loads(self.expected[f"{packager.NAME}/plugin.json"])
        for mutation in [{**manifest, "skills": "./skills"}, {**manifest, "author": "wrong"},
                         {**manifest, "$schema": "wrong"}, {**manifest, "name": "UPPER"}]:
            with self.subTest(manifest=mutation), self.assertRaises(ValueError):
                packager.check_schema(mutation, self.schema)

    def test_subtitle_and_secret_rejected(self):
        for subtitle in ["x" * 31, "ghp_" + "a" * 30]:
            expected = copy.deepcopy(self.expected)
            name = f"{packager.NAME}/plugin.json"
            manifest = json.loads(expected[name])
            manifest["extensions"]["com.openai"]["interface"]["shortDescription"] = subtitle
            expected[name] = json.dumps(manifest).encode()
            with self.subTest(subtitle=subtitle), self.assertRaises(ValueError):
                packager.audit_archive(self.archive(list(expected.items())), expected, self.schema)


if __name__ == "__main__":
    unittest.main()
