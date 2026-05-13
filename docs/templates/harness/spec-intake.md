# Spec Intake — <project name>

> **Pattern G template** — adapted from `hoangnb24/harness-experimental`.
> Use this once at the start of a greenfield project before any RRI or
> story work.  Equivalent to (but lighter than) the VibecodeKit
> `references/35-vision-blueprint-template.md`.

## Source Material

Paste or link the original spec the human handed off.  Do not edit it
in place — preserve the as-received version.

```
<paste spec here>
```

## Distillation

Restate the spec in 3-7 bullets.  Each bullet must be unambiguous to a
new agent reading only this file.

- Bullet 1
- Bullet 2
- Bullet 3

## Personas

| Persona | Goal | Pain today |
|:--------|:-----|:-----------|
| | | |

## Product Surface

| Surface | Description | Owner |
|:--------|:------------|:------|
| | | |

## Domain Boundaries

List the bounded contexts you can already see.  One per row.

| Domain | Responsibility | Cross-domain edge |
|:-------|:---------------|:------------------|
| | | |

## Risk Surface (preliminary)

Run `vibe harness classify "<distilled-spec>"` and paste the JSON output
here:

```json
{
  "lane": "...",
  "flags_set": [...],
  "hard_gates": [...]
}
```

## Initial Story Cuts

List the first 5-10 stories you'd cut.  Mark lane preliminary.

| US ID | Title | Lane (prelim) |
|:------|:------|:--------------|
| US-001 | | |
| US-002 | | |

## Open Questions for the Human

- Q1
- Q2
- Q3

## Next Step

- [ ] Run `vibe harness story <title> --lane <l>` for each US row above.
- [ ] Run `vibe rri start --mode CHALLENGE` to surface deeper assumptions.
- [ ] Decide if the project warrants `vibe install` (full pipeline) or stays Harness-only.
