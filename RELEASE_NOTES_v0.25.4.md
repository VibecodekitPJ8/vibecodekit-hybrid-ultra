# Release notes — VibecodeKit Hybrid Ultra v0.25.4

**Tag:** `v0.25.4` (annotated, from `main` HEAD post-PR-J1 merge)
**Date:** 2026-05-05
**Type:** patch — clean release artifact (no new features, no breaking
changes)
**Previous tag:** [`v0.25.3`](RELEASE_NOTES_v0.25.3.md) (2026-05-01)

---

## TL;DR

This release rolls up **cycle 20** (3 merged PRs: #30, #31, #32) and
**cycle 21** (this PR-J1 version bump) into one tagged artifact.

Downstream consumers (PyPI publish, skill-zip bundles, fresh
`git clone --branch v0.25.4`, the `devin-session-init` workflow) can
now pin a single version string instead of resolving the floating tip
of `main`.

| Gate | v0.25.3 | v0.25.4 |
|:-----|:-------:|:-------:|
| Tests | 1566 pass | **1566 pass** (no change) |
| Audit probes | 96/96 | **96/96** (no change) |
| Ruff full repo | clean | clean |
| Mypy `--strict` 9 core | clean | clean |
| New features | n/a | **0** (release-engineering only) |
| Breaking changes | n/a | **0** |

---

## Why a clean tag for a no-feature cycle?

Three reasons:

1. **PyPI / skill-zip publishers** expect each consumable artifact to
   match a tagged commit.  Without a tag, scripts that build
   `vibecodekit-hybrid-ultra-vX.Y.Z-skill.zip` from `main` HEAD would
   produce artefacts that don't correspond to a stable version.
2. **`docs/DEVIN_NEW_SESSION_GUIDE.md`** (shipped in cycle 20 PR #32)
   tells new Devin users to run `git checkout v0.25.4` to pin a
   reproducible setup.  The reference must resolve to an actual tag.
3. **Audit traceability:** the conformance audit at HEAD already
   reports 96/96 with the cycle 20 PR chain merged, but no tag pins
   that commit.  Future "what's the conformance state at vX.Y.Z?"
   queries need a tagged answer.

---

## Cycle 20 PR chain (merged before this release)

### PR [#30](https://github.com/VibecodekitPJ8/vibecodekit-hybrid-ultra/pull/30) — Cycle 20 PR-I1: `.devin` skill + `examples/devin_pipeline_demo.py`

Added two artefacts so Devin sessions can drive the 8-step pipeline
**without** Claude Code:

- **`.devin/skills/build-with-vibecodekit/SKILL.md`** (~200 lines) —
  auto-discoverable Devin skill.  When a Devin session is started in a
  clone of this repo (or in any repo that has a copy of the skill file),
  Devin loads it automatically whenever user prompts mention
  "vibecodekit", "/vibe", "vck-ship", "build with the methodology", or
  similar.  The skill documents:
  - One-time setup (Python ≥ 3.9, `PYTHONPATH=./scripts`, `pip install
    -e .` for editable mode).
  - 17 CLI subcommands (`vibe scan / scaffold / audit / permission /
    doctor / memory / intent / mcp / rri-t / rri-ux / vn-check / config
    / install / ledger / discover`).
  - 8-step pipeline with the exact CLI invocation per step.
  - ACL boundary on what Devin may run autonomously vs. what requires
    explicit user OK.
  - 6 gotchas (most-common new-user pitfalls).

- **`examples/devin_pipeline_demo.py`** (~280 lines) — programmatic
  walkthrough.  Run `PYTHONPATH=./scripts python
  examples/devin_pipeline_demo.py --target /tmp/myproject` and watch
  ~20 deterministic file artefacts get generated end-to-end (vision.md,
  blueprint.md, 4 TIPs, scaffold `api-todo/fastapi`, RRI answers, RRI-T
  touchfiles, intent router classifications).  Offline, no network,
  exit 0.

Bonus: `examples/README.md` registers the new demo + scrubs stale "87
probe" → 96 from a cross-link.  `README.md §6` links the demo so it's
discoverable from the entry-point.

### PR [#31](https://github.com/VibecodekitPJ8/vibecodekit-hybrid-ultra/pull/31) — Cycle 20 PR-I2 hot-fix: Devin Review BUG findings on PR #30

Two BUG findings on PR #30 from the Devin Review pass:

1. **`--keep` flag dead code.**  `args.keep` was declared but never
   referenced anywhere in `main()`.  The help text advertised a
   non-existent `--no-keep` flag — argparse would actually accept
   `--no-keep` literally (eating the next positional arg) and silently
   confuse users.  Fix: switched to `argparse.BooleanOptionalAction`
   (Python 3.9+ — matches the `requires-python` constraint in
   `pyproject.toml`), `default=True`, plus added `if not args.keep:
   shutil.rmtree(target, ignore_errors=True)` cleanup at end of
   `main()`.  Verified both code paths:
   ```
   $ python examples/devin_pipeline_demo.py --target /tmp/keep      # persists
   $ python examples/devin_pipeline_demo.py --target /tmp/nokeep --no-keep  # wiped
   ```

2. **Subprocess env replacement.**  `subprocess.run(env={"PYTHONPATH":
   ...})` *replaces* the entire parent environment.  This works for the
   one shell-out the demo does today (`vibe doctor`), but would silently
   strip `HOME` / `LANG` / `LC_ALL` / `TMPDIR` / `PATH` if the demo
   ever spawns child processes that depend on them.  Fix:
   ```python
   child_env = {**os.environ, "PYTHONPATH": str(REPO_ROOT / "scripts")}
   subprocess.run(..., env=child_env)
   ```
   so parent env propagates and only `PYTHONPATH` is overridden.

### PR [#32](https://github.com/VibecodekitPJ8/vibecodekit-hybrid-ultra/pull/32) — Cycle 20 PR-I3: deep audit cleanup + README §9 + DEVIN_NEW_SESSION_GUIDE

Two streams folded into one PR:

**A. Deep audit drift cleanup — 4 findings sót after cycle 17 cleanup
chain (PR #22 → #26):**

| # | File | Drift |
|:-:|:-----|:------|
| 1 | `scripts/vibecodekit/conformance/_registry.py:3` | "92 conformance probes" docstring → expanded to mention 96 since cycle 16 PR-E1 |
| 2 | `USAGE_GUIDE.md:1424` | "§23 catalog đầy đủ 87 probe" → 96 |
| 3 | `update-package/USAGE_GUIDE.md:1237` | mirror — same |
| 4 | `tests/test_content_depth.py:259-264` | "All 9 scaffold presets ship" comment + 10-entry tuple did not include `osint-terminal` (added cycle 16 PR #21) — regression coverage gap |

**B. Devin new-session workflow doc:**

- **`README.md` §9 new (~150 lines)** — "Dùng tool với Devin session
  mới" — 9 subsections: Devin vs Claude comparison table, prompt
  template + filled example, workflow timeline 5 phases × 8 steps, **10
  prompt templates pre-filled by project type** (saas / blog / api /
  dashboard / osint-terminal / mobile / portfolio / docs / crm / shop),
  auto-discover skill mechanism explained, Q&A 6 entries, ACL
  escalation.

- **`docs/DEVIN_NEW_SESSION_GUIDE.md` new (~400 lines)** — deep-dive
  companion: 1-time install, prompt template + 4 anti-patterns,
  per-step walkthrough (action / output / gate / failure / tip) for all
  8 steps, **5 patterns** (new project / add module / audit / generate
  tests / code review), secret / 2FA / approval workflow,
  troubleshooting 10 errors, glossary 12 terms.

---

## Cycle 21 — this PR (PR-J1)

**Scope:** version bookkeeping only.  No code changes, no doc changes
beyond what's required to surface the new version string.

### Changes

- `VERSION` 0.25.3 → 0.25.4
- 7 mirror surfaces synced via `tools/sync_version.py`:
  - `pyproject.toml [project] version`
  - `manifest.llm.json version`
  - `assets/plugin-manifest.json version`
  - `update-package/.claw.json version`
  - `.devin/skills/build-with-vibecodekit/SKILL.md` frontmatter
  - `update-package/.claude/commands/vck-pipeline.md` frontmatter
  - `tools.json` (regenerated via `tools/gen_tools_json.py`)
- `benchmarks/intent_router_0.25.4.json` generated via
  `PYTHONPATH=./scripts python3 tools/dump_intent_confusion.py`
- Forward-facing doc banners bumped to v0.25.4 in:
  - `README.md` (intro + benchmark filename reference)
  - `USAGE_GUIDE.md`
  - `docs/GUIDE_NONTECH_BEGINNER.md` (3 places: title, cheatsheet,
    footer date 2026-05-01 → 2026-05-05)
  - `BENCHMARKS-METHODOLOGY.md`
  - `update-package/CLAUDE.md` (3 places)
  - `update-package/README.md` (2 places + 1 historical-context note)
- `CHANGELOG.md` + mirror entry `[0.25.4] — 2026-05-05`
- `RELEASE_NOTES_v0.25.4.md` (this file)

### Audit gates at v0.25.4

```
pytest                → 1566 passed, 9 skipped
ruff check .          → All checks passed
audit                 → 96/96 met=True parity=1.0000
mypy --strict scripts/vibecodekit/{permission_engine,scaffold_engine,verb_router,denial_store,_audit_log,tool_executor,team_mode,task_runtime,subagent_runtime}.py
                      → Success: no issues found in 9 source files
```

---

## Migration notes — none

This is a pure bookkeeping bump.  Code behaviour at v0.25.4 is bit-for-
bit identical to `main` HEAD after PR #32 merge.  Existing v0.25.3
installations can upgrade by:

```bash
git pull && git checkout v0.25.4
```

…or by re-running their package-manager install command against the new
tag.

No deprecations, no removed APIs, no config schema changes.

---

## What's next?

Two options openly discussed with the user during cycle 20 wrap-up; not
scheduled in this release:

1. **PyPI publish:** build deterministic wheel/sdist for v0.25.4 +
   `twine upload`.  Pattern documented in cycle 13/14/15 — would land
   as a follow-up cycle 22 if user requests.
2. **Cycle 22 feature backlog:** 12th scaffold preset / probe #97 / new
   sub-agent role / etc.  No commitment yet; awaiting user direction.

---

## Cycle 20 + 21 PR commit map

| PR | Title | Status |
|:--:|:------|:-------|
| [#30](https://github.com/VibecodekitPJ8/vibecodekit-hybrid-ultra/pull/30) | Cycle 20 PR-I1: `.devin` skill + `examples/devin_pipeline_demo.py` | merged |
| [#31](https://github.com/VibecodekitPJ8/vibecodekit-hybrid-ultra/pull/31) | Cycle 20 PR-I2 hot-fix: Devin Review BUG findings on PR #30 | merged |
| [#32](https://github.com/VibecodekitPJ8/vibecodekit-hybrid-ultra/pull/32) | Cycle 20 PR-I3: deep audit cleanup + README §9 + DEVIN_NEW_SESSION_GUIDE | merged |
| PR-J1 | Cycle 21: bump v0.25.4 clean release artifact | **this PR** |

Tag `v0.25.4` will be created from `main` HEAD immediately after PR-J1
merges (annotated tag, `git tag -a v0.25.4 -m "..."`).
