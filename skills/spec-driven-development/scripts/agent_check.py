#!/usr/bin/env python3
"""Run deterministic, credential-free checks for the complete skill package."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def validate_frontmatter() -> None:
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", text, flags=re.DOTALL)
    if not match:
        fail("SKILL.md frontmatter is missing")
    lines = [line for line in match.group(1).splitlines() if line.strip()]
    keys = [line.split(":", 1)[0].strip() for line in lines if not line.startswith((" ", "\t"))]
    if keys != ["name", "description"]:
        fail(f"frontmatter must contain only name and description, got {keys}")
    if "name: spec-driven-development" not in match.group(1):
        fail("frontmatter name does not match the directory")
    description_match = re.search(r'^description:\s*["\'](.*)["\']$', match.group(1), flags=re.MULTILINE)
    if not description_match or not (1 <= len(description_match.group(1)) <= 1024):
        fail("description must be quoted and 1..1024 characters")
    if len(text.splitlines()) > 200:
        fail("SKILL.md exceeds the local 200-line routing budget")


def validate_structure() -> None:
    required = [
        "agents/openai.yaml",
        "scripts/spec_flow.py",
        "references/workflow.md",
        "references/artifact-contract.md",
        "references/materiality-and-review.md",
        "references/verification.md",
        "references/check-flow.md",
        "references/test-case-quality.md",
        "references/host-integration.md",
        "evals/evals.json",
        "evals/trigger-evals.json",
        "tests/test_spec_flow.py",
    ]
    required += [f"assets/{name}.template.md" for name in (
        "intent", "feature-model", "proposal", "decisions", "spec", "design",
        "impact-analysis", "verification-cases", "test-plan", "tasks", "review",
        "review-brief", "implementation-evidence", "post-implementation-review",
        "verification-report", "check-source", "impact-map", "case-review",
        "verification-brief",
    )]
    required += [
        "assets/spec-session.template.json",
        "assets/check.template.json",
        "assets/verification-config.template.yaml",
    ]
    missing = [path for path in required if not (ROOT / path).is_file()]
    if missing:
        fail(f"required files are missing: {missing}")

    skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    referenced = set(re.findall(r"(?:\(|`)((?:references|scripts|assets)/[^)`\s]+)", skill_text))
    missing_refs = sorted(path for path in referenced if not (ROOT / path).exists())
    if missing_refs:
        fail(f"SKILL.md references missing resources: {missing_refs}")


def validate_evals() -> None:
    quality = json.loads((ROOT / "evals/evals.json").read_text(encoding="utf-8"))
    if quality.get("skill_name") != "spec-driven-development":
        fail("eval skill_name mismatch")
    evals = quality.get("evals")
    if not isinstance(evals, list) or len(evals) < 3:
        fail("quality evals must contain at least three cases")
    ids = [item.get("id") for item in evals]
    if len(ids) != len(set(ids)):
        fail("quality eval IDs must be unique")
    for item in evals:
        for key in ("prompt", "expected_output", "files", "expectations"):
            if key not in item:
                fail(f"quality eval {item.get('id')} lacks {key}")

    trigger = json.loads((ROOT / "evals/trigger-evals.json").read_text(encoding="utf-8"))
    if not isinstance(trigger, list) or len(trigger) < 16:
        fail("trigger evals must contain at least sixteen cases")
    positive = sum(item.get("should_trigger") is True for item in trigger)
    negative = sum(item.get("should_trigger") is False for item in trigger)
    if positive < 8 or negative < 8:
        fail("trigger evals need at least eight positive and eight near-miss negative cases")


def validate_portability() -> None:
    """The package is copied to several tools and machines; it may not carry local paths."""
    machine_specific = re.compile(r"(/Users/[a-z0-9._-]+|/home/[a-z0-9._-]+|[A-Z]:\\\\Users\\\\)", re.IGNORECASE)
    offenders: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in {".md", ".py", ".json", ".yaml", ".yml"}:
            continue
        if "__pycache__" in path.parts:
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if machine_specific.search(line):
                offenders.append(f"{path.relative_to(ROOT)}:{number}")
    if offenders:
        fail(f"machine-specific paths in a portable package: {offenders[:5]}")


def validate_documented_lifecycle() -> None:
    """Every check state the code accepts must appear in the documented lifecycle, and back."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import spec_flow  # noqa: PLC0415 - imported after the path is prepared

    documented = set(re.findall(r"\bCHECK_[A-Z_]+\b", (ROOT / "references/workflow.md").read_text(encoding="utf-8")))
    coded = set(spec_flow.CHECK_STATES)
    if documented != coded:
        fail(f"lifecycle drift: only in docs {sorted(documented - coded)}, only in code {sorted(coded - documented)}")


def shipped_files(*suffixes: str) -> list[Path]:
    return [
        path
        for path in ROOT.rglob("*")
        if path.is_file() and path.suffix in set(suffixes) and "__pycache__" not in path.parts
    ]


def validate_documentation_links() -> None:
    """A relative link that does not resolve sends the agent to a file that is not there."""
    broken: list[str] = []
    for markdown in shipped_files(".md"):
        for text, target in re.findall(r"\[([^\]]+)\]\(([^)]+)\)", markdown.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            if not (markdown.parent / target.split("#")[0]).resolve().exists():
                broken.append(f"{markdown.relative_to(ROOT)}: [{text}]({target})")
    if broken:
        fail(f"unresolvable documentation links: {broken[:5]}")


def validate_no_drafting_markers() -> None:
    """Instructions ship finished. Quoted content is documentation, not a leftover marker."""
    markers: list[str] = []
    for markdown in [ROOT / "SKILL.md", *sorted((ROOT / "references").glob("*.md"))]:
        for number, line in enumerate(markdown.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = re.sub(r"`[^`]*`", "", line)
            if re.search(r"\b(TODO|FIXME|XXX|WIP|TBD)\b", stripped):
                markers.append(f"{markdown.relative_to(ROOT)}:{number}")
    if markers:
        fail(f"unfinished instructions: {markers[:5]}")


def validate_file_hygiene() -> None:
    messy: list[str] = []
    for path in shipped_files(".md", ".py", ".json", ".yaml", ".yml"):
        raw = path.read_text(encoding="utf-8")
        relative = path.relative_to(ROOT)
        if raw and not raw.endswith("\n"):
            messy.append(f"{relative}: no final newline")
        if raw.endswith("\n\n"):
            messy.append(f"{relative}: blank line at end of file")
        if any(line != line.rstrip() for line in raw.splitlines()):
            messy.append(f"{relative}: trailing whitespace")
    for reference in sorted((ROOT / "references").glob("*.md")):
        length = len(reference.read_text(encoding="utf-8").splitlines())
        if length > 200:
            messy.append(f"{reference.relative_to(ROOT)}: {length} lines exceeds the selective-load budget")
    if messy:
        fail(f"file hygiene: {messy[:5]}")


def validate_security_patterns() -> None:
    forbidden = (
        "ssl." + "CERT_NONE",
        "verify" + "=False",
        "curl " + "-k",
        "dangerously" + "-skip-permissions",
    )
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in {".md", ".py", ".json", ".yaml"}:
            continue
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            if token in text:
                fail(f"forbidden pattern {token!r} in {path.relative_to(ROOT)}")


def run(command: list[str]) -> None:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if result.returncode:
        sys.stderr.write(result.stdout)
        sys.stderr.write(result.stderr)
        fail(f"command failed ({result.returncode}): {' '.join(command)}")


def main() -> int:
    validate_frontmatter()
    validate_structure()
    validate_evals()
    validate_portability()
    validate_documented_lifecycle()
    validate_documentation_links()
    validate_no_drafting_markers()
    validate_file_hygiene()
    validate_security_patterns()
    run([sys.executable, "-m", "py_compile", "scripts/spec_flow.py", "scripts/agent_check.py"])
    run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"])
    run([sys.executable, "scripts/spec_flow.py", "env"])
    print("PASS: spec-driven-development package checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
