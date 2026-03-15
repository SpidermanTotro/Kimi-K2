"""
NullClaw Dashboard
==================
A CLI status summary: shows recent logs, patches, reports, and model status.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from nullclaw.config import NullClawConfig, load_config, ollama_available


def print_dashboard(cfg: Optional[NullClawConfig] = None) -> None:
    cfg = cfg or load_config()

    print(f"\n{'═'*60}")
    print("🦀  NullClaw — Status Dashboard")
    print(f"{'═'*60}")

    # ── Ollama health ──────────────────────────────────────────────
    ok = ollama_available(cfg)
    status = "✅ reachable" if ok else "❌ not running (start with: ollama serve)"
    print(f"\n  Ollama      : {cfg.ollama_host}  {status}")
    print(f"  Primary     : {cfg.primary_model}")
    print(f"  Planner     : {cfg.planner_model}")

    # ── Workspace ─────────────────────────────────────────────────
    print(f"\n  Workspace   : {cfg.workspace_root}")
    print(f"  Log dir     : {cfg.log_dir}")
    print(f"  Report dir  : {cfg.report_dir}")
    print(f"  Patch dir   : {cfg.patch_dir}")

    # ── Recent logs ───────────────────────────────────────────────
    logs = sorted(Path(cfg.log_dir).glob("build_*.log"), reverse=True)[:5] if Path(cfg.log_dir).exists() else []
    print(f"\n  Build logs  : {len(list(Path(cfg.log_dir).glob('build_*.log'))) if Path(cfg.log_dir).exists() else 0} total")
    for p in logs:
        size = p.stat().st_size
        print(f"    {p.name}  ({size:,} bytes)")

    # ── Latest error ──────────────────────────────────────────────
    err_path = Path(cfg.report_dir) / "first_error.json"
    if err_path.exists():
        try:
            err = json.loads(err_path.read_text())
            print(f"\n  Last error  : [{err.get('code','?')}] {err.get('message','?')}")
            print(f"    file: {err.get('file_path','?')}:{err.get('line','?')}")
        except Exception:
            pass

    # ── Patches ───────────────────────────────────────────────────
    gen_dir = Path(cfg.patch_dir) / "generated"
    if gen_dir.exists():
        patches = sorted(gen_dir.glob("*.patch"), reverse=True)[:3]
        notes   = sorted(gen_dir.glob("*.md"),    reverse=True)[:3]
        print(f"\n  Patches     : {len(list(gen_dir.glob('*.patch')))}")
        for p in patches:
            print(f"    {p.name}")
        print(f"  AI notes    : {len(list(gen_dir.glob('*.md')))}")
        for n in notes:
            print(f"    {n.name}")

    # ── Reply preview ─────────────────────────────────────────────
    reply_path = Path(cfg.report_dir) / "ollama_reply.txt"
    if reply_path.exists():
        preview = "\n".join(reply_path.read_text()[:1000].splitlines()[:15])
        print(f"\n  Latest AI reply preview:")
        for line in preview.splitlines():
            print(f"    {line}")

    print(f"\n{'═'*60}\n")
