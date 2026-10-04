from __future__ import annotations

import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "release_script", PLUGIN_ROOT / "scripts/release.py"
)
release = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release)

CHANGELOG = """# Changelog

## 2.0.0 — 2026-01-02

- Second line one.
- Second line two.

## 1.0.0 — 2026-01-01

- First release.
"""


class ReleaseScriptTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for relative, _ in release.JSON_VERSION_FILES:
            self._copy(relative)
        self._copy(release.TEST_PIN_FILE)
        self.version = release.read_version(self.root)
        (self.root / release.CHANGELOG).write_text(
            CHANGELOG.replace("2.0.0", self.version), encoding="utf-8"
        )

    def _copy(self, relative: str) -> None:
        target = self.root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(PLUGIN_ROOT / relative, target)

    def test_repository_versions_and_changelog_agree(self) -> None:
        version = release.read_version()
        self.assertEqual(version, release.check(f"v{version}"))

    def test_agreement_passes(self) -> None:
        self.assertEqual(self.version, release.check(f"v{self.version}", self.root))

    def test_mismatched_version_file_fails(self) -> None:
        path = self.root / ".claude-plugin/marketplace.json"
        text = path.read_text(encoding="utf-8")
        path.write_text(
            text.replace(f'"{self.version}"', '"9.9.9"'), encoding="utf-8"
        )
        with self.assertRaisesRegex(release.ReleaseError, "marketplace.json has 9.9.9"):
            release.check(f"v{self.version}", self.root)

    def test_mismatched_test_pin_fails(self) -> None:
        path = self.root / release.TEST_PIN_FILE
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace(f'"{self.version}"', '"9.9.9"'), encoding="utf-8")
        with self.assertRaisesRegex(release.ReleaseError, "test_plugin_bundle.py has 9.9.9"):
            release.check(f"v{self.version}", self.root)

    def test_tag_mismatch_fails(self) -> None:
        with self.assertRaisesRegex(release.ReleaseError, "disagree with v9.9.9"):
            release.check("v9.9.9", self.root)

    def test_missing_changelog_section_fails(self) -> None:
        (self.root / release.CHANGELOG).write_text(
            "# Changelog\n\n## 0.0.1 — 2026-01-01\n\n- Old.\n", encoding="utf-8"
        )
        with self.assertRaisesRegex(release.ReleaseError, "no '## "):
            release.check(f"v{self.version}", self.root)

    def test_bad_tag_fails(self) -> None:
        with self.assertRaisesRegex(release.ReleaseError, "not in the form"):
            release.check(self.version, self.root)

    def test_notes_return_exactly_the_section_body(self) -> None:
        self.assertEqual(
            "- Second line one.\n- Second line two.\n",
            release.changelog_notes(self.version, self.root),
        )
        self.assertEqual("- First release.\n", release.changelog_notes("1.0.0", self.root))


if __name__ == "__main__":
    unittest.main()
