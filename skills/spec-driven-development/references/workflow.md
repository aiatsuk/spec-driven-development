# Workflow and lifecycle

## Contents

- Command contract
- Lifecycle
- Status and resumption
- Failure handling

## Command contract

| User command | Required behavior | Deterministic guard |
|---|---|---|
| `/spec new` | Preserve raw intent, discover context, scaffold artifacts, plan autonomously | `init` |
| `/spec status` | Show state, version, blockers, approval validity, next action | `status` |
| `/spec history` | Show this machine's past specification and check work | `list`, `where` |
| `/spec review` | Present `review-brief.md`; do not implement | `validate` |
| `/spec approve` | Record explicit actor, version, timestamp, and semantic fingerprint | `approve` |
| `/spec revise` | Clear approval, increment version, reopen affected planning | `revise` |
| `/spec apply` | Verify approved fingerprint, then enter implementation | `apply` |
| `/spec verify` | Inventory actual diff, disposition surprises, run mapped checks | `begin-verify` |
| `/spec complete` | Close only from passing evidence | `complete` |
| `/spec check <source>` | Run the whole verification pipeline and return one brief | `check-init` … `check-render` |
| `/spec check run` | Execute authorized cases after the human gate | `check-authorize` |

`/spec new` and `/spec check` are the two commands a user needs. Everything else is an internal
stage or an expert override; never make the user sequence the internal passes.

Slash commands are semantic conventions. If the host passes ordinary text, interpret it exactly as
the corresponding command without claiming that the host registered a native command.

## Lifecycle

```text
NEW -> INTENT_CAPTURED -> CONTEXT_DISCOVERY -> DECOMPOSING
-> SPECIFYING -> ANALYZING_IMPACT -> DESIGNING_VERIFICATION
-> PLANNING -> REVIEWING -> WAITING_APPROVAL -> APPROVED
-> IMPLEMENTING -> POST_IMPLEMENTATION_REVIEW -> VERIFYING -> DONE
```

`BLOCKED` remembers the state it interrupted. Resume only after all blocking decisions have a
resolution. `REVISING` clears approval and returns to the earliest phase affected by the change.

Use `advance` only for ordinary planning transitions. `APPROVED`, `IMPLEMENTING`, and `DONE` are
privileged states entered only by `approve`, `apply`, and `complete`.

A check session records `mode: check` and uses its own lifecycle:

```text
CHECK_NEW -> CHECK_SOURCE_RESOLVED -> CHECK_CHANGE_ANALYZED -> CHECK_SURFACE_MAPPED
-> CHECK_RISK_ITERATING -> CHECK_CASES_DRAFTED -> CHECK_CASES_REVIEWED
-> CHECK_ENVIRONMENT_PLANNED -> CHECK_BRIEF_READY -> CHECK_EXECUTING -> CHECK_DONE
```

`CHECK_BRIEF_READY` may return to `CHECK_RISK_ITERATING` when review or user feedback opens a new
risk. `CHECK_EXECUTING` and `CHECK_DONE` are privileged states entered only by `check-authorize`
and `complete`. A check may complete with `FAIL`: finding a real defect is a successful check, and
a planning session may not. Read [check-flow.md](check-flow.md) for the pipeline itself.

## Status and resumption

Persist `spec-session.json` after every meaningful transition, decision, or gate. Report:

- current state and `spec_version`;
- completed phases;
- open blockers and unresolved Critical findings;
- whether approval exists and still matches;
- one concrete next action.

When the active interaction ends before completion, record state and stop. Never imply polling,
background execution, or automatic continuation.

## Failure handling

- Stale revision: reload status; do not overwrite newer state.
- Malformed session: preserve the file, report the validation error, and recover from reviewed
  evidence rather than guessing.
- Baseline drift: block apply and require `revise` plus new review and approval.
- Missing artifact: return to the owning planning phase.
- Tool unavailable: preserve the same semantic gate manually and record reduced automation.
