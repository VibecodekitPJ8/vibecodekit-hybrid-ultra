# US-XXX Execution Plan

> **Pattern G high-risk template** — sibling to
> [`overview.md`](overview.md), [`design.md`](design.md),
> [`validation.md`](validation.md).

## Build Sequence

Steps must be ordered so each can be validated independently before
proceeding.  Mark dependencies.

| # | Step | Depends on | Owner | Validate via |
|:--|:-----|:-----------|:------|:-------------|
| 1 | | — | | |
| 2 | | 1 | | |
| 3 | | 1, 2 | | |

## Checkpoints

After each numbered checkpoint, run the partial validation ladder and
record outcome.

### Checkpoint α — after step <N>

Validation expected: …
Rollback strategy: …
Sign-off: __________

### Checkpoint β — after step <M>

…

## Risk Mitigation

For each hard gate flagged in `overview.md`, document the active
mitigation during build.

| Hard gate | Mitigation strategy |
|:----------|:--------------------|
| auth | Feature flag, dual-stack rollout, fallback to old endpoint |
| authorization | Shadow-write authorization checks, alert on drift |
| data_model | Reversible migration, two-phase deploy, schema-compat tests |
| audit_security | Add log assertions, OWASP self-check, secret-scan in CI |
| external_systems | Mock SDK in CI, circuit breaker in prod, contract test |

## Rollback Plan

State the explicit rollback per build step:

- Step 1 rollback: …
- Step 2 rollback: …
- Step 3 rollback: …

If a checkpoint fails post-merge, the rollback strategy must be
executable in ≤ 1 hour.  Document it concretely (which migration to
reverse, which feature flag to flip, which deploy to redeploy).

## Communication Plan

- Pre-build: who approves the high-risk classification?
- Mid-build: how often to update stakeholders?
- Post-build: how to announce rollout?  Where to log incidents?

## VibecodeKit Cross-Refs

- Sub-agent profile used (`builder` / `qa` / `security`):
- Permission engine invocations expected (list commands to be classified):
- MCP server integrations needed:
