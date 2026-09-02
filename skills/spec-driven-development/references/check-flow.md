# Check flow

`/spec check` is the verification entrypoint. One user command, several internal passes, one
human-facing `verification-brief.md`. Never ask the user to drive the internal stages.

## Contents

- Source resolution
- Pipeline
- Depth modes
- Iteration rules
- Environment and capability plan
- Human gate
- Deterministic commands

## Source resolution

Accept any input and detect its kind without asking:

| Input | Treat as | Authority |
|---|---|---|
| working tree, staged, or `HEAD` diff | implementation | implementation |
| branch or commit range | implementation | implementation |
| GitHub/GitLab/Bitbucket PR or MR | implementation plus stated intent | both |
| ticket, issue, or spec change | stated intent | intent |
| design file, doc page, or ADR | expected behavior | context |
| free text or voice transcript | stated intent | intent |

Preserve every source verbatim in `source.md`; never replace raw wording with a summary. Record
each source in `check.json.sources` with its authority.

When both intent and implementation exist, reconcile them explicitly:

- what the source said it would change;
- what the diff actually changes;
- every divergence, recorded in `intent.divergences` and treated as a risk candidate.

When only a diff exists, reconstruct intent from the code and mark it `reconstructed`, not stated.
When only intent exists, say so and scope the check to design-level risks, not observed behavior.

Collect the documents the check must cite — ticket, design, spec, ADR, dashboard, runbook — into
`check.json.references` with stable `REF-*` IDs. Every risk and every case cites them.

Record the change surface machine-readably in `actual-diff.json`: use repository-native diff
tooling when it is authoritative, otherwise `check-diff --before <tree> --after <tree>`. An empty
risk register is a finding, never a pass; if a change genuinely carries no material risk, record
`no_material_risk_rationale` naming the surfaces you examined.

## Pipeline

```text
source -> intent reconstruction -> actual change analysis -> affected-surface map
-> pass 1 broad risk generation -> pass 2 realism filter -> pass 3 adversarial expansion
-> pass 4 detailed cases -> pass 5 case review -> environment plan -> execution order
-> Verification Brief -> human gate
```

Pass semantics:

1. **Broad.** Generate candidate failures fast and wide. Quantity over precision. No filtering yet.
2. **Realism.** For each candidate decide: is it possible in this architecture; which changed file,
   contract, or document proves it; does a protection already exist; how severe; is checking it
   worth the cost. Drop or downgrade unsupported candidates and record why.
3. **Adversarial.** For surviving risks search variations: simultaneous client and server retry,
   restart between side effect and persistence, duplicate delivery, stale cache, reordered
   requests, partial failure of an external system, old client versions, exact boundary values,
   permission edges, clock skew, migration mid-flight.
4. **Cases.** Turn every surviving Critical, High, and correctness-critical Medium risk into a
   detailed case. Read [test-case-quality.md](test-case-quality.md) before writing them.
5. **Review.** A separate reviewer pass audits the cases against the rubric in
   [test-case-quality.md](test-case-quality.md) and records findings in `case-review.md`.

## Depth modes

`mode` is chosen from blast radius, not asked:

| Mode | Trigger | Minimum passes |
|---|---|---|
| `lite` | local UI, copy, styling, isolated refactor, no contract or persistence change | 2 |
| `standard` | ordinary product feature, bounded state, one owned service | 3 |
| `deep` | any `critical_areas` hit: payments, auth, permissions, persistence, migrations, concurrency, autonomous agent actions, external integrations, or cross-service contracts | 4 |

Compute the suggestion with `check-mode`, then state the chosen mode and its reason in the brief.
Escalate a mode mid-run when a new risk reaches a critical area; never silently downgrade.

## Iteration rules

Continue iterating while any holds:

- a pass produced a new Critical or High risk;
- the affected surface changed;
- an uncovered invariant appeared.

Stop when all hold:

- the configured minimum passes ran;
- two consecutive passes produced no new material risk;
- every Critical and High risk has a case or a recorded waiver;
- the case reviewer found no Critical gap.

`maximum_iterations` is a hard ceiling. Hitting it is a finding: report the unexplored area in the
brief instead of implying full coverage. Record every pass with `check-pass` so the stop decision
is evidence, not judgment.

## Environment and capability plan

List what executing the plan actually needs: services, seeded data, sandbox credentials, network
proxy, clock control, event replay, restart control, log and metric access, evidence paths. Read
the project's `verification` config for what already exists.

When a capability is missing, do not silently weaken the case. Record it in
`environment.missing` with the cases it blocks and the concrete request, for example:
`RISK-004 needs Kafka event replay; add a replay hook to the consumer test harness.`

## Human gate

Stop and ask only when:

- expected behavior is genuinely unclear;
- a check could move real money or touch production;
- fault injection would run outside a sandbox;
- the check is destructive or irreversible;
- criticality depends on a business call;
- someone must accept residual risk.

Otherwise decide and proceed. Reaching `CHECK_BRIEF_READY` is the default stop: the brief is
delivered, execution waits for `check-authorize`. This skill never grants production, destructive,
payment, or publication authority.

## Deterministic commands

```bash
python3 scripts/spec_flow.py list --limit 10          # what this machine has checked before
python3 scripts/spec_flow.py check-init --session-id <slug> --mode auto   # resolves its own location
python3 scripts/spec_flow.py check-diff --root <check-dir> --before <tree> --after <tree>
python3 scripts/spec_flow.py check-mode --root <check-dir> --path src/payments/retry.py
python3 scripts/spec_flow.py check-pass --root <check-dir> --kind broad --new-critical 2 --new-high 3 --summary "<what changed>"
python3 scripts/spec_flow.py check-validate --root <check-dir>
python3 scripts/spec_flow.py check-render --root <check-dir>
python3 scripts/spec_flow.py advance --root <check-dir> --to CHECK_BRIEF_READY
python3 scripts/spec_flow.py check-authorize --root <check-dir> --actor <human> --scope safe
```

`verification-cases.md` and `verification-brief.md` are rendered from `check.json`; edit the JSON
and re-render rather than hand-editing the markdown. Read
[artifact-contract.md](artifact-contract.md) for the check package shape.
