# Reference 43 — Harness Engineering Compatibility (Pattern G)

> **Added in cycle 22 / v0.26.0.**  Pattern G adopts a lighter-weight
> "Harness Engineering" ops layer alongside the existing 8-step VIBECODE
> pipeline.  Inspired by OpenAI's Harness Engineering writeup
> (https://openai.com/index/harness-engineering/) and the
> `hoangnb24/harness-experimental` reference repository.

## Why this reference exists

**VibecodeKit Hybrid Ultra ≠ Harness-Experimental** — but they share a
DNA: *both are operating frameworks for AI coding agents.*

- VibecodeKit is **heavy** (8-step pipeline, 96 conformance probes,
  scaffold engine, permission engine, MCP servers, sub-agent ACL, intent
  router, slash command surface).  Maximum capability, maximum opinion.
- Harness Engineering is **light** (templates + risk classifier +
  validation ladder + ADR + test matrix).  Maximum portability, minimum
  baked-in stack.

Pattern G is the bridge: it adds a Harness-style lightweight entry-path
for users who want to drive agent work through a smaller surface than
the full 8-step pipeline.  Existing users keep their slash commands,
scaffold engine, and 96-probe audit untouched.

## When to use which entry path

| Scenario | Use VibecodeKit 8-step | Use Pattern G Harness |
|:---------|:----------------------:|:---------------------:|
| Greenfield project, picks from 11 scaffold preset | ✓ | |
| Existing brownfield repo, want to add an agentic layer | | ✓ |
| Need built-in 96-probe audit + permission engine | ✓ | (audit still runs; permission engine remains active) |
| Want minimal docs-only ops layer; no Python runtime | | ✓ |
| Use Devin session (auto-discovers `.devin/skills/`) | ✓ (skill loads full pipeline) | ✓ (skill also exposes harness verbs) |
| Want OpenAI Harness Engineering vocabulary parity | | ✓ |

Both paths can coexist in the same repo.  Pattern G output (story
packets, ADRs, test matrix rows) is consumed by the full pipeline as
input material when work crosses into implementation.

## Vocabulary map — VibecodeKit ↔ Harness

| Concept | VibecodeKit term | Harness term | Notes |
|:--------|:-----------------|:-------------|:------|
| Agent entrypoint | `SKILL.md` + `.devin/skills/build-with-vibecodekit/SKILL.md` | `AGENTS.md` | Both are discoverable doc files |
| Top-level methodology doc | `references/30-vibecode-master.md` (8-step pipeline) | `docs/HARNESS.md` (human-agent collab model) | Harness is shorter & less prescriptive |
| Risk classification | RRI 5 persona × 3 mode + permission 6-layer | Feature intake 10-flag + 3-lane + hard gates | Harness's flag taxonomy is sharper; both are used together in Pattern G |
| Pre-implementation packet | TIP (Task Instruction Pack) | Story packet (story.md) + high-risk-4-file | Different shapes; Pattern G ships harness templates as alternative |
| Decision record | `docs/DESIGN-LOG.md` (cycle-narrative) | ADR (numbered `0001-…`, `0002-…`) | Harness's ADR added as parallel system; DESIGN-LOG kept for cycle-level narrative |
| Test taxonomy | RRI-T 7 dim × 8 axes | Test matrix story × {unit, integration, e2e, platform, release} | Different shapes; both kept |
| Friction → improvement | `vck-learn` + `.vibecode/learnings.jsonl` + `vck-retro` | `docs/HARNESS_BACKLOG.md` | Functionally equivalent; harness is doc-only |
| Install mechanism | `vibe install <dst>` Python CLI + update-package | `curl ... \| bash install-harness.sh` | Pattern G adds `vibe harness init` shortcut |
| Validation ladder | 96-probe audit + pytest + ruff + mypy strict 9-core | declarative ladder (validate:quick → test:integration → e2e → platform → release) | VibecodeKit ladder is executable; Harness ladder is contractual |

## Pattern G CLI surface

`vibe harness {init, classify, story, decision}`

### `vibe harness init [--root <path>] [--merge|--override] [--dry-run]`

Install Harness v0 templates (5 files in `docs/templates/harness/`)
into a target project, alongside any existing VibecodeKit overlay.
Equivalent to the upstream `curl … install-harness.sh` one-liner but
runs through `tool_executor` (permission engine sees it).

### `vibe harness classify <prompt> [--flags <comma>] [--json]`

Run the 10-flag risk classifier against a prompt string.  Output:

```json
{
  "lane": "high_risk",
  "flags_set": ["auth", "data_model", "audit_security"],
  "hard_gates": ["auth"],
  "reason": "hard gate(s) auth tripped → high-risk regardless of total flag count (3)",
  "validation_required": ["unit", "integration", "e2e", "platform", "release"]
}
```

(The enum value uses the underscore form ``high_risk`` to match the
Python :class:`RiskLane.HIGH_RISK` member; the CLI ``--lane`` argument
accepts both ``high-risk`` and ``high_risk``.)

The classifier is heuristic (keyword + pattern matching), not LLM-
backed.  For LLM-driven classification, pipe through
`intent_router.route()` first then feed the classified verb into
`harness.classify()`.

### `vibe harness story <title> [--lane <tiny|normal|high-risk>] [--id US-XXX]`

Generate a new story packet from `docs/templates/harness/story.md`,
filling in title + lane + auto-incremented `US-NNN` ID.  For
`high-risk` lane, generates the 4-file folder
(`execplan.md` + `overview.md` + `design.md` + `validation.md`).

Output written to `docs/stories/US-NNN-<slug>.md` (or
`docs/stories/US-NNN-<slug>/` for high-risk).

### `vibe harness decision <title> [--status <proposed|accepted|...>]`

Generate next-numbered ADR from `docs/templates/harness/decision.md`
under `docs/decisions/`.  Scans existing `docs/decisions/NNNN-*.md`
files and picks the next ID.

## Risk classifier — 10 flag taxonomy

| Flag | Triggers on (keywords / patterns) | Hard gate? |
|:-----|:----------------------------------|:----------:|
| `auth` | login, logout, session, JWT, password, refresh_token, oauth | ✓ |
| `authorization` | role, permission, RBAC, ACL, tenant, scope, admin | ✓ |
| `data_model` | schema, migration, alembic, unique constraint, drop, delete cascade, retention | ✓ |
| `audit_security` | audit log, PII, sensitive, redact, encryption, secret, vault, OWASP | ✓ |
| `external_systems` | email, payment, stripe, twilio, webhook, queue, SQS, SNS, kafka, provider SDK | ✓ |
| `public_contracts` | API shape, OpenAPI, response envelope, client-visible, breaking change | |
| `cross_platform` | desktop, mobile, browser split, native shell, deep link, electron | |
| `existing_behavior` | refactor, rewrite, replace, deprecate, migrate from | |
| `weak_proof` | (heuristic: prompt mentions a code area with no test coverage) | |
| `multi_domain` | (heuristic: prompt mentions 2+ product domain names) | |

### Lane decision rule

```
hard_gates_count >= 1     → high_risk  (unless user explicitly narrows)
flags_count == 0          → tiny       (no risk surface)
flags_count == 1          → tiny       (single flag, low blast radius)
flags_count in {2, 3}     → normal     (story packet + validation)
flags_count >= 4          → high_risk  (4-file packet + decision)
```

## Pattern G probe (#97)

`probes_governance.py::probe_97_harness_templates_ship` verifies:

1. `docs/templates/harness/{story,spec-intake,decision,validation-report}.md` all exist
2. `docs/templates/harness/high-risk-story/{execplan,overview,design,validation}.md` all exist
3. Classifier is importable + deterministic (same prompt → same lane)
4. CLI accepts `vibe harness classify "test" --json` and returns parseable JSON
5. `references/43-harness-engineering.md` exists + cross-links the templates

## Attribution

Templates in `docs/templates/harness/` are adapted from
`https://github.com/hoangnb24/harness-experimental` (Harness v0, MIT
license assumed pending upstream LICENSE).  Adaptations:

- VibecodeKit-specific cross-links added (link to RRI, scaffold engine,
  permission engine).
- Risk classifier moved into Python (`scripts/vibecodekit/
  harness_classifier.py`) instead of leaving as a doc-only checklist.
- Install path: `vibe harness init` instead of `curl|bash`.

## Cross-references

- `docs/templates/harness/` — template files
- `scripts/vibecodekit/harness_classifier.py` — Python classifier
- `scripts/vibecodekit/cli.py::_cmd_harness` — CLI handler
- `tests/test_harness_classifier.py` — 15+ unit test
- `scripts/vibecodekit/conformance/probes_governance.py::probe_97_harness_templates_ship`
- README §10 — user-facing intro
- USAGE_GUIDE §32 — deep-dive
