# Host integration

## Contents

- Portable contract
- Discovery and paths
- Slash-command adapters
- Specialist-agent fallback

## Portable contract

The skill is an Agent Skills directory: `SKILL.md` plus optional `scripts/`, `references/`,
`assets/`, and host metadata. Hosts load `name` and `description` for discovery, then the full
instructions only when relevant. Keep behavior in the portable package and host adapters thin.

## Discovery and paths

Install the whole directory, not only `SKILL.md`. Resolve relative references from the skill root.
Do not copy runtime state into the installed skill; each project stores its own change session.
Project-level skill copies may override user-level copies, so report which path is active when
diagnosing drift.

## Slash-command adapters

`/spec new`, `check`, `status`, `review`, `approve`, `revise`, `apply`, `verify`, and `complete` are
semantic messages. A native host command may forward its arguments to the skill, but must not
duplicate lifecycle logic or bypass guards. If native routing is absent, ordinary text must behave
the same.

Expose only `new` and `check` in user-facing help. Keep approval and apply separate even if a host
supports one-click actions, and keep `check-authorize` separate from producing the brief. Never
claim a native command exists unless discovery proves it.

## Specialist-agent fallback

Independent product, architecture, risk, implementation, and QA passes can improve review quality
when the host supports isolated agents. They are synchronous inputs to one coordinator and cannot
approve, broaden scope, weaken constraints, or bypass state gates.

When specialists are unavailable, run the same passes sequentially in fresh mental/contextual
sections. Preserve artifacts, traceability, human gates, and verification requirements. Do not
imply asynchronous work or reduced safety.
