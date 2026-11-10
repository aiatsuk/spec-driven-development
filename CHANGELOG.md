# Changelog

## 1.1.1 — 2026-11-10

- Skill frontmatter says `model: inherit` and keeps `effort: high`. A frontmatter pin lasts one turn and each model switch
  re-writes the prompt cache; on a session that runs a higher model the 1.1.0 pin moved the planning turn one tier down.
  Start the session on the model that should plan the work.

## 1.1.0 — 2026-10-24

- Skill frontmatter sets `model: opus` and `effort: high`.
- `scripts/agent_check.py` accepts optional `model` and `effort` after `name` and `description`,
  checks their values, and refuses duplicates, indented lines and lines that are not keys.

## 1.0.1 — 2026-10-01

- The fallback YAML parser in the engine is now strict: it refuses invalid verification YAML instead of reading it loosely.

## 1.0.0 — 2026-09-02

- First public release of the Spec Driven Development plugin with Codex and Claude manifests.
- The public-content check scans only tracked files.
