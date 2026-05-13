"""Pattern G — Harness Engineering risk classifier (cycle 22 / v0.26.0).

Implements the 10-flag risk taxonomy + 3-lane decision logic adapted
from ``hoangnb24/harness-experimental`` (see
``references/43-harness-engineering.md`` for the full Pattern G
rationale and vocabulary map).

Public surface (kept narrow on purpose):

- :class:`RiskFlag` (Enum) — the 10 flag identifiers.
- :class:`RiskLane` (Enum) — ``tiny`` / ``normal`` / ``high_risk``.
- :func:`classify` — heuristic + manual override classifier returning a
  :class:`ClassificationResult` dataclass.
- :func:`classify_to_dict` — JSON-serialisable wrapper used by the CLI.

Design notes:

- Classification is intentionally heuristic (keyword matching).  This
  module is *not* an LLM-backed classifier.  For LLM-driven dispatch
  pipe through :mod:`vibecodekit.intent_router` first, then feed the
  routed verb into :func:`classify`.
- ``hard_gates`` are a *subset* of the 10 flags; tripping any one of
  them forces the ``high_risk`` lane regardless of total flag count.
- The lane decision rule mirrors the Harness intake doc exactly:
  ``0/1 flag → tiny``, ``2-3 flags → normal``, ``4+ flags → high_risk``,
  but is overridden by hard-gate hits.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Mapping


class RiskFlag(str, Enum):
    """The 10 Pattern G risk flags."""

    AUTH = "auth"
    AUTHORIZATION = "authorization"
    DATA_MODEL = "data_model"
    AUDIT_SECURITY = "audit_security"
    EXTERNAL_SYSTEMS = "external_systems"
    PUBLIC_CONTRACTS = "public_contracts"
    CROSS_PLATFORM = "cross_platform"
    EXISTING_BEHAVIOR = "existing_behavior"
    WEAK_PROOF = "weak_proof"
    MULTI_DOMAIN = "multi_domain"


class RiskLane(str, Enum):
    """The 3 Pattern G lanes (lane decides packet shape + validation depth)."""

    TINY = "tiny"
    NORMAL = "normal"
    HIGH_RISK = "high_risk"


# Hard gates: tripping any of these forces ``high_risk`` even with one flag.
HARD_GATES: frozenset[RiskFlag] = frozenset(
    {
        RiskFlag.AUTH,
        RiskFlag.AUTHORIZATION,
        RiskFlag.DATA_MODEL,
        RiskFlag.AUDIT_SECURITY,
        RiskFlag.EXTERNAL_SYSTEMS,
    }
)


# Keyword heuristics per flag.  Lowercase substring match against the
# normalised prompt.  Conservative on purpose — false negatives are
# preferable to spurious high-risk classifications.
_KEYWORDS: dict[RiskFlag, tuple[str, ...]] = {
    RiskFlag.AUTH: (
        "login",
        "logout",
        "sign-in",
        "sign in",
        "sign-up",
        "sign up",
        "signup",
        "signin",
        "session",
        "jwt",
        "password",
        "refresh-token",
        "refresh token",
        "refresh_token",
        "oauth",
        "magic link",
        "magic-link",
        "two-factor",
        "2fa",
        "mfa",
    ),
    RiskFlag.AUTHORIZATION: (
        "role",
        "permission",
        "rbac",
        "acl",
        "tenant",
        "company scope",
        "scope to",
        "admin only",
        "admin-only",
        "owner only",
        "owner-only",
        "is_admin",
        "can_edit",
        "policy decision",
    ),
    RiskFlag.DATA_MODEL: (
        "schema",
        "migration",
        "alembic",
        "drop column",
        "drop table",
        "unique constraint",
        "delete cascade",
        "retention",
        "purge",
        "soft delete",
        "soft-delete",
        "hard delete",
        "hard-delete",
        "backfill",
        "ddl",
    ),
    RiskFlag.AUDIT_SECURITY: (
        "audit log",
        "audit-log",
        "auditlog",
        "pii",
        "sensitive data",
        "redact",
        "encryption",
        "encrypt",
        "decrypt",
        "vault",
        "owasp",
        "csrf",
        "xss",
        "sql injection",
        "rate limit",
        "rate-limit",
    ),
    RiskFlag.EXTERNAL_SYSTEMS: (
        "stripe",
        "twilio",
        "sendgrid",
        "ses ",
        "ses.",
        "webhook",
        "queue",
        "sqs",
        "sns",
        "kafka",
        "rabbitmq",
        "celery",
        "email send",
        "send email",
        "payment",
        "checkout",
        "third-party",
        "third party",
        "provider sdk",
        "cloud function",
    ),
    RiskFlag.PUBLIC_CONTRACTS: (
        "api shape",
        "openapi",
        "swagger",
        "response envelope",
        "client-visible",
        "breaking change",
        "rename endpoint",
        "deprecate endpoint",
        "public api",
        "sdk version",
    ),
    RiskFlag.CROSS_PLATFORM: (
        "desktop",
        "mobile",
        "ios ",
        "android ",
        "electron",
        "native shell",
        "deep link",
        "deep-link",
        "universal link",
        "browser only",
        "browser-only",
        "react-native",
    ),
    RiskFlag.EXISTING_BEHAVIOR: (
        "refactor",
        "rewrite",
        "replace existing",
        "deprecate",
        "migrate from",
        "remove the old",
        "drop support for",
        "swap out",
    ),
    RiskFlag.WEAK_PROOF: (
        "no tests",
        "untested",
        "no coverage",
        "missing tests",
        "no test coverage",
    ),
    RiskFlag.MULTI_DOMAIN: (
        "billing and auth",
        "auth and billing",
        "multi-domain",
        "multi domain",
        "cross-domain",
        "cross domain",
        "across modules",
    ),
}


@dataclass(frozen=True)
class ClassificationResult:
    """Outcome of :func:`classify`.

    Attributes:
        lane: One of :class:`RiskLane`.
        flags_set: Sorted tuple of flags that fired (deterministic order).
        hard_gates: Subset of ``flags_set`` that are hard gates.
        reason: Short human-readable explanation of the lane decision.
        validation_required: Validation ladder layers expected for this
            lane (advisory; the validation-report template decides final
            shape).
    """

    lane: RiskLane
    flags_set: tuple[RiskFlag, ...]
    hard_gates: tuple[RiskFlag, ...]
    reason: str
    validation_required: tuple[str, ...]


def _normalise(prompt: str) -> str:
    return prompt.lower().strip()


def _detect_keyword_flags(normalised_prompt: str) -> set[RiskFlag]:
    detected: set[RiskFlag] = set()
    for flag, keywords in _KEYWORDS.items():
        for kw in keywords:
            if kw in normalised_prompt:
                detected.add(flag)
                break
    return detected


def _coerce_flag(token: str) -> RiskFlag | None:
    """Coerce a CLI/config token (``"auth"``, ``"data-model"``, etc.) to enum.

    Returns ``None`` for unknown tokens so the caller can decide whether
    to surface a usage error or silently drop.
    """
    norm = token.strip().lower().replace("-", "_")
    for flag in RiskFlag:
        if flag.value == norm:
            return flag
    return None


def _decide_lane(
    flags_set: set[RiskFlag],
    hard_gates_hit: set[RiskFlag],
) -> tuple[RiskLane, str]:
    """Apply the Pattern G lane decision rule."""
    if hard_gates_hit:
        names = ", ".join(sorted(g.value for g in hard_gates_hit))
        return (
            RiskLane.HIGH_RISK,
            f"hard gate(s) {names} tripped → high-risk regardless of "
            f"total flag count ({len(flags_set)})",
        )
    count = len(flags_set)
    if count <= 1:
        return (
            RiskLane.TINY,
            f"{count} flag(s); no hard gate → tiny lane",
        )
    if count <= 3:
        return (
            RiskLane.NORMAL,
            f"{count} flags; no hard gate → normal lane with stronger validation",
        )
    return (
        RiskLane.HIGH_RISK,
        f"{count} flags (>= 4); no hard gate but breadth → high-risk lane",
    )


_VALIDATION_BY_LANE: Mapping[RiskLane, tuple[str, ...]] = {
    RiskLane.TINY: ("unit",),
    RiskLane.NORMAL: ("unit", "integration"),
    RiskLane.HIGH_RISK: ("unit", "integration", "e2e", "platform", "release"),
}


def classify(
    prompt: str,
    *,
    extra_flags: Iterable[str] | None = None,
    override_lane: RiskLane | None = None,
) -> ClassificationResult:
    """Classify a prompt into a Pattern G risk lane.

    Args:
        prompt: The natural-language story / feature description.
        extra_flags: Optional iterable of flag tokens (CLI ``--flags``
            comma-list) to add to the detected set.  Unknown tokens are
            silently ignored; downstream callers should validate first
            if they want to surface a usage error.
        override_lane: If set, the result's ``lane`` is forced to this
            value (the ``reason`` annotates the override).  ``flags_set``
            and ``hard_gates`` are still computed from heuristics +
            ``extra_flags`` for traceability.

    Returns:
        :class:`ClassificationResult` with frozen flags + decision.
    """
    normalised = _normalise(prompt)
    flags_set = _detect_keyword_flags(normalised)
    if extra_flags:
        for token in extra_flags:
            flag = _coerce_flag(token)
            if flag is not None:
                flags_set.add(flag)

    hard_gates_hit = flags_set & HARD_GATES

    lane, reason = _decide_lane(flags_set, hard_gates_hit)
    if override_lane is not None and override_lane is not lane:
        reason = (
            f"override: caller forced lane={override_lane.value} "
            f"(heuristic would have chosen {lane.value}: {reason})"
        )
        lane = override_lane

    sorted_flags = tuple(sorted(flags_set, key=lambda f: f.value))
    sorted_gates = tuple(sorted(hard_gates_hit, key=lambda f: f.value))
    return ClassificationResult(
        lane=lane,
        flags_set=sorted_flags,
        hard_gates=sorted_gates,
        reason=reason,
        validation_required=_VALIDATION_BY_LANE[lane],
    )


def classify_to_dict(
    prompt: str,
    *,
    extra_flags: Iterable[str] | None = None,
    override_lane: RiskLane | None = None,
) -> dict[str, object]:
    """JSON-serialisable wrapper for :func:`classify` (used by the CLI)."""
    result = classify(
        prompt,
        extra_flags=extra_flags,
        override_lane=override_lane,
    )
    return {
        "lane": result.lane.value,
        "flags_set": [f.value for f in result.flags_set],
        "hard_gates": [f.value for f in result.hard_gates],
        "reason": result.reason,
        "validation_required": list(result.validation_required),
    }


@dataclass(frozen=True)
class StoryStub:
    """Minimal story scaffolding payload (returned by ``vibe harness story``)."""

    story_id: str
    title: str
    slug: str
    lane: RiskLane
    classification: ClassificationResult
    target_relpath: str  # repo-relative path the CLI writes into


def slugify(title: str) -> str:
    """Lower-case, hyphen-separated slug.

    Non-ASCII characters and punctuation are treated as separators so
    the output is always URL-safe (matches ``[a-z0-9-]+``).  Returns
    ``"story"`` when the title is empty or contains no alphanumerics.
    """
    out: list[str] = []
    for char in title.lower():
        if ("a" <= char <= "z") or ("0" <= char <= "9"):
            out.append(char)
        else:
            out.append(" ")
    tokens = [t for t in "".join(out).split() if t]
    return "-".join(tokens) or "story"


def next_story_id(existing_ids: Iterable[str]) -> str:
    """Pick the next ``US-NNN`` ID given a set of already-used IDs.

    Accepts iterables of strings like ``"US-001"`` and returns the next
    free padded ID.  Returns ``"US-001"`` when the input is empty.
    """
    used: set[int] = set()
    for raw in existing_ids:
        stem = raw.upper().removeprefix("US-")
        try:
            used.add(int(stem))
        except ValueError:
            continue
    next_num = 1
    while next_num in used:
        next_num += 1
    return f"US-{next_num:03d}"


def next_adr_id(existing_ids: Iterable[str]) -> str:
    """Pick the next ``NNNN`` ADR ID given a set of already-used IDs."""
    used: set[int] = set()
    for raw in existing_ids:
        stem = raw.strip().lstrip("0") or "0"
        try:
            used.add(int(stem))
        except ValueError:
            continue
    next_num = 1
    while next_num in used:
        next_num += 1
    return f"{next_num:04d}"


# Public re-exports — keep small.
__all__ = [
    "ClassificationResult",
    "HARD_GATES",
    "RiskFlag",
    "RiskLane",
    "StoryStub",
    "classify",
    "classify_to_dict",
    "next_adr_id",
    "next_story_id",
    "slugify",
]
