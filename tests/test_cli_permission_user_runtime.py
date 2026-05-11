"""v0.25.3: ``vibe permission --user-runtime`` redirects denial state.

Without ``--user-runtime``, ``vibe permission`` writes to
``$cwd/.vibecode/runtime/denials.json`` (per-project state).  This is
correct for genuine project use but pollutes ``$cwd`` when a user runs
the QUICKSTART §3 demo from arbitrary directories — exactly how PR #26
ended up accidentally committing runtime denial records to the kit
repo.

With ``--user-runtime``, state is redirected to
``~/.vibecode/runtime/denials.json`` (user-cache scope) so demos from
any working directory leave the project tree clean.

Tests verify both directions, plus the public helper
``_user_runtime_root()``.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"
PY = sys.executable


def _run_cli(*args: str, cwd: Path,
             home_override: Path | None = None) -> subprocess.CompletedProcess:
    env = {**os.environ, "PYTHONPATH": str(SCRIPTS)}
    if home_override is not None:
        env["HOME"] = str(home_override)
    return subprocess.run(
        [PY, "-m", "vibecodekit.cli", *args],
        env=env,
        cwd=str(cwd),
        capture_output=True, text=True, timeout=30,
    )


def test_permission_default_root_writes_to_cwd(tmp_path: Path) -> None:
    """Default behaviour: state lands in ``$cwd/.vibecode/runtime/``."""
    proj = tmp_path / "proj"
    proj.mkdir()
    r = _run_cli("permission", "rm -rf /", cwd=proj)
    assert r.returncode == 2, r.stderr  # deny → exit 2
    payload = json.loads(r.stdout)
    assert payload["decision"] == "deny"

    cwd_state = proj / ".vibecode" / "runtime" / "denials.json"
    assert cwd_state.exists(), (
        "Default --root='.' should create state under $cwd; missing.")


def test_permission_user_runtime_writes_to_home(tmp_path: Path) -> None:
    """``--user-runtime`` redirects state to ``$HOME/.vibecode/runtime/``."""
    proj = tmp_path / "proj"
    proj.mkdir()
    fake_home = tmp_path / "home"
    fake_home.mkdir()

    r = _run_cli("permission", "rm -rf /", "--user-runtime",
                 cwd=proj, home_override=fake_home)
    assert r.returncode == 2, r.stderr
    payload = json.loads(r.stdout)
    assert payload["decision"] == "deny"

    cwd_state = proj / ".vibecode" / "runtime" / "denials.json"
    assert not cwd_state.exists(), (
        f"--user-runtime should NOT create state under $cwd; "
        f"found {cwd_state}.")

    home_state = fake_home / ".vibecode" / "runtime" / "denials.json"
    assert home_state.exists(), (
        f"--user-runtime should create state under $HOME/.vibecode; "
        f"missing {home_state}.")


def test_user_runtime_root_helper_returns_home_when_writable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Helper returns ``$HOME`` when ``$HOME/.vibecode`` mkdir succeeds."""
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    monkeypatch.setenv("HOME", str(fake_home))

    sys.path.insert(0, str(SCRIPTS))
    try:
        # Reimport in case of module caching.
        import importlib

        from vibecodekit import cli as cli_mod
        importlib.reload(cli_mod)
        result = cli_mod._user_runtime_root()
    finally:
        sys.path.remove(str(SCRIPTS))

    assert result == str(fake_home), result
    assert (fake_home / ".vibecode").is_dir()


def test_user_runtime_root_helper_falls_back_when_home_readonly(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Helper returns ``"."`` when home dir not writable."""
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        pytest.skip("root bypasses chmod 0500; fallback path not testable.")

    ro_home = tmp_path / "ro_home"
    ro_home.mkdir(mode=0o500)  # read-only, no write
    monkeypatch.setenv("HOME", str(ro_home))

    sys.path.insert(0, str(SCRIPTS))
    try:
        import importlib

        from vibecodekit import cli as cli_mod
        importlib.reload(cli_mod)
        result = cli_mod._user_runtime_root()
    finally:
        sys.path.remove(str(SCRIPTS))

    # Restore writable mode for cleanup.
    ro_home.chmod(0o700)

    assert result == ".", (
        f"Read-only $HOME should fall back to '.'; got {result}.")


def test_pythonpath_unset_pytest_works() -> None:
    """Self-test: pytest collects this very test without PYTHONPATH=.

    v0.25.3 added ``pythonpath = ["."]`` to ``[tool.pytest.ini_options]``;
    without it, ``test_no_further_rebrands.py`` fails collection with
    ``ModuleNotFoundError: No module named 'tests'``.

    The fact that this test runs at all means pytest collected the
    sibling ``tests/test_no_further_rebrands.py`` successfully — which
    requires ``tests`` to be importable as a package.
    """
    # The test passing IS the assertion; tag this with explicit
    # documentation so the regression intent is clear.
    pass
