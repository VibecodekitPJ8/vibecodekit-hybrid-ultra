"""CI guard: every github.com/<org>/ URL in the repo must reference an
allowed organisation.  Prevents stale fork / personal-account URLs from
leaking into releases.

Lý do tồn tại của từng org trong ``ALLOWED_ORGS`` (PR2 mở rộng,
updated PR1 cycle 8 — re-lock sau 9 lần rebrand; updated cycle 17
PR-F2 — re-lock lần 10 sau khi audit phát hiện live origin đã ở PJ8
từ cycle 13+ nhưng docs/tests vẫn lock PJ7):

- ``VibecodekitPJ8`` — **canonical FINAL** GitHub org của project
  hiện tại từ v0.25.2+.  Repo này đã rebrand 10 lần
  (``ykjpalbubp`` → ``N-NewteamPJ369`` → ``VibecodekitPJ`` →
  ``VibecodekitPJ2`` → ``VibecodekitPJ3`` → ``VibecodekitPJ4`` →
  ``VibecodekitPJ5`` → ``VibecodekitPJ6`` → ``VibecodekitPJ7`` →
  ``VibecodekitPJ8``); xem ``CHANGELOG.md`` cho lịch sử đầy đủ.

  **CAM KẾT MẠNH (cycle 17 PR-F2):** ``VibecodekitPJ8`` là canonical
  **FINAL** — DỪNG REBRAND Ở ĐÂY.  Mỗi lần rebrand là enterprise
  red flag, tạo churn documentation + CI cost.  Nếu PR sau muốn
  đổi canonical org lần thứ 11, **reviewer phải reject** trừ khi
  có lý do hard-blocking (legal / trademark) được trình bày rõ
  ràng trong PR body kèm sign-off của maintainer.

  Background của rebrand lần 10: cycle 8 PR1 lock PJ7 FINAL; live
  origin sau đó đã move sang PJ8 (cycle 13+), nhưng docs + tests
  vẫn assert PJ7 đến cycle 17.  Cycle 17 deep audit (PR-F2) phát
  hiện mismatch — clone URL trong README chỉ về repo PJ7 mà thực tế
  repo ở PJ8 — nên flip canonical sang PJ8 để doc match reality.

  Drift guard này **không có cơ chế env-gated bypass**
  (anti-pattern đã loại bỏ ở PR1 cycle 6); nếu fork CI cần
  override, fork phải tự sync ``ALLOWED_ORGS`` hoặc dùng
  ``pytest -k 'not test_repo_urls_canonical'`` cho fork suite.
  Mọi tài liệu chỉ nên link tới ``VibecodekitPJ8``.
- ``VagabondKingsman`` — upstream attribution cho
  `taw-kit <https://github.com/VagabondKingsman/taw-kit>`_, layer
  được tích hợp vào VibecodeKit Hybrid Ultra ở giai đoạn BIG-UPDATE
  (xem ``USAGE_GUIDE.md`` §16 — Release history).  Reference này tồn
  tại để giữ MIT-style attribution; **không** phải fork / không phải
  source of releases.
- ``garrytan`` — upstream MIT attribution cho
  `gstack <https://github.com/garrytan/gstack>`_, từ đó VCK port
  Python browser daemon + 16 ``/vck-*`` slash command (clean-room
  reimplementation).  Reference cũng tồn tại thuần để giữ
  attribution; không pull code thực từ org này lúc build.

Quy tắc bổ sung (PR2):

- ``ALLOWED_ORGS`` size **phải ≤ 3**; xem
  ``tests/test_no_further_rebrands.py`` (gate riêng).
- Mọi PR muốn thêm org thứ 4 phải sửa cả comment block ở đầu file
  này, mô tả rõ "tại sao not a duplicate of an existing entry".
"""
from __future__ import annotations

import pathlib
import re

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]

# Orgs that are legitimate references in this codebase.  Đọc comment
# block ở đầu file cho lý do chi tiết.  Nếu cần thêm/bớt entry, đồng
# thời cập nhật ``tests/test_no_further_rebrands.py`` để giữ size cap.
ALLOWED_ORGS = {"VibecodekitPJ8", "VagabondKingsman", "garrytan"}

# Placeholder orgs used in examples (e.g. "github.com/.../pull/42").
_PLACEHOLDER_ORGS = {"...", "OWNER", "owner", "example", "your-org"}

_ORG_RE = re.compile(r"github\.com/([A-Za-z0-9_.-]+)/")

# Only scan text-ish files; skip binary and vendored content.
_SCAN_SUFFIXES = {".md", ".toml", ".json", ".py", ".yml", ".yaml", ".cfg", ".txt"}
_SKIP_DIRS = {".git", "node_modules", "__pycache__", ".mypy_cache", ".pytest_cache"}

# Historical artefacts are time-stamped releases — content is immutable
# and accurately reflects the canonical org *at the time of release*.
# After cycle 17 PR-F2 flipped PJ7 → PJ8, prior release notes (v0.17 -
# v0.25.1) still legitimately reference PJ7 because that's where the
# release was published.  Re-writing historical files would falsify the
# audit trail; instead, we skip them in the canonical-org scan.
_HISTORICAL_GLOBS = (
    "RELEASE_NOTES_v0.1*.md",   # v0.10..v0.19
    "RELEASE_NOTES_v0.2[0-4]*.md",  # v0.20..v0.24
    "RELEASE_NOTES_v0.25.0.md",
    "RELEASE_NOTES_v0.25.1.md",
)
# CHANGELOG accumulates historical entries; only the topmost section
# (current release) is held to the canonical-org rule via
# tests/test_docs_count_sync.py + the per-PR review.  Older sections
# may reference PJ7 because that's the org that shipped them.
_HISTORICAL_NAMES = {"CHANGELOG.md"}

# Cycle 22 / v0.26.0 — Pattern G "Harness Engineering" was adapted from
# the upstream ``hoangnb24/harness-experimental`` repository.  The two
# attribution files below must reference that org by URL so that human
# readers can find the source material.  Treat them as permanent
# upstream-attribution exceptions (like the historical release-notes
# blocks above).  Do NOT widen this set lightly — additions must be
# tied to a real upstream provenance, not convenience.
_UPSTREAM_ATTRIBUTION_PATHS = {
    "references/43-harness-engineering.md",
    "docs/templates/harness/README.md",
    "RELEASE_NOTES_v0.26.0.md",
}


def _is_historical(p: pathlib.Path) -> bool:
    rel = p.relative_to(REPO_ROOT).as_posix()
    if rel in _UPSTREAM_ATTRIBUTION_PATHS:
        return True
    if p.name in _HISTORICAL_NAMES:
        return True
    for pattern in _HISTORICAL_GLOBS:
        if p.match(pattern):
            return True
    return False


def _scan_files():
    bad: list[str] = []
    for p in REPO_ROOT.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix not in _SCAN_SUFFIXES:
            continue
        if any(skip in p.parts for skip in _SKIP_DIRS):
            continue
        if _is_historical(p):
            continue
        try:
            text = p.read_text(errors="ignore")
        except OSError:
            continue
        for m in _ORG_RE.finditer(text):
            org = m.group(1)
            if org in _PLACEHOLDER_ORGS:
                continue
            if org not in ALLOWED_ORGS:
                rel = p.relative_to(REPO_ROOT)
                bad.append(f"{rel}: found org {org!r} in {m.group(0)!r}")
    return bad


def test_no_stale_org_in_repo():
    bad = _scan_files()
    assert not bad, (
        "Stale / non-canonical GitHub org references found:\n"
        + "\n".join(f"  - {b}" for b in bad)
    )


def test_allowed_orgs_have_documented_rationale():
    """Mọi org trong ``ALLOWED_ORGS`` phải được nhắc trong module
    docstring (``__doc__``) — tức là có lý do tồn tại được ghi rõ
    bằng tiếng Việt cho người review sau này.  Nếu thêm org mới mà
    quên cập nhật comment block, test này fail."""
    import sys
    mod = sys.modules[__name__]
    doc = mod.__doc__ or ""
    missing = [org for org in ALLOWED_ORGS if org not in doc]
    assert not missing, (
        "Các org sau có trong ALLOWED_ORGS nhưng không được giải thích "
        "trong module docstring (vi phạm guideline PR2): "
        f"{sorted(missing)}.  Hãy thêm bullet giải thích trong "
        "module-level docstring của tests/test_repo_urls_canonical.py."
    )
