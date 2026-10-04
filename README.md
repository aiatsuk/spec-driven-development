# Spec Driven Development

Spec Driven Development is a self-contained skill and plugin for turning rough software ideas into reviewable, approval-gated specifications and for checking an implementation against its intended behavior and actual diff.

## Included

- recursive intent decomposition from outcome to executable tasks;
- stable decision IDs and explicit human approval gates;
- impact and risk analysis;
- detailed verification cases with observable oracles;
- actual-diff review and lifecycle-safe verification tooling;
- Codex and Claude plugin manifests.

## Use

Install this repository with your host's normal plugin workflow. The root contains a Codex manifest in `.codex-plugin/plugin.json` and a Claude-compatible manifest and marketplace entry in `.claude-plugin/`.

Invoke `$spec-driven-development`, use `/spec new <idea>` to prepare an approval-ready plan, or use `/spec check <source>` to produce a verification brief for a PR, branch, diff, ticket, or design document.

## Verification

```bash
python3 skills/spec-driven-development/scripts/agent_check.py
python3 scripts/public_check.py
```

The first command validates the complete skill package and runs its unit tests. The second checks the public export for Cyrillic text, vendor-specific material, machine-specific paths, secret-like values, and unsafe generated files.

## Releasing

Every release is a `vX.Y.Z` tag on `main` and a GitHub Release whose notes are that version's section in `CHANGELOG.md`.

1. In the release pull request, bump the version in `.codex-plugin/plugin.json`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` and the pin in `tests/test_plugin_bundle.py`, and add a `## X.Y.Z — YYYY-MM-DD` section to `CHANGELOG.md`. `python3 scripts/release.py check --tag vX.Y.Z` confirms they agree.
2. After merge, tag the merged commit on `main` and push the tag:

   ```bash
   git tag -a vX.Y.Z -m "spec-driven-development X.Y.Z" <merged main sha>
   git push origin vX.Y.Z
   ```

3. The release workflow checks the versions, runs the tests and publishes the GitHub Release.

To republish the release for an existing tag, run `gh workflow run release.yml -f tag=vX.Y.Z`.

## Privacy and portability

Specification artifacts are stored outside the project by default. The plugin contains no credentials, user data, lifecycle hooks, network services, or bundled project artifacts.

No license is included because the original source did not specify one.
