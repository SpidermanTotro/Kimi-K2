"""
NullClaw Patch Tools
====================
Extracts unified diffs from AI replies, backs up target files, and applies
patches safely using ``git apply``.

Patch extraction heuristics (in order):
  1. ```diff … ``` fenced block
  2. ```patch … ``` fenced block
  3. Bare --- / +++ / @@ pattern in the reply
"""
from __future__ import annotations

import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------

_FENCED_DIFF_RE = re.compile(
    r"```(?:diff|patch)\s*\n(.*?)```",
    re.DOTALL | re.IGNORECASE,
)

_BARE_DIFF_RE = re.compile(
    r"((?:^---\s.+\n\+\+\+\s.+\n(?:@@.*\n)?(?:[+\- @\\].*\n?)+)+)",
    re.MULTILINE,
)


def extract_patch(reply: str) -> Optional[str]:
    """
    Try to pull a unified diff out of *reply*.

    Returns the patch text (without fences), or ``None`` if none found.
    """
    # Priority 1 — fenced block
    m = _FENCED_DIFF_RE.search(reply)
    if m:
        patch = m.group(1).strip()
        if patch:
            return patch

    # Priority 2 — bare diff heuristic
    m = _BARE_DIFF_RE.search(reply)
    if m:
        patch = m.group(1).strip()
        if patch:
            return patch

    return None


# ---------------------------------------------------------------------------
# Backup
# ---------------------------------------------------------------------------

def backup_file(file_path: str) -> Path:
    """
    Copy *file_path* to *file_path*.bak (overwriting any old backup).
    Returns the backup path.
    """
    src = Path(file_path)
    bak = src.with_suffix(src.suffix + ".bak")
    shutil.copy2(src, bak)
    return bak


# ---------------------------------------------------------------------------
# Apply
# ---------------------------------------------------------------------------

class PatchResult:
    def __init__(self, success: bool, output: str, patch_path: Path) -> None:
        self.success    = success
        self.output     = output
        self.patch_path = patch_path

    def __bool__(self) -> bool:
        return self.success

    def __repr__(self) -> str:
        s = "✅ applied" if self.success else "❌ failed"
        return f"PatchResult({s})"


def save_patch(
    patch_text: str,
    patch_dir: str = "patches/generated",
    *,
    name_hint: str = "",
) -> Path:
    """Write *patch_text* to a timestamped ``.patch`` file.  Returns path."""
    Path(patch_dir).mkdir(parents=True, exist_ok=True)
    ts    = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem  = f"{name_hint}_" if name_hint else ""
    path  = Path(patch_dir) / f"{stem}repair_{ts}.patch"
    path.write_text(patch_text, encoding="utf-8")
    return path


def apply_patch(
    project_dir: str,
    patch_file: str,
    *,
    dry_run: bool = False,
    verbose: bool = True,
) -> PatchResult:
    """
    Apply *patch_file* inside *project_dir* using ``git apply``.

    Set *dry_run=True* to only check (``git apply --check``).
    """
    cmd = ["git", "apply"]
    if dry_run:
        cmd.append("--check")
    cmd.append(str(patch_file))

    proc = subprocess.run(
        cmd,
        cwd=project_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    output  = proc.stdout.strip()
    success = proc.returncode == 0

    if verbose:
        label = "dry-run" if dry_run else "apply"
        status = "✅" if success else "❌"
        print(f"[null-claw] git apply {label}: {status}")
        if output:
            print(output)

    return PatchResult(success=success, output=output, patch_path=Path(patch_file))


def save_patch_note(
    reply: str,
    patch_dir: str = "patches/generated",
) -> Path:
    """Save the full Ollama reply as a markdown note.  Returns path."""
    Path(patch_dir).mkdir(parents=True, exist_ok=True)
    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = Path(patch_dir) / f"repair_note_{ts}.md"
    path.write_text(reply, encoding="utf-8")
    return path
