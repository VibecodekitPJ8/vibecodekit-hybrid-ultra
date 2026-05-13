# VibecodeKit Hybrid Ultra

> **Permission engine + scaffold + MCP server for AI coding agents — pure Python stdlib runtime.**
> Use when an AI agent needs to audit shell commands through a 6-layer pipeline, scaffold a project from a preset, expose tools via Model Context Protocol, or run RRI / RRI-T / RRI-UX methodology gates.
> Start at [`QUICKSTART.md`](QUICKSTART.md) or run `PYTHONPATH=./scripts python -m vibecodekit.cli demo` for an offline 2-second tour.
>
> 🇻🇳 **Người mới / không phải dev?** Đọc
> [`docs/GUIDE_NONTECH_BEGINNER.md`](docs/GUIDE_NONTECH_BEGINNER.md) —
> hướng dẫn step-by-step bằng tiếng Việt: chỉ cần mô tả dự án, tool tự
> đi qua 8 bước (scan → RRI → vision → blueprint → task → code →
> verify → ship) và sinh ra sản phẩm chạy được.  ~20 phút đọc, có
> worked example "App quản lý chi tiêu gia đình" A→Z.

> **Current release:** v0.26.0 ([CHANGELOG](CHANGELOG.md)) — see [Layout](#layout) below for the surface inventory (42 slash commands, 7 sub-agent roles, 33 hook events, 97 conformance probes, …).
>
> **License:** MIT — see [`LICENSE`](LICENSE) and the third-party
> attribution manifest [`LICENSE-third-party.md`](LICENSE-third-party.md).

## Quick demo (< 2 seconds, zero network)

```bash
git clone https://github.com/VibecodekitPJ8/vibecodekit-hybrid-ultra.git
cd vibecodekit-hybrid-ultra
PYTHONPATH=./scripts python -m vibecodekit.cli demo
```

Runs 6 steps offline: doctor health-check, permission engine (classify 5
commands), conformance audit (97 probes), scaffold preview, intent router,
and MCP selfcheck.  See [`examples/`](examples/) for standalone scripts.

---

## 🇻🇳 Hướng dẫn tiếng Việt — từ A → Z cho người mới

> **Đối tượng:** product owner, founder, designer, analyst, hoặc developer
> đang dùng AI coding agent (Claude Code / ChatGPT / Cursor / Codex) muốn
> nâng cấp từ "vibe coding bừa bãi" lên **phương pháp + document + audit
> gate**. Không cần biết Python / Git / TypeScript — chỉ cần biết gõ chat
> + copy-paste lệnh đôi lúc.

### Tool này dùng để làm gì?

VibecodeKit Hybrid Ultra là một **bộ "luật chơi"** cho AI coding agent.
Thay vì gõ "AI ơi làm cho tôi app X" rồi cầu mong AI hiểu đúng, bạn gõ
**một câu mô tả tiếng Việt** và tool tự bắt AI đi qua **8 bước có document
+ có gate kiểm tra**:

```
scan repo → RRI (16 câu phỏng vấn) → vision → blueprint → task graph
   → build từng task → verify (RRI-T / RRI-UX) → ship (CI + deploy)
```

Mỗi bước in ra một file `.md` để bạn duyệt. Bước nào lỗi thì tool hỏi
lại bằng tiếng Việt. Cuối pipeline bạn có **dự án chạy được** + đầy đủ
spec + test + RRI release-gate report.

**Vì sao cần tool này thay vì gõ thẳng vào ChatGPT?**

| Nếu bạn... | Vấn đề khi gõ thẳng | VibecodeKit giúp |
|:----------|:--------------------|:-----------------|
| Mô tả "làm app X" → AI sinh code thẳng | Code lỗi vặt, thiếu test, thiếu spec | Bắt AI làm 8 bước có document trước khi code |
| Mô tả lại lần 2 | AI quên context, làm lại từ đầu | Lưu blueprint + RRI vào `.md`, AI đọc lại |
| Muốn kiểm tra UX | "Trông OK" — không có thước đo | RRI-UX gate 7 dimension × 8 stress axes |
| Muốn tránh lỗi UI hay gặp | Tự nhớ thuộc | Anti-pattern catalog 12 lỗi kèm BAD/GOOD |
| Cần chọn màu / font | Tốn 30 phút lượn Pinterest | 7 palette + 5 font pair sẵn theo ngành |
| Lo AI chạy lệnh nguy hiểm | Không kiểm soát được | Permission engine 6-layer chặn `rm -rf /` v.v. |

### 1. Cài đặt 3 bước (~5 phút)

**Yêu cầu:** Python ≥ 3.9 + Git + 1 trong các AI CLI (Claude Code, Cursor,
ChatGPT web, hoặc Codex CLI).

```bash
# Bước 1 — tải tool
git clone https://github.com/VibecodekitPJ8/vibecodekit-hybrid-ultra.git
cd vibecodekit-hybrid-ultra

# Bước 2 — chạy demo offline (~2 giây, không cần internet)
PYTHONPATH=./scripts python3 -m vibecodekit.cli demo

# Bước 3 — verify (không bắt buộc, nhưng đẹp khi pass)
pytest -q                                          # → 1566 passed
PYTHONPATH=./scripts python3 -m vibecodekit.conformance_audit
                                                   # → 97/97 probes met=True
```

Nếu cả 3 bước OK → tool đã sẵn sàng.

> **Tip cho Claude Code / Cursor:** copy thư mục `update-package/.claude/`
> vào project của bạn để có sẵn 42 slash command (`/vibe`, `/vibe-scaffold`,
> `/vck-ship`, v.v.). Xem [`Option 2`](#option-2--install-update-package-into-an-existing-project)
> bên dưới hoặc đọc [`update-package/README.md`](update-package/README.md).

### 2. Lệnh đầu tiên — chạy pipeline 8 bước

**Cách 1 (đơn giản nhất):** dùng master command `/vibe` với mô tả tự nhiên.

Trong Claude Code / Cursor:

```
/vibe Tôi muốn làm app quản lý chi tiêu cho gia đình, có web + mobile
```

Tool sẽ **tự route** câu đó qua intent router → dispatch sang
`/vibe-scaffold + /vibe-rri + /vibe-vision + …` và đi qua đủ 8 bước.

**Cách 2 (gõ tay từng bước):** xem bảng §3 bên dưới.

### 3. Pipeline 8 bước — mỗi bước 1 dòng

| # | Bước | Để làm gì | Lệnh | Output |
|:-:|:----|:----------|:-----|:-------|
| 1 | **Scan** | Đọc repo + docs hiện có | `/vibe-scan` | `runtime/scan/*.md` |
| 2 | **RRI** | 5 personas hỏi 16 câu để rõ requirement | `/vibe-rri` | `runtime/rri/cycle-*/answers.jsonl` |
| 3 | **Vision** | Chốt mục tiêu 1 dòng + 3 KPI + non-goals | `/vibe-vision` | `vision.md` |
| 4 | **Blueprint** | Architecture + data model + interface | `/vibe-blueprint` | `blueprint.md` |
| 5 | **Task graph** | Chia 5-30 task TIP (Task Instruction Pack) | `/vibe-task graph` | `runtime/tasks/*.json` |
| 6 | **Build** | Spawn `builder` sub-agent build từng task | `/vibe-subagent builder <tip>` | code thực |
| 7 | **Verify** | Run RRI-T (test) + RRI-UX (UX) + VN-12 gate | `/vibe-rri-t`, `/vibe-rri-ux`, `/vibe-vn-check` | report `.md` |
| 8 | **Ship** | Test → review → commit → push → PR → deploy | `/vck-ship`, `/vibe-ship vercel` | PR + preview URL |

Mỗi bước có thể chạy độc lập (gõ slash command trực tiếp) hoặc để
master `/vibe` tự điều phối.

### 4. 10 lệnh hay dùng nhất

| Lệnh | Dùng khi | Ví dụ |
|:-----|:--------|:------|
| `/vibe <mô tả>` | Muốn AI tự đi 8 bước từ mô tả tự nhiên | `/vibe Tôi muốn làm shop online bán giày` |
| `/vibe-scaffold <preset>/<stack>` | Cần khung dự án sẵn (11 preset × 3 stack) | `/vibe-scaffold saas/nextjs` |
| `/vibe-doctor` | Health-check tool sau khi cài | `vibe doctor --root .` |
| `/vibe-audit` | 97 conformance probe (xem code có sạch không) | `vibe audit --threshold 1.0` |
| `/vibe-permission "<lệnh>"` | Hỏi tool: "lệnh này có an toàn không?" | `vibe permission "rm -rf /" --user-runtime` |
| `/vibe-memory query <q>` | Tìm trong 3-tier memory (user/project/team) | `vibe memory query "color palette"` |
| `/vibe-rri-t <jsonl>` | Test release gate 7 dimension × 8 axes | `vibe rri-t tests/touchfiles.json` |
| `/vibe-rri-ux <jsonl>` | UX release gate (Flow Physics) | `vibe rri-ux ux-flags.json` |
| `/vck-review` | Adversarial review 7 specialist (security + perf + a11y + ...) | `/vck-review` |
| `/vck-ship` | Atomic: test → review → qa → commit → push → PR | `/vck-ship` |

### 5. Tính năng chính — mỗi cái 1 đoạn + 1 lệnh demo

#### 5.1. Scaffold engine — 11 preset × 3 stack

11 khung dự án sẵn (`saas` / `landing-page` / `shop-online` / `blog` /
`dashboard` / `portfolio` / `docs` / `api-todo` / `mobile-app` / `crm` /
`osint-terminal`) × 3 stack (`nextjs` / `fastapi` / `expo`). Mỗi preset
có sẵn design tokens (6 màu × dark/light) + sample component (Button /
Input / Card) + Tailwind config pre-wired.

```bash
PYTHONPATH=./scripts python3 -m vibecodekit.cli scaffold preview saas/nextjs
# → liệt 23 file sẽ được sinh + checksum
```

Chi tiết: [`references/41-component-library-pattern.md`](references/41-component-library-pattern.md),
[`references/42-osint-terminal-template.md`](references/42-osint-terminal-template.md).

#### 5.2. Permission engine — 6-layer pipeline

Trước khi AI agent chạy bất kỳ shell command nào, tool đi qua 6 layer:
(1) dangerous-pattern regex → (2) classification (read/write/network/destructive)
→ (3) mode policy (default/auto_safe/accept_edits/yolo/plan) → (4) escalation
gate → (5) approval contract → (6) audit log.

```bash
vibe permission "rm -rf /" --user-runtime
# → deny (layer 1: dangerous_pattern), exit 2

vibe permission "git status" --user-runtime
# → allow (default mode), exit 0
```

`--user-runtime` (xem `CHANGELOG.md` cho release ship) lưu state về `~/.vibecode/` thay vì `$cwd` —
tránh pollute working directory. Chi tiết:
[`references/10-permission-classification.md`](references/10-permission-classification.md).

#### 5.3. Conformance audit — 97 internal probe

Mỗi release chạy 97 probe kiểm tra **architectural invariant** (không
phải benchmark code-quality ngoài). Probe cover: install pipeline, doc
parity, mirror surface sync, scaffold integrity, permission engine
coverage, etc.

```bash
PYTHONPATH=./scripts python3 -m vibecodekit.conformance_audit --threshold 1.0
# → parity: 100.00% (97/97, threshold 100%)
```

Methodology: [`BENCHMARKS-METHODOLOGY.md`](BENCHMARKS-METHODOLOGY.md).

#### 5.4. Doctor — health-check

Kiểm tra 30+ invariant: VERSION mirror sync, scaffold manifest schema,
references count, hook script exists, MCP server registry, etc.

```bash
vibe doctor --root .
# → ✓ 32 checks passed
```

#### 5.5. Memory hierarchy — 3 tier

- **user**: `~/.vibecode/memory/` (cross-project)
- **project**: `./.vibecode/memory/` (repo-local)
- **team**: `./.vibecode/memory/team/` (commit vào repo)

Retrieval lai lexical + embedding (default `hash-256` offline; có thể
switch sang `sentence-transformers` qua `vibe config set-backend`).

```bash
vibe memory write user "Tôi thích palette xanh tealmint"
vibe memory query user "palette"
# → match score 0.83: "Tôi thích palette xanh tealmint"
```

#### 5.6. MCP integration — stdio + inproc

Đăng ký MCP server (Model Context Protocol) để expose tool tới Claude /
Codex. Bundled sample: `vibecodekit.mcp_servers.selfcheck` (tool `ping`,
`echo`, `now`).

```bash
vibe mcp register selfcheck \
  --transport inproc --module vibecodekit.mcp_servers.selfcheck
vibe mcp tools selfcheck
# → ping, echo, now
```

#### 5.7. Intent router — natural-language dispatch

Master `/vibe <prose>` route câu của bạn (cả tiếng Anh + tiếng Việt) vào
1 trong 8 verb (`scan / plan / build / review / qa / ship / audit /
doctor`) hoặc 1 trong 11 scaffold preset.

```bash
vibe intent route "tôi muốn làm trang điều khiển OSINT"
# → preset=osint-terminal, verb=BUILD, locale=vi
```

Benchmark hiện tại: set-inclusion accuracy 0.9808 (xem
`benchmarks/intent_router_0.26.0.json`).

#### 5.8. Hooks — 33 lifecycle event

4 hook script trong `.claw/hooks/` chặn pattern nguy hiểm, redact secret,
trigger pre-compact, init session. Cover 33 event group: tool (3) +
permission (2) + session (3) + agent (3) + task (4) + context (3) +
filesystem (4) + UI/config (5) + query legacy (6).

#### 5.9. Sub-agent — 7 role ACL-enforced

`coordinator / scout / builder / qa / security / reviewer / qa-lead` —
mỗi role có ACL trong `subagent_runtime.PROFILES`. Read-only role
(coordinator, scout, qa, security, reviewer, qa-lead) **không thể** ghi
file (`can_mutate=False`).

```bash
vibe subagent spawn builder "Implement /api/expense POST endpoint"
```

#### 5.10. RRI — Reverse Requirements Interview

5 personas (PM / engineer / designer / QA / ops) × 3 mode (CHALLENGE /
GUIDED / EXPLORE) hỏi tới 16 câu để clarify requirement. Question bank
trong `assets/rri-question-bank.json` (schema 1.2.0, 12 project-type
buckets).

```bash
vibe rri start --mode CHALLENGE --project-type saas
```

3 flavor release-gate: RRI-T (testing 7 dim × 8 axes), RRI-UX (Flow
Physics), RRI-UI (design pipeline 4-phase).

### 6. Worked example A → Z

Có sẵn 1 worked example đầy đủ trong
[`docs/GUIDE_NONTECH_BEGINNER.md` §4](docs/GUIDE_NONTECH_BEGINNER.md):
**"App quản lý chi tiêu gia đình"** — từ mô tả 1 dòng tới sản phẩm
deploy lên Vercel, đi qua hết 8 bước, tổng thời gian ~45 phút.

**Dùng Devin?** Chạy programmatic walkthrough 8 bước trong 1 lệnh:

```bash
PYTHONPATH=./scripts python examples/devin_pipeline_demo.py \
    --target /tmp/myproject
```

Demo sinh 20 file (vision.md, blueprint.md, 4 TIP, scaffold api-todo
fastapi, RRI answers, RRI-T touchfiles) — không cần Claude Code, không
cần network. Skill cho Devin session: [`.devin/skills/build-with-vibecodekit/SKILL.md`](.devin/skills/build-with-vibecodekit/SKILL.md).

### 7. Xử lý 5 lỗi hay gặp

| Lỗi | Nguyên nhân | Sửa |
|:----|:-----------|:----|
| `pytest` báo `ModuleNotFoundError: No module named 'tests'` | Repo cũ chưa có `pythonpath = ["."]` trong `pyproject.toml` (xem `CHANGELOG.md` cho release ship fix) | Update lên release mới nhất hoặc tạm dùng `PYTHONPATH=. pytest` |
| `vibe permission` để lại `.vibecode/runtime/denials.json` trong `$cwd` | Quên cờ `--user-runtime` | Dùng `vibe permission "<cmd>" --user-runtime` để state về `~/.vibecode/` |
| `pip3 install ...` báo `externally-managed-environment` | Python system protected (PEP 668) | `python3 -m venv .venv && source .venv/bin/activate && pip install ...` |
| Tool không hiểu mô tả tiếng Việt | Intent router cần keyword cụ thể (xem `references/00-overview.md` §intent) | Thêm từ khoá scaffold: "tôi muốn làm **app saas**…" hoặc "**trang điều khiển**…" |
| CLI báo `command not found: vibe` | `pip install -e .` chưa chạy | Hoặc `pip install -e .` hoặc dùng `PYTHONPATH=./scripts python3 -m vibecodekit.cli <subcmd>` |

### 8. Đi sâu hơn

| Tài liệu | Khi nào đọc | Độ dài |
|:---------|:-----------|:------:|
| [`docs/GUIDE_NONTECH_BEGINNER.md`](docs/GUIDE_NONTECH_BEGINNER.md) | Người không phải dev, muốn worked-example A→Z | ~20 phút |
| [`docs/DEVIN_NEW_SESSION_GUIDE.md`](docs/DEVIN_NEW_SESSION_GUIDE.md) | Dùng Devin để build project end-to-end (xem §9 bên dưới) | ~15 phút |
| [`QUICKSTART.md`](QUICKSTART.md) | Đã quen pipeline, cần 5-min refresher | 5 phút |
| [`USAGE_GUIDE.md`](USAGE_GUIDE.md) | Reference đầy đủ 31 CLI + 42 slash + 7 sub-agent + 33 hook + 97 probe | ~60 phút |
| [`SKILL.md`](SKILL.md) | Cài làm Claude/Cursor skill | 5 phút |
| [`.devin/skills/build-with-vibecodekit/SKILL.md`](.devin/skills/build-with-vibecodekit/SKILL.md) | Skill cho Devin session (auto-load) | 5 phút |
| [`references/00-overview.md`](references/00-overview.md) | Hiểu architecture + design decision | ~30 phút |
| [`BENCHMARKS-METHODOLOGY.md`](BENCHMARKS-METHODOLOGY.md) | Hiểu "97 probe" thực sự đo gì | 10 phút |
| [`CHANGELOG.md`](CHANGELOG.md) | Lịch sử release + breaking change | tra cứu |

### 9. Dùng tool với Devin session mới — paste link repo + 1 prompt

Section này dành cho user muốn **dùng [Devin](https://app.devin.ai)** thay cho Claude Code / Cursor để build project end-to-end qua pipeline 8 bước của VibecodeKit. Toàn bộ workflow: paste link repo này + 1 prompt mô tả project → Devin tự clone, tự load skill `.devin/skills/build-with-vibecodekit/SKILL.md`, tự drive 8 bước qua Python CLI (không cần slash command, không cần Claude/Cursor).

#### 9.1. Khi nào dùng Devin thay cho Claude Code / Cursor?

| Tiêu chí | Devin | Claude Code / Cursor |
|:---------|:-----:|:--------------------:|
| Chạy autonomous nhiều giờ liền (overnight build, batch task) | ✓✓ | ✗ |
| Có VM cloud riêng (PR tự push, server tự deploy) | ✓ | ✗ (chỉ local) |
| Slash command UX (`/vibe-scan`, `/vck-ship`, …) | gián tiếp (đọc markdown làm prompt template) | ✓ trực tiếp |
| Test browser end-to-end (Playwright + real Chrome) | ✓✓ | ✗ |
| Cần Python + git auth có sẵn | ✓ (auth proxied) | dev tự cài |
| Phù hợp scope task | medium-large project, multi-step | small change, single-file edit |

→ Devin tốt nhất cho: **build project mới từ đầu**, **deep audit + refactor**, **end-to-end test có browser**, **chạy đêm tự deploy**. Claude/Cursor tốt nhất cho: **iterative single-file edit**, **rapid prototyping với UX feedback ngay lập tức**.

#### 9.2. Prompt template (paste vào Devin session mới)

```
Tôi muốn build [LOẠI PROJECT] dùng VibecodeKit Hybrid Ultra.

Repo tool: https://github.com/VibecodekitPJ8/vibecodekit-hybrid-ultra

Yêu cầu:
1. Clone repo trên vào /home/ubuntu/repos/
2. Đọc và load skill .devin/skills/build-with-vibecodekit/SKILL.md
3. Chạy pipeline 8 bước (scan → RRI → vision → blueprint → task graph →
   build → verify → ship) cho project sau:

   [MÔ TẢ PROJECT 2-3 CÂU — gồm goal, user, stack ưu tiên]

4. Mỗi bước báo lại kết quả + chờ tôi confirm trước khi sang bước sau.
5. Build xong push PR vào branch riêng + chia sẻ link preview deploy.
```

**Ví dụ điền:**

```
Tôi muốn build SaaS landing-page "tích kim cương loyalty cho cafe" dùng
VibecodeKit Hybrid Ultra.

Repo tool: https://github.com/VibecodekitPJ8/vibecodekit-hybrid-ultra

Yêu cầu:
1. Clone repo trên vào /home/ubuntu/repos/
2. Đọc và load skill .devin/skills/build-with-vibecodekit/SKILL.md
3. Chạy pipeline 8 bước cho project sau:

   Web app cho chuỗi cafe nhỏ (3-10 chi nhánh), nhân viên scan QR khách
   mỗi lần khách order, sau N lần thì khách đổi thưởng. Stack ưu tiên
   Next.js 15 + Supabase. Mục tiêu deploy Vercel preview trong < 2h.

4. Mỗi bước báo lại + chờ tôi confirm.
5. Push PR + link preview Vercel.
```

#### 9.3. Workflow Devin sẽ chạy (timeline 5 phase, ~30-90 phút tuỳ scope)

| Phase | Bước | Devin action | Expected output | Có cần user OK? |
|:-----:|:-----|:-------------|:----------------|:---------------:|
| **Setup** (5 min) | 0 | `git clone https://github.com/VibecodekitPJ8/vibecodekit-hybrid-ultra.git` + verify `python examples/devin_pipeline_demo.py --no-keep` chạy được | demo exit 0, 8 step pass | ✗ |
| **Discover** (10 min) | 1 SCAN | `vibe doctor --root <target>` + đọc README user paste | doctor exit=0 + 1-line health summary | ✗ |
| **Discover** (10 min) | 2 RRI | Đọc `assets/rri-question-bank.json`, sinh 5 câu hỏi cho user theo project_type | 5 câu hỏi tóm tắt | ✓ (user trả lời 5 câu) |
| **Plan** (10 min) | 3 VISION | Tổng hợp answers → write `vision.md` (goal + 3 KPI + non-goal) | `vision.md` ~50 dòng | ✓ (confirm goal đúng) |
| **Plan** (10 min) | 4 BLUEPRINT | Write `blueprint.md` (architecture + REQ-* matrix + 4-5 TIP) | `blueprint.md` ~150 dòng | ✓ (confirm scope) |
| **Build** (20-60 min) | 5 TASK GRAPH | `vibe task graph blueprint.md` → DAG 4-5 node | `task-graph.json` | ✗ |
| **Build** (20-60 min) | 6 BUILD | `vibe scaffold apply <preset> <stack>` → loop sub-agent builder qua mỗi TIP | scaffold files + diff per TIP | ✓ (review từng TIP) |
| **Ship** (10 min) | 7 VERIFY | `vibe rri-t` + `vibe audit` + `vibe vn-check` (nếu VN scope) + `pytest` | gate PASS hết | ✗ |
| **Ship** (10 min) | 8 SHIP | `git commit + push + gh pr create` + (option) `vibe ship vercel` | PR link + preview URL | ✗ (sau khi user gật bước 6) |

#### 9.4. 10 prompt mẫu sẵn cho 10 loại project

| # | Project type | Mô tả ngắn paste vào prompt |
|:-:|:-------------|:----------------------------|
| 1 | **SaaS landing** | "Landing page cho [service]. Goal capture email + 1 CTA. Next.js + Tailwind. Deploy Vercel preview." |
| 2 | **Blog** | "Blog cá nhân + RSS + sitemap. Mỗi bài MDX. Stack Next.js. Theme: minimal serif." |
| 3 | **API service** | "API thuần FastAPI cho [domain]. SQLite, 4 endpoint CRUD, OpenAPI auto. Deploy Fly.io." |
| 4 | **Dashboard** | "Internal dashboard cho [team]. Table + chart + auth. Stack Next.js + Recharts + Supabase." |
| 5 | **OSINT terminal** | "Terminal-UI single-page cho [investigation]. Theme cyan-on-black. Stack Next.js + xterm.js." |
| 6 | **Mobile app** | "Expo React Native app cho [use case]. 3 screen + AsyncStorage local. Build preview qua EAS." |
| 7 | **Portfolio** | "Portfolio dev/designer. About + Projects (CMS) + Contact. Stack Astro. Deploy Cloudflare Pages." |
| 8 | **Docs site** | "Docs site cho [library]. Search + dark mode + i18n vi/en. Stack Docusaurus hoặc Nextra." |
| 9 | **CRM** | "Mini CRM cho [SMB]. Lead + contact + activity log. Auth + role admin/agent. Stack Next.js + Postgres." |
| 10 | **Shop online** | "Shop e-commerce nhỏ (< 50 SKU). Cart + checkout Stripe. Stack Next.js + Vercel." |

Mỗi prompt mẫu khớp 1 scaffold preset có sẵn trong `assets/scaffolds/` — Devin sẽ tự pick preset đúng ở bước 6 BUILD (xem `vibe scaffold list`).

#### 9.5. Cơ chế Devin auto-discover skill

Khi Devin session khởi động trong repo, nó tự scan thư mục `.devin/skills/` ở root. Mỗi sub-folder có `SKILL.md` với YAML frontmatter sẽ được parse + đăng ký vào skill registry. User prompt mention keyword (`vibecodekit`, `/vibe`, `vck-ship`, `8-step pipeline`, …) → Devin matching skill rồi auto-invoke trước khi response.

Verify skill load đúng (chạy trong session):

```
session> "Bạn có skill nào liên quan vibecodekit không?"
Devin>   "Có skill build-with-vibecodekit ở .devin/skills/. Khi user
          mention pipeline / scaffold / audit / vibe-*, mình sẽ chạy
          theo 8 bước được document trong SKILL.md."
```

#### 9.6. Q&A nhanh

| Q | A |
|:--|:--|
| Devin có cần install Python không? | Không — VM Devin đã có Python 3.9+ + git. Repo có `requires-python = ">=3.9"`. |
| Có cần Claude Code / Cursor không? | Không — pipeline 8 bước drive được 100% qua Python CLI. Slash command markdown chỉ là **prompt template** Devin đọc, không phải dependency. |
| Devin cần secret/credential gì? | Mặc định không cần. Nếu deploy: `VERCEL_TOKEN` / `FLY_API_TOKEN` / etc. Nếu test browser: không cần. Nếu MCP: tuỳ MCP server. |
| Có miễn phí không? | Tool VibecodeKit MIT free. Devin tính phí session theo plan riêng — xem [docs.devin.ai](https://docs.devin.ai). |
| Devin có thể chạy đêm tự build không? | Có. Skill document workflow async + user OK gate ở bước 3/4/6. Devin sẽ pause + ping khi cần input. |
| Bug Devin báo không match codebase? | Reproducer: paste lệnh `vibe doctor` output + step Devin đang stuck. Devin sẽ tự `git diff` + report. |

#### 9.7. Khi nào Devin escalate hỏi user

Skill `.devin/skills/build-with-vibecodekit/SKILL.md` mặc định ACL:

| Lệnh | Tự chạy | Hỏi user |
|:-----|:-------:|:--------:|
| `vibe scan` / `doctor` / `audit` (read-only) | ✓ | ✗ |
| `vibe scaffold apply` (vào dir mới) | ✓ | ✗ |
| `vibe scaffold apply` (overwrite dir đã có file) | ✗ | ✓ (force) |
| `git push --force` / `git reset --hard` | ✗ | ✓ |
| `rm -rf` / `sudo` / `curl | sh` | ✗ | ✓ chỉ-explicit |
| `vibe ship --prod` (deploy production) | ✗ | ✓ (luôn) |
| Test có audit-trail lock (`test_canonical_org_no_bypass.py`) | ✗ | ✓ |

Khi Devin escalate, user nhận message + có thể click button "Approve" / "Deny" / "Skip" trong webapp.

**Bonus: chạy demo trước khi build thật**

Trước khi giao project thật cho Devin, có thể chạy demo end-to-end 8 bước trong < 30 giây để verify tool hoạt động:

```bash
PYTHONPATH=./scripts python examples/devin_pipeline_demo.py \
    --target /tmp/devin-demo --no-keep
```

Output sẽ in 8 banner step + ~20 artefact, exit 0 nếu tool healthy. Xem [`docs/DEVIN_NEW_SESSION_GUIDE.md`](docs/DEVIN_NEW_SESSION_GUIDE.md) để hiểu sâu hơn về từng bước.

---

### 10. Harness Engineering compatibility — `vibe harness` (Pattern G, v0.26.0+)

Kể từ v0.26.0, VibecodeKit cung cấp một entry path "Harness-style ops layer" như alternative nhẹ hơn so với full 8-step pipeline.  Dựa trên [OpenAI Harness Engineering writeup](https://openai.com/index/harness-engineering/) + reference repo upstream (xem attribution trong [`references/43-harness-engineering.md`](references/43-harness-engineering.md)).

**Khi nào dùng Pattern G thay cho full pipeline?**

| Tình huống | Dùng | Vì sao |
|:-----------|:-----|:-------|
| Greenfield, chưa có repo, muốn intake nhanh | `vibe harness init` + `spec-intake.md` | Lighter than RRI |
| Story nhỏ, scope rõ (1-2 file change) | `vibe harness story "..."` | Tránh boilerplate TIP / Blueprint |
| Story đụng auth/data/migrations | `vibe harness classify ...` rồi `story` | Auto-route sang `high-risk` 4-file folder |
| Architecture decision (FE framework, DB choice) | `vibe harness decision "..."` | Auto-numbered ADR parallel với DESIGN-LOG |
| Multi-team product, nhiều domain | Full pipeline (`/vibe-scan` → `/vibe-rri` → ...) | Pattern G chưa đủ depth cho multi-domain |

**4 lệnh chính:**

```bash
# 10-flag risk classifier (heuristic + manual override)
vibe harness classify "Add a refresh-token endpoint" --json
# → lane: high_risk (auth là hard gate), validation: 5 layer

# Copy 9 Harness templates vào project bất kỳ
vibe harness --root /path/to/project init

# Scaffold story packet, auto-classify lane
vibe harness --root . story "User can reset password"
# → docs/stories/US-001-user-can-reset-password.md (hoặc 4-file folder cho high-risk)

# Scaffold ADR
vibe harness --root . decision "Adopt JWT with refresh-token rotation"
# → docs/decisions/0001-adopt-jwt-with-refresh-token-rotation.md
```

**10-flag taxonomy + 5 hard gate:**

| Flag | Hard gate? | Trigger ví dụ |
|:-----|:----------:|:--------------|
| `auth` / `authorization` / `data_model` / `audit_security` / `external_systems` | ✓ | login, RBAC, migration, audit log, webhook |
| `public_contracts` / `cross_platform` / `existing_behavior` / `weak_proof` / `multi_domain` | | API shape, mobile, refactor, no-tests, multi-domain |

**Lane decision rule:**
- ≥ 1 hard gate → `high_risk` (5-layer validation ladder)
- 0/1 flag → `tiny` (unit test only)
- 2-3 flag → `normal` (unit + integration)
- ≥ 4 flag → `high_risk`

**Pattern G là additive, không thay thế:**

Existing users tiếp tục dùng `vibe scan` / `vibe rri` / `vibe blueprint` / 42 slash command như cũ.  Pattern G chỉ thêm 1 CLI surface mới (`vibe harness ...`) + 9 template + 1 reference doc + probe #97 — không touch logic cũ.

**Đi sâu hơn:** [`references/43-harness-engineering.md`](references/43-harness-engineering.md) (vocabulary map VCK ↔ Harness, probe #97 contract, attribution).

---

## Skills inspired by gstack

The `/vck-*` slash commands + Python browser daemon are adapted —
with attribution — from
[gstack](https://github.com/garrytan/gstack) (© Garry Tan, MIT,
commit `675717e3`).  Per-version evolution (which release introduced
which subset, audit probe count growth, etc.) is tracked in
[`CHANGELOG.md`](CHANGELOG.md); the kit currently ships **97** internal
conformance probes — see
[`BENCHMARKS-METHODOLOGY.md`](BENCHMARKS-METHODOLOGY.md) for what that
number measures and what it does **not** claim.

Canonical `/vck-*` inventory:

- `/vck-cso` — Chief Security Officer audit (OWASP Top 10 + STRIDE).
- `/vck-review` — 7-perspective adversarial review (architect / security / perf / a11y / ux / dx / risk).
- `/vck-qa`, `/vck-qa-only` — real-browser QA checklist VN-12.
- `/vck-ship` — atomic test → review → qa → commit → push → PR.
- `/vck-investigate` — NO-FIX-WITHOUT-INVESTIGATION root-cause flow.
- `/vck-canary` — 30-minute post-deploy monitor.
- (plus `/vck-pipeline`, `/vck-eng-review`, `/vck-ceo-review`,
  `/vck-second-opinion`, `/vck-design-consultation`,
  `/vck-design-review`, `/vck-office-hours`, `/vck-learn`,
  `/vck-retro` — xem `manifest.llm.json` cho danh sách đầy đủ 16
  command ở phiên bản hiện tại.)

The browser daemon is a **clean-room Python reimplementation** of
gstack's persistent-daemon architecture (atomic state file + idle
timeout + permission-classified commands + ARIA datamarking + URL
blocklist).  It ships stdlib-only for the core; Playwright + FastAPI
are gated behind the `[browser]` extra:

```bash
pip install "vibecodekit-hybrid-ultra[browser]"
playwright install chromium
```

See [`LICENSE-third-party.md`](LICENSE-third-party.md) for the full
per-artefact attribution table and
[`references/40-ethos-vck.md`](references/40-ethos-vck.md) for the
ETHOS adaptation.

### Activation cheat sheet

| Module | Auto-merged into VCK-HU flow? | Activate by |
|---|---|---|
| `security_classifier` | ✓ via `pre_tool_use` hook (auto-on default since the gstack-port wiring; xem CHANGELOG.md) | always on; opt-out `VIBECODE_SECURITY_CLASSIFIER=0` |
| `eval_select` | ✓ via `/vck-ship` Bước 2 + CI preview | drop `tests/touchfiles.json` |
| `learnings` | ✓ via `session_start` hook (auto-inject 10 latest, PR-B) + `/vck-learn` + `/vck-retro` | always on; opt-out `VIBECODE_LEARNINGS_INJECT=0` |
| `team_mode` + `session_ledger` | ✓ via `/vck-ship` Bước 0 (gate enforcement) | `python -m vibecodekit.team_mode init …` |
| browser daemon | ✓ via `/vck-qa` skill | `pip install -e ".[browser]"` |
| 16 `/vck-*` slash commands | ✓ via manifest + intent_router | type `/vck-<name>` in host |
| GitHub Actions CI | ✓ on every PR/push (3.9 / 3.11 / 3.12) | always on |

Full walkthrough: [`USAGE_GUIDE.md` §18](USAGE_GUIDE.md#18-activation-cheat-sheet--gstack-port-modules-v0120v0150).

---

## Layout

**Surface inventory (v0.26.0)** — moved here from the opening to keep
the front matter focused on what the kit *does* rather than how many
buttons it has:

- **42 slash commands** — 25 `/vibe-*` + 1 master `/vibe` + 16 `/vck-*`
  (5 of which are marked `deprecated: true` with explicit canonical
  replacement, target removal in `v1.0.0`; see
  [`tests/test_deprecated_frontmatter.py`](tests/test_deprecated_frontmatter.py)).
- **8-verb unified front-door** — `/vibe <verb>` dispatches to one of
  `scan / plan / build / review / qa / ship / audit / doctor` →
  canonical slash command (additive layer on top of the 42).
- **7 sub-agent roles** — coordinator, scout, builder, qa, security,
  reviewer, qa-lead (ACL-enforced in `subagent_runtime.PROFILES`).
- **33 hook events** — 9 lifecycle groups in
  `hook_interceptor.SUPPORTED_EVENTS`.
- **6-layer permission pipeline** — see
  `references/10-permission-classification.md`.
- **3-tier persistent memory** — user / project / team, retrieval
  hybrid lexical + embedding (default `hash-256`, offline).
- **MCP integration** — stdio + inproc adapters; bundled selfcheck
  server (`vibecodekit.mcp_servers.selfcheck`).
- **97 internal conformance probes** — see
  [`BENCHMARKS-METHODOLOGY.md`](BENCHMARKS-METHODOLOGY.md) for what
  these measure and what they explicitly do **not** claim (no
  HumanEval / MBPP / SWE-bench, no external benchmark, no API key
  dependency).
- **VIBECODE-MASTER v5 methodology** — 8-step workflow (Scan → RRI →
  Vision → Blueprint → Task graph → Build → Verify → Release).
- **RRI / RRI-T / RRI-UI / RRI-UX** — 4 release-gate question banks +
  evaluators in `methodology.py`.
- **Python-pure browser daemon** — Playwright wired in Phase 1, used
  by `/vck-qa` for sub-second checklist verification.
- **Scaffold engine** — 11 presets × 3 stacks (saas / landing / shop /
  blog / dashboard / portfolio / docs / api-todo / mobile / crm /
  osint-terminal).

```
vibecodekit-hybrid-ultra/
├── SKILL.md                ← Claude/Cursor skill manifest (entry point)
├── USAGE_GUIDE.md          ← User-facing walkthrough
├── QUICKSTART.md           ← 5-minute setup
├── CHANGELOG.md            ← Release history
├── VERSION                 ← Canonical version (single source of truth)
├── manifest.llm.json       ← LLM-readable manifest
│
├── assets/                 ← Plugin manifest, RRI question banks, scaffold templates
├── scripts/                ← Python runtime (vibecodekit/ package)
│   └── vibecodekit/
│       ├── cli.py
│       ├── permission_engine.py    ← classify_cmd, _normalise_unicode (Cf strip)
│       ├── install_manifest.py     ← fcntl-locked installer
│       ├── methodology.py          ← RRI loaders + VIBECODE-MASTER v5
│       ├── scaffold_engine.py      ← 11 presets × 3 stacks
│       ├── doctor.py
│       └── audit.py
│
├── tests/                  ← 367 pytest cases (root: 366 + 1 skipped)
├── tools/                  ← validate_release_matrix.py + helpers
├── references/             ← VIBECODE-MASTER v5, RRI methodology docs
├── runtime/                ← Runtime data (RRI cycles, etc.)
│
└── update-package/         ← Drop-in payload that gets copied into a user project
    ├── README.md
    ├── USAGE_GUIDE.md
    ├── CLAUDE.md
    ├── VERSION
    ├── .claw.json
    └── .claude/            ← Claude config (commands, hooks)
```

---

## Install (for end users)

### Option 1 — drop the skill into Claude Code / Cursor

Download the latest skill bundle from
[Releases](https://github.com/VibecodekitPJ8/vibecodekit-hybrid-ultra/releases/latest):

```bash
# Skill bundle (full runtime + tests + docs)
# Replace vX.Y.Z with the latest release tag (see /releases page).
curl -L https://github.com/VibecodekitPJ8/vibecodekit-hybrid-ultra/releases/download/vX.Y.Z/vibecodekit-hybrid-ultra-vX.Y.Z-skill.zip -o skill.zip
unzip skill.zip -d ~/.claude/skills/vibecodekit-hybrid-ultra
```

### Option 2 — install update package into an existing project

```bash
# Replace vX.Y.Z with the latest release tag (see /releases page).
curl -L https://github.com/VibecodekitPJ8/vibecodekit-hybrid-ultra/releases/download/vX.Y.Z/vibecodekit-hybrid-ultra-vX.Y.Z-update-package.zip -o update.zip
unzip update.zip -d /path/to/your/project/
```

The update package is what `python -m vibecodekit.cli install <dst>`
copies under the hood (251 files into `.claude/`, `.claw.json`,
docs, etc.).

---

## Develop locally

```bash
git clone https://github.com/VibecodekitPJ8/vibecodekit-hybrid-ultra.git
cd vibecodekit-hybrid-ultra

# Run the canonical release gate
VIBECODE_UPDATE_PACKAGE="$(pwd)/update-package" \
PYTHONPATH=./scripts \
python3 -m pytest tests -q

python3 tools/validate_release_matrix.py \
    --skill   "$(pwd)" \
    --update  "$(pwd)/update-package"
```

Expected gate output (concrete count grows with each release — the
important invariant is that pytest exits 0 with no failures and the
internal conformance self-test reports all probes passing).  Số liệu
tham khảo dưới đây ứng với commit hiện tại trên nhánh `main` (xem
[`CHANGELOG.md`](CHANGELOG.md) cho từng release):

```
pytest                            : <N> passed                # at current main (see CHANGELOG.md)
audit (×any)                      : 97/97 met=True[^bench]    # at current main (internal self-test)
validate_release_matrix (default) : PASS
```

[^bench]: Internal regression gate — see [BENCHMARKS-METHODOLOGY.md](BENCHMARKS-METHODOLOGY.md) for what the 97/97 number actually measures (architectural invariants only, not external code-quality benchmarks).

Để lấy số chính xác cho bản đang ở local, chạy:

```bash
cat VERSION                                                  # ví dụ: 0.16.2
VIBECODE_UPDATE_PACKAGE="$(pwd)/update-package" \
  PYTHONPATH=./scripts python3 -m pytest tests -q | tail -1  # số case pytest
PYTHONPATH=./scripts python3 -m vibecodekit.conformance_audit \
    --threshold 1.0 | head -1                                # ví dụ: parity: 100.00% (97/97, threshold 100%)
```

(Under `root`, the `test_install_into_readonly_dir` test is intentionally
`skipif(geteuid() == 0)` because root bypasses POSIX DAC and the
sibling file-where-dir test already covers the surface.)

---

## Release artifacts

Each tagged release ships three artifacts:

| Artifact | Description |
|---|---|
| `vibecodekit-hybrid-ultra-vX.Y.Z-skill.zip` | Full skill bundle (drop into `~/.claude/skills/`) |
| `vibecodekit-hybrid-ultra-vX.Y.Z-update-package.zip` | Drop-in payload for existing projects |
| `vX.Y.Z-refine-report.md` | Stress-dipdive / refine notes for the release |

The canonical CHANGELOG is in [`CHANGELOG.md`](CHANGELOG.md).

---

## Methodology

This repo implements two layered methodologies:

* **VIBECODE-MASTER v5** — 8-phase release cycle:
  SCAN → RRI → VISION → BLUEPRINT → TASK GRAPH → BUILD → VERIFY → REFINE.
  See `references/VIBECODE-MASTER-v5.txt`.

* **RRI (Reverse Requirements Interview)** — three flavours:
  * RRI-T (Testing) — 7 dimensions × 8 stress axes
  * RRI-UI — UI-state coverage matrix
  * RRI-UX — UX-flow coverage matrix

  See `references/RRI-*_METHODOLOGY.docx` and `runtime/rri/`.

Question banks live in `assets/rri-question-bank.json`
(schema 1.2.0, 12 project-type buckets, 5 personas × 3 modes).

---

## License

MIT (with attribution paragraph for the gstack-derived `/vck-*` slash
commands).  See [`LICENSE`](LICENSE) for the canonical text and
[`LICENSE-third-party.md`](LICENSE-third-party.md) for the inspiration
/ rewrite-and-integration credit on the gstack → `/vck-*` derivation.

---

## Quality assurance

Số ca pytest và số probe lớn dần theo từng release; bảng dưới đây
phản ánh trạng thái **tại nhánh `main` hiện tại** (xem
[`CHANGELOG.md`](CHANGELOG.md) cho lịch sử số liệu theo từng version,
và [`BENCHMARKS-METHODOLOGY.md`](BENCHMARKS-METHODOLOGY.md) để biết
"97/97" thực sự đo cái gì — không phải benchmark chất lượng ngoài).

| Gate | Result | What it measures |
|---|---|---|
| pytest (xem `pytest --collect-only -q \| tail`) | PASS | Unit + integration correctness |
| conformance self-test | 97/97 met=True[^bench] | Internal regression invariants ([details](BENCHMARKS-METHODOLOGY.md)) |
| validate_release_matrix (default) | PASS | Layout integrity across 3 deploy modes |
| All 170 Cf codepoints × `rm -rf /` bypass | blocked | Permission engine coverage |

See `CHANGELOG.md` for full version history and the per-release
`*-refine-report.md` artifacts (kept under `docs/historical/` for
releases more than two minors old).
