"""
NullClaw Project Tools
======================
Index, search, and inventory a codebase.

Uses fast external tools when available (ripgrep, fd) and falls back to
a pure-Python walker that works everywhere.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# File types
# ---------------------------------------------------------------------------

_SOURCE_EXTS = {
    ".ts", ".tsx", ".js", ".jsx", ".mts", ".cts",
    ".py", ".rs", ".go", ".c", ".cpp", ".cc", ".cxx",
    ".h", ".hpp", ".java", ".kt", ".swift", ".rb",
    ".sh", ".bash", ".zsh", ".fish",
    ".yaml", ".yml", ".toml", ".json", ".md",
    ".html", ".css", ".scss", ".vue", ".svelte",
}

_SKIP_DIRS = {
    "node_modules", ".git", "dist", "build", ".next",
    "target", "__pycache__", ".cargo", ".rustup",
    "vendor", ".venv", "venv", "env", ".tox",
}


# ---------------------------------------------------------------------------
# File indexer
# ---------------------------------------------------------------------------

def index_project(
    root: str,
    out_file: Optional[str] = None,
    *,
    max_files: int = 10_000,
    verbose: bool = True,
) -> Dict:
    """
    Walk *root* and build a project index dict.
    Saves JSON to *out_file* if given.  Returns the dict.
    """
    root_path = Path(root).resolve()
    files: List[str] = []

    if shutil.which("fd"):
        try:
            result = subprocess.run(
                ["fd", "--type", "f", "--hidden", ".",  str(root_path)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            files = [l for l in result.stdout.splitlines() if l][:max_files]
        except Exception:
            pass

    if not files:
        files = _walk_files(str(root_path), max_files=max_files)

    ext_counts: Counter = Counter(Path(f).suffix.lower() for f in files)
    source_files = [f for f in files if Path(f).suffix.lower() in _SOURCE_EXTS]

    index = {
        "root":         str(root_path),
        "file_count":   len(files),
        "source_count": len(source_files),
        "ext_counts":   dict(ext_counts.most_common(20)),
        "files":        files,
    }

    if out_file:
        Path(out_file).write_text(json.dumps(index, indent=2), encoding="utf-8")
        if verbose:
            print(f"[null-claw] indexed {len(files)} files → {out_file}")

    if verbose:
        print(f"[null-claw] project: {root_path}")
        print(f"[null-claw] {len(files)} total files, {len(source_files)} source files")

    return index


def _walk_files(root: str, max_files: int) -> List[str]:
    files: List[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
        for name in filenames:
            files.append(os.path.join(dirpath, name))
            if len(files) >= max_files:
                return files
    return files


# ---------------------------------------------------------------------------
# Code search
# ---------------------------------------------------------------------------

def search_code(
    pattern: str,
    root: str = ".",
    *,
    max_results: int = 50,
    case_insensitive: bool = False,
) -> List[str]:
    """
    Search *root* for *pattern*.  Uses ripgrep when available, falls back
    to pure-Python grep.  Returns list of matching ``file:line:content`` strings.
    """
    if shutil.which("rg"):
        cmd = ["rg", "--line-number", "--no-heading", "--color=never"]
        if case_insensitive:
            cmd.append("-i")
        cmd += [pattern, root]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )
            lines = [l for l in result.stdout.splitlines() if l]
            return lines[:max_results]
        except Exception:
            pass

    return _python_grep(pattern, root, max_results, case_insensitive)


def _python_grep(
    pattern: str, root: str, limit: int, case_insensitive: bool
) -> List[str]:
    import re
    flags = re.IGNORECASE if case_insensitive else 0
    compiled = re.compile(re.escape(pattern), flags)
    results: List[str] = []

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
        for name in filenames:
            path = os.path.join(dirpath, name)
            if Path(path).suffix.lower() not in _SOURCE_EXTS:
                continue
            try:
                for i, line in enumerate(
                    Path(path).read_text(
                        encoding="utf-8", errors="replace"
                    ).splitlines(),
                    1,
                ):
                    if compiled.search(line):
                        results.append(f"{path}:{i}:{line.rstrip()}")
                        if len(results) >= limit:
                            return results
            except OSError:
                pass
    return results


# ---------------------------------------------------------------------------
# Inventory
# ---------------------------------------------------------------------------

def inventory_project(root: str) -> Dict:
    """
    Return a quick stat dict: file type counts, total size, tree depth.
    """
    root_path = Path(root)
    counts: Counter = Counter()
    total_size = 0
    total_files = 0

    for dirpath, dirnames, filenames in os.walk(str(root_path)):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
        for name in filenames:
            total_files += 1
            ext = Path(name).suffix.lower()
            if ext in _SOURCE_EXTS:
                counts[ext] += 1
            try:
                total_size += os.path.getsize(os.path.join(dirpath, name))
            except OSError:
                pass

    return {
        "root":        str(root_path),
        "total_files": total_files,
        "total_size_mb": round(total_size / 1_048_576, 2),
        "source_by_ext": dict(counts.most_common()),
    }


# ---------------------------------------------------------------------------
# Repo map (tree view)
# ---------------------------------------------------------------------------

def repo_map(root: str, max_depth: int = 4, max_files_per_dir: int = 8) -> str:
    """Return a readable tree view of *root*."""
    lines: List[str] = [str(Path(root).resolve())]
    _tree_walk(Path(root), lines, depth=0, max_depth=max_depth,
               max_files=max_files_per_dir)
    return "\n".join(lines)


def _tree_walk(
    path: Path, lines: List[str], depth: int, max_depth: int, max_files: int
) -> None:
    if depth >= max_depth:
        return
    indent = "  " * (depth + 1)
    try:
        entries = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name))
    except PermissionError:
        return
    dirs   = [e for e in entries if e.is_dir()  and e.name not in _SKIP_DIRS]
    files  = [e for e in entries if e.is_file()][:max_files]
    for d in dirs:
        lines.append(f"{indent}📁 {d.name}/")
        _tree_walk(d, lines, depth + 1, max_depth, max_files)
    for f in files:
        lines.append(f"{indent}  {f.name}")
    if len([e for e in entries if e.is_file()]) > max_files:
        extra = len([e for e in entries if e.is_file()]) - max_files
        lines.append(f"{indent}  … (+{extra} more)")
