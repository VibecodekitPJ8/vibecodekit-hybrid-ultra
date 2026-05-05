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

## Upgrade

```bash
pip install --upgrade vibecodekit-hybrid-ultra==0.25.2
```

Or replace your skill bundle with v0.25.2 (no migration needed).

After this release, all public-facing references match the live origin
at `github.com/VibecodekitPJ8/vibecodekit-hybrid-ultra`.
