#!/usr/bin/env python3
"""End-to-end programmatic walkthrough of the VIBECODE-MASTER v5 8-step pipeline.

Designed for **Devin** sessions (or any Python-driven agent) that want to
exercise the pipeline without going through Claude Code slash commands.

Usage:
    PYTHONPATH=./scripts python examples/devin_pipeline_demo.py \\
        --target /tmp/devin-pipeline-demo

Runs 8 annotated steps. No network. No Claude/Cursor required. All writes
go into ``--target`` (a fresh temp directory by default); the repo working
tree is untouched.

The demo uses the ``api-todo / fastapi`` preset because it ships with all 3
stacks and is the smallest scaffold (~15 files). Swap via ``--preset``.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import warnings
from pathlib import Path

# Make the bundled package importable without a venv.
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

# Suppress noisy DeprecationWarnings while the demo walks the pipeline;
# decide() is still functional and decide_typed() routes through it.
warnings.filterwarnings("ignore", category=DeprecationWarning)

from vibecodekit.intent_router import IntentRouter  # noqa: E402
from vibecodekit.permission_engine import classify_cmd, decide_typed  # noqa: E402
from vibecodekit.scaffold_engine import ScaffoldEngine  # noqa: E402
from vibecodekit.subagent_runtime import PROFILES  # noqa: E402


def banner(step: int, title: str) -> None:
    bar = "═" * 68
    print(f"\n{bar}\n  STEP {step}/8 — {title}\n{bar}")


def sub(msg: str) -> None:
    print(f"  → {msg}")


def step_1_scan(target: Path) -> None:
    """Read the repo / target directory — invariant health check."""
    banner(1, "SCAN — health-check + read-only repo discovery")

    sub(f"Scanning REPO_ROOT={REPO_ROOT}")
    md_files = sorted(REPO_ROOT.glob("*.md"))
    sub(f"  found {len(md_files)} top-level .md docs (README, CHANGELOG, ...)")

    sub(f"Scanning TARGET={target}")
    target.mkdir(parents=True, exist_ok=True)
    existing = list(target.iterdir())
    sub(f"  target has {len(existing)} entries (clean slate OK)")

    sub("Running `vibe doctor --root <REPO_ROOT>` invariant check ...")
    proc = subprocess.run(
        [sys.executable, "-m", "vibecodekit.cli", "doctor", "--root", str(REPO_ROOT)],
        env={"PYTHONPATH": str(REPO_ROOT / "scripts"), "PATH": ""},
        capture_output=True,
        text=True,
        check=False,
    )
    last_line = (proc.stdout.strip().splitlines() or [""])[-1]
    sub(f"  doctor exit={proc.returncode} last_line={last_line!r}")


def step_2_rri(target: Path) -> None:
    """Reverse Requirements Interview — load question bank, synthesise answers."""
    banner(2, "RRI — load 5 personas × 3 modes question bank")

    bank_path = REPO_ROOT / "assets" / "rri-question-bank.json"
    bank = json.loads(bank_path.read_text())
    sub(f"Question bank schema: {bank.get('version', '?')}")
    sub(f"  personas:      {len(bank.get('personas', []))}")
    sub(f"  modes:         {len(bank.get('modes', []))}")
    sub(f"  project_types: {len(bank.get('project_types', {}))}")
    for ptype in list(bank.get("project_types", {}).keys())[:5]:
        sub(f"    • {ptype}")

    answers_dir = target / "runtime" / "rri" / "cycle-1"
    answers_dir.mkdir(parents=True, exist_ok=True)
    answers_path = answers_dir / "answers.jsonl"
    sample_answers = [
        {"persona": "pm", "q_id": "saas.scope.1", "answer": "tracking spending across family members"},
        {"persona": "engineer", "q_id": "saas.tech.1", "answer": "FastAPI + SQLite + 1 user"},
        {"persona": "designer", "q_id": "saas.ux.1", "answer": "single-page, no dark mode v1"},
        {"persona": "qa", "q_id": "saas.test.1", "answer": "happy-path + 1 edge case per endpoint"},
        {"persona": "ops", "q_id": "saas.deploy.1", "answer": "Vercel preview, no prod yet"},
    ]
    with answers_path.open("w") as fh:
        for entry in sample_answers:
            fh.write(json.dumps(entry) + "\n")
    sub(f"  wrote {len(sample_answers)} synthesised answers → {answers_path}")


def step_3_vision(target: Path) -> None:
    """Pin 1-line goal + 3 KPIs + non-goals."""
    banner(3, "VISION — 1-line goal + 3 KPIs + non-goals")

    vision_path = target / "vision.md"
    vision_path.write_text(
        "# Vision — demo family-expense API\n\n"
        "**Goal:** ship a single-tenant family-expense tracking API in <1 day.\n\n"
        "## KPIs\n\n"
        "1. POST /expenses creates a record in <100ms (p95).\n"
        "2. GET /summary returns monthly totals (1 endpoint, 1 join).\n"
        "3. 100% test coverage on the 2 endpoints above.\n\n"
        "## Non-goals\n\n"
        "- Multi-tenant / authentication (v2)\n"
        "- Currency conversion (v2)\n"
        "- Mobile UI (v2)\n"
    )
    sub(f"wrote {vision_path}")


def step_4_blueprint(target: Path) -> None:
    """Architecture + data model + interface."""
    banner(4, "BLUEPRINT — architecture + data model + REQ-* matrix")

    blueprint_path = target / "blueprint.md"
    blueprint_path.write_text(
        "# Blueprint — family-expense API\n\n"
        "## Architecture\n\n"
        "- FastAPI + SQLite (single file `expenses.db`)\n"
        "- 2 endpoints: `POST /expenses`, `GET /summary`\n"
        "- No auth, no migration (initial schema in `init_db()`)\n\n"
        "## Data model\n\n"
        "```python\n"
        "class Expense(BaseModel):\n"
        "    id: int\n"
        "    amount_vnd: int        # VND, integer to avoid float\n"
        "    category: str          # e.g. 'food', 'transport'\n"
        "    created_at: datetime\n"
        "```\n\n"
        "## REQ-* matrix\n\n"
        "| REQ-ID | Description | Verified by |\n"
        "|:-------|:------------|:------------|\n"
        "| REQ-01 | POST /expenses creates row | test_post_expense |\n"
        "| REQ-02 | GET /summary returns monthly totals | test_get_summary |\n"
        "| REQ-03 | p95 latency < 100ms | locust profile |\n"
    )
    sub(f"wrote {blueprint_path}")


def step_5_task_graph(target: Path) -> None:
    """Break blueprint into TIPs (Task Instruction Packs)."""
    banner(5, "TASK GRAPH — 4 TIPs split from blueprint")

    tasks_dir = target / "runtime" / "tasks"
    tasks_dir.mkdir(parents=True, exist_ok=True)
    tips = [
        {"id": "TIP-01", "title": "scaffold api-todo/fastapi", "depends_on": []},
        {"id": "TIP-02", "title": "rename to family-expense + add Expense model", "depends_on": ["TIP-01"]},
        {"id": "TIP-03", "title": "implement POST /expenses + GET /summary", "depends_on": ["TIP-02"]},
        {"id": "TIP-04", "title": "add pytest cases for REQ-01 + REQ-02", "depends_on": ["TIP-03"]},
    ]
    for tip in tips:
        (tasks_dir / f"{tip['id']}.json").write_text(json.dumps(tip, indent=2))
    sub(f"wrote {len(tips)} TIPs → {tasks_dir}")


def step_6_build(target: Path, preset: str, stack: str) -> None:
    """Build TIP-01 by applying the scaffold; show sub-agent ACL summary."""
    banner(6, f"BUILD — apply scaffold {preset}/{stack} (TIP-01)")

    engine = ScaffoldEngine()
    plan = engine.preview(preset, stack=stack)
    sub(f"preview: {len(plan.files)} files, ~{plan.estimated_loc} LOC")

    scaffold_target = target / "scaffold"
    if scaffold_target.exists():
        shutil.rmtree(scaffold_target)
    result = engine.apply(preset, target_dir=scaffold_target, stack=stack)
    sub(f"applied → {scaffold_target} ({len(result.files_written)} files)")

    sub("Sub-agent ACL (would route TIP-02..TIP-04 to `builder` role):")
    builder_profile = PROFILES.get("builder", {})
    sub(f"  builder.can_mutate={builder_profile.get('can_mutate')}")
    has_shell = "run_command" in builder_profile.get("tools", [])
    sub(f"  builder.run_command_tool={has_shell}")
    sub(f"  builder.permission_mode={builder_profile.get('permission_mode')!r}")


def step_7_verify(target: Path) -> None:
    """Run conformance audit + permission check; demo RRI-T JSONL shape."""
    banner(7, "VERIFY — audit + permission engine + RRI-T sample")

    sub("Sample permission classifications (6-layer pipeline):")
    for cmd in ("git status", "pytest -q", "rm -rf /", "sudo apt install"):
        cls, _ = classify_cmd(cmd)
        verdict = decide_typed(cmd, mode="default", root=str(target))
        sub(f"  {cmd:<28s} class={cls:<14s} decision={verdict.decision}")

    rri_t_path = target / "runtime" / "rri-t-touchfiles.json"
    rri_t_path.parent.mkdir(parents=True, exist_ok=True)
    rri_t_entries = [
        {
            "test_id": "REQ-01-happy",
            "dimension": "correctness",
            "stress_axis": "happy_path",
            "result": "PASS",
            "severity": "P2",
        },
        {
            "test_id": "REQ-02-monthly",
            "dimension": "correctness",
            "stress_axis": "happy_path",
            "result": "PASS",
            "severity": "P2",
        },
    ]
    with rri_t_path.open("w") as fh:
        for entry in rri_t_entries:
            fh.write(json.dumps(entry) + "\n")
    sub(f"wrote sample RRI-T JSONL ({len(rri_t_entries)} entries) → {rri_t_path}")
    sub("  (run `vibe rri-t <path>` to validate against the 7-dim × 8-axis matrix)")


def step_8_ship(target: Path) -> None:
    """Demonstrate intent router + ship dry-run."""
    banner(8, "SHIP — intent router classify + ship dry-run signal")

    router = IntentRouter()
    for phrase in (
        "deploy lên vercel preview",
        "ship the family expense API to production",
        "tôi muốn build trang điều khiển OSINT",
    ):
        match = router.classify(phrase)
        if hasattr(match, "intents"):
            intents = ",".join(match.intents) or "(none)"
            sub(
                f"  {phrase!r:<55s} "
                f"intents={intents:<24s} lang={match.lang}"
            )
        else:
            sub(f"  {phrase!r:<55s} → clarification needed (low confidence)")

    sub("Ship orchestrator: would invoke `vibe ship --target vercel --dry-run`")
    sub("  (real deploy gated behind --prod + valid credentials)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--target",
        type=Path,
        default=Path(tempfile.gettempdir()) / "devin-pipeline-demo",
        help="directory where demo artefacts are written (default: temp dir)",
    )
    parser.add_argument(
        "--preset",
        default="api-todo",
        help="scaffold preset for STEP 6 (default: api-todo)",
    )
    parser.add_argument(
        "--stack",
        default="fastapi",
        help="scaffold stack for STEP 6 (default: fastapi)",
    )
    parser.add_argument(
        "--keep",
        action="store_true",
        help="keep target directory after demo (default: keep; --no-keep to wipe)",
    )
    args = parser.parse_args()

    target = args.target.resolve()
    print(f"Devin pipeline demo — target={target}")
    print(f"  REPO_ROOT={REPO_ROOT}")

    step_1_scan(target)
    step_2_rri(target)
    step_3_vision(target)
    step_4_blueprint(target)
    step_5_task_graph(target)
    step_6_build(target, preset=args.preset, stack=args.stack)
    step_7_verify(target)
    step_8_ship(target)

    print("\n" + "═" * 68)
    print("  Pipeline demo complete. Artefacts:")
    print("═" * 68)
    for path in sorted(target.rglob("*")):
        if path.is_file():
            try:
                rel = path.relative_to(target)
            except ValueError:
                continue
            print(f"  {rel}")

    print(f"\n  total files: {sum(1 for _ in target.rglob('*') if _.is_file())}")
    print(f"  target dir : {target}")
    print("\n  Next steps Devin can take from here:")
    print("    • Edit `scaffold/` to match the family-expense blueprint")
    print("    • Run `pytest scaffold/tests/` to validate REQ-* coverage")
    print("    • Open a PR with the resulting tree")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
