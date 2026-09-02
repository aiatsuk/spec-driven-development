---
name: spec-driven-development
description: "Turn rough feature ideas, voice transcripts, or /spec commands into recursively decomposed, human-reviewed, approval-gated specifications, then govern implementation and actual-diff verification. Also runs /spec check: given a PR, ticket, branch, diff, or spoken description, it reconstructs intent, iteratively generates and filters risks and corner cases, writes detailed documented test cases, and returns one Verification Brief. Use for non-trivial features, migrations, cross-component or high-risk changes, plans that must be approved before coding, requests to decompose, review, approve, apply, verify, or iterate from intent through tested delivery, and requests to work out what a change could break and how to prove it. Do not use for one-step mechanical edits, self-contained factual answers, routine unit tests for touched files, or plain code-review summaries."
---

# Spec-Driven Development

Convert rough intent into a reviewable semantic baseline, stop for explicit approval, then keep
implementation and verification bound to that baseline. Treat `/spec ...` as a semantic command
even when the host has no native slash-command registry.

## Two entrypoints

Everyday work needs only two commands; the rest are internal stages or expert overrides.

| Command | Direction | Output |
|---|---|---|
| `/spec new <idea>` | forward: intent to approved plan | `review-brief.md`, stop for approval |
| `/spec check <source>` | backward: change to proven behavior | `verification-brief.md`, stop before execution |

`/spec check` accepts any source and detects its kind itself: a PR, ticket, issue, branch, commit
range, working diff, design doc, free text, or voice transcript. It runs source resolution, intent
reconstruction, change analysis, several risk-generation and filtering passes, detailed case
design, case review, and environment planning as one invocation. Never ask the user to drive those
stages. Read [references/check-flow.md](references/check-flow.md) before running it and
[references/test-case-quality.md](references/test-case-quality.md) before writing cases.

## Start here

1. Preserve the user's exact wording in `intent.md` before normalizing it.
2. Run `python3 scripts/spec_flow.py init --session-id <slug>` from this skill directory to
   scaffold the package and lifecycle state. The package lands in the machine's artifact store,
   outside the project, so specification work never enters the repository's diff. Report the
   resolved path once; afterwards pass it as `--root`.
3. Continue autonomously through planning. Ask only when a missing answer materially changes
   behavior, contract, permission, privacy, money, migration, compatibility, scope, or the oracle.
4. Stop in `WAITING_APPROVAL` with `review-brief.md`. Approval records the baseline; it never starts
   implementation by itself.

Before ending a planning turn, replace every template placeholder with reviewed content, run
`validate`, and persist the truthful lifecycle state. If a material decision remains open, finish
all unaffected artifacts, record its stable ID, and use `block`; never present scaffold filenames
as an implementation-ready package.

Read [references/workflow.md](references/workflow.md) for command semantics and lifecycle rules.

## Start a check

1. Scaffold with `python3 scripts/spec_flow.py check-init --session-id <slug>`; the package lands
   in the machine's artifact store, never in the project being checked.
2. Preserve every source verbatim in `source.md` and record which sources carry intent and which
   carry implementation.
3. Let `check-mode` choose depth from blast radius. Escalate on a critical-area hit; never
   silently downgrade.
4. Record every risk pass with `check-pass`; the stop rule is evidence, not judgment.
5. Author `check.json`, then `check-render` it into `verification-cases.md` and
   `verification-brief.md`. Show the user the brief, not the internal artifacts.
6. Stop in `CHECK_BRIEF_READY`. Execution requires `check-authorize` from a named human.

## Non-negotiable gates

- Do not synthesize approval or infer it from earlier enthusiasm, silence, readiness, or a task
  request. `/spec approve` and `/spec apply` are distinct actions.
- Block apply unless the current semantic fingerprint exactly matches the approved fingerprint.
- Invalidate approval after any material revision; increment `spec_version` and return to planning.
- Start post-implementation review from the actual changed-file inventory, not the planned list.
- Never execute a check case that is not `safe` without a recorded `check-authorize` actor and
  scope. Reaching a brief is not permission to run it.
- A case that only observes a status code is not verified behavior; observe the actual side effect.
- Do not claim background progress. Persist status and name one resumable next action.
- Preserve repository, user, security, and publication constraints; this skill never grants commit,
  push, merge, deploy, destructive-test, or production authority.

## Recursive model

Decompose only as far as needed to eliminate hidden decisions and create objective oracles:

- L0 raw source intent
- L1 outcome, scope, constraints, non-goals
- L2 capabilities
- L3 journeys and scenarios
- L4 state and transitions
- L5 components, contracts, data, integrations
- L6 consequences, invariants, risks, verification
- L7 milestones, tasks, dependencies, evidence

A leaf is ready when it has one responsibility, an observable result, known dependencies, an
objective oracle, and no hidden material decision. Avoid artificial subdivisions.

Read [references/artifact-contract.md](references/artifact-contract.md) when creating or reviewing
artifacts. Copy the matching files from `assets/` rather than inventing a new package shape.

## Human review

Classify uncertainties before asking. Keep local reversible engineering choices with the agent;
surface material alternatives with stable decision IDs, consequences, a recommendation, and the
exact artifacts affected. Read
[references/materiality-and-review.md](references/materiality-and-review.md) for the rubric,
readiness review, and Review Brief contract.

## Apply and verify

After explicit approval, run `scripts/spec_flow.py apply` before editing. If the guard reports
drift, stop and use `/spec revise`; do not reapprove implicitly.

After implementation:

1. Record implementation evidence.
2. Run `scripts/spec_flow.py begin-verify --before <tree> --after <tree>` or use the repository's
   authoritative diff and write the equivalent `actual-diff.json`.
3. Disposition every unexpected surface and derive new consequence hypotheses where needed.
4. Execute mapped checks with authoritative oracles and exact side-effect counts where relevant.
5. Complete only with `PASS` or governed `PASS_WITH_WAIVERS` and a verification report.

Read [references/verification.md](references/verification.md) before impact analysis, verification
case design, actual-diff review, or completion.

## Host portability

Use the same gates in Codex, Claude Code, OpenCode, Cursor, Code Assistant, and sequential-only
hosts. Specialist agents are an optimization, never a dependency. Read
[references/host-integration.md](references/host-integration.md) only when installing, routing, or
adapting `/spec` for a host.

## Artifact store

Packages live on the machine, not in the project: specification and check work is a record of how
a change was reasoned about, and it must never appear in the repository's diff or a reviewer's
pull request.

```text
$SPEC_FLOW_HOME | $XDG_STATE_HOME/spec-driven-development | ~/.local/state/spec-driven-development
  └── <project-name>-<path-digest>/
        ├── project.json          which real directory this belongs to
        ├── changes/<slug>/       /spec new packages
        └── checks/<slug>/        /spec check packages
```

The project is found by walking up to the enclosing repository, so the same store entry is reached
from any subdirectory. Two checkouts with the same name stay separate: the digest is of the
absolute path. Nothing is written into the project, so no ignore rules are needed.

Use `list` for the machine's history and `where` to resolve a path; never ask the user to remember
one. A repository that genuinely wants its packages versioned alongside the code sets
`verification.artifact_store: repo`, and an explicit `--root` always wins.

## Deterministic tooling

Run commands from the skill directory. `init` and `check-init` resolve their own location; the
other commands take the `--root` those reported:

```bash
python3 scripts/spec_flow.py env
python3 scripts/spec_flow.py list --limit 10
python3 scripts/spec_flow.py where --project <repo>
python3 scripts/spec_flow.py status --root <change-dir>
python3 scripts/spec_flow.py validate --root <change-dir>
python3 scripts/spec_flow.py check-validate --root <check-dir>
python3 scripts/spec_flow.py check-render --root <check-dir>
python3 scripts/agent_check.py
```

The tooling enforces lifecycle, atomic revision-checked writes, baseline hashing, diff inventory,
risk-iteration stop rules, case-quality rules, and coverage thresholds. It does not decide product
semantics or replace human review.

Projects tune thresholds, critical areas, and available test capabilities in
`.spec/verification.yml`; copy `assets/verification-config.template.yaml` to start. Missing
capabilities become explicit requests in the brief, never silently weakened cases.
