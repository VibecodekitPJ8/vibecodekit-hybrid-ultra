# US-XXX Validation Strategy

> **Pattern G high-risk template** — sibling to
> [`overview.md`](overview.md), [`design.md`](design.md),
> [`execplan.md`](execplan.md).  Pair with
> [`../validation-report.md`](../validation-report.md) for the
> post-implementation report.

## Validation Ladder Requirement

High-risk stories MUST run all 5 layers.  Below, declare *what* each
layer covers — actual results go into the `validation-report.md` after
implementation.

### Layer 1 — Unit

Coverage target:
- Domain rules:
- Edge cases:
- Property tests (if any):

Tests to author:

- [ ] `tests/test_<area>_unit.py::test_<case>`

### Layer 2 — Integration

Coverage target:
- DB roundtrip
- Inter-module contracts
- External SDK mocks

Tests to author:

- [ ] `tests/integration/test_<flow>.py::test_<case>`

### Layer 3 — End-to-End

Coverage target:
- Full user journey (UI → API → DB → response)
- Authentication/authorization happy paths AND denied paths
- Multi-step flow (signup → login → action → logout)

Tests to author:

- [ ] `e2e/test_<journey>.spec.ts`

### Layer 4 — Platform

Coverage target:
- 96-probe conformance still passes
- Permission engine classifies new commands correctly
- Sub-agent ACL boundaries respected
- MCP server health checks pass

Tests to author / run:

- [ ] `vibe audit --threshold 1.0`
- [ ] `vibe permission "<new command>"`
- [ ] `vibe doctor`

### Layer 5 — Release

Coverage target:
- Deploy dry-run succeeds for target platform
- Migration is reversible
- Rollback plan executable in ≤ 1 hour
- Observability dashboard shows expected metrics

Tests to author / run:

- [ ] `vibe ship <target> --dry-run`
- [ ] Migration up→down→up roundtrip on staging
- [ ] Smoke test in staging

## Failure Modes

For each failure mode, document the *signal* (how we detect) and the
*response* (what we do).

| Failure | Signal | Response |
|:--------|:-------|:---------|
| Auth bypass | Audit log alert + 401 spike | Roll back, rotate keys |
| Data corruption | Foreign key violation in error log | Pause writes, run reconciliation |
| External system outage | Circuit breaker open > 5 min | Failover to fallback or degrade gracefully |

## Acceptance Threshold

Each AC must trace to ≥ 1 test in ≥ 1 layer.  Build the AC→test matrix
below — gaps block merge.

| AC | Layer | Test ID |
|:---|:------|:--------|
| AC1 | Integration | tests/integration/test_X.py::test_AC1 |
| AC2 | E2E | e2e/test_Y.spec.ts |

## Sign-off Criteria

- [ ] All 5 ladder layers green
- [ ] AC→test matrix has no gaps
- [ ] Failure modes have signals AND responses defined
- [ ] Rollback plan tested on staging
- [ ] `validation-report.md` populated and linked from `overview.md`
