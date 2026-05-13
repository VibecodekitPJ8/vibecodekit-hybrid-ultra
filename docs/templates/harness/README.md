# Harness templates (Pattern G)

> Added in cycle 22 / v0.26.0.  See
> [`references/43-harness-engineering.md`](../../../references/43-harness-engineering.md)
> for the full Pattern G rationale + vocabulary map.

These templates are adapted from
[`hoangnb24/harness-experimental`](https://github.com/hoangnb24/harness-experimental)
to give VibecodeKit users a lighter-weight ops layer alongside the full
8-step pipeline.

## Files

| File | Purpose |
|:-----|:--------|
| [`story.md`](story.md) | Normal-lane story packet (single file) |
| [`spec-intake.md`](spec-intake.md) | First-time intake when a user provides a new project spec |
| [`decision.md`](decision.md) | Architecture / process Decision Record (ADR), numbered `NNNN-…` |
| [`validation-report.md`](validation-report.md) | Validation evidence after implementation |
| [`high-risk-story/`](high-risk-story/) | 4-file folder for high-risk lane work |

## Quick start

```bash
# 1. Install templates into your project (alternative to full `vibe install`)
vibe harness init --root /path/to/project

# 2. Classify a new prompt
vibe harness classify "Add a refresh-token endpoint to /api/auth"
# → lane: high-risk, hard_gates: [auth], flags: [auth, public_contracts]

# 3. Generate a story packet
vibe harness story "User can reset password" --lane normal
# → docs/stories/US-002-user-can-reset-password.md

# 4. Generate an ADR
vibe harness decision "Adopt JWT with refresh-token rotation"
# → docs/decisions/0004-adopt-jwt-with-refresh-token-rotation.md
```

## How this interacts with the full VibecodeKit pipeline

| Pipeline step | Pattern G counterpart |
|:--------------|:----------------------|
| Step 1 Scan | `vibe scan` still runs unchanged |
| Step 2 RRI | Optional — Pattern G can replace this with `vibe harness classify` for lighter-weight intake |
| Step 3 Vision | Still used (or replaced by `spec-intake.md` for greenfield) |
| Step 4 Blueprint | Replaced or augmented by `story.md` (for normal lane) or `high-risk-story/*.md` (for high-risk) |
| Step 5 Task graph | `vibe task graph` consumes either TIPs or story packets |
| Step 6 Build | Unchanged — `vibe subagent spawn builder ...` works for both |
| Step 7 Verify | RRI-T / RRI-UX still run; Pattern G adds a `validation-report.md` artifact |
| Step 8 Ship | Unchanged — `vibe ship vercel/...` |

## Attribution

Original templates by `hoangnb24/harness-experimental` (Harness v0).
See [`references/43-harness-engineering.md`](../../../references/43-harness-engineering.md)
for adaptation details.
