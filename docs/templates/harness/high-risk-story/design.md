# US-XXX Design

> **Pattern G high-risk template** — sibling to
> [`overview.md`](overview.md), [`execplan.md`](execplan.md),
> [`validation.md`](validation.md).

## Decision Summary

If this story produces 1+ ADRs, list them here with one-sentence
rationales.  Each linked file lives in `docs/decisions/`.

| ADR | Title | Status |
|:----|:------|:-------|
| `docs/decisions/NNNN-*.md` | | proposed/accepted |

## Domain Model Changes

### New entities

| Entity | Fields | Invariants |
|:-------|:-------|:-----------|
| | | |

### Modified entities

| Entity | Change | Migration impact |
|:-------|:-------|:-----------------|
| | | |

## API Surface

### New endpoints

| Method | Path | Auth | Request | Response | Notes |
|:-------|:-----|:-----|:--------|:---------|:------|
| | | | | | |

### Changed endpoints

| Method | Path | Change | Backwards-compat? |
|:-------|:-----|:-------|:------------------|
| | | | |

## Data Model

### New tables

```sql
-- DDL preview (final lives in migration file)
```

### Migrations

| Migration ID | Direction | Risk | Rollback strategy |
|:-------------|:----------|:-----|:------------------|
| | up/down | | |

## Auth & Authorization

(Required section for any story with `auth` or `authorization` flag.)

- Authentication flow:
- Authorization checks:
- Token handling:
- Session lifecycle:

## External Systems

(Required for any story with `external_systems` flag.)

| System | Interaction | Failure mode | Retry / fallback |
|:-------|:------------|:-------------|:-----------------|
| | | | |

## Non-Functional Requirements

- Latency: p50 / p95 / p99 targets
- Throughput: max RPS
- Availability:
- Observability: metrics / logs / traces required

## Out of Scope

Explicitly list what this story does *not* address.  Link follow-up
stories.

- Out 1 → US-YYY
- Out 2 → US-ZZZ

## VibecodeKit Cross-Refs

- Permission engine impact (new commands needing classification):
- Sub-agent ACL change (if any):
- New conformance probe(s):
