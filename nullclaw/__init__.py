"""
NullClaw — Local AI Programming Agent
======================================
A self-repairing build tool that uses your local GPU (Ollama) to detect,
diagnose, and patch build errors across TypeScript, Python, Rust, Go, and C/C++.

Architecture
============
NullClaw CLI
  └── Skill Engine (this package)
        ├── build_runner     — run any build, capture log
        ├── error_parser     — parse TS / Python / Rust / Go / C errors
        ├── context_collector — extract source around the error
        ├── ollama_client    — query local models (Ollama REST → subprocess → Gemini fallback)
        ├── patch_tools      — extract diff from AI reply, backup, apply
        ├── project_tools    — index, search, inventory a codebase
        ├── agents           — Planner → Debugger → Patcher three-agent pipeline
        ├── repair_loop      — automated build → detect → fix → rebuild cycle
        ├── git_tools        — branch / commit / diff helpers
        ├── dashboard        — CLI status summary
        └── config           — load config.json + env overrides
"""

from nullclaw.config import NullClawConfig, load_config
from nullclaw.error_parser import BuildError, parse_first_error, parse_all_errors
from nullclaw.build_runner import run_build
from nullclaw.context_collector import collect_context
from nullclaw.ollama_client import OllamaClient
from nullclaw.repair_loop import RepairLoop

__all__ = [
    "NullClawConfig",
    "load_config",
    "BuildError",
    "parse_first_error",
    "parse_all_errors",
    "run_build",
    "collect_context",
    "OllamaClient",
    "RepairLoop",
]
