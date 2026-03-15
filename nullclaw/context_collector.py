"""
NullClaw Context Collector
===========================
Grabs the source lines surrounding a build error for inclusion in the AI prompt.
Displays a >> marker at the exact error line and numbers each line.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional


def collect_context(
    file_path: str,
    line_no: int,
    radius: int = 25,
    *,
    max_file_size_mb: int = 10,
) -> str:
    """
    Return a formatted string with *radius* lines above and below *line_no*
    in *file_path*.  Marks the target line with ``>>>``.

    Returns an informative message string (not an exception) if the file
    cannot be read.
    """
    path = Path(file_path)

    if not path.exists():
        return f"[null-claw] context: file not found: {file_path}"

    size_mb = path.stat().st_size / 1_048_576
    if size_mb > max_file_size_mb:
        return (
            f"[null-claw] context: file too large "
            f"({size_mb:.1f} MB > {max_file_size_mb} MB limit): {file_path}"
        )

    try:
        source = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return f"[null-claw] context: cannot read {file_path}: {exc}"

    lines  = source.splitlines()
    total  = len(lines)
    start  = max(1, line_no - radius)
    end    = min(total, line_no + radius)

    out = [
        f"FILE  : {file_path}",
        f"LINES : {start}–{end} of {total}",
        "",
    ]
    for i in range(start, end + 1):
        marker = ">>>" if i == line_no else "   "
        out.append(f"{marker} {i:5d}: {lines[i - 1]}")

    return "\n".join(out)
