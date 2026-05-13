# Dùng VibecodeKit với Devin session mới — guide A → Z

> **Audience:** user mới muốn dùng [Devin](https://app.devin.ai) để build project end-to-end qua pipeline 8 bước của VibecodeKit Hybrid Ultra mà KHÔNG cần Claude Code / Cursor / dev environment riêng.
>
> **TL;DR:** paste link repo này + 1 prompt mô tả project vào Devin session mới → Devin tự clone, tự load skill `.devin/skills/build-with-vibecodekit/SKILL.md`, tự drive 8 bước qua Python CLI.
>
> Companion ngắn gọn ở [`README.md §9`](../README.md#9-dùng-tool-với-devin-session-mới--paste-link-repo--1-prompt).

---

## Mục lục

1. [Cài đặt 1 lần (Devin VM)](#1-cài-đặt-1-lần-devin-vm)
2. [Prompt template chi tiết](#2-prompt-template-chi-tiết)
3. [Pipeline 8 bước qua góc nhìn Devin](#3-pipeline-8-bước-qua-góc-nhìn-devin)
4. [Patterns: 5 cách dùng Devin với tool này](#4-patterns-5-cách-dùng-devin-với-tool-này)
5. [Approval / Secret / 2FA workflow](#5-approval--secret--2fa-workflow)
6. [Troubleshooting 10 lỗi hay gặp](#6-troubleshooting-10-lỗi-hay-gặp)
7. [Glossary 12 thuật ngữ](#7-glossary-12-thuật-ngữ)

---

## 1. Cài đặt 1 lần (Devin VM)

Khi bạn mở session Devin mới (https://app.devin.ai/sessions/new), VM Devin **đã có sẵn**:

- Python 3.9+ (repo yêu cầu `>= 3.9`)
- `git` (auth qua git proxy của Devin, không cần token)
- `node` / `npm` / `bun` cho Next.js scaffold
- Chrome browser + Playwright cho real-browser test
- Persistent home directory (`/home/ubuntu`)

Devin sẽ tự chạy bước setup này (user không cần input):

```bash
cd /home/ubuntu/repos
git clone https://github.com/VibecodekitPJ8/vibecodekit-hybrid-ultra.git
cd vibecodekit-hybrid-ultra
pip install -e .         # hoặc PYTHONPATH=./scripts
vibe doctor              # smoke check
vibe audit               # 97/97 probe verify
```

Nếu `pip install -e .` fail vì PEP 668 (`externally-managed-environment`):

```bash
python3 -m venv .venv && source .venv/bin/activate && pip install -e .
```

Hoặc dùng PYTHONPATH:

```bash
export PYTHONPATH=$PWD/scripts
python -m vibecodekit.cli --help     # 31 subcommand
```

**Verify skill load** (chạy demo end-to-end trong < 30 giây):

```bash
PYTHONPATH=./scripts python examples/devin_pipeline_demo.py \
    --target /tmp/devin-demo --no-keep
```

Output sẽ in 8 banner `STEP N/8 — ...` + ~20 artefact, exit 0 nếu tool healthy.

---

## 2. Prompt template chi tiết

### 2.1. Template tối thiểu (paste vào session mới)

```
Tôi muốn build [LOẠI PROJECT] dùng VibecodeKit Hybrid Ultra.

Repo tool: https://github.com/VibecodekitPJ8/vibecodekit-hybrid-ultra

Yêu cầu:
1. Clone repo trên vào /home/ubuntu/repos/
2. Đọc và load skill .devin/skills/build-with-vibecodekit/SKILL.md
3. Chạy pipeline 8 bước (scan → RRI → vision → blueprint → task graph →
   build → verify → ship) cho project sau:

   [MÔ TẢ PROJECT 2-3 CÂU]

4. Mỗi bước báo lại kết quả + chờ tôi confirm trước khi sang bước sau.
5. Build xong push PR vào branch riêng + chia sẻ link preview deploy.
```

### 2.2. Template đầy đủ (kèm constraint + budget)

```
Tôi muốn build [LOẠI PROJECT] dùng VibecodeKit Hybrid Ultra.

Repo tool: https://github.com/VibecodekitPJ8/vibecodekit-hybrid-ultra

PROJECT:
- Tên: [tên project]
- Mục tiêu: [1 câu — what + why]
- User chính: [persona ngắn]
- Tính năng MVP: [3-5 bullet]
- Stack ưu tiên: [Next.js / FastAPI / Expo / ...]
- Deploy: [Vercel / Fly / Cloudflare / không deploy lần này]
- Deadline: [thời gian — Devin sẽ tự ước lượng budget]

CONSTRAINTS:
- Tuyệt đối KHÔNG: [vd: không dùng Firebase / không gửi data về EU / không
  gọi paid API > $5]
- BẮT BUỘC: [vd: phải có dark mode / phải VN i18n / phải audit-trail
  immutable]

YÊU CẦU PIPELINE:
1. Clone repo VibecodeKit + load skill
2. Pipeline 8 bước; tại bước 3 (vision) + 4 (blueprint) + 6 (build TIP-N)
   pause + chờ tôi review trước khi tiến tiếp.
3. Khi escalate (rm -rf / sudo / ship --prod / overwrite existing dir):
   hỏi tôi qua message_user với content_type=user_question.
4. Build xong push PR vào branch devin/<timestamp>-<slug>, không push main.
5. Test end-to-end qua browser nếu có UI (Devin Test Mode).
6. Cuối session: ghi report ngắn + link PR + link preview.
```

### 2.3. Anti-patterns trong prompt (TRÁNH)

| Prompt xấu | Vấn đề | Fix |
|:-----------|:------|:----|
| "Build cho tao 1 app." | Quá vague — Devin không biết stack / scope / deploy | Thêm "[LOẠI PROJECT] + mô tả 2-3 câu" |
| "Làm hết, đừng hỏi gì cả." | Tắt safety gate — risk overwrite / push main / leak secret | Giữ default ACL từ skill |
| "Skip step 2 (RRI), tao biết rồi." | Bỏ RRI = vision drift cao, blueprint thiếu requirement | RRI 5 personas chỉ tốn 5 phút — nên giữ |
| "Đừng dùng VibecodeKit, tự build đi." | Phá toàn bộ pipeline + audit trail | Nếu không muốn dùng tool, mở session mới không paste repo |

---

## 3. Pipeline 8 bước qua góc nhìn Devin

### Bước 1 — SCAN (read-only health-check, ~3 min)

**Devin action:**
```bash
vibe doctor --root /home/ubuntu/repos/<target-project>
vibe audit                              # 97/97 verify
ls -la                                  # discover existing files
git log --oneline -20 2>/dev/null || echo "fresh project, no git"
```

**Expected output:**
- `vibe doctor` exit 0 + 1-line health summary
- `vibe audit` parity = 1.0000
- File tree summary (5-10 dòng)

**Có gate user?** Không — read-only.

**Nếu fail:**
- `vibe doctor` exit ≠ 0 → fix invariant trước khi tiếp (xem `vibe doctor --verbose`)
- `vibe audit` < 97/97 → bug môi trường, Devin sẽ retry hoặc escalate

---

### Bước 2 — RRI (Reverse Requirements Interview, ~5-10 min)

**Devin action:**
```bash
vibe rri start --mode CHALLENGE --project-type <inferred-from-prompt>
```

Tool sẽ load `assets/rri-question-bank.json` (5 persona × 3 mode × 12 project type) và pick ra 5-8 câu hỏi theo persona quan trọng nhất cho project type.

**Devin sẽ chuyển 5-8 câu hỏi sang user qua `message_user` với `content_type=user_question`** (mỗi câu là 1 question option).

**Expected output user thấy:**

```
[Question 1/5 — PM persona]
Goal lớn nhất 6 tháng tới của sản phẩm là gì?
- [ ] Tăng MAU (acquisition)
- [ ] Tăng retention (D7+)
- [ ] Tăng revenue per user
- [ ] Khác — text input

[Question 2/5 — Engineer persona]
...
```

**Có gate user?** Có — user trả lời 5-8 câu.

**Tip:**
- Trả lời ngắn gọn (1-2 câu mỗi câu), Devin sẽ tổng hợp.
- Nếu chưa biết câu trả lời, chọn "Khác — text input" và viết "chưa rõ, cần Devin recommend".

---

### Bước 3 — VISION (synthesise → vision.md, ~3 min)

**Devin action:**
- Tổng hợp answers RRI thành `vision.md`:
  - 1-line goal
  - 3 KPI có số đo cụ thể (vd: "1000 MAU sau 3 tháng")
  - 3-5 non-goal (cái KHÔNG làm)
  - 1 deadline coarse-grained
- Write file vào `/home/ubuntu/repos/<project>/vision.md`

**Expected output:**
- `vision.md` ~30-60 dòng
- Devin gửi user preview vision.md (attached file) + ask "Confirm vision này đúng?"

**Có gate user?** Có — user OK/edit vision.

**Tip:**
- Nếu vision sai goal → user sửa thẳng vào prompt: "Vision sai, KPI 3 nên là X chứ không phải Y, fix lại".

---

### Bước 4 — BLUEPRINT (architecture + REQ-* matrix, ~5-10 min)

**Devin action:**
- Đọc `references/35-blueprint-template.md` làm guide structure
- Write `blueprint.md` gồm:
  - **Architecture diagram** (ASCII, 5-15 component)
  - **Data model** (entities + relationship)
  - **API surface** (endpoint list nếu có backend)
  - **REQ-\* matrix** (vd: REQ-1 = "user có thể tạo account", REQ-2 = "auth qua email", …)
  - **4-5 TIP** (Task Instruction Pack) — mỗi TIP = 1 unit work, có acceptance criteria

**Expected output:**
- `blueprint.md` ~100-200 dòng
- Devin gửi user preview blueprint + ask "Confirm scope + REQ-* + 4-5 TIP đúng?"

**Có gate user?** Có — user OK/cắt scope.

**Tip:**
- Đây là gate quan trọng nhất. Sai blueprint = build sai. User nên đọc kỹ blueprint trước khi OK.
- Nếu thấy TIP-3 thừa: nói "bỏ TIP-3, scope MVP không cần phần đó".

---

### Bước 5 — TASK GRAPH (DAG of TIPs, ~2 min)

**Devin action:**
```bash
vibe task graph blueprint.md > task-graph.json
```

Tool parse blueprint → DAG node (TIP) + edge (dependency).

**Expected output:**
- `task-graph.json` (~30 dòng JSON)
- Devin có thể visualize qua `mermaid` diagram nếu user yêu cầu

**Có gate user?** Không — deterministic transform.

---

### Bước 6 — BUILD (apply scaffold + per-TIP sub-agent, ~20-60 min)

**Devin action:**

**6a. Pick + apply scaffold preset:**
```bash
vibe scaffold list
vibe scaffold preview <preset> --stack <nextjs|fastapi|expo>
vibe scaffold apply <preset> --stack <stack> --target /home/ubuntu/repos/<project>
```

11 preset có sẵn: `saas / landing-page / blog / dashboard / portfolio / docs / shop-online / mobile-app / api-todo / crm / osint-terminal`. Devin sẽ pick preset matching project type (vd: "SaaS landing" → `saas` preset).

**6b. Loop sub-agent builder qua mỗi TIP:**
```bash
vibe subagent spawn builder TIP-01
vibe subagent spawn builder TIP-02
...
```

Mỗi sub-agent builder có ACL hạn chế (`can_mutate=true`, `run_command=true`, `push=false`). Bug high-blast-radius → bubble-escalate lên Devin coordinator → escalate user.

**Expected output per TIP:**
- 5-20 file diff
- Devin commit từng TIP riêng (`git commit -m "TIP-01: <description>"`)
- Devin gửi user diff preview sau mỗi TIP + ask "Review TIP-01 OK?"

**Có gate user?** Có — review per-TIP (nếu user muốn skip review, prompt thêm "auto-confirm tất cả TIP nếu tests pass").

**Tip:**
- Nếu thấy TIP-2 đi sai hướng: nói "TIP-2 sai, rollback + viết lại với approach Y".
- Devin tự rollback (`git reset --soft HEAD~1`) + retry.

---

### Bước 7 — VERIFY (gate chạy hết, ~5 min)

**Devin action:**
```bash
vibe rri-t --jsonl tests/touchfiles.jsonl     # 7 dim × 8 axes
vibe rri-ux --jsonl ux/touchfiles.jsonl       # nếu có UI
vibe vn-check --file flags.json               # nếu VN scope
vibe audit                                     # 97/97
pytest                                         # full suite
```

**Expected output:**
- Tất cả gate PASS (≥ 70 % per dim, ≥ 5/7 @ ≥ 85 %, 0 P0 FAIL)
- Audit 97/97 met=True parity=1.0000
- pytest exit 0

**Nếu fail:**
- Devin tự fix loop (max 3 attempt) → escalate user nếu vẫn fail

**Có gate user?** Không (auto-fix), trừ khi fail 3 lần.

---

### Bước 8 — SHIP (PR + deploy preview, ~5 min)

**Devin action:**
```bash
git checkout -b devin/$(date +%s)-<slug>
git add -A
git commit -m "Initial scaffold + 5 TIP — <project name>"
git push -u origin HEAD
gh pr create --title "<project>" --body "$(cat .pr-template-filled.md)"

# Nếu user yêu cầu deploy:
vibe ship vercel --preview        # hoặc fly / cloudflare / netlify
```

**Expected output:**
- PR URL
- Preview deploy URL (Vercel / Fly / Cloudflare)
- Final report ngắn với:
  - Files created/modified count
  - Test pass rate
  - Audit parity
  - Estimated cost (Devin token + deploy cost)

**Có gate user?** Có — nếu deploy `--prod`. Preview deploy tự chạy.

---

## 4. Patterns: 5 cách dùng Devin với tool này

### Pattern A — Project mới from-zero (default)

→ Workflow chính ở §3. Bắt đầu từ prompt "build project mới ...".

### Pattern B — Add module vào existing repo

```
Tôi đã có repo <your-repo-url>. Thêm module
"loyalty-points" theo Pattern F (reuse-max / build-min) của VibecodeKit.

Repo tool: https://github.com/VibecodekitPJ8/vibecodekit-hybrid-ultra
```

→ Devin sẽ chạy `vibe-module` workflow thay cho 8 step (scan existing repo, plan reuse-max, build module mới, integrate test).

### Pattern C — Audit + refactor existing project

```
Repo dự án của tôi: <your-repo-url>

Repo tool: https://github.com/VibecodekitPJ8/vibecodekit-hybrid-ultra

Hãy chạy deep audit (vulture / ruff / mypy / grep stale ref / link check)
+ propose 3 refactor priority + hỏi tôi pick 1 trước khi sửa.
```

→ Devin sẽ chạy `vibe audit --external` (against external repo, không touch core probe) + propose plan, không build mới.

### Pattern D — Generate test suite cho code có sẵn

```
Code của tôi: <path or repo URL>

Repo tool: https://github.com/VibecodekitPJ8/vibecodekit-hybrid-ultra

Generate test suite (pytest cho Python / vitest cho TS) đạt coverage ≥ 80 %.
Theo phương pháp RRI-T 7 dim × 8 axes của VibecodeKit.
```

→ Devin run `vibe rri-t` mode write + sinh test files.

### Pattern E — Code review cho PR người khác

```
Repo: <your-repo-url>
PR cần review: #123

Repo tool: https://github.com/VibecodekitPJ8/vibecodekit-hybrid-ultra

Chạy review theo /vck-review (adversarial 7-specialist) +
/vck-cso (security audit) + comment finding vào PR.
```

→ Devin run reviewer + security sub-agent + post comment.

---

## 5. Approval / Secret / 2FA workflow

### 5.1. Khi Devin escalate hỏi user

Skill `.devin/skills/build-with-vibecodekit/SKILL.md` document ACL — Devin chỉ escalate khi gặp:

- Lệnh trong blacklist: `rm -rf` / `sudo` / `dd` / `curl | sh` / `chmod 777`
- `git push --force` / `git reset --hard` / `git push main`
- `vibe scaffold apply` overwrite directory đã có file
- `vibe ship --prod` (production deploy)
- Test có audit-trail lock (vd: `test_canonical_org_no_bypass.py`)
- Bất kỳ lệnh nào dùng secret chưa được provision (xem 5.2)

Khi escalate, user thấy message + 3 button:
- **Approve** — chạy lệnh
- **Deny** — block + Devin pick alternative
- **Skip** — bỏ qua step này

### 5.2. Provision secret (vd: deploy Vercel)

Devin sẽ ask user 3 option (theo skill spec):

1. **Skip** — proceed without secret (vd: build local, không deploy)
2. **Temporary for session** — paste secret 1 lần, mất khi session kết thúc
3. **Permanent for all future sessions** — save vào org / user / repo scope

Naming convention secret:
- `VERCEL_TOKEN` / `FLY_API_TOKEN` / `CLOUDFLARE_API_TOKEN`
- `OPENAI_API_KEY` / `ANTHROPIC_API_KEY`
- `_2FA_<service>` cho TOTP

### 5.3. 2FA (TOTP) cho deploy

Nếu deploy cần 2FA (vd: Vercel CLI), Devin ask user export TOTP secret từ password manager:
- **1Password:** Edit item → copy "one-time password secret"
- **Authy:** Settings → Export → copy `otpauth://` URI
- Paste vào Devin với `type=totp`, Devin sẽ tự generate code mỗi 30s

---

## 6. Troubleshooting 10 lỗi hay gặp

| # | Lỗi | Nguyên nhân | Fix |
|:-:|:----|:-----------|:----|
| 1 | `ModuleNotFoundError: No module named 'vibecodekit'` | `pip install -e .` chưa chạy hoặc PYTHONPATH chưa set | `pip install -e .` HOẶC `export PYTHONPATH=$PWD/scripts` |
| 2 | `ModuleNotFoundError: No module named 'tests'` | Repo cũ < v0.25.3 | Update v0.25.3+ (có `pythonpath = ["."]` trong pyproject) |
| 3 | `vibe permission` để lại denials.json trong cwd | Quên cờ `--user-runtime` | `vibe permission "<cmd>" --user-runtime` |
| 4 | `pip install` báo `externally-managed-environment` | PEP 668 | `python3 -m venv .venv && source .venv/bin/activate && pip install -e .` |
| 5 | Devin không tự load skill | Skill folder không đúng convention | Kiểm tra `.devin/skills/build-with-vibecodekit/SKILL.md` có frontmatter + path đúng |
| 6 | `vibe audit` báo < 97 probe | Repo chưa sync với main HEAD | `git pull origin main && pip install -e .` |
| 7 | Devin push direct vào main | Prompt thiếu constraint | Thêm `"luôn push vào branch devin/<timestamp>-<slug>, không push main"` vào prompt |
| 8 | Scaffold apply fail "directory not empty" | Target đã có file | Either `vibe scaffold apply ... --force` HOẶC chọn dir trống |
| 9 | Build TIP fail loop > 3 lần | Sub-agent builder không break được | Devin sẽ escalate user — user có thể edit TIP requirement hoặc skip |
| 10 | Test browser fail "Chrome not found" | Devin VM không có Chrome (rare) | Re-init session hoặc dùng `vibe ship` thay vì test E2E |

---

## 7. Glossary 12 thuật ngữ

| Thuật ngữ | Định nghĩa |
|:----------|:-----------|
| **VIBECODE-MASTER v5** | Methodology 8 bước (scan → RRI → vision → blueprint → task graph → build → verify → ship) — xem `references/VIBECODE-MASTER-v5.txt` |
| **TIP** | Task Instruction Pack — 1 unit work atomic (vd: TIP-01 "implement signup endpoint") |
| **REQ-\*** | Requirement matrix item từ blueprint (vd: REQ-3 "user có thể đổi password") |
| **RRI** | Reverse Requirements Interview — 5 personas (PM/Engineer/Designer/QA/Ops) × 3 mode (CHALLENGE/GUIDED/EXPLORE) |
| **RRI-T** | RRI Testing dimension — 7 dim × 8 axes test plan |
| **RRI-UX** | RRI UX dimension — 7 dim × 8 Flow Physics axes UX critique |
| **Scaffold preset** | Pre-built template cho 1 project type (11 preset × 3 stack = 33 combo) |
| **Conformance audit** | 96 internal regression probe — chạy `vibe audit` để verify tool healthy |
| **Permission engine** | 6-layer classifier (literal block → glob → semantic → user-override → audit log → escalate) — `permission_engine.py` |
| **Sub-agent** | 7 role (coordinator/scout/builder/qa/security/reviewer/qa-lead) với ACL khác nhau — `subagent_runtime.py` |
| **Intent router** | NL → CLI subcommand mapping (vd: "audit cho tao" → `vibe audit`) — `intent_router.py` |
| **Hook events** | 33 lifecycle event (pre/post tool, session start/end, …) — `.claw/hooks/` |

---

## Reference docs (đọc thêm)

- [`README.md §9`](../README.md#9-dùng-tool-với-devin-session-mới--paste-link-repo--1-prompt) — VN summary 1 page
- [`.devin/skills/build-with-vibecodekit/SKILL.md`](../.devin/skills/build-with-vibecodekit/SKILL.md) — skill spec Devin auto-load
- [`examples/devin_pipeline_demo.py`](../examples/devin_pipeline_demo.py) — programmatic 8-step walkthrough
- [`docs/GUIDE_NONTECH_BEGINNER.md`](GUIDE_NONTECH_BEGINNER.md) — worked example A→Z (45 min)
- [`USAGE_GUIDE.md`](../USAGE_GUIDE.md) — reference đầy đủ 31 CLI + 42 slash + 7 sub-agent + 33 hook + 97 probe
- [`references/VIBECODE-MASTER-v5.txt`](../references/VIBECODE-MASTER-v5.txt) — methodology bản gốc
- [Devin docs](https://docs.devin.ai) — Devin platform reference
