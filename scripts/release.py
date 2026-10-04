#!/usr/bin/env python3
"""Check release versions and print release notes from CHANGELOG.md.

Commands:
  version               print the version from the primary version file
  check --tag vX.Y.Z    fail unless every version file and the changelog agree
  notes --tag vX.Y.Z    print the CHANGELOG section body for that version
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHANGELOG = "CHANGELOG.md"
PRIMARY_VERSION_FILE = ".codex-plugin/plugin.json"
# Files kept in sync by tests/test_plugin_bundle.py.
JSON_VERSION_FILES = (
    (".codex-plugin/plugin.json", ("version",)),
    (".claude-plugin/plugin.json", ("version",)),
    (".claude-plugin/marketplace.json", ("plugins", 0, "version")),
)
TEST_PIN_FILE = "tests/test_plugin_bundle.py"
TEST_PIN = re.compile(r'self\.assertEqual\("([^"]+)", codex\["version"\]\)')
TAG = re.compile(r"^v(\d+\.\d+\.\d+)$")
HEADING = re.compile(r"^## (\S+) — ", re.MULTILINE)


class ReleaseError(Exception):
    pass


def _json_version(root: Path, relative: str, keys: tuple) -> str:
    try:
        value = json.loads((root / relative).read_text(encoding="utf-8"))
        for key in keys:
            value = value[key]
    except (OSError, ValueError, KeyError, IndexError, TypeError) as error:
        raise ReleaseError(f"{relative}: cannot read version ({error})") from error
    if not isinstance(value, str):
        raise ReleaseError(f"{relative}: version is not a string")
    return value


def read_version(root: Path = ROOT) -> str:
    keys = dict(JSON_VERSION_FILES)[PRIMARY_VERSION_FILE]
    return _json_version(root, PRIMARY_VERSION_FILE, keys)


def version_files(root: Path = ROOT) -> dict[str, str]:
    found = {
        relative: _json_version(root, relative, keys)
        for relative, keys in JSON_VERSION_FILES
    }
    try:
        text = (root / TEST_PIN_FILE).read_text(encoding="utf-8")
    except OSError as error:
        raise ReleaseError(f"{TEST_PIN_FILE}: cannot read ({error})") from error
    match = TEST_PIN.search(text)
    if not match:
        raise ReleaseError(f"{TEST_PIN_FILE}: version pin not found")
    found[TEST_PIN_FILE] = match.group(1)
    return found


def parse_tag(tag: str) -> str:
    match = TAG.match(tag)
    if not match:
        raise ReleaseError(f"tag {tag!r} is not in the form vX.Y.Z")
    return match.group(1)


def changelog_notes(version: str, root: Path = ROOT) -> str:
    try:
        text = (root / CHANGELOG).read_text(encoding="utf-8")
    except OSError as error:
        raise ReleaseError(f"{CHANGELOG}: cannot read ({error})") from error
    headings = list(HEADING.finditer(text))
    for index, heading in enumerate(headings):
        if heading.group(1) != version:
            continue
        start = text.index("\n", heading.start())
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        return text[start:end].strip() + "\n"
    raise ReleaseError(f"{CHANGELOG}: no '## {version} — ' section")


def check(tag: str, root: Path = ROOT) -> str:
    version = parse_tag(tag)
    mismatched = [
        f"{relative} has {found}"
        for relative, found in version_files(root).items()
        if found != version
    ]
    if mismatched:
        raise ReleaseError(
            f"version files disagree with {tag}: " + "; ".join(mismatched)
        )
    changelog_notes(version, root)
    return version


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("version", help="print the current version")
    for name in ("check", "notes"):
        command = commands.add_parser(name)
        command.add_argument("--tag", required=True, help="release tag, vX.Y.Z")
    args = parser.parse_args(argv)
    try:
        if args.command == "version":
            print(read_version())
        elif args.command == "check":
            check(args.tag)
            print(f"OK: {args.tag} matches every version file and {CHANGELOG}")
        else:
            sys.stdout.write(changelog_notes(parse_tag(args.tag)))
    except ReleaseError as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
