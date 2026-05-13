# claw-code-pack (VibecodeKit Hybrid Ultra v0.26.0)

Drop-in overlay for projects that use `claw-code` / Claude Code / Codex.
After extracting into your project root you'll have:

- `.claude/commands/` — **42 slash commands** at v0.26.0: 25 `/vibe-*` + 1 master `/vibe`
  (`/vibe`, `/vibe-scaffold`, `/vibe-ship`, `/vibe-run`, `/vibe-doctor`,
  `/vibe-subagent`, `/vibe-memory`, `/vibe-approval`, `/vibe-task`,
  `/vibe-scan`, `/vibe-vision`, `/vibe-rri`, `/vibe-rri-t`, `/vibe-rri-ux`,
  `/vibe-rri-ui`, …) plus 16 `/vck-*` (`/vck-pipeline`, `/vck-ship`,
  `/vck-review`, `/vck-cso`, `/vck-qa`, …)
- `.claude/agents/` — 7 role cards (coordinator, scout, builder, qa, security, reviewer, qa-lead)
- `.claw/hooks/` — 4 lifecycle hooks (pre/post tool use, pre compact, session start)
- `ai-rules/vibecodekit/` — runtime package + references + templates
- `QUICKSTART.md` — 5-minute onboarding (read this first)
- `CLAUDE.md` — project-overlay notes for Claude Code
- `VERSION` — canonical version string (current: see top-level `VERSION`)

## Install

The update package ships **advisory content only** (slash commands, hooks,
agents, placeholder `ai-rules/` landing-zone). The Python runtime lives in the
**skill bundle** (`vibecodekit-hybrid-ultra-vX.Y.Z-skill.zip`).  Install
both (replace `vX.Y.Z` with the release tag you downloaded):

```bash
# 1. extract the skill bundle somewhere stable on your machine
unzip vibecodekit-hybrid-ultra-vX.Y.Z-skill.zip -d ~/.vibecode

# 2. extract the update package into your project root (slash cmds + hooks + agents)
unzip vibecodekit-hybrid-ultra-vX.Y.Z-update-package.zip -d /path/to/myproject

# 3. run the reconciliation installer from the skill bundle — this copies
#    scripts/references/templates into /path/to/myproject/ai-rules/vibecodekit/
PYTHONPATH=~/.vibecode/vibecodekit-hybrid-ultra/scripts \
  python -m vibecodekit.cli install /path/to/myproject --dry-run

# 4. confirm health
PYTHONPATH=/path/to/myproject/ai-rules/vibecodekit/scripts \
  python -m vibecodekit.cli doctor --root /path/to/myproject
```

Note: `python -m ai-rules.vibecodekit...` is **not** a valid Python module path
(hyphens are not allowed in package names). Always invoke via `vibecodekit.cli`
with `PYTHONPATH` pointing at the scripts directory.

## Release gate

Bản hiện tại trên nhánh `main` (xem `CHANGELOG.md` cho từng release; số
ca pytest tăng theo thời gian — chạy `pytest --collect-only -q | tail`
để xem con số chính xác cho commit của bạn):

- **pytest**: all actionable tests pass (số case tăng theo release; xem `CHANGELOG.md`)
- **conformance self-test**: 96 / 97 internal regression probes pass[^bench] (self-test, not external benchmark; see `BENCHMARKS-METHODOLOGY.md`)
- **fresh-extract self-test**: 92 / 97 probes pass
- **integration tests**: 8 e2e + 3 UX + 6 version-sync

[^bench]: Internal regression gate — chi tiết "97/97" đo cái gì xem `BENCHMARKS-METHODOLOGY.md` (architectural invariants only, không phải benchmark code-quality ngoài như HumanEval / SWE-bench).

Lịch sử các milestone (v0.11.x / v0.15.x / v0.16.x) được giữ trong `CHANGELOG.md`.

See `ai-rules/vibecodekit/SKILL.md`, `ai-rules/vibecodekit/references/00-overview.md`
and `CLAUDE.md` for the complete methodology reference.

---

## 🇻🇳 Hướng dẫn tiếng Việt nhanh (sau khi cài update-package)

Sau khi extract update-package vào project, bạn có 42 slash command sẵn
trong `.claude/commands/`. Lệnh hay dùng:

| Lệnh | Để làm gì |
|:-----|:----------|
| `/vibe <mô tả>` | Master router — AI tự đi qua 8 bước pipeline từ mô tả tự nhiên |
| `/vibe-scaffold <preset>/<stack>` | Sinh khung dự án (11 preset × 3 stack) |
| `/vibe-doctor` | Health-check overlay đã cài đúng chưa |
| `/vibe-audit` | 97 conformance probe (regression guard) |
| `/vibe-permission "<cmd>"` | Hỏi: lệnh shell này có an toàn không (6-layer pipeline) |
| `/vck-ship` | Atomic: test → review → qa → commit → push → PR |
| `/vck-review` | Adversarial review 7 specialist |

**Pipeline 8 bước:** scan → RRI → vision → blueprint → task graph →
build → verify → ship. Đầy đủ hướng dẫn tiếng Việt cho người mới (kèm
worked example "App quản lý chi tiêu" A→Z, ~20 phút đọc):

- [`docs/GUIDE_NONTECH_BEGINNER.md`](../docs/GUIDE_NONTECH_BEGINNER.md) — A→Z cho người không phải dev
- [`README.md` §🇻🇳 Hướng dẫn tiếng Việt](../README.md#-hướng-dẫn-tiếng-việt--từ-a--z-cho-người-mới) — comprehensive cheatsheet
- [`USAGE_GUIDE.md`](USAGE_GUIDE.md) — reference đầy đủ 31 CLI + 42 slash + 7 sub-agent + 33 hook + 97 probe

> **Lưu ý (since v0.25.3 — xem `CHANGELOG.md`):** Khi chạy `vibe permission` demo nên thêm cờ
> `--user-runtime` để state lưu về `~/.vibecode/` thay vì pollute project.
