"""
NullClaw Repair Loop
====================
The main automated cycle:

  for pass in 1 … max_passes:
    1. run_build()
    2. parse_first_error()
    3. collect_context()
    4. agents.run() → reply
    5. extract_patch()
    6. (optional) apply_patch()
    7. save reports
    8. if build passed → done

Each pass produces a full report in reports/ so you can review the AI output.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from nullclaw.agents import AgentResult, NullClawAgents
from nullclaw.build_runner import BuildResult, run_build
from nullclaw.config import NullClawConfig, load_config
from nullclaw.context_collector import collect_context
from nullclaw.error_parser import BuildError, parse_first_error, load_log_file
from nullclaw.patch_tools import (
    PatchResult,
    apply_patch,
    backup_file,
    extract_patch,
    save_patch,
    save_patch_note,
)


# ---------------------------------------------------------------------------
# Pass result
# ---------------------------------------------------------------------------

@dataclass
class RepairPass:
    pass_number:  int
    build:        Optional[BuildResult] = None
    error:        Optional[BuildError]  = None
    agent_result: Optional[AgentResult] = None
    patch_text:   Optional[str]        = None
    patch_result: Optional[PatchResult] = None
    report_dir:   str = "reports"

    @property
    def build_passed(self) -> bool:
        return self.build is not None and self.build.success

    @property
    def patch_applied(self) -> bool:
        return self.patch_result is not None and self.patch_result.success

    def summary(self) -> str:
        parts = [f"Pass {self.pass_number}"]
        if self.build_passed:
            parts.append("✅ build passed")
        elif self.error:
            parts.append(f"❌ {self.error}")
        else:
            parts.append("❌ build failed (no error parsed)")
        if self.patch_applied:
            parts.append("🩹 patch applied")
        return "  ".join(parts)


# ---------------------------------------------------------------------------
# Full loop
# ---------------------------------------------------------------------------

@dataclass
class RepairLoop:
    project_dir: str
    build_cmd:   Optional[str] = None
    cfg:         Optional[NullClawConfig] = None
    passes:      List[RepairPass] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        if self.cfg is None:
            self.cfg = load_config()
        self.cfg.ensure_dirs()
        self._agents = NullClawAgents(self.cfg)

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------

    def run(
        self,
        *,
        max_passes: Optional[int] = None,
        auto_apply: Optional[bool] = None,
        verbose: bool = True,
    ) -> List[RepairPass]:
        """
        Run up to *max_passes* repair cycles.

        Returns the list of :class:`RepairPass` objects (one per cycle).
        """
        n     = max_passes  if max_passes  is not None else self.cfg.max_repair_passes
        apply = auto_apply  if auto_apply  is not None else self.cfg.auto_apply_patch

        print(f"\n{'═'*60}")
        print(f"🦀  NullClaw — Repair Loop")
        print(f"    project : {self.project_dir}")
        print(f"    command : {self.build_cmd or self.cfg.default_build_cmd}")
        print(f"    passes  : {n}")
        print(f"    model   : {self.cfg.primary_model}")
        print(f"{'═'*60}\n")

        for i in range(1, n + 1):
            rp = self._one_pass(i, auto_apply=apply, verbose=verbose)
            self.passes.append(rp)

            print(f"\n  {rp.summary()}")

            if rp.build_passed:
                print("\n🎉  Build passed — repair complete!\n")
                break

            if rp.patch_text and not apply:
                print(
                    "\n  💡  Patch available but auto-apply is OFF.\n"
                    f"      Review: {self.cfg.patch_dir}/generated/\n"
                    "      Apply:  python3 nullclaw.py apply <project> <patch>"
                )
                break   # stop loop; user must review

        return self.passes

    # ------------------------------------------------------------------
    # Single pass
    # ------------------------------------------------------------------

    def _one_pass(
        self, pass_num: int, *, auto_apply: bool, verbose: bool
    ) -> RepairPass:
        rp = RepairPass(pass_number=pass_num)

        print(f"\n{'─'*50}")
        print(f"  Pass {pass_num}/{self.cfg.max_repair_passes}")
        print(f"{'─'*50}")

        # 1. Build
        rp.build = run_build(
            self.project_dir,
            self.build_cmd,
            self.cfg,
            verbose=verbose,
        )

        if rp.build.success:
            return rp

        # 2. Parse first error
        rp.error = parse_first_error(rp.build.log_text)

        if rp.error is None:
            print("[null-claw] no parseable error found — check the log:")
            print(f"  {rp.build.log_path}")
            self._save_report(pass_num, rp)
            return rp

        print(f"[null-claw] first error: {rp.error}")

        # 3. Collect context
        ctx = collect_context(
            rp.error.file_path,
            rp.error.line,
            self.cfg.context_radius,
        )

        # 4. Ask AI
        rp.agent_result = self._agents.run(rp.error, ctx, verbose=verbose)

        reply = rp.agent_result.best_reply()
        if not reply:
            print("[null-claw] AI returned no reply — all backends unavailable")
            self._save_report(pass_num, rp)
            return rp

        # 5. Extract patch
        rp.patch_text = extract_patch(reply)

        # 6. Save reports
        self._save_report(pass_num, rp)

        # 7. Apply patch (if requested)
        if rp.patch_text and auto_apply:
            backup_file(rp.error.file_path)
            patch_path = save_patch(
                rp.patch_text, self.cfg.patch_dir + "/generated",
                name_hint=f"pass{pass_num}",
            )
            dry = apply_patch(self.project_dir, str(patch_path), dry_run=True)
            if dry.success:
                rp.patch_result = apply_patch(
                    self.project_dir, str(patch_path), verbose=verbose
                )
            else:
                print("[null-claw] patch dry-run failed — not applied")
                rp.patch_result = dry

        elif rp.patch_text:
            # Save patch for manual review even if not auto-applying
            save_patch(
                rp.patch_text, self.cfg.patch_dir + "/generated",
                name_hint=f"pass{pass_num}",
            )

        return rp

    # ------------------------------------------------------------------
    # Report writer
    # ------------------------------------------------------------------

    def _save_report(self, pass_num: int, rp: RepairPass) -> None:
        report_dir = Path(self.cfg.report_dir)
        report_dir.mkdir(parents=True, exist_ok=True)

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")

        if rp.error:
            (report_dir / "first_error.json").write_text(
                json.dumps(rp.error.to_dict(), indent=2), encoding="utf-8"
            )

        reply = rp.agent_result.best_reply() if rp.agent_result else ""
        if reply:
            (report_dir / "ollama_reply.txt").write_text(reply, encoding="utf-8")
            save_patch_note(reply, self.cfg.patch_dir + "/generated")

        if rp.patch_text:
            (report_dir / "suggested.patch").write_text(
                rp.patch_text, encoding="utf-8"
            )

        # Summary JSON
        summary = {
            "pass":          pass_num,
            "timestamp":     ts,
            "project":       self.project_dir,
            "build_exit":    rp.build.returncode if rp.build else None,
            "error":         rp.error.to_dict() if rp.error else None,
            "patch_applied": rp.patch_applied,
        }
        (report_dir / f"pass_{pass_num:02d}_{ts}.json").write_text(
            json.dumps(summary, indent=2), encoding="utf-8"
        )
