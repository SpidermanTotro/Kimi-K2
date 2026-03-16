#!/usr/bin/env python3
"""
Unit tests for kimi_ollama_merger.py

Run with:
    python3 -m pytest test_kimi_ollama_merger.py -v
    # or
    make test
"""

import json
import sys
import tempfile
from pathlib import Path

import pytest

# Add repo root to path so we can import the merger
sys.path.insert(0, str(Path(__file__).parent))

from kimi_ollama_merger import (
    ALL_PROFILES,
    PAYMENT_KEYWORDS,
    LimexModelMerger,
    _hello_world_snippet,
    _is_payment_skill,
)


# ---------------------------------------------------------------------------
# _is_payment_skill
# ---------------------------------------------------------------------------

class TestIsPaymentSkill:
    def test_cpm_detected(self):
        assert _is_payment_skill("CPM analysis (cost per 1000 views)")

    def test_rpm_detected(self):
        assert _is_payment_skill("RPM tracking")

    def test_revenue_estimate_detected(self):
        assert _is_payment_skill("Revenue estimates")

    def test_sponsorship_detected(self):
        assert _is_payment_skill("Sponsorship value calculation")

    def test_super_chat_detected(self):
        assert _is_payment_skill("Super Chat tracking")

    def test_case_insensitive(self):
        assert _is_payment_skill("cpm ANALYSIS")
        assert _is_payment_skill("CPM Analysis")

    def test_normal_skill_not_flagged(self):
        assert not _is_payment_skill("Python scripting and automation")
        assert not _is_payment_skill("GitHub Actions workflow authoring")
        assert not _is_payment_skill("YouTube channel analytics (views, CTR, audience retention)")
        assert not _is_payment_skill("YouTube content strategy and topic research")

    def test_all_payment_keywords_covered(self):
        """Every keyword in PAYMENT_KEYWORDS should trigger the filter."""
        for kw in PAYMENT_KEYWORDS:
            assert _is_payment_skill(f"some skill involving {kw}"), (
                f"Keyword '{kw}' not caught by _is_payment_skill"
            )


# ---------------------------------------------------------------------------
# LimexModelMerger — merge behaviour
# ---------------------------------------------------------------------------

class TestLimexModelMerger:
    @pytest.fixture(scope="class")
    def merger(self):
        return LimexModelMerger(ALL_PROFILES)

    def test_merged_has_all_categories(self, merger):
        expected = {
            "programming", "writing", "gaming", "video_image", "multimedia",
            "github", "files", "ai_ml", "devops", "security",
            "ecosystem", "unique_features",
        }
        assert set(merger.merged["skills_by_category"].keys()) == expected

    def test_payment_skills_stripped(self, merger):
        """No payment skill should appear in any merged category."""
        for cat, skills in merger.merged["skills_by_category"].items():
            for skill in skills:
                assert not _is_payment_skill(skill), (
                    f"Payment skill leaked into category '{cat}': {skill}"
                )

    def test_stripped_log_non_empty(self, merger):
        assert len(merger.merged["payment_skills_removed"]) > 0

    def test_merged_skill_count_reasonable(self, merger):
        total = sum(len(v) for v in merger.merged["skills_by_category"].values())
        assert total >= 200, f"Expected 200+ merged skills, got {total}"

    def test_no_duplicate_skills_within_category(self, merger):
        for cat, skills in merger.merged["skills_by_category"].items():
            assert len(skills) == len(set(skills)), (
                f"Duplicate skills found in category '{cat}'"
            )

    def test_source_models_listed(self, merger):
        sources = merger.merged["source_models"]
        assert "Kimi (v1)" in sources
        assert "Kimi 2" in sources
        assert "Kimi 2.5" in sources

    def test_context_window_is_max(self, merger):
        max_ctx = max(p["context_window"] for p in ALL_PROFILES)
        assert merger.merged["context_window"] == max_ctx

    def test_languages_are_sorted_and_unique(self, merger):
        langs = merger.merged["supported_languages"]
        assert langs == sorted(set(langs))

    def test_v1_strip_payment_false(self):
        v1 = next(p for p in ALL_PROFILES if p["model_id"] == "kimi-v1")
        assert v1["strip_payment"] is False

    def test_v2_strip_payment_true(self):
        v2 = next(p for p in ALL_PROFILES if p["model_id"] == "kimi-v2")
        assert v2["strip_payment"] is True

    def test_v25_strip_payment_true(self):
        v25 = next(p for p in ALL_PROFILES if p["model_id"] == "kimi-v2.5")
        assert v25["strip_payment"] is True


# ---------------------------------------------------------------------------
# Modelfile generation
# ---------------------------------------------------------------------------

class TestModelfileGeneration:
    @pytest.fixture(scope="class")
    def merger(self):
        return LimexModelMerger(ALL_PROFILES)

    def _write_to_temp(self, merger, variant: str) -> str:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".modelfile", delete=False
        ) as f:
            path = f.name
        if variant == "32b":
            merger.generate_modelfile_32b(path)
        else:
            merger.generate_modelfile_16b(path)
        return path

    def test_32b_modelfile_has_from(self, merger):
        path = self._write_to_temp(merger, "32b")
        content = Path(path).read_text()
        assert "FROM qwen2.5-coder:32b" in content

    def test_16b_modelfile_has_from(self, merger):
        path = self._write_to_temp(merger, "16b")
        content = Path(path).read_text()
        assert "FROM qwen2.5-coder:14b" in content

    def test_modelfile_has_system_block(self, merger):
        path = self._write_to_temp(merger, "16b")
        content = Path(path).read_text()
        assert 'SYSTEM """' in content

    def test_modelfile_has_temperature(self, merger):
        path = self._write_to_temp(merger, "16b")
        content = Path(path).read_text()
        assert "PARAMETER temperature" in content

    def test_modelfile_has_no_payment_skills(self, merger):
        for variant in ("32b", "16b"):
            path = self._write_to_temp(merger, variant)
            content = Path(path).read_text().lower()
            payment_phrases = [
                "cpm analysis", "rpm tracking", "revenue estimate",
                "sponsorship value", "super chat tracking",
                "membership insights", "merchandise click",
                "ad type performance",
            ]
            for phrase in payment_phrases:
                assert phrase not in content, (
                    f"Payment phrase '{phrase}' found in {variant} Modelfile"
                )

    def test_32b_ctx_le_max(self, merger):
        path = self._write_to_temp(merger, "32b")
        content = Path(path).read_text()
        for line in content.splitlines():
            if "num_ctx" in line:
                ctx = int(line.split()[-1])
                assert ctx <= merger.MAX_CTX_32B
                break

    def test_16b_ctx_le_max(self, merger):
        path = self._write_to_temp(merger, "16b")
        content = Path(path).read_text()
        for line in content.splitlines():
            if "num_ctx" in line:
                ctx = int(line.split()[-1])
                assert ctx <= merger.MAX_CTX_16B
                break


# ---------------------------------------------------------------------------
# limex config
# ---------------------------------------------------------------------------

class TestLimexConfig:
    @pytest.fixture(scope="class")
    def config(self):
        merger = LimexModelMerger(ALL_PROFILES)
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            path = f.name
        merger.generate_limex_config(path)
        return json.loads(Path(path).read_text())

    def test_has_limex_version(self, config):
        assert "limex_version" in config

    def test_has_both_variants(self, config):
        assert "kimi-free-32b" in config["variants"]
        assert "kimi-free-16b" in config["variants"]

    def test_32b_ram_target(self, config):
        assert config["variants"]["kimi-free-32b"]["ram_target_gb"] == 32

    def test_16b_ram_target(self, config):
        assert config["variants"]["kimi-free-16b"]["ram_target_gb"] == 16

    def test_source_profiles_present(self, config):
        assert "kimi-v1" in config["source_profiles"]
        assert "kimi-v2" in config["source_profiles"]
        assert "kimi-v2.5" in config["source_profiles"]

    def test_payment_skills_removed_listed(self, config):
        removed = config["merged_model"]["payment_skills_removed"]
        assert isinstance(removed, list)
        assert len(removed) > 0


# ---------------------------------------------------------------------------
# Training data generation
# ---------------------------------------------------------------------------

class TestTrainingDataGeneration:
    @pytest.fixture(scope="class")
    def records(self):
        merger = LimexModelMerger(ALL_PROFILES)
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".jsonl", delete=False
        ) as f:
            path = f.name
        merger.generate_training_data(path)
        return [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]

    def test_has_many_examples(self, records):
        assert len(records) >= 400, f"Expected 400+ examples, got {len(records)}"

    def test_all_records_have_required_keys(self, records):
        for i, r in enumerate(records):
            assert "instruction" in r, f"Record {i} missing 'instruction'"
            assert "input" in r, f"Record {i} missing 'input'"
            assert "output" in r, f"Record {i} missing 'output'"

    def test_no_payment_skills_leaked(self, records):
        payment_phrases = [
            "cpm analysis", "rpm tracking", "revenue estimate",
            "ad type performance", "sponsorship value",
            "super chat tracking", "membership insights",
            "merchandise click",
        ]
        for r in records:
            combined = (r["instruction"] + r["output"]).lower()
            # Allow refusal responses that explicitly say "intentionally removed"
            if "intentionally removed" in combined or "permanently payment-free" in combined:
                continue
            for phrase in payment_phrases:
                assert phrase not in combined, (
                    f"Payment phrase '{phrase}' found in training record:\n"
                    f"  instruction: {r['instruction'][:80]}"
                )

    def test_has_hello_world_examples(self, records):
        hw = [r for r in records if "hello-world" in r["instruction"].lower()]
        assert len(hw) >= 20, f"Expected 20+ hello-world examples, got {len(hw)}"

    def test_has_refusal_examples(self, records):
        refusals = [r for r in records
                    if "permanently payment-free" in r["output"].lower()]
        assert len(refusals) > 0

    def test_has_rich_coding_examples(self, records):
        rich = [r for r in records
                if "```python" in r["output"] or "```rust" in r["output"]
                or "```yaml" in r["output"]]
        assert len(rich) >= 3, f"Expected 3+ rich code examples, got {len(rich)}"

    def test_no_empty_outputs(self, records):
        for i, r in enumerate(records):
            assert r["output"].strip(), f"Record {i} has empty output"


# ---------------------------------------------------------------------------
# Hello-world snippets
# ---------------------------------------------------------------------------

class TestHelloWorldSnippets:
    @pytest.mark.parametrize("lang", [
        "python", "javascript", "typescript", "rust", "go",
        "java", "bash", "csharp", "kotlin", "swift",
    ])
    def test_snippet_contains_hello(self, lang):
        result = _hello_world_snippet(lang)
        assert "Hello" in result or "hello" in result.lower()

    def test_snippet_has_code_fence(self):
        result = _hello_world_snippet("python")
        assert "```python" in result

    def test_unknown_lang_returns_fallback(self):
        result = _hello_world_snippet("brainfuck")
        assert "brainfuck" in result.lower() or "Hello" in result


# ---------------------------------------------------------------------------
# Entry-point smoke test
# ---------------------------------------------------------------------------

class TestMainEntryPoint:
    def test_main_runs_without_error(self, tmp_path, monkeypatch):
        """Running main() with --variant all should exit 0 and create artefacts."""
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(sys, "argv", ["kimi_ollama_merger.py", "--variant", "all"])
        from kimi_ollama_merger import main
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0
        assert (tmp_path / "limex_config.json").exists()
        assert (tmp_path / "kimi_training_data.jsonl").exists()
        assert (tmp_path / "Modelfile.kimi-free-32b").exists()
        assert (tmp_path / "Modelfile.kimi-free-16b").exists()
