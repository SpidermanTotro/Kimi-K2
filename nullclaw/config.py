"""
NullClaw Configuration
======================
Loads settings from (in priority order):
  1. Environment variables  (NULLCLAW_MODEL, OLLAMA_HOST, …)
  2. ~/projects/null-claw/config.json
  3. ./nullclaw_config.json
  4. Built-in defaults
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


# ---------------------------------------------------------------------------
# Default model candidates (tried in order until one is available)
# ---------------------------------------------------------------------------
_DEFAULT_MODELS = [
    "qwen2.5-coder:latest",
    "qwen2.5-coder:7b",
    "codellama:latest",
    "llama3:8b-instruct-q8_0",
    "llama3:latest",
    "dolphin-mistral:latest",
]

_DEFAULT_PLANNER_MODELS = [
    "llama3:8b-instruct-q8_0",
    "llama3:latest",
    "qwen2.5-coder:latest",
]


@dataclass
class NullClawConfig:
    # ── Ollama / model settings ───────────────────────────────────────
    ollama_host: str = "http://localhost:11434"
    primary_model: str = "qwen2.5-coder:latest"
    planner_model: str = "llama3:8b-instruct-q8_0"
    fallback_models: List[str] = field(default_factory=lambda: _DEFAULT_MODELS[2:])

    # ── Workspace ────────────────────────────────────────────────────
    workspace_root: str = str(Path.home() / "projects")
    max_file_size_mb: int = 10
    log_dir: str = "logs"
    report_dir: str = "reports"
    patch_dir: str = "patches"

    # ── Build ────────────────────────────────────────────────────────
    default_build_cmd: str = "npm run build"
    build_timeout_sec: int = 300
    context_radius: int = 25   # lines above/below the error line

    # ── Repair loop ──────────────────────────────────────────────────
    max_repair_passes: int = 5
    auto_apply_patch: bool = False   # require human confirmation by default
    auto_git_branch: bool = True

    # ── Autonomy ─────────────────────────────────────────────────────
    autonomy_level: str = "supervised"   # supervised | auto
    allowed_paths: List[str] = field(default_factory=list)

    def ensure_dirs(self) -> None:
        for d in (self.log_dir, self.report_dir, self.patch_dir,
                  self.patch_dir + "/generated", self.patch_dir + "/manual"):
            Path(d).mkdir(parents=True, exist_ok=True)


def load_config(path: Optional[str] = None) -> NullClawConfig:
    """Load config from JSON file + env overrides."""
    cfg = NullClawConfig()

    # Search order for config file
    candidates = []
    if path:
        candidates.append(Path(path))
    candidates += [
        Path.home() / "projects" / "null-claw" / "config.json",
        Path("nullclaw_config.json"),
    ]

    for candidate in candidates:
        if candidate.exists():
            try:
                data = json.loads(candidate.read_text())
                _apply_json(cfg, data)
                break
            except Exception:
                pass

    # Environment overrides
    if os.getenv("OLLAMA_HOST"):
        cfg.ollama_host = os.environ["OLLAMA_HOST"]
    if os.getenv("NULLCLAW_MODEL"):
        cfg.primary_model = os.environ["NULLCLAW_MODEL"]
    if os.getenv("NULLCLAW_PLANNER"):
        cfg.planner_model = os.environ["NULLCLAW_PLANNER"]
    if os.getenv("NULLCLAW_WORKSPACE"):
        cfg.workspace_root = os.environ["NULLCLAW_WORKSPACE"]
    if os.getenv("NULLCLAW_AUTO_APPLY") == "1":
        cfg.auto_apply_patch = True

    return cfg


def _apply_json(cfg: NullClawConfig, data: dict) -> None:
    models = data.get("models", {})
    if models.get("base_url"):
        cfg.ollama_host = models["base_url"]
    if models.get("primary"):
        cfg.primary_model = models["primary"]
    if models.get("planner"):
        cfg.planner_model = models["planner"]

    workspace = data.get("workspace", {})
    if workspace.get("root"):
        cfg.workspace_root = workspace["root"]
    if workspace.get("max_file_size_mb"):
        cfg.max_file_size_mb = workspace["max_file_size_mb"]

    autonomy = data.get("autonomy", {})
    if autonomy.get("level"):
        cfg.autonomy_level = autonomy["level"]
    if autonomy.get("allowed_paths"):
        cfg.allowed_paths = autonomy["allowed_paths"]

    if data.get("max_repair_passes"):
        cfg.max_repair_passes = int(data["max_repair_passes"])
    if data.get("repair", {}).get("max_passes"):
        cfg.max_repair_passes = int(data["repair"]["max_passes"])
    if data.get("auto_apply_patch") is not None:
        cfg.auto_apply_patch = bool(data["auto_apply_patch"])


def detect_available_model(cfg: NullClawConfig) -> Optional[str]:
    """Ask Ollama which models are installed and return the best available one."""
    try:
        import urllib.request
        req = urllib.request.urlopen(
            cfg.ollama_host.rstrip("/") + "/api/tags", timeout=3
        )
        data = json.loads(req.read())
        installed = {m["name"].split(":")[0] for m in data.get("models", [])}
        for candidate in _DEFAULT_MODELS:
            base = candidate.split(":")[0]
            if base in installed or candidate in installed:
                return candidate
    except Exception:
        pass
    return None


def ollama_available(cfg: NullClawConfig) -> bool:
    """Return True if the Ollama server is reachable."""
    try:
        import urllib.request
        urllib.request.urlopen(
            cfg.ollama_host.rstrip("/") + "/api/tags", timeout=3
        )
        return True
    except Exception:
        return False
