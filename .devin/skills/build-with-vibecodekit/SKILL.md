# Build a project with VibecodeKit Hybrid Ultra (Devin-session skill)

Auto-discoverable skill for **Devin** sessions that want to use
VibecodeKit Hybrid Ultra as the methodology backbone when building or
auditing a project. Devin doesn't have native `/slash` command routing
like Claude Code, but it can drive the same 8-step pipeline through the
Python CLI (`python -m vibecodekit.cli <subcommand>`) + by reading the
slash-command markdown files as prompt templates.

## When to invoke this skill

- User asks Devin to "build a project using vibecodekit pipeline".
- User wants Devin to walk through the **VIBECODE-MASTER v5** 8-step
  pipeline (scan → RRI → vision → blueprint → task graph → build →
  verify → ship).
- User wants Devin to run the **conformance audit** (97 probes) or
  **permission engine** (6-layer classification) before merging a PR.
- User mentions any of: `vibe`, `vibecodekit`, `VibecodeKit`,
  `vck-ship`, `vck-review`, `rri`, `RRI-T`, `RRI-UX`, `scaffold preset`,
  `permission engine`, or specific subcommands like `vibe scaffold`,
  `vibe audit`, `vibe permission`.

## Setup (one-time per Devin session)

```bash
# 1. Clone the repo (skip if already at /home/ubuntu/repos/vibecodekit-hybrid-ultra)
cd /home/ubuntu/repos
git clone https://github.com/VibecodekitPJ8/vibecodekit-hybrid-ultra.git || true
cd vibecodekit-hybrid-ultra

# 2. Editable install OR just set PYTHONPATH
pip install -e . 2>/dev/null || true        # picks up scripts/vibecodekit/...
# OR (no install): prefix every command with PYTHONPATH=./scripts

# 3. Verify health (~2 seconds, offline)
PYTHONPATH=./scripts python -m vibecodekit.cli demo
# Expected output: 6 sections — doctor, permission, audit, scaffold preview, intent router, MCP selfcheck
```

After setup, all `vibe <subcommand>` calls from this skill assume the
Devin session is in `/home/ubuntu/repos/vibecodekit-hybrid-ultra/` (or
the user's target project root with `PYTHONPATH` pointing at the
vibecodekit scripts dir).

## CLI surface (what Devin can drive directly)

| Subcommand | Purpose | Devin can call? |
|:-----------|:--------|:---------------:|
| `vibe demo` | All-in-one offline tour (6 sections, ~2s) | ✓ |
| `vibe doctor [--root <dir>]` | Health-check repo layout (32+ checks) | ✓ |
| `vibe audit [--threshold 1.0] [--json]` | 97-probe conformance self-test | ✓ |
| `vibe permission "<cmd>" [--user-runtime]` | Classify shell command (6-layer pipeline) | ✓ |
| `vibe scaffold list` | List 11 presets | ✓ |
| `vibe scaffold preview <preset>/<stack>` | Dry-run scaffold (no files written) | ✓ |
| `vibe scaffold apply <preset>/<stack> --target <dir>` | Materialise scaffold to a target dir | ✓ |
| `vibe rri-t <jsonl>` | Validate RRI-T release-gate JSONL (7 dim × 8 axes) | ✓ |
| `vibe rri-ux <jsonl>` | Validate RRI-UX release-gate JSONL (Flow Physics) | ✓ |
| `vibe intent classify "<text>"` | Map free-form prose to canonical verb | ✓ |
| `vibe intent route "<text>"` | Full route (verb + preset + locale) | ✓ |
| `vibe memory add <tier> "<note>"` | Write to 3-tier memory (user/project/team) | ✓ |
| `vibe memory retrieve <tier> "<query>"` | Lexical+embedding hybrid retrieval | ✓ |
| `vibe subagent spawn <role> "<task>"` | Spawn ACL-enforced sub-agent (7 roles) | ✓ |
| `vibe task <action>` | 7-task-kind runtime (`start`, `agent`, `list`, ...) | ✓ |
| `vibe mcp <action>` | Manage MCP servers (`register`, `tools`, ...) | ✓ |
| `vibe ship [--target vercel\|fly\|...] [--prod]` | Deploy orchestrator (7 targets) | ✓ (real deploys need creds) |
| `vibe verify coverage` | Compute REQ-* coverage from blueprint+report | ✓ |

Full list: `vibe --help` shows all 31 subcommands.

## 8-step pipeline — Devin walkthrough

Each step has a recommended **CLI call** (Devin runs directly) and a
companion **slash-command markdown** (Devin can read for prompt-style
guidance). Slash commands live in `update-package/.claude/commands/`.

### Step 1 — SCAN

Read the repo layout, dependencies, and any existing docs. No CLI
subcommand for "scan" specifically — use `vibe doctor` for invariant
check, and use Devin's native `find`/`read`/`grep` tools for exploration.

```bash
vibe doctor --root <project>          # invariant health check
find <project> -type f -name "*.md" | head -20
```

Companion slash command: `update-package/.claude/commands/vibe-scan.md`.

### Step 2 — RRI (Reverse Requirements Interview)

5 personas (PM / engineer / designer / QA / ops) × 3 modes (CHALLENGE /
GUIDED / EXPLORE) ask up to 16 questions. No subcommand starts an
interactive session — Devin reads the question bank and synthesises a
session manually.

```bash
cat assets/rri-question-bank.json | jq '.buckets[] | select(.name == "saas")'
# Devin then writes runtime/rri/cycle-<N>/answers.jsonl
```

Companion: `update-package/.claude/commands/vibe-rri.md`, `vibe-rri-ui.md`.

### Step 3 — VISION

Devin writes `vision.md` (1-line goal + 3 KPIs + non-goals) based on RRI
answers. Reference template:
`update-package/.claude/commands/vibe-vision.md`.

### Step 4 — BLUEPRINT

Devin writes `blueprint.md` (architecture + data model + interface +
REQ-* matrix). Reference template:
`update-package/.claude/commands/vibe-blueprint.md` +
`references/35-blueprint-template.md`.

### Step 5 — TASK GRAPH

Devin breaks the blueprint into 5–30 TIPs (Task Instruction Pack —
small JSON files in `runtime/tasks/`). For ad-hoc work, just write the
JSON files; for structured orchestration use `vibe task`:

```bash
vibe task start <kind> '<json-payload>'
vibe task list
vibe task status <task-id>
```

Reference: `references/31-tip-runtime.md`.

### Step 6 — BUILD

For each TIP, Devin either:

- **Builds inline** (writes code with native edit/write tools), or
- **Delegates to sub-agent** with ACL:

```bash
vibe subagent spawn builder "<TIP description>"
```

7 ACL-enforced roles: `coordinator`, `scout`, `builder`, `qa`,
`security`, `reviewer`, `qa-lead`. Only `builder` has `can_mutate=True`
by default. Reference: `references/14-subagent-acl.md`.

### Step 7 — VERIFY

Run release-gate JSONL through the methodology validators:

```bash
vibe rri-t  tests/rri-t-touchfiles.json     # 7 dims × 8 stress axes
vibe rri-ux runtime/rri/ux-flags.json       # Flow Physics
vibe verify coverage                         # REQ-* coverage from blueprint
vibe audit --threshold 1.0                   # 97 probes (regression guard)
```

Reference: `references/RRI-T_METHODOLOGY.docx`,
`references/RRI-UX_METHODOLOGY.docx`.

### Step 8 — SHIP

```bash
vibe ship --target vercel --prod             # real deploy (needs creds)
vibe ship --target vercel --dry-run          # DryRunner, safe to call from Devin
git add . && git commit -m "..." && git push  # native git via Devin
```

Reference: `update-package/.claude/commands/vck-ship.md` (atomic
test → review → qa → commit → push → PR flow).

## ACL — what Devin should NOT do without user approval

| Action | Default | Why |
|:-------|:-------:|:----|
| `vibe permission "<destructive cmd>"` | OK to **classify** | Read-only, just returns allow/deny |
| Run `rm -rf` / `sudo` / `dd` / `kubectl delete` | **DENY** | Permission engine layer 1 blocks; Devin should never bypass |
| `vibe ship --prod` | **ASK USER** | Real deploy to production |
| `vibe scaffold apply ... --target /home/ubuntu/repos/<existing>` | **ASK USER** | May overwrite existing files |
| `git push --force` | **NEVER** (default rules) | Stated in core rules |
| Modify `tests/test_canonical_org_no_bypass.py` or `tests/test_no_further_rebrands.py` | **NEVER** | Audit-trail-locked tests |

When in doubt, classify the command first:

```bash
vibe permission "<command>" --user-runtime
# exit 0 = allow, exit 2 = deny
```

`--user-runtime` keeps denial state in `~/.vibecode/` instead of the
project's `$cwd/.vibecode/runtime/denials.json`, avoiding pollution of
the working tree (added v0.25.3+).

## Demo script — end-to-end programmatic walkthrough

For a full programmatic demo of the 8-step pipeline (no Claude Code,
no slash commands, just Python), run:

```bash
PYTHONPATH=./scripts python examples/devin_pipeline_demo.py --target /tmp/myproject
```

This walks through all 8 steps with annotated output. Source:
[`examples/devin_pipeline_demo.py`](../../../examples/devin_pipeline_demo.py).

## Reference docs (ordered by depth)

| Doc | Length | When to read |
|:----|:------:|:-------------|
| [`README.md`](../../../README.md) §🇻🇳 Hướng dẫn tiếng Việt | ~275 dòng | First read — comprehensive cheatsheet (VN) |
| [`docs/GUIDE_NONTECH_BEGINNER.md`](../../../docs/GUIDE_NONTECH_BEGINNER.md) | ~800 dòng | Worked example A→Z "app quản lý chi tiêu" |
| [`QUICKSTART.md`](../../../QUICKSTART.md) | ~150 dòng | 5-min refresher |
| [`USAGE_GUIDE.md`](../../../USAGE_GUIDE.md) | ~2700 dòng | Deep reference: 31 CLI + 42 slash + 7 sub-agent + 33 hook + 97 probe |
| [`SKILL.md`](../../../SKILL.md) | ~250 dòng | Claude/Cursor skill manifest (yaml frontmatter) |
| [`references/00-overview.md`](../../../references/00-overview.md) | ~400 dòng | Architecture + design decisions |
| [`references/VIBECODE-MASTER-v5.txt`](../../../references/VIBECODE-MASTER-v5.txt) | ~600 dòng | Full 8-step methodology spec |
| [`BENCHMARKS-METHODOLOGY.md`](../../../BENCHMARKS-METHODOLOGY.md) | ~500 dòng | What "97/97" actually measures |

## Common gotchas in Devin sessions

1. **`ModuleNotFoundError: vibecodekit`** — either `pip install -e .`
   or prefix with `PYTHONPATH=./scripts`. Skill assumes one of these is
   set.
2. **`vibe permission` writes `.vibecode/runtime/denials.json` into the
   target project** — always pass `--user-runtime` for ad-hoc demos to
   keep state in `~/.vibecode/`.
3. **`vibe scaffold apply` is destructive** — it writes files into the
   `--target` directory. Use `vibe scaffold preview` first to inspect.
4. **`vibe ship` without `--dry-run` triggers real deploys** — only run
   with `--target` set + explicit user approval.
5. **Slash commands in `update-package/.claude/commands/` are NOT
   directly executable from Devin** — they are markdown prompt templates
   for Claude Code / Cursor. Devin should read them for guidance, then
   chain the corresponding `vibe <subcommand>` CLI calls.
6. **The 97-probe audit is an internal regression guard**, NOT an
   external code-quality benchmark (no HumanEval / MBPP / SWE-bench).
   See `BENCHMARKS-METHODOLOGY.md`.

## Verifying skill activation

When this skill is loaded, Devin should be able to answer:

- "What 8 steps does VIBECODE-MASTER v5 cover?" → Scan / RRI / Vision /
  Blueprint / Task graph / Build / Verify / Ship.
- "What does `vibe permission` do?" → 6-layer classification pipeline.
- "How many scaffold presets?" → 11 (api-todo, blog, crm, dashboard,
  docs, landing-page, mobile-app, osint-terminal, portfolio, saas,
  shop-online) × 3 stacks (nextjs, fastapi, expo) when available.
- "Where is the worked-example?" → `docs/GUIDE_NONTECH_BEGINNER.md` §4.

If any of these fail, re-read this skill file from the top.
