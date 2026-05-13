# US-XXX Overview (high-risk)

> **Pattern G high-risk template** — adapted from
> `hoangnb24/harness-experimental`.  High-risk stories use this 4-file
> folder instead of the single `story.md`.  Generate via
> `vibe harness story "<title>" --lane high-risk`.

## Status

planned

## Lane

high-risk

## Why high-risk?

State which hard gates trip or how many flags fired.  Quote the
`vibe harness classify` JSON output verbatim:

```json
{
  "lane": "high-risk",
  "flags_set": [...],
  "hard_gates": [...],
  "reason": "..."
}
```

## Product Contract

Same shape as normal story — describe the behavior this story must make
true.  Be more explicit than usual: enumerate edge cases the validation
ladder must cover.

## Acceptance Criteria

Cap at 5-8 ACs.  If you need more, split the story.

- AC1
- AC2
- AC3

## Companion Files

| File | Purpose |
|:-----|:--------|
| [`design.md`](design.md) | Architecture decisions specific to this story |
| [`execplan.md`](execplan.md) | Step-by-step build & rollout plan with checkpoints |
| [`validation.md`](validation.md) | Validation strategy across the 5-layer ladder |

## Cross-Refs

- ADR(s) this story produced: `docs/decisions/NNNN-*.md`
- TIP equivalent (if pipeline crosses to implementation):
- Conformance probe added:
