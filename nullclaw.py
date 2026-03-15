#!/usr/bin/env python3
"""
🦀 NullClaw — Local AI Programming Agent
==========================================
Uses your local GPU (via Ollama) to debug, diagnose, and patch build errors.
Works offline. No paid subscription required.

Commands
--------
  repair  <project_dir> [model]     Full repair loop: build → detect → AI → patch
  build   <project_dir> [command]   Run a build and save the log
  parse   <log_file>                Parse first error from a build log
  context <file> <line>             Show source context around an error line
  search  <pattern> [project_dir]   Search codebase for pattern (uses ripgrep)
  analyze <project_dir>             Index and summarize a project
  map     <project_dir>             Print a repo tree
  apply   <project_dir> <patch>     Apply a patch file with git apply
  status                            Show NullClaw status dashboard
  config                            Print effective configuration

Hardware requirements
---------------------
  GPU: any CUDA/Metal GPU (RTX 5060 Ti 16 GB works great)
  RAM: 8 GB minimum, 16+ GB recommended
  Disk: whatever the models need (~4 GB per 7B model)

Free model setup
----------------
  ollama pull qwen2.5-coder:7b       # best coding model
  ollama pull llama3:8b-instruct-q8_0 # best planner model
  ollama pull codellama              # strong fallback

Free API key (if Ollama unavailable)
--------------------------------------
  https://aistudio.google.com/apikey
  python3 gemini_code_fixer.py --save-key YOUR_KEY
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Ensure the repo root is on the path when run from anywhere
_ROOT = Path(__file__).parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from nullclaw.build_runner import run_build, latest_log
from nullclaw.config import load_config, NullClawConfig
from nullclaw.context_collector import collect_context
from nullclaw.dashboard import print_dashboard
from nullclaw.error_parser import parse_first_error, load_log_file
from nullclaw.git_tools import create_branch, is_git_repo, git_diff
from nullclaw.patch_tools import apply_patch, extract_patch, save_patch
from nullclaw.project_tools import (
    index_project,
    inventory_project,
    repo_map,
    search_code,
)
from nullclaw.repair_loop import RepairLoop


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

_USAGE = """\
🦀 NullClaw — Local AI Programming Agent

Usage:
  python3 nullclaw.py <command> [args…]

Commands:
  repair  <project_dir> [model]
      Full repair loop: build → detect error → AI analysis → patch suggestion

  build   <project_dir> [command]
      Run a build, save log (default command: npm run build)

  parse   <log_file>
      Parse the first build error from a log file

  context <file> <line> [radius]
      Show source lines around an error location

  search  <pattern> [project_dir]
      Fast code search (uses ripgrep when available)

  analyze <project_dir>
      Index + inventory a project

  map     <project_dir> [depth]
      Print a repo tree

  apply   <project_dir> <patch_file>
      Apply a .patch file with git apply

  status
      Show NullClaw dashboard (Ollama health, logs, patches)

  config
      Print the effective NullClaw configuration

Options (repair command):
  --model <name>          Override the primary AI model
  --planner <name>        Override the planner model  
  --passes <N>            Maximum repair passes (default: 5)
  --auto-apply            Automatically apply patches (default: off)
  --branch                Create a git branch before repairing
  --cmd <build_command>   Override the build command

Examples:
  python3 nullclaw.py repair ~/projects/gemini-cli qwen2.5-coder:latest
  python3 nullclaw.py build  ~/projects/myapp "cargo build"
  python3 nullclaw.py parse  logs/build_20240101_120000.log
  python3 nullclaw.py search AppContainer ~/projects/gemini-cli
  python3 nullclaw.py analyze ~/projects/big-repo
  python3 nullclaw.py status
"""


class NullClawCLI:
    def run(self, argv: list[str] = None) -> int:
        args = argv if argv is not None else sys.argv[1:]

        if not args:
            print(_USAGE)
            return 1

        cmd = args[0].lower()
        rest = args[1:]

        dispatch = {
            "repair":  self._cmd_repair,
            "build":   self._cmd_build,
            "parse":   self._cmd_parse,
            "context": self._cmd_context,
            "search":  self._cmd_search,
            "analyze": self._cmd_analyze,
            "map":     self._cmd_map,
            "apply":   self._cmd_apply,
            "status":  self._cmd_status,
            "config":  self._cmd_config,
            # aliases
            "fix":     self._cmd_repair,
            "index":   self._cmd_analyze,
            "tree":    self._cmd_map,
            "debug":   self._cmd_repair,
        }

        fn = dispatch.get(cmd)
        if fn is None:
            print(f"❌ Unknown command: {cmd}\n")
            print(_USAGE)
            return 1

        try:
            return fn(rest)
        except KeyboardInterrupt:
            print("\n[null-claw] interrupted")
            return 130

    # ------------------------------------------------------------------
    # repair
    # ------------------------------------------------------------------

    def _cmd_repair(self, args: list[str]) -> int:
        if not args:
            print("Usage: nullclaw.py repair <project_dir> [model] [options]")
            return 1

        project_dir = args[0]
        rest = args[1:]

        # Parse flags
        model       = None
        planner     = None
        passes      = None
        auto_apply  = False
        do_branch   = False
        build_cmd   = None

        i = 0
        positional = []
        while i < len(rest):
            a = rest[i]
            if a == "--model" and i + 1 < len(rest):
                model = rest[i + 1]; i += 2
            elif a == "--planner" and i + 1 < len(rest):
                planner = rest[i + 1]; i += 2
            elif a == "--passes" and i + 1 < len(rest):
                passes = int(rest[i + 1]); i += 2
            elif a == "--auto-apply":
                auto_apply = True; i += 1
            elif a == "--branch":
                do_branch = True; i += 1
            elif a == "--cmd" and i + 1 < len(rest):
                build_cmd = rest[i + 1]; i += 2
            else:
                positional.append(a); i += 1

        # First positional after project_dir = model name
        if positional and model is None:
            model = positional[0]

        cfg = load_config()
        if model:
            cfg.primary_model = model
        if planner:
            cfg.planner_model = planner
        if passes:
            cfg.max_repair_passes = passes
        if auto_apply:
            cfg.auto_apply_patch = True

        # Optional git branch
        if do_branch and is_git_repo(project_dir):
            create_branch(project_dir)

        loop = RepairLoop(
            project_dir=project_dir,
            build_cmd=build_cmd,
            cfg=cfg,
        )
        loop.run(verbose=True)

        # Print summary
        print("\n📋 Summary:")
        for rp in loop.passes:
            print(f"  {rp.summary()}")

        last = loop.passes[-1] if loop.passes else None
        return 0 if (last and last.build_passed) else 1

    # ------------------------------------------------------------------
    # build
    # ------------------------------------------------------------------

    def _cmd_build(self, args: list[str]) -> int:
        if not args:
            print("Usage: nullclaw.py build <project_dir> [command]")
            return 1
        project_dir = args[0]
        cmd = " ".join(args[1:]) if len(args) > 1 else None
        result = run_build(project_dir, cmd, verbose=True)
        return result.returncode

    # ------------------------------------------------------------------
    # parse
    # ------------------------------------------------------------------

    def _cmd_parse(self, args: list[str]) -> int:
        if not args:
            # Try latest log
            p = latest_log()
            if p is None:
                print("Usage: nullclaw.py parse <log_file>")
                return 1
            log_path = str(p)
        else:
            log_path = args[0]

        if not Path(log_path).exists():
            print(f"Log file not found: {log_path}")
            return 1

        log = load_log_file(log_path)
        err = parse_first_error(log)

        if err is None:
            print("No parseable build error found in log.")
            return 1

        print(json.dumps(err.to_dict(), indent=2))
        return 0

    # ------------------------------------------------------------------
    # context
    # ------------------------------------------------------------------

    def _cmd_context(self, args: list[str]) -> int:
        if len(args) < 2:
            print("Usage: nullclaw.py context <file> <line> [radius]")
            return 1
        file_path = args[0]
        line_no   = int(args[1])
        radius    = int(args[2]) if len(args) > 2 else 25
        print(collect_context(file_path, line_no, radius))
        return 0

    # ------------------------------------------------------------------
    # search
    # ------------------------------------------------------------------

    def _cmd_search(self, args: list[str]) -> int:
        if not args:
            print("Usage: nullclaw.py search <pattern> [project_dir]")
            return 1
        pattern = args[0]
        root    = args[1] if len(args) > 1 else "."
        results = search_code(pattern, root)
        if not results:
            print(f"No matches for '{pattern}' in {root}")
            return 1
        for line in results:
            print(line)
        print(f"\n({len(results)} result{'s' if len(results) != 1 else ''})")
        return 0

    # ------------------------------------------------------------------
    # analyze
    # ------------------------------------------------------------------

    def _cmd_analyze(self, args: list[str]) -> int:
        if not args:
            print("Usage: nullclaw.py analyze <project_dir>")
            return 1
        root = args[0]
        inv  = inventory_project(root)
        print(f"\n📦 Project: {inv['root']}")
        print(f"   Files  : {inv['total_files']}")
        print(f"   Size   : {inv['total_size_mb']} MB")
        print(f"\n   Source files by type:")
        for ext, count in sorted(
            inv["source_by_ext"].items(), key=lambda x: -x[1]
        ):
            print(f"     {ext:<12}  {count}")

        # Also run full indexer
        index_project(root, "project_map.json", verbose=True)
        return 0

    # ------------------------------------------------------------------
    # map
    # ------------------------------------------------------------------

    def _cmd_map(self, args: list[str]) -> int:
        root  = args[0] if args else "."
        depth = int(args[1]) if len(args) > 1 else 4
        print(repo_map(root, max_depth=depth))
        return 0

    # ------------------------------------------------------------------
    # apply
    # ------------------------------------------------------------------

    def _cmd_apply(self, args: list[str]) -> int:
        if len(args) < 2:
            print("Usage: nullclaw.py apply <project_dir> <patch_file>")
            return 1
        project_dir = args[0]
        patch_file  = args[1]
        result = apply_patch(project_dir, patch_file, verbose=True)
        return 0 if result.success else 1

    # ------------------------------------------------------------------
    # status
    # ------------------------------------------------------------------

    def _cmd_status(self, args: list[str]) -> int:
        print_dashboard()
        return 0

    # ------------------------------------------------------------------
    # config
    # ------------------------------------------------------------------

    def _cmd_config(self, args: list[str]) -> int:
        cfg = load_config()
        data = {
            "ollama_host":       cfg.ollama_host,
            "primary_model":     cfg.primary_model,
            "planner_model":     cfg.planner_model,
            "workspace_root":    cfg.workspace_root,
            "default_build_cmd": cfg.default_build_cmd,
            "max_repair_passes": cfg.max_repair_passes,
            "auto_apply_patch":  cfg.auto_apply_patch,
            "context_radius":    cfg.context_radius,
            "autonomy_level":    cfg.autonomy_level,
        }
        print(json.dumps(data, indent=2))
        return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    sys.exit(NullClawCLI().run())


if __name__ == "__main__":
    main()
