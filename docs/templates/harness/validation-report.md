# Validation Report — US-XXX

> **Pattern G template** — adapted from `hoangnb24/harness-experimental`.
> Generated after a story is implemented to capture *executable* proof
> that the acceptance criteria hold.

## Story

Link: `docs/stories/US-XXX-<slug>.md`

Lane: tiny | normal | high-risk

## Implementation Summary

What changed?  List touched files + 1-sentence per change.

| File | Change |
|:-----|:-------|
| | |

## Validation Ladder Execution

Mark each layer required by the story.  Paste evidence in the "Evidence"
column or link to CI logs.

| Layer | Required? | Command | Result | Evidence |
|:------|:---------:|:--------|:-------|:---------|
| Unit | | `pytest tests/test_<area>.py -q` | pass / fail / N tests | |
| Integration | | `pytest tests/integration/test_<flow>.py -q` | | |
| E2E | | `playwright test ...` or equivalent | | |
| Platform | | `vibe audit --threshold 1.0` | 97/97 | |
| Release | | `vibe ship <target> --dry-run` | exit 0 | |

## Acceptance Criteria Trace

For each AC in the story, state how it was verified.

| AC | Verified by | Evidence |
|:---|:------------|:---------|
| AC1 | | |
| AC2 | | |

## Risk Flag Trace

Re-run `vibe harness classify` on the *implemented* surface (file
diff + new public API) and compare to the story's predicted flags.

```json
{
  "predicted": {...},
  "actual": {...},
  "delta": [...]
}
```

If new flags appeared that weren't in the predicted set, document the
mitigation here.

## Regression Audit

- [ ] `vibe audit --threshold 1.0` → 97/97 (or document new probe count)
- [ ] `pytest -q` → all pass (or document the diff)
- [ ] `ruff check .` → clean
- [ ] `mypy --strict <module>` → clean for any touched 9-core module

## Harness Delta Closed

Cross-check the "Harness Delta" section of the story.  If templates /
classifier / probe / RRI question bank were updated, link the PR(s) and
mark closed.

- [ ] All harness deltas shipped or explicitly deferred (with new story
      ID for the deferred work).

## Open Issues / Follow-ups

- Issue 1 (link new story)
- Issue 2

## Sign-off

- Implementing agent: <handle / session URL>
- Reviewer (human or peer agent): <handle>
- Date: YYYY-MM-DD
