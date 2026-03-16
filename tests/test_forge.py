"""
Tests for forge_implementation.py and build_system.py

  - ForgeDocumentLoader — document loading, skill counts, export
  - ForgeSystemPrompt   — system prompt generation, vLLM config
  - ForgeAI             — initialization, stats, list_capabilities
  - ForgeBuilder        — setup, build steps, distribution creation
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Dict
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from forge_implementation import ForgeDocumentLoader, ForgeSystemPrompt, ForgeAI
from build_system import ForgeBuilder


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).parent.parent
_DOCS_DIR = _REPO_ROOT / "docs"


def _make_docs_dir(tmp_path: Path, files: Dict[str, str]) -> Path:
    """Create a temporary docs directory with the given filename → content map."""
    docs = tmp_path / "docs"
    docs.mkdir()
    for name, content in files.items():
        (docs / name).write_text(content, encoding="utf-8")
    return docs


# ---------------------------------------------------------------------------
# ForgeDocumentLoader
# ---------------------------------------------------------------------------

class TestForgeDocumentLoader:
    def test_load_all_documents_returns_dict(self, tmp_path):
        docs = _make_docs_dir(tmp_path, {"guide.md": "# Guide\n\n✅ skill one"})
        loader = ForgeDocumentLoader(str(docs))
        result = loader.load_all_documents()
        assert isinstance(result, dict)
        assert "guide.md" in result

    def test_load_multiple_docs(self, tmp_path):
        docs = _make_docs_dir(tmp_path, {
            "a.md": "# A",
            "b.md": "# B",
            "c.md": "# C",
        })
        loader = ForgeDocumentLoader(str(docs))
        loader.load_all_documents()
        assert len(loader.list_documents()) >= 3

    def test_get_document_returns_content(self, tmp_path):
        docs = _make_docs_dir(tmp_path, {"test.md": "Hello World"})
        loader = ForgeDocumentLoader(str(docs))
        loader.load_all_documents()
        content = loader.get_document("test.md")
        assert content == "Hello World"

    def test_get_document_missing_returns_none(self, tmp_path):
        docs = _make_docs_dir(tmp_path, {})
        loader = ForgeDocumentLoader(str(docs))
        loader.load_all_documents()
        assert loader.get_document("nonexistent.md") is None

    def test_get_all_content_contains_filenames(self, tmp_path):
        docs = _make_docs_dir(tmp_path, {
            "alpha.md": "# Alpha content",
            "beta.md":  "# Beta content",
        })
        loader = ForgeDocumentLoader(str(docs))
        loader.load_all_documents()
        combined = loader.get_all_content()
        assert "alpha.md" in combined
        assert "beta.md" in combined

    def test_list_documents_is_list(self, tmp_path):
        docs = _make_docs_dir(tmp_path, {"x.md": "x"})
        loader = ForgeDocumentLoader(str(docs))
        loader.load_all_documents()
        assert isinstance(loader.list_documents(), list)

    def test_empty_docs_dir(self, tmp_path):
        docs = tmp_path / "empty_docs"
        docs.mkdir()
        loader = ForgeDocumentLoader(str(docs))
        result = loader.load_all_documents()
        assert isinstance(result, dict)

    def test_skill_icons_counted_in_summary(self, tmp_path):
        content = "✅ skill1\n✅ skill2\n🔄 skill3\n🌱 skill4\nplain line"
        docs = _make_docs_dir(tmp_path, {"ALL_SKILLS.md": content})
        loader = ForgeDocumentLoader(str(docs))
        loader.load_all_documents()
        summary = loader.get_skills_summary()
        assert summary["total_skills"] == 4

    def test_get_skills_summary_missing_file(self, tmp_path):
        docs = _make_docs_dir(tmp_path, {"other.md": "no skills"})
        loader = ForgeDocumentLoader(str(docs))
        loader.load_all_documents()
        result = loader.get_skills_summary()
        assert "error" in result

    def test_export_for_model_creates_json_file(self, tmp_path):
        docs = _make_docs_dir(tmp_path, {"guide.md": "# Hello"})
        loader = ForgeDocumentLoader(str(docs))
        loader.load_all_documents()

        out_file = str(tmp_path / "kb.json")
        loader.export_for_model(out_file)

        assert Path(out_file).exists()
        data = json.loads(Path(out_file).read_text(encoding="utf-8"))
        assert "documents" in data
        assert "combined_content" in data

    def test_export_for_model_contains_correct_total(self, tmp_path):
        docs = _make_docs_dir(tmp_path, {
            "a.md": "AAA",
            "b.md": "BBB",
        })
        loader = ForgeDocumentLoader(str(docs))
        loader.load_all_documents()

        out_file = str(tmp_path / "kb.json")
        loader.export_for_model(out_file)
        data = json.loads(Path(out_file).read_text(encoding="utf-8"))
        assert data["total_documents"] >= 2

    def test_all_content_grows_after_load(self, tmp_path):
        docs = _make_docs_dir(tmp_path, {"ref.md": "X" * 500})
        loader = ForgeDocumentLoader(str(docs))
        before = len(loader.get_all_content())
        loader.load_all_documents()
        after = len(loader.get_all_content())
        assert after > before

    def test_load_real_docs_dir_if_exists(self):
        """Smoke test: if docs/ exists in the repo, loading should succeed."""
        if not _DOCS_DIR.exists():
            pytest.skip("docs/ directory not present")
        loader = ForgeDocumentLoader(str(_DOCS_DIR))
        docs = loader.load_all_documents()
        assert len(docs) > 0


# ---------------------------------------------------------------------------
# ForgeSystemPrompt
# ---------------------------------------------------------------------------

class TestForgeSystemPrompt:
    def _make_prompt_gen(self, tmp_path: Path) -> ForgeSystemPrompt:
        docs = _make_docs_dir(tmp_path, {
            "SKILLS.md": "## Programming\n✅ Python\n✅ Rust",
            "GUIDE.md":  "# Guide\nHow to use THE FORGE",
        })
        loader = ForgeDocumentLoader(str(docs))
        loader.load_all_documents()
        return ForgeSystemPrompt(loader)

    def test_generate_system_prompt_returns_string(self, tmp_path):
        gen = self._make_prompt_gen(tmp_path)
        result = gen.generate_system_prompt()
        assert isinstance(result, str)
        assert len(result) > 100

    def test_system_prompt_contains_kimi(self, tmp_path):
        gen = self._make_prompt_gen(tmp_path)
        prompt = gen.generate_system_prompt()
        assert "Kimi" in prompt or "FORGE" in prompt

    def test_system_prompt_contains_doc_headers(self, tmp_path):
        gen = self._make_prompt_gen(tmp_path)
        prompt = gen.generate_system_prompt()
        # The prompt should reference at least one of the loaded doc names
        assert "SKILLS" in prompt or "GUIDE" in prompt

    def test_generate_for_vllm_returns_dict(self, tmp_path):
        gen = self._make_prompt_gen(tmp_path)
        config = gen.generate_for_vllm()
        assert isinstance(config, dict)

    def test_generate_for_vllm_required_keys(self, tmp_path):
        gen = self._make_prompt_gen(tmp_path)
        config = gen.generate_for_vllm()
        for key in ("model_name", "system_prompt", "temperature",
                    "max_tokens", "top_p"):
            assert key in config, f"missing key: {key}"

    def test_generate_for_vllm_temperature_range(self, tmp_path):
        gen = self._make_prompt_gen(tmp_path)
        config = gen.generate_for_vllm()
        assert 0.0 <= config["temperature"] <= 1.0

    def test_generate_for_vllm_max_tokens_positive(self, tmp_path):
        gen = self._make_prompt_gen(tmp_path)
        config = gen.generate_for_vllm()
        assert config["max_tokens"] > 0

    def test_generate_for_vllm_system_prompt_non_empty(self, tmp_path):
        gen = self._make_prompt_gen(tmp_path)
        config = gen.generate_for_vllm()
        assert config["system_prompt"]


# ---------------------------------------------------------------------------
# ForgeAI
# ---------------------------------------------------------------------------

class TestForgeAI:
    def _make_forge(self, tmp_path: Path) -> ForgeAI:
        docs = _make_docs_dir(tmp_path, {
            "ALL_SKILLS.md": "✅ skill1\n✅ skill2\n🔄 skill3",
            "README.md":     "# Forge AI\nIntroduction.",
        })
        forge = ForgeAI(str(docs))
        forge.initialize()
        return forge

    def test_initialize_sets_loaded(self, tmp_path):
        forge = self._make_forge(tmp_path)
        assert forge.loaded is True

    def test_initialize_creates_prompt_generator(self, tmp_path):
        forge = self._make_forge(tmp_path)
        assert forge.prompt_generator is not None

    def test_get_system_prompt_returns_string(self, tmp_path):
        forge = self._make_forge(tmp_path)
        prompt = forge.get_system_prompt()
        assert isinstance(prompt, str)
        assert len(prompt) > 50

    def test_initialize_lazy_on_get_system_prompt(self, tmp_path):
        docs = _make_docs_dir(tmp_path, {"guide.md": "# Guide"})
        forge = ForgeAI(str(docs))
        assert forge.loaded is False
        _ = forge.get_system_prompt()
        assert forge.loaded is True

    def test_get_documentation_stats_keys(self, tmp_path):
        forge = self._make_forge(tmp_path)
        stats = forge.get_documentation_stats()
        for key in ("total_documents", "total_characters", "total_words",
                    "documents"):
            assert key in stats

    def test_get_documentation_stats_positive_chars(self, tmp_path):
        forge = self._make_forge(tmp_path)
        stats = forge.get_documentation_stats()
        assert stats["total_characters"] > 0

    def test_get_documentation_stats_per_doc(self, tmp_path):
        forge = self._make_forge(tmp_path)
        stats = forge.get_documentation_stats()
        for doc_stat in stats["documents"].values():
            for key in ("characters", "lines", "words"):
                assert key in doc_stat

    def test_export_knowledge_base_creates_file(self, tmp_path):
        forge = self._make_forge(tmp_path)
        out = str(tmp_path / "kb.json")
        forge.export_knowledge_base(out)
        assert Path(out).exists()
        data = json.loads(Path(out).read_text(encoding="utf-8"))
        assert "documents" in data

    def test_export_vllm_config_creates_file(self, tmp_path):
        forge = self._make_forge(tmp_path)
        out = str(tmp_path / "vllm_config.json")
        forge.export_vllm_config(out)
        assert Path(out).exists()
        data = json.loads(Path(out).read_text(encoding="utf-8"))
        assert "system_prompt" in data

    def test_export_vllm_lazy_init(self, tmp_path):
        docs = _make_docs_dir(tmp_path, {"g.md": "# G"})
        forge = ForgeAI(str(docs))
        out = str(tmp_path / "v.json")
        forge.export_vllm_config(out)
        assert forge.loaded is True

    def test_list_capabilities_does_not_crash(self, tmp_path, capsys):
        forge = self._make_forge(tmp_path)
        forge.list_capabilities()  # should not raise
        captured = capsys.readouterr()
        assert "CAPABILITIES" in captured.out or "SKILLS" in captured.out


# ---------------------------------------------------------------------------
# ForgeBuilder
# ---------------------------------------------------------------------------

class TestForgeBuilder:
    def test_setup_environment_creates_dirs(self, tmp_path):
        builder = ForgeBuilder()
        # Point build/dist to tmp dirs
        builder.build_dir = tmp_path / "build"
        builder.dist_dir  = tmp_path / "dist"
        builder.setup_environment()
        assert builder.build_dir.exists()
        assert builder.dist_dir.exists()

    def test_build_core_does_not_raise(self, capsys):
        builder = ForgeBuilder()
        builder.build_core()   # just checks files exist — should never raise

    def test_build_video_editor_does_not_raise(self):
        ForgeBuilder().build_video_editor()

    def test_build_linux_os_does_not_raise(self):
        ForgeBuilder().build_linux_os()

    def test_build_documentation_does_not_raise(self):
        ForgeBuilder().build_documentation()

    def test_create_distribution_writes_zip(self, tmp_path):
        builder = ForgeBuilder()
        builder.build_dir = tmp_path / "build"
        builder.dist_dir  = tmp_path / "dist"
        builder.build_dir.mkdir()
        builder.dist_dir.mkdir()

        zip_path = builder.create_distribution()
        assert zip_path.exists()
        assert zip_path.suffix == ".zip"
        # Verify it is a valid ZIP
        assert zipfile.is_zipfile(zip_path)

    def test_create_distribution_zip_contains_python_files(self, tmp_path):
        builder = ForgeBuilder()
        builder.build_dir = tmp_path / "build"
        builder.dist_dir  = tmp_path / "dist"
        builder.build_dir.mkdir()
        builder.dist_dir.mkdir()

        zip_path = builder.create_distribution()
        with zipfile.ZipFile(zip_path) as zf:
            names = zf.namelist()
        assert any(n.endswith(".py") for n in names)

    def test_generate_checksums_creates_json(self, tmp_path):
        builder = ForgeBuilder()
        builder.build_dir = tmp_path / "build"
        builder.dist_dir  = tmp_path / "dist"
        builder.build_dir.mkdir()
        builder.dist_dir.mkdir()

        # Create a dummy zip so checksums has something to checksum
        dummy_zip = builder.dist_dir / "test.zip"
        with zipfile.ZipFile(dummy_zip, "w") as zf:
            zf.writestr("a.txt", "hello")

        builder.generate_checksums()

        checksum_file = builder.dist_dir / "checksums.json"
        assert checksum_file.exists()
        data = json.loads(checksum_file.read_text(encoding="utf-8"))
        assert "test.zip" in data

    def test_generate_checksums_has_md5(self, tmp_path):
        builder = ForgeBuilder()
        builder.build_dir = tmp_path / "build"
        builder.dist_dir  = tmp_path / "dist"
        builder.build_dir.mkdir()
        builder.dist_dir.mkdir()

        dummy_zip = builder.dist_dir / "pkg.zip"
        with zipfile.ZipFile(dummy_zip, "w") as zf:
            zf.writestr("f.txt", "data")

        builder.generate_checksums()
        data = json.loads((builder.dist_dir / "checksums.json").read_text())
        assert "md5" in data["pkg.zip"]
        assert len(data["pkg.zip"]["md5"]) == 32  # MD5 hex digest

    def test_build_all_returns_true(self, tmp_path):
        """build_all() should succeed (all steps are non-failing in the real impl)."""
        builder = ForgeBuilder()
        # Keep build/dist inside tmp to avoid polluting the repo
        builder.build_dir = tmp_path / "build"
        builder.dist_dir  = tmp_path / "dist"
        result = builder.build_all()
        assert result is True
