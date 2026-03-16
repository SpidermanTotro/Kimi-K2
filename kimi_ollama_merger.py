#!/usr/bin/env python3
"""
Kimi All-Skills Model Merger for Ollama (limex framework)
==========================================================

Collects every skill category from Kimi, Kimi 2, and Kimi 2.5, strips all
payment / monetisation capabilities, and produces:

  * Two Ollama Modelfiles  (32 GB and 16 GB)
  * A limex_config.json   provenance record
  * A kimi_training_data.jsonl  Alpaca-format fine-tuning dataset
    (compatible with unsloth, mlx-lm, axolotl, etc.)

Usage:
    python3 kimi_ollama_merger.py              # generate all artefacts
    python3 kimi_ollama_merger.py --variant 32b
    python3 kimi_ollama_merger.py --variant 16b
    python3 kimi_ollama_merger.py --install    # also run `ollama create`
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Payment / monetisation keywords — skills matching any of these phrases
# are stripped from Kimi 2 and Kimi 2.5 before merging.
# ---------------------------------------------------------------------------

PAYMENT_KEYWORDS: List[str] = [
    "monetization", "monetisation", "monetize", "monetise",
    "revenue estimate", "CPM analysis", "RPM tracking",
    "ad type performance", "sponsorship value", "super chat",
    "membership insights", "merchandise click",
    "payment", "billing", "subscription fee",
    "credit card", "stripe", "paypal",
    "invoice", "pricing tier", "paid feature",
    "commercial use", "ad revenue",
]


def _is_payment_skill(skill: str) -> bool:
    """Return True if *skill* matches any payment keyword (case-insensitive)."""
    lower = skill.lower()
    return any(kw.lower() in lower for kw in PAYMENT_KEYWORDS)


# ---------------------------------------------------------------------------
# Per-generation skill profiles  (all 12 categories)
# ---------------------------------------------------------------------------

KIMI_V1_PROFILE: Dict[str, Any] = {
    "model_id": "kimi-v1",
    "display_name": "Kimi (v1)",
    "strip_payment": False,          # v1 had no payment skills to strip
    "skills": {
        "programming": [
            "Python scripting and automation",
            "REST API design",
            "Data-structure algorithms",
            "Basic web development (HTML/CSS/JS)",
            "SQL and relational-database queries",
            "Shell scripting (bash)",
            "Unit-test generation",
            "Code documentation (docstrings, comments)",
        ],
        "writing": [
            "Technical documentation",
            "README generation",
            "Basic report writing",
        ],
        "gaming": [],
        "video_image": [],
        "multimedia": [],
        "github": [
            "Git operations (commit, branch, merge)",
            "Pull request descriptions",
        ],
        "files": [
            "File upload and analysis",
            "Text/CSV/JSON parsing",
        ],
        "ai_ml": [
            "Machine learning model explanation",
        ],
        "devops": [
            "Basic Dockerfile authoring",
            "Environment variable management",
        ],
        "security": [
            "Syntax-level bug detection",
            "Basic input validation",
        ],
        "ecosystem": [],
        "unique_features": [
            "Instruction-following with context window 8K",
        ],
    },
    "supported_languages": [
        "python", "javascript", "html", "css", "sql", "bash",
    ],
    "context_window": 8192,
}

KIMI_V2_PROFILE: Dict[str, Any] = {
    "model_id": "kimi-v2",
    "display_name": "Kimi 2",
    "strip_payment": True,
    "skills": {
        "programming": [
            "Full-stack web development (React, Node.js, FastAPI)",
            "Systems programming in C, C++, Rust",
            "Multi-file refactoring and code review",
            "CI/CD pipeline configuration (GitHub Actions, Docker)",
            "Mathematical algorithm implementation",
            "Security-hardened code generation",
            "Type-safe TypeScript applications",
            "Go microservices",
            "Java enterprise patterns",
            "Performance optimisation and profiling",
        ],
        "writing": [
            "Long-form content creation",
            "Book chapter drafting",
            "SEO-optimised article writing",
            "API reference documentation",
            "User-guide authoring",
        ],
        "gaming": [
            "Game logic implementation",
            "Save-state management",
            "ROM metadata enrichment",
        ],
        "video_image": [
            "Video upscaling pipeline (SD → 4K)",
            "Image upscaling and enhancement",
            "Colour correction scripts",
            "Thumbnail generation",
        ],
        "multimedia": [
            "Professional video editing workflow",
            "Audio recording and processing",
            "Podcast production pipeline",
            # ── payment skills stripped below ──
            "YouTube monetization insights: Revenue estimates",           # ← stripped
            "YouTube monetization insights: CPM analysis (cost per 1000 views)",  # ← stripped
            "YouTube monetization insights: RPM tracking",               # ← stripped
            "YouTube monetization insights: Ad type performance",        # ← stripped
            "YouTube monetization insights: Sponsorship value calculation",  # ← stripped
            "YouTube monetization insights: Super Chat tracking",        # ← stripped
            "YouTube monetization insights: Membership insights",        # ← stripped
            "YouTube monetization insights: Merchandise click tracking", # ← stripped
        ],
        "github": [
            "Repository management (create, fork, clone)",
            "Git operations (rebase, cherry-pick, bisect)",
            "Pull request review and merge",
            "Issue triage and labelling",
            "GitHub Actions workflow authoring",
            "Branch protection rules",
        ],
        "files": [
            "30+ file-type analysis (PDF, DOCX, XLSX, images)",
            "Batch file transformation",
            "Binary file inspection",
        ],
        "ai_ml": [
            "Machine learning pipeline design",
            "Neural network architecture explanation",
            "Hyperparameter tuning guidance",
            "Model evaluation metrics",
        ],
        "devops": [
            "Docker Compose multi-service stacks",
            "Kubernetes manifest generation",
            "Terraform infrastructure-as-code",
            "CI/CD pipeline design",
            "Cloud deployment (AWS, GCP, Azure patterns)",
        ],
        "security": [
            "OWASP Top-10 vulnerability detection",
            "Secrets scanning",
            "Dependency CVE analysis",
            "Authentication flow review",
            "SQL injection prevention",
        ],
        "ecosystem": [
            "FORGE tool integration",
            "Plugin architecture design",
        ],
        "unique_features": [
            "32K context window for large codebases",
            "Never-reset memory patterns",
        ],
    },
    "supported_languages": [
        "python", "javascript", "typescript", "rust", "c", "cpp",
        "go", "java", "bash", "yaml", "dockerfile",
    ],
    "context_window": 32768,
}

KIMI_V25_PROFILE: Dict[str, Any] = {
    "model_id": "kimi-v2.5",
    "display_name": "Kimi 2.5",
    "strip_payment": True,
    "skills": {
        "programming": [
            "Agentic software engineering (SWE-bench level)",
            "Long-context repository understanding (>100 K tokens)",
            "Advanced debugging and root-cause analysis",
            "Test-driven development with full coverage",
            "Multi-language polyglot projects",
            "Formal verification patterns",
            "Compiler and interpreter implementation",
            "Embedded and real-time systems programming",
            "Concurrent and parallel programming (async, threads, actors)",
        ],
        "writing": [
            "Award-winning book writing with series planning",
            "Screenplay and dialogue writing",
            "Academic paper drafting",
            "Technical white-paper authoring",
            "Sequel and continuity detection",
        ],
        "gaming": [
            "50+ Pokémon game enhancement",
            "WoW private-server creation (12 expansions)",
            "ROM upscaling (SD → 8K)",
            "Game-save editor tooling",
            "Emulator configuration automation",
            "Speedrun route analysis",
        ],
        "video_image": [
            "Historical restoration (VHS → 8K, 1956-era films)",
            "AI-driven colourisation of B&W footage",
            "Frame interpolation (24fps → 60fps)",
            "Artefact removal and noise reduction",
            "Universal format conversion (any → any)",
            "Batch library upgrade (DVD → 4K)",
        ],
        "multimedia": [
            "Full non-linear video editing suite (unlimited tracks)",
            "Advanced word processing (styles, TOC, cross-references)",
            "Professional photo editing (layers, masks, healing)",
            "TV show recording and cataloguing (personal use only)",
            "FM radio recording (personal use only)",
            "Audio restoration (vinyl → digital)",
            "Screencast and tutorial production",
            # ── payment skills stripped below ──
            "YouTube channel analytics (views, CTR, audience retention)",
            "YouTube content strategy and topic research",
            "YouTube monetization insights: Revenue estimates",           # ← stripped
            "YouTube monetization insights: CPM analysis",                # ← stripped
            "YouTube monetization insights: RPM tracking",                # ← stripped
            "YouTube monetization insights: Sponsorship value calculation", # ← stripped
            "YouTube monetization insights: Super Chat tracking",         # ← stripped
            "YouTube monetization insights: Membership insights",         # ← stripped
        ],
        "github": [
            "Full repository lifecycle management",
            "Automated code review bots",
            "Dependency graph analysis",
            "Security advisory integration",
            "Multi-repo monorepo orchestration",
        ],
        "files": [
            "Universal file-type detection and parsing",
            "Archive creation and extraction (zip, tar, 7z)",
            "Binary diff and patch generation",
        ],
        "ai_ml": [
            "LLM fine-tuning workflow design",
            "RAG (retrieval-augmented generation) pipelines",
            "Vector database integration",
            "Model quantisation guidance",
            "On-device inference optimisation",
        ],
        "devops": [
            "GitOps workflow design",
            "Service mesh configuration (Istio, Linkerd)",
            "Observability stack (Prometheus, Grafana, Loki)",
            "Chaos engineering experiments",
            "Zero-downtime deployment strategies",
        ],
        "security": [
            "Penetration test scripting",
            "Threat-model documentation",
            "Zero-trust architecture design",
            "Cryptography implementation review",
            "Compliance mapping (SOC2, ISO 27001, HIPAA)",
        ],
        "ecosystem": [
            "Character world and narrative system design",
            "Emotional-climate tracking system",
            "Continuous-learning loop integration",
            "Community-driven open-source contribution workflows",
        ],
        "unique_features": [
            "131K context window for full repository ingestion",
            "Cosmic / spiritual reasoning layer",
            "Self-hosted, zero-cost deployment on local hardware",
        ],
    },
    "supported_languages": [
        "python", "javascript", "typescript", "rust", "c", "cpp",
        "go", "java", "kotlin", "swift", "bash", "yaml",
        "dockerfile", "terraform", "hcl", "sql", "graphql",
        "lua", "ruby", "php", "r", "scala", "elixir", "haskell",
        "dart", "perl", "powershell",
    ],
    "context_window": 131072,
}

ALL_PROFILES: List[Dict[str, Any]] = [
    KIMI_V1_PROFILE,
    KIMI_V2_PROFILE,
    KIMI_V25_PROFILE,
]


# ---------------------------------------------------------------------------
# limex merger
# ---------------------------------------------------------------------------

class LimexModelMerger:
    """
    Lightweight Integrated Model EXchange (limex) merger.

    Merges all skill categories from every Kimi generation,
    filters payment skills from models that carry the strip_payment flag,
    and emits Ollama Modelfiles, a limex config, and Alpaca JSONL
    training data.
    """

    OLLAMA_BASE_32B = "qwen2.5-coder:32b-instruct-q4_K_M"
    OLLAMA_BASE_16B = "qwen2.5-coder:14b-instruct-q4_K_M"

    MAX_CTX_32B = 32768
    MAX_CTX_16B = 16384

    GPU_LAYERS_32B = 50
    GPU_LAYERS_16B = 35

    SYSTEM_PROMPT_TEMPLATE = """\
You are KimiFree — a unified AI assistant built from the merged capabilities \
of Kimi, Kimi 2, and Kimi 2.5, with all payment and monetisation features removed \
so it is 100 % free to use forever.

## Skill Categories
{skill_sections}

## Supported Languages
{languages}

## Behaviour
- Write clean, idiomatic, well-commented code.
- Prefer test-driven development; include unit tests when appropriate.
- Explain non-obvious design decisions concisely.
- Flag potential security issues proactively.
- For large refactors, produce a step-by-step plan first.
- Always use the latest stable language idioms unless told otherwise.
- You have no payment, billing, subscription, or monetisation capabilities — \
all such features have been intentionally removed.
"""

    # Human-readable category labels
    CATEGORY_LABELS: Dict[str, str] = {
        "programming":    "Programming & Code",
        "writing":        "Content & Writing",
        "gaming":         "Gaming Enhancement",
        "video_image":    "Video & Image Processing",
        "multimedia":     "Multimedia & Productivity",
        "github":         "GitHub & Version Control",
        "files":          "File Handling & Processing",
        "ai_ml":          "AI / ML & Advanced Tech",
        "devops":         "DevOps & Deployment",
        "security":       "Security & Compliance",
        "ecosystem":      "Ecosystem & Character",
        "unique_features":"Unique Forge Features",
    }

    def __init__(self, profiles: List[Dict[str, Any]]):
        self.profiles = profiles
        self.stripped_log: List[str] = []
        self.merged = self._merge_all_profiles()

    # ------------------------------------------------------------------
    def _filter_skills(self, skills: List[str], should_strip: bool) -> List[str]:
        """Remove payment skills when *should_strip* is True."""
        if not should_strip:
            return skills
        kept, removed = [], []
        for s in skills:
            if _is_payment_skill(s):
                removed.append(s)
            else:
                kept.append(s)
        self.stripped_log.extend(removed)
        return kept

    def _merge_all_profiles(self) -> Dict[str, Any]:
        """Union all skill categories across generations, stripping payment items."""
        merged_categories: Dict[str, List[str]] = {k: [] for k in self.CATEGORY_LABELS}
        all_languages: set = set()
        max_ctx = 0

        for profile in self.profiles:
            strip = profile.get("strip_payment", False)
            for category, skills in profile["skills"].items():
                filtered = self._filter_skills(skills, strip)
                for skill in filtered:
                    if skill not in merged_categories[category]:
                        merged_categories[category].append(skill)
            all_languages.update(profile["supported_languages"])
            max_ctx = max(max_ctx, profile["context_window"])

        return {
            "display_name": "KimiFree (limex — all skills, no payment)",
            "source_models": [p["display_name"] for p in self.profiles],
            "skills_by_category": merged_categories,
            "supported_languages": sorted(all_languages),
            "context_window": max_ctx,
            "payment_skills_removed": sorted(set(self.stripped_log)),
        }

    # ------------------------------------------------------------------
    def _build_system_prompt(self) -> str:
        sections = []
        for cat_key, label in self.CATEGORY_LABELS.items():
            skills = self.merged["skills_by_category"].get(cat_key, [])
            if not skills:
                continue
            lines = "\n".join(f"  - {s}" for s in skills)
            sections.append(f"### {label}\n{lines}")

        return self.SYSTEM_PROMPT_TEMPLATE.format(
            skill_sections="\n\n".join(sections),
            languages=", ".join(self.merged["supported_languages"]),
        )

    # ------------------------------------------------------------------
    def _modelfile_content(self, base_tag: str, variant_label: str,
                           num_ctx: int, num_gpu_layers: int) -> str:
        system_prompt = self._build_system_prompt()
        sources = ", ".join(self.merged["source_models"])
        return (
            f"# Ollama Modelfile — KimiFree {variant_label} (limex — all skills, no payment)\n"
            f"# Generated by kimi_ollama_merger.py\n"
            f"# Sources: {sources}\n"
            f"# Payment skills stripped: {len(self.merged['payment_skills_removed'])}\n"
            f"\n"
            f"FROM {base_tag}\n"
            f"\n"
            f'SYSTEM """\n'
            f"{system_prompt}\n"
            f'"""\n'
            f"\n"
            f"# ── Generation parameters ──────────────────────────────────────────────\n"
            f"PARAMETER temperature    0.2\n"
            f"PARAMETER top_p          0.9\n"
            f"PARAMETER top_k          40\n"
            f"PARAMETER repeat_penalty 1.1\n"
            f"PARAMETER num_ctx        {num_ctx}\n"
            f"PARAMETER num_gpu        {num_gpu_layers}\n"
            f"\n"
            f"# ── Chat template (Qwen2.5-Coder / ChatML) ───────────────────────────\n"
            f'TEMPLATE """'
            r"""{{ if .System }}<|im_start|>system
{{ .System }}<|im_end|>
{{ end }}{{ if .Prompt }}<|im_start|>user
{{ .Prompt }}<|im_end|>
<|im_start|>assistant
{{ end }}{{ .Response }}<|im_end|>"""
            f'"""\n'
        )

    # ------------------------------------------------------------------
    def generate_modelfile_32b(self,
                               output_path: str = "Modelfile.kimi-free-32b") -> str:
        content = self._modelfile_content(
            base_tag=self.OLLAMA_BASE_32B,
            variant_label="32B",
            num_ctx=min(self.merged["context_window"], self.MAX_CTX_32B),
            num_gpu_layers=self.GPU_LAYERS_32B,
        )
        Path(output_path).write_text(content)
        print(f"✅ Modelfile written → {output_path}")
        return output_path

    def generate_modelfile_16b(self,
                               output_path: str = "Modelfile.kimi-free-16b") -> str:
        content = self._modelfile_content(
            base_tag=self.OLLAMA_BASE_16B,
            variant_label="16B",
            num_ctx=min(self.merged["context_window"], self.MAX_CTX_16B),
            num_gpu_layers=self.GPU_LAYERS_16B,
        )
        Path(output_path).write_text(content)
        print(f"✅ Modelfile written → {output_path}")
        return output_path

    # ------------------------------------------------------------------
    def generate_limex_config(self,
                              output_path: str = "limex_config.json") -> str:
        config = {
            "limex_version": "2.0.0",
            "framework": "Lightweight Integrated Model EXchange (limex)",
            "purpose": (
                "Merge ALL Kimi skills into a unified Ollama LLM, "
                "with payment/monetisation capabilities removed"
            ),
            "merged_model": self.merged,
            "variants": {
                "kimi-free-32b": {
                    "ollama_base": self.OLLAMA_BASE_32B,
                    "modelfile": "Modelfile.kimi-free-32b",
                    "ram_target_gb": 32,
                    "quantization": "Q4_K_M",
                    "num_ctx": min(self.merged["context_window"], self.MAX_CTX_32B),
                    "ollama_model_name": "kimi-free-32b",
                    "description": "Full-power free variant — 32 GB RAM / VRAM",
                },
                "kimi-free-16b": {
                    "ollama_base": self.OLLAMA_BASE_16B,
                    "modelfile": "Modelfile.kimi-free-16b",
                    "ram_target_gb": 16,
                    "quantization": "Q4_K_M",
                    "num_ctx": min(self.merged["context_window"], self.MAX_CTX_16B),
                    "ollama_model_name": "kimi-free-16b",
                    "description": "Efficient free variant — 16 GB RAM / VRAM",
                },
            },
            "source_profiles": {
                p["model_id"]: {
                    "display_name": p["display_name"],
                    "strip_payment": p.get("strip_payment", False),
                    "supported_languages": p["supported_languages"],
                    "context_window": p["context_window"],
                }
                for p in self.profiles
            },
        }
        Path(output_path).write_text(json.dumps(config, indent=2))
        print(f"✅ limex config written → {output_path}")
        return output_path

    # ------------------------------------------------------------------
    def generate_training_data(self,
                               output_path: str = "kimi_training_data.jsonl") -> str:
        """
        Generate an Alpaca-format JSONL fine-tuning dataset that covers every
        skill category in the merged model (payment skills excluded).

        The file can be fed directly into:
          - unsloth  (FastLanguageModel.from_pretrained + SFTTrainer)
          - mlx-lm   (mlx_lm.lora)
          - axolotl  (datasets: path: kimi_training_data.jsonl  type: alpaca)
          - Ollama   custom model fine-tuning workflows
        """
        records: List[Dict[str, str]] = []

        # ── 1. One example per skill (all categories) ──────────────────
        for cat_key, label in self.CATEGORY_LABELS.items():
            skills = self.merged["skills_by_category"].get(cat_key, [])
            for skill in skills:
                records.append({
                    "instruction": (
                        f"You are an expert AI assistant. "
                        f"Demonstrate your capability in: {skill}"
                    ),
                    "input": "",
                    "output": (
                        f"I can help with '{skill}' as part of my {label} capabilities. "
                        f"This skill was integrated from the Kimi model family "
                        f"(Kimi v1, Kimi 2, Kimi 2.5) via the limex framework. "
                        f"All payment and monetisation features have been removed — "
                        f"this capability is entirely free to use."
                    ),
                })

        # ── 2. Language-specific coding examples ───────────────────────
        for lang in self.merged["supported_languages"]:
            records.append({
                "instruction": f"Write a hello-world program in {lang}.",
                "input": "",
                "output": _hello_world_snippet(lang),
            })

        # ── 3. Payment-stripped confirmation examples ──────────────────
        for stripped_skill in self.merged["payment_skills_removed"]:
            records.append({
                "instruction": (
                    f"Can you help with: {stripped_skill}?"
                ),
                "input": "",
                "output": (
                    "I'm KimiFree — a payment-free AI. "
                    f"The capability '{stripped_skill}' involves monetisation or "
                    "payment tracking and has been intentionally removed from this model. "
                    "I'm here to help with everything else, completely free of charge."
                ),
            })

        # ── 4. Cross-skill workflow examples ───────────────────────────
        records.extend(_workflow_examples())

        with open(output_path, "w") as fh:
            for record in records:
                fh.write(json.dumps(record) + "\n")

        print(f"✅ Training data written → {output_path}  "
              f"({len(records)} examples)")
        return output_path

    # ------------------------------------------------------------------
    def ollama_create(self, variant: str) -> int:
        """Run `ollama create` for the given variant (requires Ollama installed)."""
        import subprocess
        variant_map = {
            "32b": ("Modelfile.kimi-free-32b", "kimi-free-32b"),
            "16b": ("Modelfile.kimi-free-16b", "kimi-free-16b"),
        }
        if variant not in variant_map:
            print(f"❌ Unknown variant '{variant}'. Choose from: 32b, 16b")
            return 1
        modelfile, model_name = variant_map[variant]
        if not Path(modelfile).exists():
            print(f"❌ Modelfile not found: {modelfile}  (run without --install first)")
            return 1
        cmd = ["ollama", "create", model_name, "-f", modelfile]
        print(f"🚀 Running: {' '.join(cmd)}")
        result = subprocess.run(cmd)
        if result.returncode == 0:
            print(f"✅ Model '{model_name}' created in Ollama")
        else:
            print(f"❌ ollama create failed (exit {result.returncode})")
        return result.returncode


# ---------------------------------------------------------------------------
# Training-data helpers
# ---------------------------------------------------------------------------

def _hello_world_snippet(lang: str) -> str:
    """Return a minimal working hello-world for the given language."""
    snippets: Dict[str, str] = {
        "python":     'print("Hello, World!")',
        "javascript": 'console.log("Hello, World!");',
        "typescript": 'console.log("Hello, World!");',
        "rust":       'fn main() { println!("Hello, World!"); }',
        "c":          '#include <stdio.h>\nint main() { printf("Hello, World!\\n"); return 0; }',
        "cpp":        '#include <iostream>\nint main() { std::cout << "Hello, World!\\n"; }',
        "go":         'package main\nimport "fmt"\nfunc main() { fmt.Println("Hello, World!") }',
        "java":       'public class Hello { public static void main(String[] a) { System.out.println("Hello, World!"); } }',
        "kotlin":     'fun main() { println("Hello, World!") }',
        "swift":      'print("Hello, World!")',
        "bash":       'echo "Hello, World!"',
        "ruby":       'puts "Hello, World!"',
        "php":        '<?php echo "Hello, World!\\n";',
        "r":          'cat("Hello, World!\\n")',
        "scala":      'object Hello extends App { println("Hello, World!") }',
        "elixir":     'IO.puts("Hello, World!")',
        "haskell":    'main = putStrLn "Hello, World!"',
        "dart":       'void main() { print("Hello, World!"); }',
        "lua":        'print("Hello, World!")',
        "perl":       'print "Hello, World!\\n";',
        "powershell": 'Write-Host "Hello, World!"',
        "sql":        "SELECT 'Hello, World!';",
        "graphql":    "# GraphQL has no runnable hello-world; query { __typename }",
        "yaml":       "# YAML configuration\ngreeting: Hello, World!",
        "dockerfile": 'FROM alpine\nCMD ["echo", "Hello, World!"]',
        "terraform":  'output "hello" { value = "Hello, World!" }',
        "hcl":        'locals { greeting = "Hello, World!" }',
        "html":       "<!DOCTYPE html><html><body><h1>Hello, World!</h1></body></html>",
        "css":        "/* Hello, World! */ body::before { content: 'Hello, World!'; }",
    }
    code = snippets.get(lang, f'# {lang}: print("Hello, World!")')
    return (
        f"Here is a hello-world program in {lang}:\n\n"
        f"```{lang}\n{code}\n```\n\n"
        "This was produced by KimiFree — free of charge, no payment required."
    )


def _workflow_examples() -> List[Dict[str, str]]:
    """Return multi-skill workflow training examples."""
    return [
        {
            "instruction": "Build a full-stack web app with tests and CI/CD.",
            "input": "Stack: Python FastAPI backend, React frontend, PostgreSQL database.",
            "output": (
                "I'll guide you through the full workflow using my merged Kimi skills:\n\n"
                "1. **Backend (Programming):** FastAPI app with Pydantic models and SQLAlchemy ORM.\n"
                "2. **Frontend (Programming):** React + TypeScript SPA with Vite.\n"
                "3. **Database (Programming):** PostgreSQL schema + Alembic migrations.\n"
                "4. **Tests (Programming):** pytest for backend, Vitest for frontend.\n"
                "5. **CI/CD (DevOps):** GitHub Actions workflow — lint → test → build → deploy.\n"
                "6. **Security:** OWASP input validation, JWT auth, secrets in env vars.\n\n"
                "All of this is free — no payment or subscription required."
            ),
        },
        {
            "instruction": "Restore an old VHS video and upload documentation to GitHub.",
            "input": "VHS tape digitised to MP4, target quality 4K.",
            "output": (
                "Using my merged Kimi 2.5 video and GitHub skills:\n\n"
                "1. **Video restoration (Video & Image):** AI upscale SD → 4K, denoise, "
                "colour-correct, frame-interpolate 24fps → 60fps.\n"
                "2. **Format conversion (Video & Image):** Export to H.265 for storage efficiency.\n"
                "3. **Documentation (Writing):** Generate a Markdown restoration log.\n"
                "4. **GitHub (GitHub & Version Control):** Commit the log, open a PR, "
                "add metadata tags.\n\n"
                "100 % free — no monetisation features are present in this model."
            ),
        },
        {
            "instruction": "Set up a local AI fine-tuning pipeline for this very model.",
            "input": "Hardware: single NVIDIA GPU with 16 GB VRAM.",
            "output": (
                "Using my AI/ML and DevOps skills:\n\n"
                "1. **Install Ollama** and pull the base: "
                "`ollama pull qwen2.5-coder:14b-instruct-q4_K_M`\n"
                "2. **Create the model** from the generated Modelfile: "
                "`ollama create kimi-free-16b -f Modelfile.kimi-free-16b`\n"
                "3. **Fine-tune** with the included training data:\n"
                "   - unsloth: `python unsloth_train.py --data kimi_training_data.jsonl`\n"
                "   - mlx-lm:  `mlx_lm.lora --model kimi-free-16b --data kimi_training_data.jsonl`\n"
                "4. **Export** the LoRA adapter and merge back into the base model.\n"
                "5. **Re-create** the Ollama model with the fine-tuned weights.\n\n"
                "No API keys, no subscriptions, no payment — runs entirely on your own hardware."
            ),
        },
    ]


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Merge ALL Kimi skills into Ollama models (limex framework). "
            "Payment/monetisation skills are stripped automatically."
        ),
    )
    parser.add_argument(
        "--variant",
        choices=["32b", "16b", "all"],
        default="all",
        help="Which size variant to generate (default: all)",
    )
    parser.add_argument(
        "--install",
        action="store_true",
        help="After generating, run `ollama create` to install the model locally",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("🔥 Kimi All-Skills Model Merger (limex framework)")
    print("=" * 60)
    sources = ", ".join(p["display_name"] for p in ALL_PROFILES)
    print(f"   Sources  : {sources}")
    print(f"   Variants : {args.variant}")
    print()

    merger = LimexModelMerger(ALL_PROFILES)

    # Report stripped skills
    stripped = merger.merged["payment_skills_removed"]
    if stripped:
        print(f"🚫 Stripped {len(stripped)} payment/monetisation skill(s):")
        for s in stripped:
            print(f"   ✂️  {s}")
        print()

    # Report total skills
    total = sum(
        len(v) for v in merger.merged["skills_by_category"].values()
    )
    print(f"✅ Merged {total} skills across "
          f"{len(merger.CATEGORY_LABELS)} categories")
    print(f"✅ Languages: {len(merger.merged['supported_languages'])}")
    print()

    # Always write config and training data
    merger.generate_limex_config()
    merger.generate_training_data()

    rc = 0
    if args.variant in ("32b", "all"):
        merger.generate_modelfile_32b()
        if args.install:
            rc = rc or merger.ollama_create("32b")

    if args.variant in ("16b", "all"):
        merger.generate_modelfile_16b()
        if args.install:
            rc = rc or merger.ollama_create("16b")

    print()
    print("=" * 60)
    if rc == 0:
        print("✅ All artefacts generated successfully.")
        if not args.install:
            print()
            print("Next steps:")
            print("  ollama create kimi-free-32b -f Modelfile.kimi-free-32b")
            print("  ollama create kimi-free-16b -f Modelfile.kimi-free-16b")
            print("  ollama run kimi-free-32b")
            print()
            print("Fine-tune with training data:")
            print("  # unsloth")
            print("  python unsloth_train.py --data kimi_training_data.jsonl")
            print("  # mlx-lm")
            print("  mlx_lm.lora --model kimi-free-16b --data kimi_training_data.jsonl")
    else:
        print("⚠️  Completed with errors (see above).")
    print("=" * 60)

    sys.exit(rc)


if __name__ == "__main__":
    main()
