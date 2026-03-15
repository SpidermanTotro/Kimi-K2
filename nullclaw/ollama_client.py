"""
NullClaw Ollama Client
======================
Queries a local Ollama server.  Falls back gracefully:

  1. Ollama REST API  (http://localhost:11434/api/generate — streaming)
  2. ``ollama run <model>`` subprocess
  3. GeminiProgramFixer (free cloud fallback)
  4. Returns None (caller handles the no-AI case)
"""
from __future__ import annotations

import json
import subprocess
import sys
import urllib.error
import urllib.request
from typing import Optional

from nullclaw.config import NullClawConfig, load_config


class OllamaClient:
    """Ask a local Ollama model for a response to *prompt*."""

    def __init__(self, cfg: Optional[NullClawConfig] = None) -> None:
        self.cfg = cfg or load_config()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def ask(
        self,
        prompt: str,
        model: Optional[str] = None,
        *,
        verbose: bool = True,
    ) -> Optional[str]:
        """
        Send *prompt* to the local model.

        Returns the response text, or ``None`` if all methods fail.
        """
        m = model or self.cfg.primary_model

        if verbose:
            print(f"[null-claw] asking model: {m} …", flush=True)

        # Try 1 — Ollama REST API
        resp = self._ask_rest(prompt, m, verbose=verbose)
        if resp is not None:
            return resp

        # Try 2 — ollama subprocess (CLI)
        resp = self._ask_subprocess(prompt, m, verbose=verbose)
        if resp is not None:
            return resp

        # Try 3 — Gemini fallback (free tier)
        resp = self._ask_gemini_fallback(prompt, verbose=verbose)
        if resp is not None:
            return resp

        if verbose:
            print(
                "[null-claw] ⚠️  No AI backend available.\n"
                "  • Start Ollama:  ollama serve\n"
                "  • Set API key:   python3 gemini_code_fixer.py --save-key YOUR_KEY\n"
                "  • Free key:      https://aistudio.google.com/apikey",
                file=sys.stderr,
            )
        return None

    # ------------------------------------------------------------------
    # Backend 1 — REST
    # ------------------------------------------------------------------

    def _ask_rest(
        self, prompt: str, model: str, *, verbose: bool
    ) -> Optional[str]:
        url = self.cfg.ollama_host.rstrip("/") + "/api/generate"
        payload = json.dumps({
            "model":  model,
            "prompt": prompt,
            "stream": False,
        }).encode()
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read())
                return data.get("response", "").strip() or None
        except urllib.error.URLError:
            return None
        except Exception as exc:
            if verbose:
                print(f"[null-claw] REST error: {exc}", file=sys.stderr)
            return None

    # ------------------------------------------------------------------
    # Backend 2 — subprocess ``ollama run``
    # ------------------------------------------------------------------

    def _ask_subprocess(
        self, prompt: str, model: str, *, verbose: bool
    ) -> Optional[str]:
        try:
            proc = subprocess.run(
                ["ollama", "run", model],
                input=prompt,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=120,
            )
            out = proc.stdout.strip()
            return out if out else None
        except FileNotFoundError:
            return None   # ollama not installed
        except subprocess.TimeoutExpired:
            if verbose:
                print("[null-claw] ollama subprocess timed out", file=sys.stderr)
            return None
        except Exception as exc:
            if verbose:
                print(f"[null-claw] subprocess error: {exc}", file=sys.stderr)
            return None

    # ------------------------------------------------------------------
    # Backend 3 — GeminiProgramFixer (free cloud fallback)
    # ------------------------------------------------------------------

    def _ask_gemini_fallback(
        self, prompt: str, *, verbose: bool
    ) -> Optional[str]:
        try:
            from gemini_code_fixer import GeminiProgramFixer
            fixer = GeminiProgramFixer()
            if fixer.api_key is None:
                return None
            if verbose:
                print("[null-claw] Ollama unavailable → using Gemini fallback …")
            return fixer._ask_gemini(prompt)
        except Exception:
            return None


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------

def ask_ollama(
    prompt: str,
    model: Optional[str] = None,
    cfg: Optional[NullClawConfig] = None,
    *,
    verbose: bool = True,
) -> Optional[str]:
    return OllamaClient(cfg).ask(prompt, model=model, verbose=verbose)
