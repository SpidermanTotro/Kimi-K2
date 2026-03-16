#!/usr/bin/env python3
"""
THE FORGE ❤️ KIMI K2 — Student & University Access Module
Free, open-source coding tools for students. No subscriptions. No paywalls.

This module provides:
- Free local LLM coding assistance
- Skill absorption and learning aids
- University-friendly coding tools
- Resources for running Kimi K2 at zero cost
"""

from __future__ import annotations

import json
import os
import sys
import textwrap
from pathlib import Path
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Free resources students can use right now
# ---------------------------------------------------------------------------

FREE_RESOURCES: List[Dict[str, str]] = [
    {
        "name": "Kimi K2 (this project — local deployment)",
        "url": "https://github.com/moonshotai/Kimi-K2",
        "notes": "Run the full 1-trillion-parameter model locally — no API key needed.",
    },
    {
        "name": "Hugging Face (free model hub)",
        "url": "https://huggingface.co/moonshotai",
        "notes": "Download Kimi K2 weights for free and run offline via transformers/vLLM.",
    },
    {
        "name": "Ollama (one-command local LLM runner)",
        "url": "https://ollama.com",
        "notes": "Run open-source LLMs locally in one command. Completely free.",
    },
    {
        "name": "GitHub Student Developer Pack",
        "url": "https://education.github.com/pack",
        "notes": "Free GitHub Copilot, Azure credits, and 100+ other tools for students.",
    },
    {
        "name": "Google Colab (free GPU notebooks)",
        "url": "https://colab.research.google.com",
        "notes": "Free T4/A100 GPU access. Run inference or fine-tuning for free.",
    },
    {
        "name": "Kaggle Notebooks (free GPU/TPU)",
        "url": "https://www.kaggle.com/code",
        "notes": "30 h/week free GPU. Great for running smaller LLMs and ML experiments.",
    },
    {
        "name": "LM Studio (GUI for local LLMs)",
        "url": "https://lmstudio.ai",
        "notes": "Desktop app to download & run LLMs locally. Completely free.",
    },
]

SKILL_CATEGORIES: List[str] = [
    "Python fundamentals",
    "Data structures & algorithms",
    "Web development (HTML/CSS/JS/Flask/FastAPI)",
    "Database design (SQL & NoSQL)",
    "Machine learning basics (scikit-learn, PyTorch)",
    "Version control (Git & GitHub)",
    "Linux & shell scripting",
    "API development & REST design",
    "Software testing & debugging",
    "System design & architecture",
]


# ---------------------------------------------------------------------------
# Core student access class
# ---------------------------------------------------------------------------

class StudentAccess:
    """
    Free coding toolkit designed for university students.
    Runs entirely offline — no subscription or API key required.
    """

    def __init__(self) -> None:
        self.absorbed_skills: List[str] = []
        self.session_questions: List[str] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def welcome(self) -> str:
        """Return the student welcome banner."""
        banner = textwrap.dedent("""\
            ╔══════════════════════════════════════════════════════════════╗
            ║   🎓 THE FORGE ❤️ KIMI K2 — FREE STUDENT ACCESS             ║
            ║                                                              ║
            ║   No subscription. No paywall. No corporate gatekeeping.    ║
            ║   Run the full model locally — 100% free & open-source.    ║
            ╚══════════════════════════════════════════════════════════════╝
        """)
        return banner

    def list_free_resources(self) -> str:
        """Return a formatted list of free tools available to students."""
        lines = ["🆓 FREE TOOLS FOR UNIVERSITY STUDENTS\n", "=" * 60]
        for i, res in enumerate(FREE_RESOURCES, 1):
            lines.append(f"\n{i}. {res['name']}")
            lines.append(f"   🔗 {res['url']}")
            lines.append(f"   💡 {res['notes']}")
        lines.append("\n" + "=" * 60)
        lines.append("All of the above are completely free for students.")
        return "\n".join(lines)

    def get_local_setup_guide(self) -> str:
        """Return a step-by-step guide to running Kimi K2 locally for free."""
        guide = textwrap.dedent("""\
            🚀 RUN KIMI K2 LOCALLY — ZERO COST SETUP
            ==========================================

            Option A: vLLM (fastest, needs a GPU)
            ----------------------------------------
            pip install vllm
            vllm serve moonshotai/Kimi-K2-Instruct \\
                --tensor-parallel-size 4 \\
                --max-model-len 32768

            Option B: Hugging Face Transformers (CPU/GPU)
            -----------------------------------------------
            pip install transformers accelerate
            python3 - <<'EOF'
            from transformers import AutoModelForCausalLM, AutoTokenizer
            model_name = "moonshotai/Kimi-K2-Instruct"
            tok = AutoTokenizer.from_pretrained(model_name)
            mdl = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto")
            inp = tok("Write a binary search in Python", return_tensors="pt").to(mdl.device)
            out = mdl.generate(**inp, max_new_tokens=256)
            print(tok.decode(out[0], skip_special_tokens=True))
            EOF

            Option C: Ollama (easiest, any machine)
            ----------------------------------------
            # Install Ollama from https://ollama.com, then:
            ollama run kimi-k2   # downloads & runs in one command

            Option D: Google Colab (no local GPU needed)
            ---------------------------------------------
            1. Open https://colab.research.google.com
            2. Set Runtime → GPU → T4 (free tier)
            3. Run:
               !pip install vllm
               # Then use Option A commands above

            💡 TIP: All four options are completely free for students.
        """)
        return guide

    def absorb_skill(self, skill: str) -> str:
        """
        Register a skill the student wants the LLM to teach them.
        Returns study pointers for that skill.
        """
        skill = skill.strip()
        if not skill:
            return "❌ Please provide a skill name."

        self.absorbed_skills.append(skill)

        pointers = self._generate_skill_pointers(skill)
        return (
            f"✅ Skill '{skill}' added to your learning queue.\n\n"
            f"📚 Study roadmap:\n{pointers}\n\n"
            f"Total skills in queue: {len(self.absorbed_skills)}"
        )

    def show_skill_queue(self) -> str:
        """Display all skills queued for absorption."""
        if not self.absorbed_skills:
            return (
                "📭 No skills in queue yet.\n"
                "Use absorb_skill('<topic>') to add one.\n\n"
                "Suggested skills:\n"
                + "\n".join(f"  • {s}" for s in SKILL_CATEGORIES)
            )
        lines = ["📚 YOUR SKILL ABSORPTION QUEUE", "=" * 40]
        for i, skill in enumerate(self.absorbed_skills, 1):
            lines.append(f"  {i}. {skill}")
        lines.append("=" * 40)
        lines.append(f"Total: {len(self.absorbed_skills)} skill(s)")
        return "\n".join(lines)

    def generate_coding_exercise(self, topic: str, difficulty: str = "beginner") -> str:
        """
        Generate a free coding exercise on the given topic.
        Difficulty: beginner | intermediate | advanced
        """
        difficulty = difficulty.lower()
        valid = ("beginner", "intermediate", "advanced")
        if difficulty not in valid:
            difficulty = "beginner"

        exercises = self._exercises_for(topic, difficulty)
        header = (
            f"💻 CODING EXERCISE — {topic.upper()} ({difficulty})\n"
            + "=" * 55 + "\n"
        )
        return header + exercises

    def get_coding_help(self, query: str) -> str:
        """Provide free coding guidance for a student query."""
        self.session_questions.append(query)
        return (
            f"🤖 Kimi K2 Coding Assistant (free local mode)\n"
            f"{'=' * 55}\n"
            f"Query: {query}\n\n"
            "To get a real AI-powered answer entirely for free:\n\n"
            "  1. Start the local server (see /student setup)\n"
            "  2. Then ask your question directly — the full\n"
            "     1-trillion-parameter Kimi K2 model will respond.\n\n"
            "Quick tip: Switch to /mode code and ask the same\n"
            "question once the model is running locally."
        )

    def export_session(self, path: Optional[str] = None) -> str:
        """Export the student session (skills + questions) to JSON."""
        data = {
            "absorbed_skills": self.absorbed_skills,
            "session_questions": self.session_questions,
        }
        if path is None:
            path = str(Path.home() / "forge_student_session.json")
        try:
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2)
            return f"✅ Session exported to: {path}"
        except OSError as exc:
            return f"❌ Export failed: {exc}"

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _generate_skill_pointers(skill: str) -> str:
        """Return generic study pointers for any skill."""
        skill_lower = skill.lower()

        if any(kw in skill_lower for kw in ("python", "js", "javascript", "rust", "go", "c++")):
            category = "programming language"
            resources = [
                "Official documentation / language tour",
                "freeCodeCamp or The Odin Project (free)",
                "Exercism.io — hands-on challenges (free)",
                "Kimi K2 local: ask it to explain any concept",
            ]
        elif any(kw in skill_lower for kw in ("ml", "machine learning", "deep learning", "ai", "llm")):
            category = "machine learning / AI"
            resources = [
                "fast.ai — Practical Deep Learning (free course)",
                "Andrej Karpathy's YouTube channel (free)",
                "Hugging Face course: huggingface.co/course (free)",
                "Kaggle Learn (free micro-courses + free GPU)",
            ]
        elif any(kw in skill_lower for kw in ("algorithm", "data structure", "leetcode")):
            category = "algorithms & data structures"
            resources = [
                "Visualgo.net — visualise algorithms (free)",
                "LeetCode free tier — 1000+ problems",
                "NeetCode.io — structured roadmap (free)",
                "CLRS textbook (check university library)",
            ]
        else:
            category = "general software engineering"
            resources = [
                "GitHub Student Pack — 100+ free tools",
                "MIT OpenCourseWare (free university lectures)",
                "The Missing Semester — cs.mit.edu/missing (free)",
                "Kimi K2 local: ask it anything about this topic",
            ]

        lines = [f"  Category: {category}"]
        for r in resources:
            lines.append(f"  • {r}")
        return "\n".join(lines)

    @staticmethod
    def _exercises_for(topic: str, difficulty: str) -> str:
        """Return a short coding exercise template."""
        prompts = {
            "beginner": (
                f"Write a function that demonstrates a basic concept from '{topic}'.\n"
                "Requirements:\n"
                "  • Keep it under 20 lines\n"
                "  • Include a docstring\n"
                "  • Add at least one assert statement to verify it works\n"
            ),
            "intermediate": (
                f"Implement a small program/class that uses '{topic}' in a realistic scenario.\n"
                "Requirements:\n"
                "  • Handle at least one edge case\n"
                "  • Include type hints (Python) or strict types (other languages)\n"
                "  • Write 3+ unit tests\n"
            ),
            "advanced": (
                f"Design and implement a production-quality module centred on '{topic}'.\n"
                "Requirements:\n"
                "  • Follow SOLID principles\n"
                "  • Include a README explaining design decisions\n"
                "  • Achieve >80% test coverage\n"
                "  • Benchmark performance and document Big-O complexity\n"
            ),
        }
        base = prompts.get(difficulty, prompts["beginner"])
        base += (
            "\n💡 Use Kimi K2 locally for hints — it's free and runs on your own machine.\n"
            "   See /student setup for a one-command local installation guide.\n"
        )
        return base


# ---------------------------------------------------------------------------
# Standalone demo
# ---------------------------------------------------------------------------

def main() -> None:
    sa = StudentAccess()
    print(sa.welcome())
    print(sa.list_free_resources())
    print()
    print(sa.get_local_setup_guide())
    print()
    print(sa.absorb_skill("Python fundamentals"))
    print()
    print(sa.absorb_skill("machine learning"))
    print()
    print(sa.show_skill_queue())
    print()
    print(sa.generate_coding_exercise("binary search trees", "intermediate"))


if __name__ == "__main__":
    main()
