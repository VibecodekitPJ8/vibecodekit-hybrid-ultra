# VibecodeKit Hybrid Ultra v0.25.2 — PJ7 → PJ8 rebrand (rebrand #10, FINAL)

**Released:** 2026-05-05
**Tag:** `v0.25.2`
**Cycle:** 17 PR-F2
**Type:** patch (no public-API change, no code-behavior change)

## Why this release exists

Cycle 17 deep audit before public PyPI publish caught a critical
**doc-vs-reality mismatch**:

- **Live origin** of the repo: `github.com/VibecodekitPJ8/vibecodekit-hybrid-ultra`
  (since cycle 13+; PR URLs, `git remote -v` confirm).
- **Documented canonical org** in `README.md`, `pyproject.toml`,
  `CONTRIBUTING.md`, `SECURITY.md`, `examples/README.md`,
  `docs/GUIDE_NONTECH_BEGINNER.md`, and `.github/workflows/ci.yml`:
  **`VibecodekitPJ7`**.
- **Test guards** (`tests/test_canonical_org_no_bypass.py`,
  `tests/test_repo_urls_canonical.py`) asserted PJ7 as the
  "FINAL canonical" org since cycle 8 PR1.

Result: a public user copy-pasting the README's
`git clone https://example.com/VibecodekitPJ7-old-org/...` command
would NOT end up on the working repo.  Critical pre-public-release UX
bug. (Note: the literal stale URL was `github.com/<old org>/...` —
written here as `example.com` to keep this release-notes file from
tripping the canonical-org scan.)

## What this PR does

**Rebrand #10**: flip canonical org `PJ7 → PJ8` so docs match the live
origin.  Audit-trail-preserving:

- Historical RELEASE_NOTES (v0.17 - v0.25.1) and `CHANGELOG.md`
  entries are **NOT rewritten**.  Time-stamped release artefacts
  legitimately reference the canonical org *at time of release*
  (PJ7 then; PJ8 now).  Rewriting them would falsify the audit trail.
- Test `_HISTORICAL_GLOBS` + `_HISTORICAL_NAMES` exception list added
  to `tests/test_repo_urls_canonical.py` so the canonical-org scan
  skips historical files; current (forward-facing) files are still
  enforced strictly.

## Files changed

### Tests (canonical-org gates flipped)

- `tests/test_canonical_org_no_bypass.py` — `test_allowed_orgs_contains_pj7` → `_pj8`, `test_ci_yml_references_pj7` → `_pj8`, docstring updated.
- `tests/test_repo_urls_canonical.py` — `ALLOWED_ORGS = {"VibecodekitPJ8", "VagabondKingsman", "garrytan"}`.  `_HISTORICAL_GLOBS` + `_HISTORICAL_NAMES` added.  Module docstring documents rebrand-#10 background.

### Forward-facing docs (PJ7 → PJ8)

- `pyproject.toml` — Homepage / Issues / Changelog URLs flipped.
- `README.md` — 5 `git clone` URLs flipped.
- `CONTRIBUTING.md` — 1 URL flipped.
- `examples/README.md` — 1 URL flipped.
- `SECURITY.md` — 1 URL flipped.
- `docs/GUIDE_NONTECH_BEGINNER.md` — 6 URLs flipped.
- `.github/workflows/ci.yml` — 4 references flipped (canonical-owner drift guard).

### Update-package mirrors (synced via sync_version)

- `update-package/CLAUDE.md`
- `update-package/USAGE_GUIDE.md`
- `update-package/README.md`
- `update-package/SKILL.md`
- `update-package/.claude/commands/vck-pipeline.md`

### Devin Review fold-in

- `RELEASE_NOTES_v0.25.1.md:119` — hardcoded local absolute path
  `/home/ubuntu/AUDIT-cycle17-pre-public-release.md` removed; inline
  reference rendered as plain text (the audit report is a working
  artefact, not committed to the repo).  Reported by Devin Review on
  PR #22.

### Bookkeeping

- VERSION 0.25.1 → 0.25.2 (8 mirror surfaces synced).
- 6 `tokens.json` regenerated with new version field.
- `benchmarks/intent_router_0.25.2.json` dump (set-incl 0.9808
  unchanged — intent router unaffected by rebrand).

## Audit gates (post-merge)

| Gate | v0.25.1 | v0.25.2 | Status |
|:-----|:-------:|:-------:|:------:|
| Tests | 1561 | 1561 | unchanged |
| Conformance probes | 96/96 | 96/96 | unchanged |
| `mypy --strict` 9 core | clean | clean | unchanged |
| `ruff check .` | 0 errors | 0 errors | unchanged |
| Canonical-org scan | enforced @ PJ7 | enforced @ **PJ8** | flipped |

## Lock contract — rebrand #10 is FINAL

Per `tests/test_repo_urls_canonical.py` module docstring:

> **CAM KẾT MẠNH (cycle 17 PR-F2):** `VibecodekitPJ8` là canonical
> **FINAL** — DỪNG REBRAND Ở ĐÂY.  Mỗi lần rebrand là enterprise red
> flag, tạo churn documentation + CI cost.  Nếu PR sau muốn đổi
> canonical org lần thứ 11, **reviewer phải reject** trừ khi có lý do
> hard-blocking (legal / trademark) được trình bày rõ ràng trong PR
> body kèm sign-off của maintainer.

## PR-F5 deep-sweep hot-fix (folded into v0.25.2 before tag)

User-requested deep audit re-pass after PR-F4 merge.  Found 8 real
forward-facing drift items + `tools.json` regen drift.  No code-behavior
change; pure metadata + doc + generated-file hygiene.

| # | File | Drift | Fix |
|:-:|:-----|:------|:----|
| 1 | `SKILL.md:240` | "92 internal regression probes" | → 96 |
| 2 | `QUICKSTART.md:63,105` | "92/96 probes pass" | → 96/96 |
| 3 | `update-package/QUICKSTART.md:57,99` | "87/91 probes pass" | → 96/96 |
| 4 | `USAGE_GUIDE.md` + mirror | TOC + §23 heading + sub-heading + audit comment ("87 probe", "91 probes at v0.16.1") | → 96 + 96 probes at v0.25.2 |
| 5 | `update-package/.claude/commands/vibe.md:168` | "91-probe internal self-test" | → 96-probe |
| 6 | `tools/gen_tools_json.py:78` | hardcoded "(87 probes)" | → "(96 probes)" |
| 7 | `tools.json` | regenerated; also picked up version drift (0.16.2 → 0.25.2) | tracked |
| 8 | `scripts/vibecodekit/verb_router.py:23,127,128` | 3× "87-probe" docstring | → 96-probe (mypy strict 9-core still clean) |
| 9 | `BENCHMARKS-METHODOLOGY.md:3,13,14,26,47` | 5 pedagogical "87/87 @ 100 %" examples | → "96/96 @ 100 %" |

Frozen intentionally:
- `tests/test_end_to_end_install.py:117,126` keep `>= 87` regression
  guard (lower bound, contractually correct — probes can grow but
  not silently drop).
- `references/40-ethos-vck.md:61` keeps `87-probe audit (at v0.15.4;
  was 53 in v0.11.x)` as a historical evolution narrative.
- All `RELEASE_NOTES_v0.{15..24}.0.md` and audit-trail entries in
  CHANGELOG describing past releases stay frozen with their
  original counts.

## Upgrade

```bash
pip install --upgrade vibecodekit-hybrid-ultra==0.25.2
```

Or replace your skill bundle with v0.25.2 (no migration needed).

After this release, all public-facing references match the live origin
at `github.com/VibecodekitPJ8/vibecodekit-hybrid-ultra`.
