"""
NullClaw Build Runner
=====================
Runs any build command, streams output, saves a timestamped log file.

Supports:
  npm run build
  cargo build
  make
  python -m pytest
  go build ./...
  any shell command
"""
from __future__ import annotations

import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

from nullclaw.config import NullClawConfig, load_config


# ---------------------------------------------------------------------------
# Build result
# ---------------------------------------------------------------------------

class BuildResult:
    def __init__(
        self,
        returncode: int,
        log_path: Path,
        log_text: str,
        command: str,
        project_dir: str,
    ) -> None:
        self.returncode  = returncode
        self.log_path    = log_path
        self.log_text    = log_text
        self.command     = command
        self.project_dir = project_dir

    @property
    def success(self) -> bool:
        return self.returncode == 0

    def __repr__(self) -> str:
        status = "✅ PASSED" if self.success else f"❌ FAILED (exit {self.returncode})"
        return f"BuildResult({status}, log={self.log_path})"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run_build(
    project_dir: str,
    build_cmd: Optional[str] = None,
    cfg: Optional[NullClawConfig] = None,
    *,
    verbose: bool = True,
) -> BuildResult:
    """
    Run *build_cmd* inside *project_dir*.  Write stdout + stderr to a
    timestamped log file and return a :class:`BuildResult`.
    """
    if cfg is None:
        cfg = load_config()

    cmd = build_cmd or cfg.default_build_cmd
    log_dir = Path(cfg.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = log_dir / f"build_{ts}.log"

    if verbose:
        print(f"[null-claw] project : {project_dir}")
        print(f"[null-claw] command : {cmd}")
        print(f"[null-claw] log     : {log_path}")

    try:
        proc = subprocess.run(
            cmd,
            cwd=project_dir,
            shell=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=cfg.build_timeout_sec,
        )
        log_text  = proc.stdout or ""
        exit_code = proc.returncode
    except subprocess.TimeoutExpired:
        log_text  = f"[null-claw] build timed out after {cfg.build_timeout_sec}s\n"
        exit_code = -1
    except Exception as exc:
        log_text  = f"[null-claw] build error: {exc}\n"
        exit_code = -2

    log_path.write_text(log_text, encoding="utf-8", errors="replace")

    if verbose:
        print(f"[null-claw] exit code: {exit_code}")
        if not exit_code == 0:
            # Show tail of log for quick diagnosis
            tail = "\n".join(log_text.splitlines()[-15:])
            print(f"[null-claw] log tail:\n{tail}")

    return BuildResult(
        returncode=exit_code,
        log_path=log_path,
        log_text=log_text,
        command=cmd,
        project_dir=project_dir,
    )


def latest_log(log_dir: str = "logs") -> Optional[Path]:
    """Return the most recent build log file, or None."""
    logs = sorted(Path(log_dir).glob("build_*.log"), reverse=True)
    return logs[0] if logs else None
