from __future__ import annotations

import json
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = PLUGIN_ROOT / "skills/spec-driven-development"


class SpecDrivenDevelopmentBundleTest(unittest.TestCase):
    def test_plugin_is_self_contained(self) -> None:
        required = (
            SKILL_ROOT / "SKILL.md",
            SKILL_ROOT / "agents/openai.yaml",
            SKILL_ROOT / "scripts/spec_flow.py",
            SKILL_ROOT / "scripts/agent_check.py",
        )
        self.assertEqual([], [str(path) for path in required if not path.is_file()])

    def test_manifest_versions_and_names_agree(self) -> None:
        codex = json.loads((PLUGIN_ROOT / ".codex-plugin/plugin.json").read_text())
        claude = json.loads((PLUGIN_ROOT / ".claude-plugin/plugin.json").read_text())
        marketplace = json.loads(
            (PLUGIN_ROOT / ".claude-plugin/marketplace.json").read_text()
        )["plugins"][0]
        self.assertEqual("spec-driven-development", codex["name"])
        self.assertEqual(codex["name"], claude["name"])
        self.assertEqual(codex["name"], marketplace["name"])
        self.assertEqual("1.0.0", codex["version"])
        self.assertEqual(codex["version"], claude["version"])
        self.assertEqual(codex["version"], marketplace["version"])

    def test_codex_manifest_points_at_bundled_skill(self) -> None:
        manifest = json.loads((PLUGIN_ROOT / ".codex-plugin/plugin.json").read_text())
        self.assertEqual("./skills/", manifest["skills"])
        prompts = manifest["interface"]["defaultPrompt"]
        self.assertTrue(prompts)
        self.assertTrue(all("$spec-driven-development" in item for item in prompts))


if __name__ == "__main__":
    unittest.main()
