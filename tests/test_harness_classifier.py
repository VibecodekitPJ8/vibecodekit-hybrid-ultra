"""Cycle 22 / v0.26.0 — Pattern G harness risk classifier tests.

Covers the 10-flag taxonomy, the 3-lane decision rule, hard-gate
escalation, manual overrides, lane override, and the helper functions
``slugify`` / ``next_story_id`` / ``next_adr_id`` used by the CLI.

See ``references/43-harness-engineering.md`` for the rationale.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from vibecodekit import harness_classifier as hc


# ---------------------------------------------------------------------------
# Section 1 — keyword heuristics fire the right flag.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "prompt,expected_flag",
    [
        ("Add login flow with JWT", hc.RiskFlag.AUTH),
        ("Implement RBAC for admin pages", hc.RiskFlag.AUTHORIZATION),
        ("Alembic migration to drop the legacy column", hc.RiskFlag.DATA_MODEL),
        ("Make sure we redact PII in the audit log", hc.RiskFlag.AUDIT_SECURITY),
        ("Wire Stripe webhook for checkout", hc.RiskFlag.EXTERNAL_SYSTEMS),
        ("Update the OpenAPI response envelope", hc.RiskFlag.PUBLIC_CONTRACTS),
        ("Ship deep-link handler for the mobile shell", hc.RiskFlag.CROSS_PLATFORM),
        ("Refactor existing checkout module", hc.RiskFlag.EXISTING_BEHAVIOR),
        ("This area currently has no tests at all", hc.RiskFlag.WEAK_PROOF),
        ("Touches both billing and auth", hc.RiskFlag.MULTI_DOMAIN),
    ],
)
def test_single_flag_keyword_detection(
    prompt: str, expected_flag: hc.RiskFlag
) -> None:
    result = hc.classify(prompt)
    assert expected_flag in result.flags_set, (
        f"expected {expected_flag.value!r} in {result.flags_set}"
    )


# ---------------------------------------------------------------------------
# Section 2 — hard gates force high_risk regardless of count.
# ---------------------------------------------------------------------------


def test_single_hard_gate_forces_high_risk() -> None:
    result = hc.classify("Add login")
    assert result.lane is hc.RiskLane.HIGH_RISK
    assert hc.RiskFlag.AUTH in result.hard_gates
    assert "hard gate(s) auth tripped" in result.reason


def test_no_hard_gate_one_flag_stays_tiny() -> None:
    result = hc.classify("Refactor the existing search module")
    assert result.lane is hc.RiskLane.TINY
    assert result.hard_gates == ()
    assert hc.RiskFlag.EXISTING_BEHAVIOR in result.flags_set


def test_no_hard_gate_zero_flag_is_tiny() -> None:
    result = hc.classify("Rename a CSS class on the marketing page")
    assert result.lane is hc.RiskLane.TINY
    assert result.flags_set == ()
    assert result.validation_required == ("unit",)


# ---------------------------------------------------------------------------
# Section 3 — flag-count → lane rule (no hard gate).
# ---------------------------------------------------------------------------


def test_two_soft_flags_lands_normal() -> None:
    # public_contracts + cross_platform (both non-hard) → 2 flags → normal
    result = hc.classify(
        "Rename the public API endpoint and ship a deep-link change"
    )
    assert result.lane is hc.RiskLane.NORMAL
    assert result.hard_gates == ()
    assert hc.RiskFlag.PUBLIC_CONTRACTS in result.flags_set
    assert hc.RiskFlag.CROSS_PLATFORM in result.flags_set


def test_three_soft_flags_stays_normal() -> None:
    result = hc.classify(
        "Refactor public API to a new response envelope on the mobile shell"
    )
    # refactor → existing_behavior; response envelope → public_contracts;
    # mobile / shell → cross_platform.  All soft → normal.
    assert result.lane is hc.RiskLane.NORMAL
    assert result.hard_gates == ()
    assert len(result.flags_set) >= 2


def test_four_soft_flags_escalates_to_high_risk() -> None:
    result = hc.classify(
        "Refactor public API response envelope on mobile shell with "
        "no test coverage"
    )
    # refactor → existing_behavior; response envelope → public_contracts;
    # mobile → cross_platform; no test coverage → weak_proof → 4 flags
    assert result.lane is hc.RiskLane.HIGH_RISK
    assert result.hard_gates == ()
    assert len(result.flags_set) >= 4


# ---------------------------------------------------------------------------
# Section 4 — multiple hard gates escalate once (not multiply).
# ---------------------------------------------------------------------------


def test_multiple_hard_gates_escalate_once() -> None:
    result = hc.classify(
        "Add login flow with RBAC and an alembic migration"
    )
    assert result.lane is hc.RiskLane.HIGH_RISK
    # All three should be hard gates.
    assert hc.RiskFlag.AUTH in result.hard_gates
    assert hc.RiskFlag.AUTHORIZATION in result.hard_gates
    assert hc.RiskFlag.DATA_MODEL in result.hard_gates
    # Reason mentions all three flag names (sorted).
    for token in ("auth", "authorization", "data_model"):
        assert token in result.reason


# ---------------------------------------------------------------------------
# Section 5 — extra_flags merges (CLI ``--flags`` semantics).
# ---------------------------------------------------------------------------


def test_extra_flags_merge_into_detection() -> None:
    # Prompt alone has zero keyword hits, but CLI passes 2 hard gates.
    result = hc.classify(
        "Trivial cosmetic change",
        extra_flags=["auth", "audit_security"],
    )
    assert result.lane is hc.RiskLane.HIGH_RISK
    assert hc.RiskFlag.AUTH in result.flags_set
    assert hc.RiskFlag.AUDIT_SECURITY in result.flags_set


def test_extra_flags_unknown_tokens_silently_dropped() -> None:
    result = hc.classify("Trivial change", extra_flags=["not_a_flag", "auth"])
    assert hc.RiskFlag.AUTH in result.flags_set
    # No exception raised on unknown token.


def test_extra_flags_accepts_hyphen_token() -> None:
    # CLI canonicalises "data-model" → "data_model"
    result = hc.classify("Trivial change", extra_flags=["data-model"])
    assert hc.RiskFlag.DATA_MODEL in result.flags_set
    assert result.lane is hc.RiskLane.HIGH_RISK


# ---------------------------------------------------------------------------
# Section 6 — lane override.
# ---------------------------------------------------------------------------


def test_lane_override_changes_lane_keeps_flags() -> None:
    result = hc.classify(
        "Add login",  # heuristic → high_risk
        override_lane=hc.RiskLane.NORMAL,
    )
    assert result.lane is hc.RiskLane.NORMAL
    assert hc.RiskFlag.AUTH in result.flags_set
    assert "override" in result.reason.lower()


def test_lane_override_same_as_heuristic_no_annotation() -> None:
    # When override matches heuristic, reason stays clean (no "override:")
    result = hc.classify(
        "Add login",
        override_lane=hc.RiskLane.HIGH_RISK,
    )
    assert result.lane is hc.RiskLane.HIGH_RISK
    assert "override" not in result.reason.lower()


# ---------------------------------------------------------------------------
# Section 7 — deterministic output (sorted flags, frozen dataclass).
# ---------------------------------------------------------------------------


def test_classification_is_deterministic() -> None:
    prompt = "Add login flow with RBAC and an alembic migration"
    r1 = hc.classify(prompt)
    r2 = hc.classify(prompt)
    assert r1 == r2  # frozen dataclass equality


def test_flags_set_is_sorted() -> None:
    result = hc.classify(
        "Touches both billing and auth, with audit log",
    )
    values = [f.value for f in result.flags_set]
    assert values == sorted(values)


# ---------------------------------------------------------------------------
# Section 8 — validation_required tracks the lane.
# ---------------------------------------------------------------------------


def test_validation_required_for_tiny_is_unit_only() -> None:
    result = hc.classify("Rename a CSS class")
    assert result.validation_required == ("unit",)


def test_validation_required_for_normal_is_two_layers() -> None:
    result = hc.classify("Rename public API endpoint on mobile shell")
    assert result.lane is hc.RiskLane.NORMAL
    assert result.validation_required == ("unit", "integration")


def test_validation_required_for_high_risk_is_full_ladder() -> None:
    result = hc.classify("Add login")
    assert result.validation_required == (
        "unit",
        "integration",
        "e2e",
        "platform",
        "release",
    )


# ---------------------------------------------------------------------------
# Section 9 — JSON serialisation contract.
# ---------------------------------------------------------------------------


def test_classify_to_dict_is_json_serialisable() -> None:
    payload = hc.classify_to_dict("Add login flow with RBAC")
    assert set(payload.keys()) == {
        "lane",
        "flags_set",
        "hard_gates",
        "reason",
        "validation_required",
    }
    # Round-trip through json to confirm no enum leaks.
    serialised = json.dumps(payload)
    restored = json.loads(serialised)
    assert restored["lane"] == "high_risk"
    assert "auth" in restored["hard_gates"]


# ---------------------------------------------------------------------------
# Section 10 — helper functions used by the CLI.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "title,expected",
    [
        ("User can reset password", "user-can-reset-password"),
        ("ADD: New endpoint!", "add-new-endpoint"),
        ("Move /api/v1 → /api/v2", "move-api-v1-api-v2"),
        ("", "story"),
        ("    ", "story"),
    ],
)
def test_slugify(title: str, expected: str) -> None:
    assert hc.slugify(title) == expected


def test_next_story_id_empty() -> None:
    assert hc.next_story_id([]) == "US-001"


def test_next_story_id_skips_used() -> None:
    assert hc.next_story_id(["US-001", "US-003"]) == "US-002"


def test_next_story_id_pads_to_three_digits() -> None:
    assert hc.next_story_id(["US-001", "US-002", "US-003"]) == "US-004"


def test_next_adr_id_empty() -> None:
    assert hc.next_adr_id([]) == "0001"


def test_next_adr_id_skips_used() -> None:
    assert hc.next_adr_id(["0001", "0003"]) == "0002"


def test_next_adr_id_pads_to_four_digits() -> None:
    used = [f"{n:04d}" for n in range(1, 10)]
    assert hc.next_adr_id(used) == "0010"


def test_hard_gates_subset_of_flags() -> None:
    for gate in hc.HARD_GATES:
        assert isinstance(gate, hc.RiskFlag)


# ---------------------------------------------------------------------------
# Section 11 — end-to-end CLI smoke test (via subprocess).
# ---------------------------------------------------------------------------


def test_cli_classify_json_smoke() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    out = subprocess.run(
        [
            sys.executable, "-m", "vibecodekit.cli",
            "harness", "classify", "Add login", "--json",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        env={"PYTHONPATH": "scripts", "PATH": "/usr/bin:/bin"},
        check=True,
    )
    payload = json.loads(out.stdout)
    assert payload["lane"] == "high_risk"
    assert payload["hard_gates"] == ["auth"]


def test_cli_story_handles_malformed_dirname(tmp_path: Path) -> None:
    """Regression — story scanner should not crash on dirnames like ``US.md``
    or ``USsomething`` that start with ``US`` but contain no dash."""
    repo_root = Path(__file__).resolve().parent.parent
    stories = tmp_path / "docs" / "stories"
    stories.mkdir(parents=True)
    (stories / "US.md").write_text("legacy", encoding="utf-8")
    (stories / "USsomething").mkdir()
    (stories / "US-001-real-story.md").write_text("real", encoding="utf-8")
    out = subprocess.run(
        [
            sys.executable, "-m", "vibecodekit.cli",
            "harness", "--root", str(tmp_path),
            "story", "Add second real story",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        env={"PYTHONPATH": "scripts", "PATH": "/usr/bin:/bin"},
        check=True,
    )
    payload = json.loads(out.stdout)
    assert payload["story_id"] == "US-002"
