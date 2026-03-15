"""
NullClaw Git Tools
==================
Safe git helpers:  branch, commit, diff.

All operations run inside the given *project_dir* so they never accidentally
affect NullClaw's own repo.
"""
from __future__ import annotations

import subprocess
import time
from pathlib import Path
from typing import Optional


def _run(cmd, cwd: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


def create_branch(project_dir: str, prefix: str = "nullclaw-fix") -> str:
    """
    Create a new git branch like ``nullclaw-fix-1712345678`` and check it out.
    Returns the new branch name.
    """
    branch = f"{prefix}-{int(time.time())}"
    result = _run(["git", "checkout", "-b", branch], cwd=project_dir)
    if result.returncode == 0:
        print(f"[null-claw] git branch: {branch}")
    else:
        print(f"[null-claw] git branch failed: {result.stdout.strip()}")
    return branch


def commit_fix(
    project_dir: str,
    message: str = "nullclaw: apply AI-suggested fix",
    *,
    add_all: bool = True,
) -> bool:
    """
    Stage all changes (if *add_all*) and commit with *message*.
    Returns True on success.
    """
    if add_all:
        _run(["git", "add", "-A"], cwd=project_dir)

    result = _run(["git", "commit", "-m", message], cwd=project_dir)
    success = result.returncode == 0
    print("[null-claw] git commit:", "✅" if success else "❌")
    if not success:
        print(result.stdout.strip())
    return success


def git_diff(project_dir: str, *, staged: bool = False) -> str:
    """Return the current diff (working tree or staged)."""
    cmd = ["git", "diff"]
    if staged:
        cmd.append("--cached")
    result = _run(cmd, cwd=project_dir)
    return result.stdout


def is_git_repo(project_dir: str) -> bool:
    """Return True if *project_dir* is inside a git repository."""
    result = _run(
        ["git", "rev-parse", "--is-inside-work-tree"], cwd=project_dir
    )
    return result.returncode == 0 and result.stdout.strip() == "true"


def current_branch(project_dir: str) -> Optional[str]:
    """Return the current branch name, or None."""
    result = _run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=project_dir
    )
    return result.stdout.strip() if result.returncode == 0 else None
