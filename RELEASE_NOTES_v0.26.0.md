# VibecodeKit Hybrid Ultra v0.26.0 — Harness Engineering Pattern G

**Release date:** 2026-05-05
**Cycle:** 22 (PR-K1)
**Type:** Minor — additive new CLI surface, no breaking changes
**Prior tag:** [v0.25.4](RELEASE_NOTES_v0.25.4.md)
**PR commit map:** PR #34 (cycle 22 PR-K1)

---

## TL;DR

Adds a lightweight **Harness Engineering ops layer** alongside the
existing 8-step VIBECODE pipeline.  Inspired by OpenAI's
[Harness Engineering](https://openai.com/index/harness-engineering/)
writeup and the
[`hoangnb24/harness-experimental`](https://github.com/hoangnb24/harness-experimental)
reference repository.

**Why Pattern G additive?**  VibecodeKit Hybrid Ultra is heavy
(96+ probes, scaffold engine, permission engine, 42 slash commands).
Harness Engineering is light (templates + risk classifier +
validation ladder + ADR + test matrix).  Both share the same DNA —
"operating framework for AI coding agents" — but optimise for
different user surfaces.  Pattern G adds a *complementary* lighter
entry path without breaking any existing flow.

**100 % backwards-compatible.**  Existing users keep their slash
commands, scaffold engine, 8-step pipeline, and audit gates
unchanged.  New users get a lighter onboarding path via
`vibe harness init` + `vibe harness classify`.

---

## What ships

### 1. New CLI surface — `vibe harness {classify, init, story, decision}`

```bash
# 10-flag risk classifier (heuristic keyword + manual override)
vibe harness classify "Add a refresh-token endpoint" --json
# → lane: high_risk, hard_gates: [auth], flags: [auth]

# Copy 9 Harness templates into a target project
vibe harness --root /path/to/project init

# Scaffold a US-NNN story packet (auto-classifies lane)
vibe harness --root . story "User can reset password"
# → docs/stories/US-001-user-can-reset-password.md (or 4-file folder for high-risk)

# Scaffold a numbered ADR
vibe harness --root . decision "Adopt JWT with refresh-token rotation"
# → docs/decisions/0001-adopt-jwt-with-refresh-token-rotation.md
```

### 2. Risk classifier — 10 flags, 3 lanes, 5 hard gates

| Flag | Hard gate? | Triggered by (example keywords) |
|:-----|:----------:|:--------------------------------|
| `auth` | ✓ | login, JWT, refresh token, session, oauth |
| `authorization` | ✓ | RBAC, ACL, role, tenant, admin-only |
| `data_model` | ✓ | schema, migration, alembic, drop column |
| `audit_security` | ✓ | audit log, PII, redact, encryption, vault |
| `external_systems` | ✓ | stripe, twilio, webhook, queue, SQS |
| `public_contracts` | | OpenAPI, response envelope, breaking change |
| `cross_platform` | | desktop, mobile, deep-link, electron |
| `existing_behavior` | | refactor, rewrite, replace, deprecate |
| `weak_proof` | | "no tests", "untested", "missing coverage" |
| `multi_domain` | | "billing and auth", "multi-domain" |

**Lane decision rule:**
- ≥ 1 hard gate hit → `high_risk` (unless user explicitly narrows)
- 0/1 flag, no hard gate → `tiny`
- 2-3 flags, no hard gate → `normal`
- ≥ 4 flags, no hard gate → `high_risk`

### 3. 9 mirrored templates under `docs/templates/harness/`

- `README.md` — index + quick start
- `story.md` — normal-lane story packet
- `spec-intake.md` — first-time greenfield spec distillation
- `decision.md` — ADR template (numbered `NNNN-…`)
- `validation-report.md` — post-implementation evidence
- `high-risk-story/{overview,design,execplan,validation}.md` — 4-file
  folder for high-risk lane

Templates carry upstream attribution to
`hoangnb24/harness-experimental` per cycle 22 review (see
`references/43-harness-engineering.md` for adaptation notes).

### 4. New reference doc — `references/43-harness-engineering.md`

Sections:
- Why VibecodeKit ≠ Harness-Experimental (but share DNA)
- When to use which entry path (decision table)
- Vocabulary map — VCK ↔ Harness (8 row table)
- CLI surface walkthrough
- 10-flag taxonomy with hard-gate column
- Lane decision rule
- Pattern G probe (#97) contract
- Attribution

### 5. Probe #97 — `97_harness_pattern_g_ships`

Verifies:
1. All 9 harness template files exist under `docs/templates/harness/`.
2. `references/43-harness-engineering.md` exists + cross-links the templates.
3. `harness_classifier.py` is importable + classifier is deterministic.
4. `vibe harness {classify,init,story,decision}` is registered in the CLI parser.

### 6. 41 unit tests + 1 CLI smoke test

`tests/test_harness_classifier.py` covers:
- Single-flag keyword detection (10 parametrised cases)
- Hard-gate escalation (single + multiple)
- Lane decision rule (0/1/2/3/4+ flag boundaries)
- `extra_flags` CLI merge (hyphen + underscore tokenisation)
- Lane override semantics
- Deterministic output (frozen dataclass equality)
- `validation_required` ladder per lane
- JSON serialisation round-trip
- Helper functions: `slugify`, `next_story_id`, `next_adr_id`
- End-to-end CLI smoke test via `subprocess`

---

## Audit gates at v0.26.0 HEAD

```
VERSION                  → 0.26.0
pytest                   → 1607 passed, 9 skipped (was 1566 at v0.25.4)
audit                    → 97/97 met=True parity=1.0000 (was 96/96)
mypy --strict 9 core     → Success: no issues found
ruff check .             → All checks passed
```

---

## Files added

```
references/43-harness-engineering.md
docs/templates/harness/README.md
docs/templates/harness/story.md
docs/templates/harness/spec-intake.md
docs/templates/harness/decision.md
docs/templates/harness/validation-report.md
docs/templates/harness/high-risk-story/overview.md
docs/templates/harness/high-risk-story/design.md
docs/templates/harness/high-risk-story/execplan.md
docs/templates/harness/high-risk-story/validation.md
scripts/vibecodekit/harness_classifier.py
tests/test_harness_classifier.py
RELEASE_NOTES_v0.26.0.md
benchmarks/intent_router_0.26.0.json
```

## Files modified (release bookkeeping)

```
VERSION                                              0.25.4 → 0.26.0
pyproject.toml + 6 mirror surfaces                   version sync
tools.json                                           regen via tools/gen_tools_json.py
tools/gen_tools_json.py                              96 probes → 97 probes
scripts/vibecodekit/cli.py                           +harness subcommand registration
scripts/vibecodekit/conformance/_registry.py         docstring 96 → 97 + cycle 22 note
scripts/vibecodekit/conformance/probes_governance.py +probe #97 (~110 lines)
scripts/vibecodekit/verb_router.py                   96-probe → 97-probe (docstring)
tests/test_repo_urls_canonical.py                    +upstream attribution exception
README.md / USAGE_GUIDE.md / SKILL.md / QUICKSTART.md / GUIDE_NONTECH / DEVIN_NEW_SESSION_GUIDE / BENCHMARKS-METHODOLOGY
                                                     96 → 97 probe count refs + v0.25.4 → v0.26.0
update-package/ mirrors                              same as above
CHANGELOG.md + mirror                                +[0.26.0] entry
```

---

## Migration

**None.** Pattern G is fully additive.

Existing users:
- `vibe scan` / `vibe audit` / `vibe scaffold` / etc. — unchanged
- 42 slash commands — unchanged
- 8-step VIBECODE pipeline — unchanged
- Sub-agent ACL — unchanged
- Permission engine — unchanged
- 9-core mypy strict — unchanged
- Scaffold engine 11 preset × 3 stack — unchanged

New users opting into the lighter Harness path:
1. `git clone https://github.com/VibecodekitPJ8/vibecodekit-hybrid-ultra.git`
2. `vibe harness --root /path/to/your-project init`
3. `vibe harness --root /path/to/your-project classify "<your-feature>"`
4. `vibe harness --root /path/to/your-project story "<story-title>"`

---

## How this interacts with the full pipeline

| Pipeline step | Pattern G counterpart |
|:--------------|:----------------------|
| Step 1 Scan | `vibe scan` still runs unchanged |
| Step 2 RRI | Optional — Pattern G can replace this with `vibe harness classify` for lighter intake |
| Step 3 Vision | Still used (or replaced by `spec-intake.md` for greenfield) |
| Step 4 Blueprint | Replaced or augmented by `story.md` (normal lane) or `high-risk-story/*.md` (high-risk) |
| Step 5 Task graph | `vibe task graph` consumes either TIPs or story packets |
| Step 6 Build | Unchanged — `vibe subagent spawn builder ...` works for both |
| Step 7 Verify | RRI-T / RRI-UX still run; Pattern G adds a `validation-report.md` artifact |
| Step 8 Ship | Unchanged — `vibe ship vercel/...` |

---

## Cross-references

- `references/43-harness-engineering.md` — Pattern G rationale + vocabulary map
- `docs/templates/harness/` — 9 mirrored templates
- `scripts/vibecodekit/harness_classifier.py` — pure-Python classifier
- `scripts/vibecodekit/cli.py::_cmd_harness*` — CLI handlers
- `tests/test_harness_classifier.py` — 41 + 1 unit/integration tests
- `scripts/vibecodekit/conformance/probes_governance.py::probe_97_harness_pattern_g_ships`
- Upstream — https://github.com/hoangnb24/harness-experimental
- Inspiration — https://openai.com/index/harness-engineering/

---

## Acknowledgements

- OpenAI for publishing the Harness Engineering writeup.
- `hoangnb24/harness-experimental` for the open template + risk
  classifier prior art.
- VibecodeKit users who asked "can I get the harness vocabulary without
  the full 8-step pipeline?" — this release is the answer.
