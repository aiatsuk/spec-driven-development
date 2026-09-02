# Materiality and review

## Contents

- Ask-or-decide rubric
- Decision records
- Cross-artifact review
- Approval and revision

## Ask-or-decide rubric

Interrupt only when the answer can materially change at least one of:

- user-visible behavior or success criteria;
- public or internal contract, data meaning, compatibility, or migration;
- money, permission, privacy, security, legal, or autonomous action;
- destructive or production-affecting verification;
- scope, delivery commitment, or the authoritative oracle.

Follow repository conventions for local, reversible engineering choices. Record a provisional
assumption when it is safe and cheap to reverse; mark it clearly and keep it out of approval if it
changes observable behavior.

## Decision records

Use stable IDs. Each material decision includes:

- question and why it matters;
- concrete options and consequences;
- evidence and recommendation;
- owner and status (`OPEN`, `PROPOSED`, `APPROVED`, `WAIVED`);
- affected requirements, design sections, risks, tests, and tasks.

`OPEN` or `PROPOSED` blocking decisions prevent approval.

## Cross-artifact review

Review the package as one system. Look for:

- source details lost during normalization;
- conflicting requirements, states, or terminology;
- unapproved behavior introduced by design;
- unowned failure, retry, race, recovery, compatibility, or degraded states;
- missing consequence hypotheses or non-authoritative oracles;
- tasks without a requirement/risk/test source;
- scope drift and hidden publication or production actions.

Readiness is `READY`, `READY_WITH_WAIVERS`, or `NOT_READY`. Any blocking decision or unresolved
Critical finding forces `NOT_READY`.

## Approval and revision

Present `review-brief.md` with exact `spec_version`, readiness, decisions, changed surfaces,
Critical/High risks, verification, exclusions, waivers, and next action. Stop for explicit approval.

Approval records identity, timestamp, note, version, artifact manifest, and aggregate fingerprint.
It authorizes the baseline, not implementation. `/spec apply` is a separate action.

A change is material when it affects behavior, scope, contract, risk, architecture, oracle,
migration, permissions, side effects, or delivery commitment. Use `/spec revise`, clear approval,
increment the version, update affected artifacts, review again, and obtain new approval.
