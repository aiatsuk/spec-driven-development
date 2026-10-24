from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "agent_check.py"
SPEC = importlib.util.spec_from_file_location("agent_check", MODULE_PATH)
assert SPEC and SPEC.loader
agent_check = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = agent_check
SPEC.loader.exec_module(agent_check)

NAME = "name: spec-driven-development"
DESCRIPTION = 'description: "Plan and verify changes."'
ORDER = "optionally model and effort"


class FrontmatterTests(unittest.TestCase):
    def run_check(self, *lines: str) -> None:
        body = "\n".join(["---", *lines, "---", "", "# Skill", ""])
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "SKILL.md").write_text(body, encoding="utf-8")
            original = agent_check.ROOT
            agent_check.ROOT = Path(tmp)
            try:
                agent_check.validate_frontmatter()
            finally:
                agent_check.ROOT = original

    def check(self, *extra: str) -> None:
        self.run_check(NAME, DESCRIPTION, *extra)

    def refuses(self, pattern: str, *lines: str) -> None:
        with self.subTest(lines=lines):
            with self.assertRaisesRegex(SystemExit, pattern):
                self.run_check(*lines)

    def test_name_and_description_alone_pass(self) -> None:
        self.check()

    def test_model_and_effort_pass(self) -> None:
        self.check("model: opus", "effort: high")

    def test_every_effort_level_passes(self) -> None:
        for level in ("low", "medium", "high", "xhigh", "max"):
            with self.subTest(level=level):
                self.check(f"effort: {level}")

    def test_yaml_spellings_of_valid_values_pass(self) -> None:
        for extra in ('model: "sonnet"', "effort: 'high'  # reviewed", "effort : high", "model\t: opus", "effort: high # note"):
            with self.subTest(extra=extra):
                self.check(extra)

    def test_full_line_comment_passes(self) -> None:
        self.run_check(NAME, "# a comment", DESCRIPTION, "  # indented comment", "model: opus")

    def test_model_aliases_and_full_ids_pass(self) -> None:
        for model in ("inherit", "opus[1m]", "claude-opus-5-5", "claude-opus-5-5[1m]", "claude-sonnet-4.5"):
            with self.subTest(model=model):
                self.check(f"model: {model}")

    def test_unsupported_values_fail(self) -> None:
        for extra in (
            "effort: extreme", "effort: extreme  ", "effort: extreme # x", "effort:", "effort: # x",
            "effort : extreme", "effort\t: extreme", "model : not-a-model",
            'effort: "high\'', "effort: 'high", 'effort: "high"#x', 'model: "opus # x"',
            "model: unknown-model", "model: claude--", "model: claude-", "model:",
            "effort: high#x", "effort: high\u00a0# x", 'effort: "high"\u00a0# x',
        ):
            self.refuses("unsupported value", NAME, DESCRIPTION, extra)

    def test_lines_that_are_not_keys_fail(self) -> None:
        for extra in ("model", "effort:high", "-model: opus", "  model: bogus", "\teffort: high"):
            self.refuses("unsupported frontmatter line", NAME, DESCRIPTION, extra)

    def test_unknown_key_fails(self) -> None:
        self.refuses(ORDER, NAME, DESCRIPTION, "model: opus", "context: fork")

    def test_duplicate_key_fails(self) -> None:
        for extra in (("effort: low", "effort: high"), ("model: opus", "model : haiku")):
            self.refuses("each once", NAME, DESCRIPTION, *extra)

    def test_wrong_order_or_missing_name_fails(self) -> None:
        self.refuses(ORDER, "model: opus", NAME, DESCRIPTION)
        self.refuses(ORDER, DESCRIPTION, NAME)
        self.refuses(ORDER, DESCRIPTION, "model: opus")


if __name__ == "__main__":
    unittest.main()
