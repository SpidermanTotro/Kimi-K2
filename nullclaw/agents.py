"""
NullClaw Agents
===============
Three-agent pipeline:  Planner → Debugger → Patcher

Each agent receives a structured prompt and returns a response.
When single-model mode is active (Ollama only has one model), all three
agents share that model, which still works well.

Pipeline
--------
  Planner  — high-level: "what type of error is this? what approach?"
  Debugger — detailed:   "what is the root cause in this specific code?"
  Patcher  — action:     "provide the smallest safe unified diff"
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from nullclaw.config import NullClawConfig, load_config
from nullclaw.error_parser import BuildError
from nullclaw.ollama_client import OllamaClient


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

_PLANNER_PROMPT = """You are the Planner agent in NullClaw, a local AI build-repair system.

Your task: given a build error, produce a SHORT plan (3–5 bullet points) describing the repair strategy.

Rules:
- Be concise (≤ 200 words)
- Do NOT write code yet
- Focus on root cause category and repair approach

Language: {language}
Error code: {code}
Error message: {message}
File: {file_path}:{line}

Respond with a numbered plan only."""


_DEBUGGER_PROMPT = """You are the Debugger agent in NullClaw.

You received this repair plan:
{plan}

Now analyse the actual source code context and identify the EXACT root cause.

Language: {language}
File: {file_path}:{line}:{column}
Error: [{code}] {message}

Source context:
{context}

Explain:
1. The exact root cause (1–2 sentences)
2. Which lines need changing
3. What the fix should be (describe, don't write the diff yet)
Keep your answer ≤ 300 words."""


_PATCHER_PROMPT = """You are the Patcher agent in NullClaw.

You received this diagnosis:
{diagnosis}

Now produce the MINIMAL safe code fix.

Rules:
- Fix ONLY the first/reported error
- Do NOT refactor unrelated code
- Do NOT invent missing APIs
- Provide a unified diff in a ```diff block
- If a diff is not possible, write the corrected code in a ```{language} block

Language: {language}
File: {file_path}:{line}:{column}
Error: [{code}] {message}

Source context:
{context}"""


_SINGLE_AGENT_PROMPT = """You are NullClaw, a local AI code-repair agent.

Fix ONLY the first build error below.

Rules:
- smallest safe patch only
- do not refactor unrelated code
- do not invent missing APIs
- explain the root cause (1 sentence)
- provide an exact fix
- if possible, output a unified diff in a ```diff block

Language: {language}
File: {file_path}
Line: {line}
Column: {column}
Code: {code}
Message: {message}

Source context:
{context}"""


# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------

@dataclass
class AgentResult:
    plan:      Optional[str] = None
    diagnosis: Optional[str] = None
    patch:     Optional[str] = None
    full_reply: str = ""

    def best_reply(self) -> str:
        return self.patch or self.diagnosis or self.plan or self.full_reply


# ---------------------------------------------------------------------------
# Agent runner
# ---------------------------------------------------------------------------

class NullClawAgents:
    """
    Run the Planner → Debugger → Patcher pipeline.

    Falls back to a single combined prompt if:
     - the planner model equals the primary model (no point running twice)
     - any intermediate step returns None
    """

    def __init__(self, cfg: Optional[NullClawConfig] = None) -> None:
        self.cfg    = cfg or load_config()
        self.client = OllamaClient(self.cfg)

    def run(
        self,
        error: BuildError,
        context: str,
        *,
        verbose: bool = True,
    ) -> AgentResult:
        """
        Run the full pipeline for *error* + *context*.

        Returns an :class:`AgentResult` with the best available output.
        """
        use_multi_agent = (
            self.cfg.primary_model != self.cfg.planner_model
        )

        if use_multi_agent:
            return self._run_pipeline(error, context, verbose=verbose)
        else:
            return self._run_single(error, context, verbose=verbose)

    # ------------------------------------------------------------------
    # Three-agent pipeline
    # ------------------------------------------------------------------

    def _run_pipeline(
        self, error: BuildError, context: str, *, verbose: bool
    ) -> AgentResult:
        result = AgentResult()

        # 1. Planner
        if verbose:
            print("[null-claw] 🧠 Planner …")
        plan = self.client.ask(
            _PLANNER_PROMPT.format(
                language=error.language,
                code=error.code or "?",
                message=error.message,
                file_path=error.file_path,
                line=error.line,
            ),
            model=self.cfg.planner_model,
            verbose=False,
        )
        result.plan = plan

        if plan is None:
            # Planner failed — fall through to single agent
            return self._run_single(error, context, verbose=verbose)

        # 2. Debugger
        if verbose:
            print("[null-claw] 🔍 Debugger …")
        diagnosis = self.client.ask(
            _DEBUGGER_PROMPT.format(
                plan=plan,
                language=error.language,
                file_path=error.file_path,
                line=error.line,
                column=error.column,
                code=error.code or "?",
                message=error.message,
                context=context,
            ),
            model=self.cfg.primary_model,
            verbose=False,
        )
        result.diagnosis = diagnosis

        if diagnosis is None:
            return self._run_single(error, context, verbose=verbose)

        # 3. Patcher
        if verbose:
            print("[null-claw] 🔧 Patcher …")
        patch_reply = self.client.ask(
            _PATCHER_PROMPT.format(
                diagnosis=diagnosis,
                language=error.language,
                file_path=error.file_path,
                line=error.line,
                column=error.column,
                code=error.code or "?",
                message=error.message,
                context=context,
            ),
            model=self.cfg.primary_model,
            verbose=False,
        )
        result.patch      = patch_reply
        result.full_reply = "\n\n---\n\n".join(filter(None, [plan, diagnosis, patch_reply]))

        return result

    # ------------------------------------------------------------------
    # Single-agent fallback
    # ------------------------------------------------------------------

    def _run_single(
        self, error: BuildError, context: str, *, verbose: bool
    ) -> AgentResult:
        if verbose:
            print("[null-claw] 🤖 Single-agent repair …")
        reply = self.client.ask(
            _SINGLE_AGENT_PROMPT.format(
                language=error.language,
                file_path=error.file_path,
                line=error.line,
                column=error.column,
                code=error.code or "?",
                message=error.message,
                context=context,
            ),
            model=self.cfg.primary_model,
            verbose=False,
        )
        return AgentResult(
            patch=reply,
            full_reply=reply or "",
        )
