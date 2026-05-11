# Release Notes — v0.25.3 (Cycle 18 PR-G1)

**Date:** 2026-05-01
**Tag commit:** TBD (after PR-G1 merges)
**Scope:** Patch release — 2 non-blocking UX/DX issues from v0.25.2 audit.

---

## TL;DR

Two latent issues observed during the v0.25.2 release audit but
deferred as "non-blocking, future PR" are now fixed:

1. **`pytest` works standalone** — no more `PYTHONPATH=.` ritual.
2. **`vibe permission` won't pollute `$cwd` anymore** — opt into
   `--user-runtime` for ad-hoc demos so state lands in `~/.vibecode/`.

| Gate | v0.25.2 | v0.25.3 |
|:-----|:-------:|:-------:|
| Tests | 1561 | **1566** (+5) |
| Audit probes | 96/96 | 96/96 |
| Mypy --strict 9 core | clean | clean |
| Ruff full repo | clean | clean |

No code semantics changed for the default permission flow — projects
that don't use `--user-runtime` get identical behaviour to v0.25.2.

---

## Fix 1 — `pytest` standalone discovery

### Symptom

Running `pytest` from repo root without `pip install -e .` (or without
manually setting `PYTHONPATH=.`) failed with:

```
ERROR tests/test_canonical_org_no_bypass.py
ERROR tests/test_no_further_rebrands.py
ModuleNotFoundError: No module named 'tests'
```

### Root cause

Two tests cross-import shared constants:

```python
# tests/test_canonical_org_no_bypass.py
from tests.test_repo_urls_canonical import ALLOWED_ORGS
```

Without `tests/__init__.py` (which we intentionally don't ship — pytest
discovers via rootdir convention, not packages), `tests` isn't a
package on `sys.path` by default.  Devs working in the repo had to
either `pip install -e .` (which adds `scripts/` + `.` to sys.path) or
prefix commands with `PYTHONPATH=.`.

### Fix

`pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
# v0.25.3: thêm `.` (repo root) vào sys.path để pytest discover được
# `tests` như một package — 2 test (`test_no_further_rebrands.py` +
# `test_canonical_org_no_bypass.py`) import `from tests.X import Y`
# để re-export `ALLOWED_ORGS`.  Trước đây dev env phải set
# `PYTHONPATH=.` thủ công hoặc chạy `pip install -e .`; bây giờ
# `pytest` standalone từ repo root chạy được.
pythonpath = ["."]
addopts = "-q"
```

Verification:

```bash
git clone https://github.com/VibecodekitPJ8/vibecodekit-hybrid-ultra.git
cd vibecodekit-hybrid-ultra
pytest -q
# → 1566 passed, 9 skipped
```

No `PYTHONPATH=` prefix, no `pip install -e .` needed.

---

## Fix 2 — `vibe permission --user-runtime`

### Symptom

The `QUICKSTART.md` §3 example was:

```bash
PYTHONPATH=scripts python -m vibecodekit.cli permission "rm -rf /"
```

Running this from repo root caused `DenialStore` to write:

```
$cwd/.vibecode/runtime/denials.json
$cwd/.vibecode/runtime/denials.lock
```

After a few invocations: `consecutive=2, total=2, TTL 24h`.  If a dev
ran `git add -A` afterward (common during release prep), the polluted
state would be committed.  This actually happened in **PR-F5** and
required the **PR-F6 hot-fix** before tagging v0.25.2.

### Root cause (semantic)

Denial state is fundamentally **user-scoped**:
- Tracks whether *this user* keeps trying dangerous commands.
- Powers the circuit-breaker that demotes a user from `default` to
  `auto_safe` after N consecutive denials.
- Has 24h TTL — survives across project switches.

Storing it in `$cwd/.vibecode/runtime/` was wrong by default:
1. Pollutes any working directory the user runs `vibe permission` from.
2. Loses cross-project signal (each project has its own counter).
3. Encourages accidental commit of runtime state into git history.

### Fix

Added `--user-runtime` flag to `vibe permission`:

```python
# scripts/vibecodekit/cli.py

def _user_runtime_root() -> str:
    """Return ``$HOME`` as a root for cross-project denial state.

    Permission engine state (denial circuit-breaker, repeated-denial
    detection) tracks user behaviour, not per-project state — so a user
    cache is more semantically correct than ``$cwd``.  Returning the
    home dir lets ``DenialStore`` (which appends ``.vibecode/runtime/``
    to its root) write to ``~/.vibecode/runtime/denials.json`` — the
    canonical user-cache location.  Falls back to ``"."`` if home dir
    not writable (very rare).
    """
    home = Path.home()
    try:
        (home / ".vibecode").mkdir(parents=True, exist_ok=True)
    except OSError:
        return "."
    return str(home)


def _cmd_permission(args: argparse.Namespace) -> int:
    root = _user_runtime_root() if args.user_runtime else args.root
    d = permission_engine.decide(args.command, mode=args.mode, root=root,
                                 allow_unsafe_yolo=args.unsafe)
    print(json.dumps(d, ensure_ascii=False, indent=2))
    return 0 if d["decision"] == "allow" else 2
```

Argparse:

```python
sub.add_argument(
    "--user-runtime", action="store_true",
    help="Store denial state in ~/.vibecode/ instead of "
         "$cwd/.vibecode/runtime/ (recommended for ad-hoc CLI "
         "demos to avoid polluting the working directory).",
)
```

### Why not default to `--user-runtime`?

For **CLI ad-hoc demos** user-runtime is the right default.  But the
`vibe permission` subcommand is also used **inside automated tools**
(via Python API + subprocess) where `$cwd`-scoped state is desired
(e.g. test isolation, sandbox per-project policies).  So we kept the
default project-local and require an explicit opt-in flag for the demo
use case.

The `Procfile`-style hook configuration in `SKILL.md:95-97` uses the
CLI form via `python3 -m vibecodekit.cli permission ${command}`
without `--user-runtime`, which is **correct** for hook usage —
project-local state makes sense there.

### Usage

```bash
# default — state stays in $cwd/.vibecode/runtime/ (project-local, unchanged)
vibe permission "rm -rf /"

# v0.25.3+ — state in ~/.vibecode/runtime/ (user-scoped, recommended for demos)
vibe permission "rm -rf /" --user-runtime
```

### Belt-and-suspenders: `.gitignore`

Added explicit ignore for the two pollution-prone files:

```
# v0.25.3: deny pollution from `vibe permission` examples (QUICKSTART §3).
# DenialStore self-seeds on first instantiation, so no committed seed file
# is needed.  Use `vibe permission --user-runtime` for ad-hoc demos to
# write to ~/.vibecode/ instead.
.vibecode/runtime/denials.json
.vibecode/runtime/denials.lock
```

This catches the case where a future user (or future Devin session)
forgets to use `--user-runtime` and runs the bare command from repo
root — even if their state gets written to `$cwd`, `git add -A` will
no longer sweep it into a commit.

---

## Tests added (`tests/test_cli_permission_user_runtime.py`)

5 new tests, all pass:

1. **`test_permission_default_root_writes_to_cwd()`** —
   verifies default behaviour unchanged (state in `$cwd/.vibecode/`).
2. **`test_permission_user_runtime_writes_to_home()`** —
   verifies `--user-runtime` redirects state to `$HOME/.vibecode/`,
   *not* `$cwd`.
3. **`test_user_runtime_root_helper_returns_home_when_writable()`** —
   unit test of `_user_runtime_root()` happy path.
4. **`test_user_runtime_root_helper_falls_back_when_home_readonly()`** —
   exercises the `OSError` fallback path (skipped if running as root,
   since root can write anywhere).
5. **`test_pythonpath_unset_pytest_works()`** —
   documents that `pytest` collection now works without
   `PYTHONPATH=.` thanks to Fix 1.

---

## Bookkeeping changes

- **VERSION** 0.25.2 → 0.25.3 (single source of truth; mirrors synced
  via `tools/sync_version.py`).
- **8 mirror surfaces** updated by `sync_version.py`:
  `update-package/VERSION`, `pyproject.toml`, `manifest.llm.json`,
  `assets/plugin-manifest.json`, `update-package/.claw.json`,
  `SKILL.md` frontmatter,
  `update-package/.claude/commands/vck-pipeline.md` frontmatter.
- **6 `design/tokens.json`** regenerated with `version: "0.25.3"`.
- **`benchmarks/intent_router_0.25.3.json`** generated
  (set-incl 0.9808 — unchanged from v0.25.2, intent router unaffected).
- **`tools.json`** regenerated (version 0.25.2 → 0.25.3).
- **Forward-facing docs bumped** (banner / surface-inventory pointers):
  - `README.md` (current release banner + surface inventory)
  - `USAGE_GUIDE.md` + `update-package/USAGE_GUIDE.md` (5 chỗ each)
  - `update-package/README.md` (title + slash-command count)
  - `update-package/CLAUDE.md` (title + release gate text)
  - `docs/GUIDE_NONTECH_BEGINNER.md` (3 chỗ)
  - `BENCHMARKS-METHODOLOGY.md` ("at v0.25.2" → "at v0.25.3")
- **QUICKSTART.md** + mirror updated to use `--user-runtime` in §3
  example.
- **USAGE_GUIDE.md** §19.6 + mirror documents the new flag with
  inline explainer.

Historical artefacts left **untouched** (audit trail integrity):
- `RELEASE_NOTES_v0.{17..25.2}.md` — time-stamped releases.
- `CHANGELOG.md` historical entries for v0.25.0..v0.25.2.
- `SECURITY.md:65` — "Canonical org là VibecodekitPJ8 từ v0.25.2+"
  is a historical pointer (when the rebrand landed), correct as-is.

---

## Migration

**None required.**  This is a backward-compatible patch release.

If you have an existing dev workflow that always sets `PYTHONPATH=.`,
you can drop it now but it remains harmless.

If you have automation that calls `vibe permission` and relies on
state being in `$cwd/.vibecode/runtime/`, the default behaviour is
unchanged — only invocations with the new `--user-runtime` flag
write to `~/.vibecode/`.

---

## Gates verified

```
$ pytest -q
1566 passed, 9 skipped in 25.62s

$ python -m vibecodekit.conformance_audit
96/96 probes met (parity 1.0000)

$ python -m mypy --strict scripts/vibecodekit/permission_engine.py \
                          scripts/vibecodekit/scaffold_engine.py \
                          scripts/vibecodekit/verb_router.py \
                          scripts/vibecodekit/denial_store.py \
                          scripts/vibecodekit/_audit_log.py \
                          scripts/vibecodekit/tool_executor.py \
                          scripts/vibecodekit/team_mode.py \
                          scripts/vibecodekit/task_runtime.py \
                          scripts/vibecodekit/subagent_runtime.py
Success: no issues found in 9 source files

$ python -m ruff check .
All checks passed!
```

---

## PR / commit references

- PR-G1: TBD (cycle 18, this release).
- v0.25.2 tag commit: `00610c4`
- v0.25.3 tag commit: TBD (HEAD main after PR-G1 merge).

Previous release notes:
- [v0.25.2](RELEASE_NOTES_v0.25.2.md) — PJ7 → PJ8 rebrand
- [v0.25.1](RELEASE_NOTES_v0.25.1.md) — pre-public-release cleanup
- [v0.25.0](RELEASE_NOTES_v0.25.0.md) — osint-terminal scaffold (11th preset)
- [v0.24.0](RELEASE_NOTES_v0.24.0.md) — design tokens + dark-mode CP twin
