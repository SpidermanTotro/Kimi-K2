"""
Tests for the NullClaw local AI programming agent.
"""
from __future__ import annotations

import json
import os
import sys
import subprocess
import tempfile
from pathlib import Path
from typing import Optional
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

import nullclaw.config          as nc_cfg
import nullclaw.error_parser    as nc_ep
import nullclaw.build_runner    as nc_br
import nullclaw.context_collector as nc_cc
import nullclaw.patch_tools     as nc_pt
import nullclaw.project_tools   as nc_proj
import nullclaw.git_tools       as nc_git
import nullclaw.agents          as nc_ag
import nullclaw.repair_loop     as nc_rl
from nullclaw import NullClawConfig, load_config, BuildError, parse_first_error


# ===========================================================================
# Fixtures
# ===========================================================================

@pytest.fixture
def work_dir(tmp_path):
    """Set up a temporary working directory with log/report/patch dirs."""
    cfg = NullClawConfig(
        log_dir=str(tmp_path / "logs"),
        report_dir=str(tmp_path / "reports"),
        patch_dir=str(tmp_path / "patches"),
        build_timeout_sec=10,
    )
    cfg.ensure_dirs()
    return tmp_path, cfg


@pytest.fixture
def sample_ts_log() -> str:
    return (
        "src/ui/AppContainer.tsx:1439:12 - error TS2304: "
        "Cannot find name 'useBackgroundShellManager'.\n"
        "src/ui/Toolbar.tsx:55:3 - error TS2345: "
        "Argument of type 'string' is not assignable to parameter of type 'number'.\n"
    )


@pytest.fixture
def sample_rust_log() -> str:
    return (
        "error[E0425]: cannot find value `my_var` in this scope\n"
        "  --> src/main.rs:42:5\n"
        "   |\n"
        "42 |     println!(\"{}\", my_var);\n"
        "   |                    ^^^^^^ not found in this scope\n"
    )


@pytest.fixture
def sample_python_log() -> str:
    return (
        'Traceback (most recent call last):\n'
        '  File "script.py", line 15, in <module>\n'
        '    result = foo()\n'
        'NameError: name \'foo\' is not defined\n'
    )


@pytest.fixture
def sample_go_log() -> str:
    return "./main.go:10:5: undefined: myFunction\n"


@pytest.fixture
def sample_c_log() -> str:
    return "src/main.c:42:8: error: 'x' undeclared (first use in this function)\n"


# ===========================================================================
# Config tests
# ===========================================================================

class TestConfig:
    def test_defaults(self):
        cfg = NullClawConfig()
        assert cfg.ollama_host == "http://localhost:11434"
        assert cfg.max_repair_passes == 5
        assert cfg.context_radius == 25
        assert cfg.autonomy_level == "supervised"

    def test_load_config_no_file(self, monkeypatch, tmp_path):
        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv("NULLCLAW_MODEL", raising=False)
        monkeypatch.delenv("OLLAMA_HOST", raising=False)
        cfg = load_config()
        assert isinstance(cfg, NullClawConfig)

    def test_load_config_json(self, tmp_path):
        config_file = tmp_path / "nullclaw_config.json"
        config_file.write_text(json.dumps({
            "models": {
                "base_url": "http://localhost:9999",
                "primary":  "codellama:latest",
                "planner":  "llama3:latest",
            },
            "repair": {"max_passes": 3},
        }))
        cfg = load_config(str(config_file))
        assert cfg.ollama_host == "http://localhost:9999"
        assert cfg.primary_model == "codellama:latest"
        assert cfg.planner_model == "llama3:latest"
        assert cfg.max_repair_passes == 3

    def test_env_override(self, monkeypatch):
        monkeypatch.setenv("NULLCLAW_MODEL", "my-custom-model")
        monkeypatch.setenv("OLLAMA_HOST",    "http://192.168.1.100:11434")
        cfg = load_config()
        assert cfg.primary_model == "my-custom-model"
        assert cfg.ollama_host   == "http://192.168.1.100:11434"

    def test_ensure_dirs(self, tmp_path):
        cfg = NullClawConfig(
            log_dir=str(tmp_path / "logs"),
            report_dir=str(tmp_path / "reports"),
            patch_dir=str(tmp_path / "patches"),
        )
        cfg.ensure_dirs()
        assert (tmp_path / "logs").is_dir()
        assert (tmp_path / "reports").is_dir()
        assert (tmp_path / "patches").is_dir()

    def test_ollama_available_false(self):
        # Port 1 is always refused
        cfg = NullClawConfig(ollama_host="http://127.0.0.1:1")
        assert nc_cfg.ollama_available(cfg) is False


# ===========================================================================
# Error parser tests
# ===========================================================================

class TestErrorParser:

    # ── TypeScript ────────────────────────────────────────────────

    def test_parse_ts_first_error(self, sample_ts_log):
        err = parse_first_error(sample_ts_log)
        assert err is not None
        assert err.language    == "typescript"
        assert err.file_path   == "src/ui/AppContainer.tsx"
        assert err.line        == 1439
        assert err.column      == 12
        assert err.code        == "TS2304"
        assert "useBackgroundShellManager" in err.message

    def test_parse_ts_all_errors(self, sample_ts_log):
        errors = nc_ep.parse_all_errors(sample_ts_log)
        assert len(errors) == 2
        assert errors[1].line == 55

    def test_parse_esbuild(self):
        log = "src/App.tsx:10:3: error: Cannot find name 'useState'\n"
        err = parse_first_error(log)
        assert err is not None
        assert err.file_path == "src/App.tsx"
        assert err.line      == 10
        assert err.column    == 3
        assert err.code      is None
        assert err.language  == "typescript"

    # ── Rust ──────────────────────────────────────────────────────

    def test_parse_rust_error(self, sample_rust_log):
        err = parse_first_error(sample_rust_log)
        assert err is not None
        assert err.language  == "rust"
        assert err.file_path == "src/main.rs"
        assert err.line      == 42
        assert err.column    == 5
        assert err.code      == "E0425"
        assert "my_var" in err.message

    def test_parse_rust_no_code(self):
        log = "error: aborting due to previous error\n"
        err = parse_first_error(log)
        # "aborting due to" should NOT produce an error
        assert err is None

    # ── Python ────────────────────────────────────────────────────

    def test_parse_python_error(self, sample_python_log):
        err = parse_first_error(sample_python_log)
        assert err is not None
        assert err.language  == "python"
        assert err.file_path == "script.py"
        assert err.line      == 15
        assert err.code      == "NameError"
        assert "foo" in err.message

    def test_parse_python_syntax_error(self):
        log = (
            '  File "app.py", line 3\n'
            '    def foo(\n'
            '           ^\n'
            'SyntaxError: unexpected EOF while parsing\n'
        )
        err = parse_first_error(log)
        assert err is not None
        assert err.code == "SyntaxError"
        assert err.line == 3

    def test_parse_python_import_error(self):
        log = (
            'Traceback (most recent call last):\n'
            '  File "run.py", line 1, in <module>\n'
            '    import requests\n'
            'ModuleNotFoundError: No module named \'requests\'\n'
        )
        err = parse_first_error(log)
        assert err is not None
        assert err.code == "ModuleNotFoundError"

    # ── Go ────────────────────────────────────────────────────────

    def test_parse_go_error(self, sample_go_log):
        err = parse_first_error(sample_go_log)
        assert err is not None
        assert err.language  == "go"
        assert err.file_path == "./main.go"
        assert err.line      == 10

    # ── C/C++ ────────────────────────────────────────────────────

    def test_parse_c_error(self, sample_c_log):
        err = parse_first_error(sample_c_log)
        assert err is not None
        assert err.language  == "c"
        assert err.file_path == "src/main.c"
        assert err.line      == 42
        assert err.column    == 8

    # ── npm ───────────────────────────────────────────────────────

    def test_parse_npm_error(self):
        log = "npm ERR! code ENOENT\nnpm ERR! syscall open\n"
        err = parse_first_error(log)
        assert err is not None
        assert err.language == "javascript"
        assert err.code == "npm"

    # ── Edge cases ────────────────────────────────────────────────

    def test_parse_no_error(self):
        assert parse_first_error("Build succeeded\n") is None
        assert parse_first_error("") is None

    def test_parse_limit(self, sample_ts_log):
        errors = nc_ep.parse_all_errors(sample_ts_log, limit=1)
        assert len(errors) == 1

    def test_build_error_str(self):
        err = BuildError(
            file_path="foo.ts", line=1, column=1,
            code="TS2304", message="not found",
        )
        s = str(err)
        assert "foo.ts" in s
        assert "TS2304" in s

    def test_build_error_to_dict(self):
        err = BuildError("a.py", 10, 1, "NameError", "msg", "python")
        d = err.to_dict()
        assert d["file_path"] == "a.py"
        assert d["language"]  == "python"

    def test_load_log_file(self, tmp_path):
        p = tmp_path / "test.log"
        p.write_text("hello\nworld\n")
        assert nc_ep.load_log_file(str(p)) == "hello\nworld\n"


# ===========================================================================
# Build runner tests
# ===========================================================================

class TestBuildRunner:

    def test_successful_build(self, work_dir):
        tmp_path, cfg = work_dir
        result = nc_br.run_build(".", "echo hello", cfg, verbose=False)
        assert result.success
        assert result.returncode == 0
        assert result.log_path.exists()
        assert "hello" in result.log_text

    def test_failed_build(self, work_dir):
        tmp_path, cfg = work_dir
        result = nc_br.run_build(".", "exit 1", cfg, verbose=False)
        assert not result.success
        assert result.returncode == 1

    def test_log_file_created(self, work_dir):
        tmp_path, cfg = work_dir
        result = nc_br.run_build(".", "echo test", cfg, verbose=False)
        assert result.log_path.exists()
        assert result.log_path.suffix == ".log"

    def test_log_file_naming(self, work_dir):
        tmp_path, cfg = work_dir
        result = nc_br.run_build(".", "echo a", cfg, verbose=False)
        assert result.log_path.name.startswith("build_")

    def test_build_repr(self, work_dir):
        tmp_path, cfg = work_dir
        result = nc_br.run_build(".", "echo x", cfg, verbose=False)
        assert "PASSED" in repr(result)

    def test_latest_log_found(self, work_dir):
        tmp_path, cfg = work_dir
        nc_br.run_build(".", "echo a", cfg, verbose=False)
        nc_br.run_build(".", "echo b", cfg, verbose=False)
        p = nc_br.latest_log(cfg.log_dir)
        assert p is not None and p.exists()

    def test_latest_log_none_when_empty(self, tmp_path):
        p = nc_br.latest_log(str(tmp_path / "no_logs"))
        assert p is None


# ===========================================================================
# Context collector tests
# ===========================================================================

class TestContextCollector:

    def test_basic_context(self, tmp_path):
        src = tmp_path / "foo.py"
        src.write_text("\n".join(f"line {i}" for i in range(1, 101)))
        ctx = nc_cc.collect_context(str(src), 50, radius=5)
        assert ">>>" in ctx
        assert "50" in ctx
        assert "line 50" in ctx

    def test_marker_on_error_line(self, tmp_path):
        src = tmp_path / "foo.py"
        src.write_text("a\nb\nc\n")
        ctx = nc_cc.collect_context(str(src), 2, radius=1)
        lines = ctx.splitlines()
        arrow_lines = [l for l in lines if l.startswith(">>>")]
        assert len(arrow_lines) == 1
        assert "b" in arrow_lines[0]

    def test_missing_file(self):
        ctx = nc_cc.collect_context("/nonexistent/file.ts", 10)
        assert "not found" in ctx.lower()

    def test_radius_clamped_at_start(self, tmp_path):
        src = tmp_path / "x.py"
        src.write_text("only\nthree\nlines\n")
        ctx = nc_cc.collect_context(str(src), 1, radius=50)
        assert "only" in ctx

    def test_radius_clamped_at_end(self, tmp_path):
        src = tmp_path / "x.py"
        src.write_text("a\nb\nc\n")
        ctx = nc_cc.collect_context(str(src), 3, radius=50)
        assert "c" in ctx

    def test_includes_file_header(self, tmp_path):
        src = tmp_path / "x.py"
        src.write_text("x = 1\n")
        ctx = nc_cc.collect_context(str(src), 1)
        assert "FILE" in ctx


# ===========================================================================
# Patch tools tests
# ===========================================================================

class TestPatchTools:

    def test_extract_fenced_diff(self):
        reply = "Here is the fix:\n```diff\n--- a/f.ts\n+++ b/f.ts\n@@ -1 +1 @@\n-bad\n+good\n```\n"
        patch = nc_pt.extract_patch(reply)
        assert patch is not None
        assert "--- a/f.ts" in patch
        assert "-bad" in patch

    def test_extract_no_patch(self):
        assert nc_pt.extract_patch("This looks fine to me.") is None

    def test_extract_bare_diff(self):
        reply = (
            "The fix:\n"
            "--- a/main.go\n"
            "+++ b/main.go\n"
            "@@ -1,3 +1,3 @@\n"
            " package main\n"
            "-func bad() {}\n"
            "+func good() {}\n"
        )
        patch = nc_pt.extract_patch(reply)
        assert patch is not None
        assert "func good" in patch

    def test_save_patch(self, tmp_path):
        path = nc_pt.save_patch("--- a\n+++ b\n", patch_dir=str(tmp_path))
        assert path.exists()
        assert "repair_" in path.name

    def test_save_patch_note(self, tmp_path):
        path = nc_pt.save_patch_note("This is a note.", patch_dir=str(tmp_path))
        assert path.exists()
        assert path.suffix == ".md"
        assert "This is a note." in path.read_text()

    def test_backup_file(self, tmp_path):
        src = tmp_path / "source.ts"
        src.write_text("original content")
        bak = nc_pt.backup_file(str(src))
        assert bak.exists()
        assert bak.read_text() == "original content"
        assert bak.suffix == ".bak"

    def test_apply_patch_no_git(self, tmp_path):
        result = nc_pt.apply_patch(str(tmp_path), "nonexistent.patch", verbose=False)
        assert not result.success

    def test_patch_result_bool(self, tmp_path):
        pr = nc_pt.PatchResult(True, "ok", tmp_path / "p.patch")
        assert bool(pr) is True
        pr2 = nc_pt.PatchResult(False, "fail", tmp_path / "p.patch")
        assert bool(pr2) is False


# ===========================================================================
# Project tools tests
# ===========================================================================

class TestProjectTools:

    def test_index_project(self, tmp_path):
        (tmp_path / "a.ts").write_text("const x = 1;")
        (tmp_path / "b.py").write_text("x = 1")
        (tmp_path / "sub").mkdir()
        (tmp_path / "sub" / "c.rs").write_text("fn main() {}")
        idx = nc_proj.index_project(str(tmp_path), verbose=False)
        assert idx["file_count"] >= 3
        assert idx["source_count"] >= 3
        assert ".ts" in idx["ext_counts"] or ".py" in idx["ext_counts"]

    def test_search_code_pure_python(self, tmp_path):
        f = tmp_path / "app.ts"
        f.write_text("import { useState } from 'react';\nconst x = 1;")
        results = nc_proj.search_code("useState", str(tmp_path))
        assert any("useState" in r for r in results)

    def test_search_code_no_results(self, tmp_path):
        (tmp_path / "x.ts").write_text("const y = 2;")
        results = nc_proj.search_code("ZZZNOMATCH_XYZ", str(tmp_path))
        assert results == []

    def test_inventory_project(self, tmp_path):
        (tmp_path / "main.py").write_text("x = 1")
        (tmp_path / "main.rs").write_text("fn main() {}")
        inv = nc_proj.inventory_project(str(tmp_path))
        assert inv["total_files"] >= 2
        assert ".py" in inv["source_by_ext"] or ".rs" in inv["source_by_ext"]
        assert inv["total_size_mb"] >= 0

    def test_repo_map(self, tmp_path):
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.ts").write_text("")
        tree = nc_proj.repo_map(str(tmp_path), max_depth=2)
        assert "src" in tree
        assert "main.ts" in tree

    def test_search_code_case_insensitive(self, tmp_path):
        (tmp_path / "x.ts").write_text("const MyVar = 1;")
        results = nc_proj.search_code("myvar", str(tmp_path), case_insensitive=True)
        assert any("MyVar" in r for r in results)

    def test_skip_dirs(self, tmp_path):
        nm = tmp_path / "node_modules" / "lodash"
        nm.mkdir(parents=True)
        (nm / "lodash.js").write_text("const x = findMe;")
        results = nc_proj.search_code("findMe", str(tmp_path))
        # Should NOT find it inside node_modules
        assert not any("node_modules" in r for r in results)


# ===========================================================================
# Git tools tests (unit — no actual git required)
# ===========================================================================

class TestGitTools:

    def test_is_git_repo_true(self, tmp_path):
        # Initialize a git repo
        result = subprocess.run(
            ["git", "init"], cwd=str(tmp_path),
            capture_output=True, text=True
        )
        if result.returncode != 0:
            pytest.skip("git not available")
        assert nc_git.is_git_repo(str(tmp_path)) is True

    def test_is_git_repo_false(self, tmp_path):
        assert nc_git.is_git_repo(str(tmp_path)) is False

    def test_current_branch_no_repo(self, tmp_path):
        branch = nc_git.current_branch(str(tmp_path))
        assert branch is None

    def test_git_diff_no_changes(self, tmp_path):
        result = subprocess.run(
            ["git", "init"], cwd=str(tmp_path),
            capture_output=True, text=True
        )
        if result.returncode != 0:
            pytest.skip("git not available")
        diff = nc_git.git_diff(str(tmp_path))
        assert isinstance(diff, str)


# ===========================================================================
# Agents tests (mock Ollama)
# ===========================================================================

class TestAgents:

    def _mock_cfg(self) -> NullClawConfig:
        cfg = NullClawConfig()
        cfg.primary_model = "test-model"
        cfg.planner_model = "test-model"   # same → single-agent mode
        return cfg

    def test_single_agent_returns_result(self):
        cfg = self._mock_cfg()
        agents = nc_ag.NullClawAgents(cfg)

        err = BuildError("foo.ts", 1, 1, "TS2304", "Cannot find name 'x'", "typescript")
        ctx = "   1: const y = x;"

        with patch.object(agents.client, "ask", return_value="Fix: add x") as mock_ask:
            result = agents.run(err, ctx, verbose=False)

        assert result.best_reply() == "Fix: add x"
        assert mock_ask.called

    def test_multi_agent_pipeline(self):
        cfg = self._mock_cfg()
        cfg.planner_model = "planner-model"   # different → multi-agent
        agents = nc_ag.NullClawAgents(cfg)

        err = BuildError("foo.ts", 1, 1, "TS2304", "msg", "typescript")
        ctx = "ctx"

        responses = iter(["plan output", "diagnosis output", "patch output"])
        with patch.object(agents.client, "ask", side_effect=lambda *a, **kw: next(responses)):
            result = agents.run(err, ctx, verbose=False)

        assert result.plan      == "plan output"
        assert result.diagnosis == "diagnosis output"
        assert result.patch     == "patch output"

    def test_planner_failure_falls_back_to_single(self):
        cfg = self._mock_cfg()
        cfg.planner_model = "planner-model"
        agents = nc_ag.NullClawAgents(cfg)

        err = BuildError("f.py", 1, 1, "NameError", "msg", "python")
        ctx = "x"

        responses = [None, "single reply"]
        with patch.object(agents.client, "ask", side_effect=responses):
            result = agents.run(err, ctx, verbose=False)

        # Planner returned None → fell back to single reply
        assert result.best_reply() == "single reply"

    def test_agent_result_best_reply_order(self):
        r = nc_ag.AgentResult(plan="p", diagnosis="d", patch="x")
        assert r.best_reply() == "x"

        r2 = nc_ag.AgentResult(plan="p", diagnosis="d")
        assert r2.best_reply() == "d"

        r3 = nc_ag.AgentResult(plan="p")
        assert r3.best_reply() == "p"

        r4 = nc_ag.AgentResult()
        assert r4.best_reply() == ""

    def test_no_ai_returns_empty(self):
        cfg = self._mock_cfg()
        agents = nc_ag.NullClawAgents(cfg)

        err = BuildError("f.ts", 1, 1, "TS2304", "msg", "typescript")
        with patch.object(agents.client, "ask", return_value=None):
            result = agents.run(err, "ctx", verbose=False)

        assert result.best_reply() == ""


# ===========================================================================
# Repair loop (integration — no real build or Ollama)
# ===========================================================================

class TestRepairLoop:

    def test_loop_build_passes_immediately(self, tmp_path):
        cfg = NullClawConfig(
            log_dir=str(tmp_path / "logs"),
            report_dir=str(tmp_path / "reports"),
            patch_dir=str(tmp_path / "patches"),
            max_repair_passes=3,
            build_timeout_sec=5,
        )
        cfg.ensure_dirs()

        loop = nc_rl.RepairLoop(".", "echo build_ok", cfg=cfg)

        with patch.object(
            nc_rl.NullClawAgents, "run", return_value=nc_ag.AgentResult()
        ):
            passes = loop.run(verbose=False)

        assert len(passes) == 1
        assert passes[0].build_passed

    def test_loop_stops_on_error_no_ai(self, tmp_path):
        cfg = NullClawConfig(
            log_dir=str(tmp_path / "logs"),
            report_dir=str(tmp_path / "reports"),
            patch_dir=str(tmp_path / "patches"),
            max_repair_passes=2,
            build_timeout_sec=5,
        )
        cfg.ensure_dirs()

        loop = nc_rl.RepairLoop(".", "exit 1", cfg=cfg)

        with patch.object(
            nc_rl.NullClawAgents, "run", return_value=nc_ag.AgentResult()
        ):
            passes = loop.run(verbose=False)

        # With no AI reply and auto_apply=False we stop after 1 pass
        assert len(passes) >= 1
        assert not passes[0].build_passed

    def test_repair_pass_summary(self, tmp_path):
        cfg = NullClawConfig(
            log_dir=str(tmp_path / "logs"),
            report_dir=str(tmp_path / "reports"),
            patch_dir=str(tmp_path / "patches"),
            build_timeout_sec=5,
        )
        cfg.ensure_dirs()

        loop  = nc_rl.RepairLoop(".", "echo ok", cfg=cfg)
        passes = loop.run(verbose=False)
        s = passes[0].summary()
        assert "Pass 1" in s
        assert "✅" in s


# ===========================================================================
# Ollama client (mock network)
# ===========================================================================

class TestOllamaClient:

    def test_ask_rest_success(self):
        from nullclaw.ollama_client import OllamaClient
        cfg = NullClawConfig(ollama_host="http://localhost:11434")
        client = OllamaClient(cfg)

        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({"response": "test answer"}).encode()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__  = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_resp):
            result = client._ask_rest("hello", "test-model", verbose=False)

        assert result == "test answer"

    def test_ask_rest_connection_refused(self):
        from nullclaw.ollama_client import OllamaClient
        import urllib.error
        cfg = NullClawConfig(ollama_host="http://127.0.0.1:1")
        client = OllamaClient(cfg)

        with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("refused")):
            result = client._ask_rest("hello", "test-model", verbose=False)

        assert result is None

    def test_ask_subprocess_no_ollama(self):
        from nullclaw.ollama_client import OllamaClient
        client = OllamaClient()
        with patch("subprocess.run", side_effect=FileNotFoundError):
            result = client._ask_subprocess("hello", "model", verbose=False)
        assert result is None

    def test_ask_falls_through_to_none(self):
        from nullclaw.ollama_client import OllamaClient
        client = OllamaClient()
        with patch.object(client, "_ask_rest",       return_value=None), \
             patch.object(client, "_ask_subprocess",  return_value=None), \
             patch.object(client, "_ask_gemini_fallback", return_value=None):
            result = client.ask("hello", verbose=False)
        assert result is None


# ===========================================================================
# CLI tests
# ===========================================================================

class TestNullClawCLI:
    def _cli(self):
        from nullclaw_cli_import import NullClawCLI
        return NullClawCLI()

    def _run(self, args):
        # Import the CLI class from the top-level nullclaw.py
        sys.path.insert(0, str(Path(__file__).parent.parent))
        # Import from the module
        import importlib.util, types
        spec = importlib.util.spec_from_file_location(
            "nullclaw_main",
            str(Path(__file__).parent.parent / "nullclaw.py"),
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.NullClawCLI().run(args)

    def test_no_args_returns_1(self):
        rc = self._run([])
        assert rc == 1

    def test_unknown_command(self):
        rc = self._run(["__unknown__"])
        assert rc == 1

    def test_status_command(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        rc = self._run(["status"])
        assert rc == 0

    def test_config_command(self, tmp_path, monkeypatch):
        import io
        monkeypatch.chdir(tmp_path)
        out = io.StringIO()
        with patch("sys.stdout", out):
            rc = self._run(["config"])
        assert rc == 0
        data = json.loads(out.getvalue())
        assert "primary_model" in data

    def test_parse_missing_log(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        rc = self._run(["parse", str(tmp_path / "missing.log")])
        assert rc == 1

    def test_parse_real_log(self, tmp_path):
        log = tmp_path / "build.log"
        log.write_text(
            "src/App.tsx:5:3 - error TS2304: Cannot find name 'foo'.\n"
        )
        import io, sys
        out = io.StringIO()
        with patch("sys.stdout", out):
            rc = self._run(["parse", str(log)])
        assert rc == 0
        data = json.loads(out.getvalue())
        assert data["code"] == "TS2304"

    def test_context_missing_file(self):
        rc = self._run(["context", "/nonexistent/file.ts", "1"])
        assert rc == 0   # prints "not found" message but returns 0

    def test_search_no_results(self, tmp_path):
        (tmp_path / "x.ts").write_text("const a = 1;")
        rc = self._run(["search", "ZZZNOMATCH_XYZ_ABC", str(tmp_path)])
        assert rc == 1   # no results → exit 1

    def test_build_command(self, tmp_path):
        rc = self._run(["build", ".", "echo hello"])
        assert rc == 0

    def test_analyze_command(self, tmp_path):
        (tmp_path / "main.py").write_text("x = 1")
        rc = self._run(["analyze", str(tmp_path)])
        assert rc == 0

    def test_map_command(self, tmp_path):
        (tmp_path / "src").mkdir()
        rc = self._run(["map", str(tmp_path)])
        assert rc == 0

    def test_apply_missing_patch(self, tmp_path):
        rc = self._run(["apply", str(tmp_path), str(tmp_path / "none.patch")])
        assert rc == 1


# ===========================================================================
# kimi_forge_unified integration
# ===========================================================================

class TestKimiForgeNullClaw:
    def test_nullclaw_registered(self):
        import kimi_forge_unified as kfu
        tools = kfu.ForgeToolRegistry().tools
        assert "nullclaw" in tools
        caps = tools["nullclaw"]["capabilities"]
        assert "repair_loop"     in caps
        assert "error_parser"    in caps
        assert "typescript_fix"  in caps
        assert "rust_fix"        in caps

    def test_keyword_routing_build_error(self):
        import kimi_forge_unified as kfu
        model = kfu.KimiK2Model()
        calls = model._select_tools("repair my build error in typescript")
        names = [c.tool_name for c in calls]
        assert "nullclaw" in names

    def test_keyword_routing_ollama(self):
        import kimi_forge_unified as kfu
        model = kfu.KimiK2Model()
        calls = model._select_tools("use ollama to fix my code locally")
        names = [c.tool_name for c in calls]
        assert "nullclaw" in names

    def test_keyword_routing_npm_error(self):
        import kimi_forge_unified as kfu
        model = kfu.KimiK2Model()
        calls = model._select_tools("npm build fail error please help")
        names = [c.tool_name for c in calls]
        assert "nullclaw" in names

    def test_nullclaw_has_implementation(self):
        import kimi_forge_unified as kfu
        tool = kfu.ForgeToolRegistry().tools["nullclaw"]
        assert "implementation" in tool
        assert tool["implementation"] == "nullclaw.py"
