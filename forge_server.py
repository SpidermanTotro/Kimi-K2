#!/usr/bin/env python3
"""
THE FORGE AI — Production REST API Server
==========================================
All endpoints route to real implementations:

  POST /api/chat               → KimiForgeUnified.process()
  POST /api/nullclaw/repair    → NullClaw RepairLoop
  POST /api/gemini-fix         → GeminiProgramFixer
  POST /api/ai-reconstruct     → AIReconstructor pipeline
  POST /api/code-review        → KimiForgeUnified + code tool
  GET  /api/capabilities       → full tool registry
  GET  /api/tools/<name>       → single tool info
  GET  /api/stats              → system statistics
  GET  /api/system-prompt      → Forge system prompt
  GET  /health                 → health check

Start:
    pip install flask flask-cors
    python3 forge_server.py
    # → http://localhost:5000
"""
from __future__ import annotations

import json
import logging
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from flask import Flask, jsonify, request
from flask_cors import CORS

# ── Internal imports ────────────────────────────────────────────────────────
_ROOT = Path(__file__).parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from forge_implementation import ForgeAI
from kimi_forge_unified import KimiForgeUnified

# ── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s  %(message)s",
)
logger = logging.getLogger("forge-server")

# ── Flask app ────────────────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app)

# ── Lazy singletons (initialised on first request) ───────────────────────────
_forge: Optional[ForgeAI] = None
_unified: Optional[KimiForgeUnified] = None
_conversation_history: Dict[str, List[dict]] = {}
_started_at: str = datetime.utcnow().isoformat()


def _get_forge() -> ForgeAI:
    global _forge
    if _forge is None:
        logger.info("🔥 Initialising ForgeAI …")
        _forge = ForgeAI()
        _forge.initialize()
        logger.info("✅ ForgeAI ready")
    return _forge


def _get_unified() -> KimiForgeUnified:
    global _unified
    if _unified is None:
        logger.info("🔥 Initialising KimiForgeUnified …")
        _unified = KimiForgeUnified()
        logger.info("✅ KimiForgeUnified ready")
    return _unified


# ── Helpers ──────────────────────────────────────────────────────────────────

def _ts() -> str:
    return datetime.utcnow().isoformat()


def _err(msg: str, code: int = 400):
    return jsonify({"error": msg, "timestamp": _ts()}), code


# ═══════════════════════════════════════════════════════════════════════════════
# Health
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/health")
def health():
    return jsonify({
        "status":      "healthy",
        "service":     "THE FORGE AI",
        "version":     "1.1.0",
        "started_at":  _started_at,
        "timestamp":   _ts(),
        "forge_ready": _forge is not None,
        "unified_ready": _unified is not None,
    })


# ═══════════════════════════════════════════════════════════════════════════════
# Chat  — real routing via KimiForgeUnified
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/chat")
def chat():
    """
    Main chat endpoint.

    Body: { "message": "...", "session_id": "optional", "use_tools": true }
    """
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return _err("'message' is required")

    session_id = data.get("session_id", "default")
    use_tools  = bool(data.get("use_tools", True))

    # History
    _conversation_history.setdefault(session_id, [])
    _conversation_history[session_id].append(
        {"role": "user", "content": message, "timestamp": _ts()}
    )

    # Route through KimiForgeUnified (real dispatch + tool selection)
    try:
        unified   = _get_unified()
        response  = unified.process(message, use_tools=use_tools)
    except Exception as exc:
        logger.error("chat error: %s", exc, exc_info=True)
        return _err(str(exc), 500)

    _conversation_history[session_id].append(
        {"role": "assistant", "content": response, "timestamp": _ts()}
    )

    return jsonify({
        "content":    response,
        "session_id": session_id,
        "timestamp":  _ts(),
        "status":     "success",
    })


# ═══════════════════════════════════════════════════════════════════════════════
# NullClaw repair endpoint
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/nullclaw/repair")
def nullclaw_repair():
    """
    Run a NullClaw repair pass on a project directory.

    Body: {
        "project_dir": "/abs/path/to/project",
        "model":       "qwen2.5-coder:latest",   (optional)
        "build_cmd":   "npm run build",           (optional)
        "auto_apply":  false                      (optional)
    }
    """
    data = request.get_json(silent=True) or {}
    project_dir = (data.get("project_dir") or "").strip()
    if not project_dir:
        return _err("'project_dir' is required")
    if not Path(project_dir).is_dir():
        return _err(f"Directory not found: {project_dir}", 404)

    try:
        from nullclaw.config import load_config
        from nullclaw.repair_loop import RepairLoop

        cfg = load_config()
        cfg.primary_model   = data.get("model",     cfg.primary_model)
        cfg.default_build_cmd = data.get("build_cmd", cfg.default_build_cmd)
        cfg.auto_apply_patch  = bool(data.get("auto_apply", False))
        cfg.max_repair_passes = int(data.get("max_passes", 1))

        # Write outputs to a temp dir so the server stays clean
        with tempfile.TemporaryDirectory(prefix="forge-nullclaw-") as td:
            cfg.log_dir    = str(Path(td) / "logs")
            cfg.report_dir = str(Path(td) / "reports")
            cfg.patch_dir  = str(Path(td) / "patches")
            cfg.ensure_dirs()

            loop    = RepairLoop(cfg)
            passes  = loop.run(project_dir)

        results = []
        for p in passes:
            results.append({
                "pass":         p.pass_number,
                "build_passed": p.build_passed,
                "error":        str(p.error) if p.error else None,
                "patch_applied": p.patch_applied,
                "ai_response":  (p.agent_result.final_reply[:2000]
                                 if p.agent_result and p.agent_result.final_reply
                                 else None),
            })

        return jsonify({
            "project_dir": project_dir,
            "passes":      len(results),
            "results":     results,
            "status":      "success",
            "timestamp":   _ts(),
        })

    except Exception as exc:
        logger.error("nullclaw/repair error: %s", exc, exc_info=True)
        return _err(str(exc), 500)


# ═══════════════════════════════════════════════════════════════════════════════
# GeminiProgramFixer endpoint
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/gemini-fix")
def gemini_fix():
    """
    Fix / explain / review code using GeminiProgramFixer (free Gemini 1.5 Flash).

    Body: {
        "code":    "source code string",
        "action":  "fix" | "explain" | "review",   (default: "fix")
        "language": "python"                        (optional, auto-detected)
    }
    """
    data   = request.get_json(silent=True) or {}
    code   = (data.get("code") or "").strip()
    action = (data.get("action") or "fix").strip().lower()
    if not code:
        return _err("'code' is required")
    if action not in ("fix", "explain", "review"):
        return _err("'action' must be one of: fix, explain, review")

    try:
        from gemini_code_fixer import GeminiProgramFixer
        fixer = GeminiProgramFixer()

        if action == "fix":
            result = fixer.fix_code(code)
        elif action == "explain":
            result = fixer.explain_code(code)
        else:
            result = fixer.review_code(code)

        return jsonify({
            "action":    action,
            "result":    result,
            "status":    "success",
            "timestamp": _ts(),
        })

    except Exception as exc:
        logger.error("gemini-fix error: %s", exc, exc_info=True)
        return _err(str(exc), 500)


# ═══════════════════════════════════════════════════════════════════════════════
# AI Reconstructor endpoint
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/ai-reconstruct")
def ai_reconstruct():
    """
    Run the ELF X-Ray / scroll-technique reconstructor on an uploaded or
    path-referenced binary.

    Body: {
        "binary_path": "/abs/path/to/elf",
        "scan_depth":  3,          (1-6, default 3)
        "mode":        "full"      ("xray"|"unwrap"|"reconstruct"|"understand"|"full")
    }
    """
    data        = request.get_json(silent=True) or {}
    binary_path = (data.get("binary_path") or "").strip()
    if not binary_path:
        return _err("'binary_path' is required")
    if not Path(binary_path).exists():
        return _err(f"File not found: {binary_path}", 404)

    scan_depth = int(data.get("scan_depth", 3))
    mode       = (data.get("mode") or "full").strip().lower()

    try:
        from ai_reconstructor import (
            BinaryXRay,
            DeepElfParser,
            ElfUnderstanding,
            VirtualUnwrapper,
            AIPatternMatcher,
            ScrollAssembler,
        )

        out: dict = {"binary": binary_path, "mode": mode, "timestamp": _ts()}

        if mode in ("xray", "full"):
            xray   = BinaryXRay(binary_path)
            result = xray.scan(depth=scan_depth)
            out["xray"] = result

        if mode in ("unwrap", "full"):
            unwrap = VirtualUnwrapper(binary_path)
            out["unwrap"] = unwrap.unwrap()

        if mode in ("reconstruct", "full"):
            matcher    = AIPatternMatcher(binary_path)
            assembler  = ScrollAssembler(binary_path)
            patterns   = matcher.match()
            out["patterns"]      = patterns
            out["reconstruction"] = assembler.assemble(patterns)

        if mode in ("understand", "full"):
            parser  = DeepElfParser(binary_path)
            elf_map = parser.parse()
            udr     = ElfUnderstanding(binary_path)
            out["deep_parse"]    = elf_map
            out["understanding"] = udr.understand(elf_map)

        out["status"] = "success"
        return jsonify(out)

    except Exception as exc:
        logger.error("ai-reconstruct error: %s", exc, exc_info=True)
        return _err(str(exc), 500)


# ═══════════════════════════════════════════════════════════════════════════════
# Capabilities & tool registry
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/capabilities")
def get_capabilities():
    """Return the full tool registry with descriptions and capability lists."""
    unified = _get_unified()
    tools   = unified.forge_tools.tools
    return jsonify({
        "total_tools":    len(tools),
        "total_capabilities": sum(len(t.get("capabilities", [])) for t in tools.values()),
        "tools":          tools,
        "timestamp":      _ts(),
    })


@app.get("/api/tools/<tool_name>")
def get_tool(tool_name: str):
    """Return info for a single tool."""
    unified = _get_unified()
    tool    = unified.forge_tools.get_tool(tool_name)
    if not tool:
        return _err(f"Tool not found: {tool_name}", 404)
    return jsonify({"name": tool_name, **tool, "timestamp": _ts()})


# ═══════════════════════════════════════════════════════════════════════════════
# System prompt
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/system-prompt")
def get_system_prompt():
    """Return the Forge system prompt (built from all docs/)."""
    forge  = _get_forge()
    prompt = forge.get_system_prompt()
    return jsonify({"system_prompt": prompt, "length": len(prompt), "timestamp": _ts()})


# ═══════════════════════════════════════════════════════════════════════════════
# Stats
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/stats")
def get_stats():
    total_msgs = sum(len(v) for v in _conversation_history.values())
    forge      = _get_forge()
    unified    = _get_unified()
    return jsonify({
        "system": {
            "status":     "running",
            "version":    "1.1.0",
            "started_at": _started_at,
        },
        "documentation": {
            "files_loaded": len(forge.loader.documents),
            "total_chars":  len(forge.loader.all_content),
        },
        "tools": {
            "total_tools":        len(unified.forge_tools.tools),
            "total_capabilities": unified.get_stats()["total_capabilities"],
        },
        "sessions": {
            "active":        len(_conversation_history),
            "total_messages": total_msgs,
        },
        "timestamp": _ts(),
    })


# ═══════════════════════════════════════════════════════════════════════════════
# Session management
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/sessions/<session_id>/history")
def session_history(session_id: str):
    msgs = _conversation_history.get(session_id)
    if msgs is None:
        return _err(f"Session not found: {session_id}", 404)
    return jsonify({"session_id": session_id, "messages": msgs, "count": len(msgs)})


@app.delete("/api/sessions/<session_id>")
def clear_session(session_id: str):
    _conversation_history.pop(session_id, None)
    return jsonify({"status": "success", "session_id": session_id})


# ═══════════════════════════════════════════════════════════════════════════════
# Entry point
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    port  = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FORGE_DEBUG", "0") == "1"

    logger.info("🔥 THE FORGE AI server starting …")
    logger.info("   http://localhost:%d", port)
    logger.info("   health:  GET  /health")
    logger.info("   chat:    POST /api/chat")
    logger.info("   repair:  POST /api/nullclaw/repair")
    logger.info("   fix:     POST /api/gemini-fix")
    logger.info("   xray:    POST /api/ai-reconstruct")
    logger.info("   tools:   GET  /api/capabilities")
    logger.info("   stats:   GET  /api/stats")

    app.run(host="0.0.0.0", port=port, debug=debug, threaded=True)
