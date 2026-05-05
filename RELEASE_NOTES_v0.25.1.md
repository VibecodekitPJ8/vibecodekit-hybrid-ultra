# VibecodeKit Hybrid Ultra v0.25.1 — public-readiness audit pass

**Released:** 2026-05-01
**Tag:** `v0.25.1`
**Cycle:** 17 PR-F1
**Type:** patch (no public-API change, no code-behavior change)
**Compat:** drop-in upgrade from v0.25.0; bump version, replace bundle, done.

## What is this release?

After v0.25.0 (cycle 16 — added the 11th scaffold preset
`osint-terminal`), a **deep audit** was run before public PyPI publish:

```
1561 tests + 96 probes + mypy --strict 9 core + ruff full repo +
vulture dead-code + markdown link integrity + secret scan +
forbidden-module integrity + dependency hygiene
```

Audit produced 1 report ([`AUDIT-cycle17-pre-public-release.md`])
with 19 findings:

| Severity | Count | What |
|:---------|:-----:|:-----|
| 🔴 Critical | 3 | PyPI metadata + 2 broken doc cross-links |
| 🟡 High (count drift) | 4 | stale 92→96 + 10→11 in 4 user docs |
| 🟡 High (PJ7→PJ8) | 6 | clone URLs across README/CONTRIBUTING/SECURITY |
| 🟢 Medium (lint) | 15 | F401 unused imports + 1 F841 unused var |
| 🔵 Low (no action) | many | vulture false positives, by-design empty files |

**This release (v0.25.1) fixes Critical + count-drift + lint** —
13 findings, ~17 file diff, 0 line of code-behavior change.
**The PJ7 → PJ8 rebrand lives in PR-F2 (separate PR)** because it
requires flipping `tests/test_canonical_org_no_bypass.py` ("FINAL"
gate) and is a separate decision.

## Concrete fixes

### Critical — public PyPI metadata + cross-link integrity

1. **`pyproject.toml` description**:
   - Was: `"…+ 67-probe audit + sub-second browser daemon."`
   - Now: `"…+ scaffold engine (11 presets) + 96-probe conformance audit + sub-second browser daemon."`
   - This text shows on the PyPI package page + in `pip show`, so this
     was the highest-impact pre-publish item.
2. **Broken `BENCHMARKS-METHODOLOGY.md` cross-link** in
   `update-package/CLAUDE.md:39` and `update-package/CHANGELOG.md:11` —
   the file is at repo root, but the link was relative to
   `update-package/`.  Fixed to `../BENCHMARKS-METHODOLOGY.md`.

### Count drift — 4 user-facing docs

3. **`SKILL.md`** lines 201, 208 — `92-probe internal self-test` → `96-probe`.
4. **`USAGE_GUIDE.md`** lines 1678, 1841, 1843 — `92 probes` → `96 probes`,
   `87-probe conformance audit` → `96-probe`, `(10 × 3 = 30)` → `(11 × 3 = 33)`.
5. **`update-package/USAGE_GUIDE.md`** — same drift mirrored.
6. **`docs/GUIDE_NONTECH_BEGINNER.md`** lines 144, 577 — `92 probes` → `96 probes`.

### Lint cleanup — 15 ruff F-rule warnings → 0

Cleaned up dead imports in 14 files:

| File | Was unused |
|:-----|:-----------|
| `tests/browser/test_state_atomic.py` | `import json` |
| `tests/test_install_concurrency.py` | `import pytest` |
| `tests/test_manifest_llm_json_no_yaml_leakage.py` | `import pytest` |
| `tests/test_mcp_core_server.py` | `import pytest` |
| `tests/test_pipeline_v015_pr_b.py` | `import pytest` |
| `tests/test_pipeline_v015_pr_c.py` | `import pytest`, `PipelineDecision` |
| `tests/test_security_classifier.py` | `import os` |
| `tests/test_session_ledger.py` | `import pytest` |
| `tests/test_tool_executor_decide_integration.py` | `import os` |
| `tests/test_tool_executor_paths.py` | `import re` |
| `tests/test_vn_faker.py` | `import pytest` |
| `tools/gen_tools_json.py` | `import sys` |
| `tools/validate_release.py` | `import json` |
| `tests/test_vn_error_translator.py:162` | `yaml_mod = pytest.importorskip("yaml")` (assignment, never read) |

After this PR, `python -m ruff check .` returns `All checks passed!`
on the entire repo, not just on `scripts/vibecodekit/`.

## Audit gates (post-merge)

| Gate | v0.25.0 | v0.25.1 | Status |
|:-----|:-------:|:-------:|:------:|
| Tests | 1561 | 1561 | unchanged |
| Conformance probes | 96/96 | 96/96 | unchanged |
| `mypy --strict` 9 core | clean | clean | unchanged |
| `ruff check .` (full repo) | 15 errors | **0 errors** | ↓ −15 |
| `vulture --min-conf 80` | 2 FP | 2 FP | unchanged |
| Tracked trash | 0 | 0 | unchanged |
| Committed secrets | 0 | 0 | unchanged |

## What's NOT in this release

**PR-F2 (PJ7 → PJ8 rebrand)** — separate PR.  Tracked via the audit
report's #4–#9 findings.  Affects:

- `pyproject.toml` URLs (Homepage, Issues, Changelog)
- `README.md` 5 clone URLs
- `CONTRIBUTING.md`, `SECURITY.md`, `examples/README.md`
- `docs/GUIDE_NONTECH_BEGINNER.md` 6 clone URLs
- `tests/test_canonical_org_no_bypass.py` (flip canonical org)
- `tests/test_repo_urls_canonical.py` (`ALLOWED_ORGS`)

## Upgrade

```bash
pip install --upgrade vibecodekit-hybrid-ultra==0.25.1
```

Or if vendored as a skill bundle:

```bash
# replace your skill bundle with v0.25.1; no migration needed.
```

[`AUDIT-cycle17-pre-public-release.md`]: /home/ubuntu/AUDIT-cycle17-pre-public-release.md
