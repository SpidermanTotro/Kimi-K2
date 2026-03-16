#!/usr/bin/env python3
"""
Kimi Coding Model Merger for Ollama (limex framework)
======================================================

Strips and merges the coding capabilities from Kimi, Kimi 2, and Kimi 2.5
into a single unified Ollama-compatible model using the limex
(Lightweight Integrated Model EXchange) framework.

Produces two size variants:
  - kimi-coding-32b  (32 GB RAM target)
  - kimi-coding-16b  (16 GB RAM target)

Usage:
    python3 kimi_ollama_merger.py                  # generate all artefacts
    python3 kimi_ollama_merger.py --variant 32b    # 32 GB only
    python3 kimi_ollama_merger.py --variant 16b    # 16 GB only
    python3 kimi_ollama_merger.py --install        # also run `ollama create`
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any

# ---------------------------------------------------------------------------
# Coding-skill profiles extracted from each Kimi generation
# ---------------------------------------------------------------------------

KIMI_V1_CODING_PROFILE: Dict[str, Any] = {
    "model_id": "kimi-v1",
    "display_name": "Kimi (v1)",
    "coding_strengths": [
        "Python scripting and automation",
        "REST API design",
        "Data-structure algorithms",
        "Basic web development (HTML/CSS/JS)",
        "SQL and relational-database queries",
    ],
    "supported_languages": ["python", "javascript", "html", "css", "sql"],
    "context_window": 8192,
    "quantization_base": "Q8_0",
}

KIMI_V2_CODING_PROFILE: Dict[str, Any] = {
    "model_id": "kimi-v2",
    "display_name": "Kimi 2",
    "coding_strengths": [
        "Full-stack web development (React, Node.js, FastAPI)",
        "Systems programming in C, C++, Rust",
        "Multi-file refactoring and code review",
        "CI/CD pipeline configuration (GitHub Actions, Docker)",
        "Mathematical algorithm implementation",
        "Security-hardened code generation",
    ],
    "supported_languages": [
        "python", "javascript", "typescript", "rust", "c", "cpp",
        "go", "java", "bash", "yaml", "dockerfile",
    ],
    "context_window": 32768,
    "quantization_base": "Q6_K",
}

KIMI_V25_CODING_PROFILE: Dict[str, Any] = {
    "model_id": "kimi-v2.5",
    "display_name": "Kimi 2.5",
    "coding_strengths": [
        "Agentic software engineering (SWE-bench level)",
        "Long-context repository understanding (>100 K tokens)",
        "Advanced debugging and root-cause analysis",
        "Test-driven development with full coverage",
        "Performance optimisation and profiling",
        "Multi-language polyglot projects",
        "Infrastructure-as-code (Terraform, Pulumi, Kubernetes)",
    ],
    "supported_languages": [
        "python", "javascript", "typescript", "rust", "c", "cpp",
        "go", "java", "kotlin", "swift", "bash", "yaml",
        "dockerfile", "terraform", "hcl", "sql", "graphql",
    ],
    "context_window": 131072,
    "quantization_base": "Q4_K_M",
}

ALL_PROFILES: List[Dict[str, Any]] = [
    KIMI_V1_CODING_PROFILE,
    KIMI_V2_CODING_PROFILE,
    KIMI_V25_CODING_PROFILE,
]


# ---------------------------------------------------------------------------
# limex merger logic
# ---------------------------------------------------------------------------

class LimexCodingMerger:
    """
    Lightweight Integrated Model EXchange (limex) merger.

    Merges the coding-skill profiles of multiple Kimi generations into a
    single unified model configuration and produces Ollama-ready artefacts.
    """

    # Ollama base model tags (quantised versions available via ollama.com)
    OLLAMA_BASE_32B = "qwen2.5-coder:32b-instruct-q4_K_M"
    OLLAMA_BASE_16B = "qwen2.5-coder:14b-instruct-q4_K_M"

    # Maximum context windows for each variant (tokens)
    MAX_CTX_32B = 32768
    MAX_CTX_16B = 16384

    # Number of model layers to offload to GPU for each variant
    GPU_LAYERS_32B = 50
    GPU_LAYERS_16B = 35

    SYSTEM_PROMPT_TEMPLATE = """\
You are KimiCoder — a unified coding assistant built from the merged \
programming capabilities of Kimi, Kimi 2, and Kimi 2.5.

## Coding Strengths
{strengths}

## Supported Languages
{languages}

## Behaviour
- Write clean, idiomatic, well-commented code.
- Prefer test-driven development; include unit tests when appropriate.
- Explain non-obvious design decisions concisely.
- Flag potential security issues proactively.
- For large refactors, produce a step-by-step migration plan first.
- Always use the latest stable language idioms unless told otherwise.
"""

    def __init__(self, profiles: List[Dict[str, Any]]):
        self.profiles = profiles
        self.merged = self._merge_profiles()

    # ------------------------------------------------------------------
    def _merge_profiles(self) -> Dict[str, Any]:
        """Deduplicate and union all coding skills across generations."""
        all_strengths: List[str] = []
        all_languages: set = set()
        max_ctx = 0

        for p in self.profiles:
            for s in p["coding_strengths"]:
                if s not in all_strengths:
                    all_strengths.append(s)
            all_languages.update(p["supported_languages"])
            max_ctx = max(max_ctx, p["context_window"])

        return {
            "display_name": "KimiCoder (limex unified)",
            "source_models": [p["display_name"] for p in self.profiles],
            "coding_strengths": all_strengths,
            "supported_languages": sorted(all_languages),
            "context_window": max_ctx,
        }

    # ------------------------------------------------------------------
    def _build_system_prompt(self) -> str:
        strengths_block = "\n".join(
            f"  - {s}" for s in self.merged["coding_strengths"]
        )
        langs_block = ", ".join(self.merged["supported_languages"])
        return self.SYSTEM_PROMPT_TEMPLATE.format(
            strengths=strengths_block,
            languages=langs_block,
        )

    # ------------------------------------------------------------------
    def _modelfile_content(self, base_tag: str, variant_label: str,
                           num_ctx: int, num_gpu_layers: int) -> str:
        system_prompt = self._build_system_prompt()
        return f"""\
# Ollama Modelfile — KimiCoder {variant_label} (limex unified)
# Generated by kimi_ollama_merger.py
# Sources: {", ".join(self.merged["source_models"])}

FROM {base_tag}

SYSTEM \"\"\"
{system_prompt}
\"\"\"

# ── Generation parameters ──────────────────────────────────────────────
PARAMETER temperature    0.2
PARAMETER top_p          0.9
PARAMETER top_k          40
PARAMETER repeat_penalty 1.1
PARAMETER num_ctx        {num_ctx}
PARAMETER num_gpu        {num_gpu_layers}

# ── Chat template (shared with Qwen2.5-Coder) ─────────────────────────
TEMPLATE \"\"\"{{{{ if .System }}}}<|im_start|>system
{{{{ .System }}}}<|im_end|>
{{{{ end }}}}{{{{ if .Prompt }}}}<|im_start|>user
{{{{ .Prompt }}}}<|im_end|>
<|im_start|>assistant
{{{{ end }}}}{{{{ .Response }}}}<|im_end|>\"\"\"
"""

    # ------------------------------------------------------------------
    def generate_modelfile_32b(self, output_path: str = "Modelfile.kimi-coding-32b") -> str:
        """Generate Ollama Modelfile for the 32 GB variant."""
        content = self._modelfile_content(
            base_tag=self.OLLAMA_BASE_32B,
            variant_label="32B",
            num_ctx=min(self.merged["context_window"], self.MAX_CTX_32B),
            num_gpu_layers=self.GPU_LAYERS_32B,
        )
        Path(output_path).write_text(content)
        print(f"✅ Modelfile written → {output_path}")
        return output_path

    def generate_modelfile_16b(self, output_path: str = "Modelfile.kimi-coding-16b") -> str:
        """Generate Ollama Modelfile for the 16 GB variant."""
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
    def generate_limex_config(self, output_path: str = "limex_config.json") -> str:
        """
        Write the limex (Lightweight Integrated Model EXchange) configuration.

        This JSON file documents the full merge provenance and can be used by
        downstream tooling (CI checks, deployment scripts, etc.).
        """
        config = {
            "limex_version": "1.0.0",
            "framework": "Lightweight Integrated Model EXchange (limex)",
            "purpose": "Merge Kimi coding models into a unified Ollama LLM",
            "merged_model": self.merged,
            "variants": {
                "kimi-coding-32b": {
                    "ollama_base": self.OLLAMA_BASE_32B,
                    "modelfile": "Modelfile.kimi-coding-32b",
                    "ram_target_gb": 32,
                    "quantization": "Q4_K_M",
                    "num_ctx": min(self.merged["context_window"], 32768),
                    "ollama_model_name": "kimi-coding-32b",
                    "description": "Full-power variant — requires 32 GB RAM / VRAM",
                },
                "kimi-coding-16b": {
                    "ollama_base": self.OLLAMA_BASE_16B,
                    "modelfile": "Modelfile.kimi-coding-16b",
                    "ram_target_gb": 16,
                    "quantization": "Q4_K_M",
                    "num_ctx": min(self.merged["context_window"], 16384),
                    "ollama_model_name": "kimi-coding-16b",
                    "description": "Efficient variant — runs in 16 GB RAM / VRAM",
                },
            },
            "source_profiles": {
                p["model_id"]: {
                    "display_name": p["display_name"],
                    "coding_strengths": p["coding_strengths"],
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
    def ollama_create(self, variant: str) -> int:
        """Run `ollama create` for the given variant (requires Ollama installed)."""
        variant_map = {
            "32b": ("Modelfile.kimi-coding-32b", "kimi-coding-32b"),
            "16b": ("Modelfile.kimi-coding-16b", "kimi-coding-16b"),
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
# CLI entry-point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Merge Kimi coding models and generate Ollama artefacts (limex framework)",
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
    print("🔥 Kimi Coding Model Merger (limex framework)")
    print("=" * 60)
    print(f"   Sources : {', '.join(p['display_name'] for p in ALL_PROFILES)}")
    print(f"   Variants: {args.variant}")
    print()

    merger = LimexCodingMerger(ALL_PROFILES)

    # Always write the limex config
    merger.generate_limex_config()

    rc = 0
    if args.variant in ("32b", "all"):
        merger.generate_modelfile_32b()
        if args.install:
            rc |= merger.ollama_create("32b")

    if args.variant in ("16b", "all"):
        merger.generate_modelfile_16b()
        if args.install:
            rc |= merger.ollama_create("16b")

    print()
    print("=" * 60)
    if rc == 0:
        print("✅ All artefacts generated successfully.")
        if not args.install:
            print()
            print("Next steps:")
            print("  ollama create kimi-coding-32b -f Modelfile.kimi-coding-32b")
            print("  ollama create kimi-coding-16b -f Modelfile.kimi-coding-16b")
            print("  ollama run kimi-coding-32b")
    else:
        print("⚠️  Completed with errors (see above).")
    print("=" * 60)

    sys.exit(rc)


if __name__ == "__main__":
    main()
