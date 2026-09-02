# Impact and verification

## Contents

- Consequence analysis
- Verification cases
- Actual-diff review
- Completion evidence

## Consequence analysis

Start from behavior, state, data, contracts, permissions, dependencies, compatibility, operations,
and performance. For each material hypothesis record:

- mechanism and violated invariant;
- evidence, plausibility, severity, detectability, and blast radius;
- reproduction prerequisites and controlled dependencies;
- prevention, mitigation, verification, owner, or explicit waiver.

Consider duplication, loss, reordering, stale state, partial success, retry ambiguity, races,
permission leakage, compatibility regression, rollout/rollback failure, observability gaps, and
performance degradation only where the system makes them plausible.

## Verification cases

For Critical, High, and correctness-critical Medium risks define:

- exact setup and fixtures;
- ordered actions with expected result and how to observe it;
- intermediate observations that localize a failure;
- final stable state and prohibited outcomes;
- authoritative oracle and exact side-effect count where relevant;
- the ticket, design, spec, or ADR that defines the expectation;
- evidence path, cleanup, repetition, timeout, flake policy, and safety class.

A case is written for someone who did not design the change. Read
[test-case-quality.md](test-case-quality.md) for the full field contract, the step and oracle
contracts, the documentation binding, and the reviewer rubric; the same bar applies to cases
written inside a planning package and to cases produced by `/spec check`.

Map every changed requirement scenario to a test, evaluation, proof, or approved waiver. Structural
validation supplements domain checks; it never replaces them.

## Actual-diff review

Inventory actual added, modified, deleted, renamed, generated, configuration, dependency, data, and
contract surfaces. Compare them with the planned change surface. Every unexpected surface needs a
disposition:

- expected indirect consequence;
- implementation defect to fix;
- material baseline deviation requiring revision and reapproval;
- verified non-material change with evidence;
- explicit waiver with owner and revisit trigger.

Use repository-native diff tooling when it is authoritative. `scripts/spec_flow.py begin-verify`
provides a deterministic directory-tree fallback and metadata-only hashes.

## Completion evidence

`verification-report.md` records commands/scenarios, environment, revision, expected oracle, actual
result, evidence, residual risk, owner, and verdict. Completion requires:

- approved baseline still matches or an explicitly reapproved revision;
- all actual surfaces reviewed;
- no unresolved material finding or blocker;
- required checks pass;
- verdict is `PASS` or governed `PASS_WITH_WAIVERS`.

Do not convert skipped, unavailable, flaky, or stale checks into a passing claim.
