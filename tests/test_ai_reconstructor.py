"""
Tests for ai_reconstructor.py and gemini_code_fixer.py
"""
import json
import os
import struct
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Make sure repo root is on the path
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent.parent))

import ai_reconstructor as ar
import gemini_code_fixer as gcf

# ---------------------------------------------------------------------------
# Helpers — build minimal ELF files in memory
# ---------------------------------------------------------------------------

def _make_elf64(
    *,
    sections: bool = False,
    has_dynamic: bool = False,
    has_debug: bool = False,
) -> bytes:
    """
    Construct a minimal but structurally valid 64-bit ELF.

    This is used to exercise DeepElfParser without needing a real binary.
    """
    e_ident = (
        b"\x7fELF"   # magic
        + b"\x02"    # 64-bit
        + b"\x01"    # little-endian
        + b"\x01"    # ELF version 1
        + b"\x00"    # OS/ABI: UNIX System V
        + b"\x00" * 8  # padding
    )

    # We'll build: ELF header + optionally a tiny section header table
    e_type    = 3    # ET_DYN (PIE executable)
    e_machine = 0x3E # x86-64
    e_version = 1
    e_entry   = 0x1000
    e_phoff   = 0       # no program headers for simplicity
    e_shoff   = 0
    e_flags   = 0
    e_ehsize  = 64
    e_phentsize = 56
    e_phnum   = 0
    e_shentsize = 64
    e_shnum   = 0
    e_shstrndx = 0

    header_body = struct.pack(
        "<HHIQQQIHHHHHH",
        e_type, e_machine, e_version,
        e_entry, e_phoff, e_shoff,
        e_flags, e_ehsize,
        e_phentsize, e_phnum,
        e_shentsize, e_shnum, e_shstrndx,
    )

    return e_ident + header_body  # 64 bytes total


def _write_elf(tmp_path: Path, data: bytes = None) -> Path:
    p = tmp_path / "test.elf"
    p.write_bytes(data or _make_elf64())
    return p


# ===========================================================================
# DeepElfParser tests
# ===========================================================================

class TestDeepElfParser:
    def test_rejects_non_elf(self, tmp_path):
        p = tmp_path / "notelf"
        p.write_bytes(b"not an ELF file at all")
        with pytest.raises(ValueError, match="Not a valid ELF"):
            ar.DeepElfParser(str(p)).parse()

    def test_rejects_missing_file(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            ar.DeepElfParser(str(tmp_path / "missing.elf")).parse()

    def test_parses_minimal_elf64(self, tmp_path):
        p = _write_elf(tmp_path)
        result = ar.DeepElfParser(str(p)).parse()
        assert result["class"] == "64-bit"
        assert result["endian"] == "little"
        assert result["header"]["e_type"] == "ET_DYN"
        assert result["header"]["e_machine"] == "x86-64"
        assert result["header"]["is_pie"] is True
        assert result["header"]["is_64bit"] is True
        assert result["size_bytes"] == 64

    def test_parse_returns_required_keys(self, tmp_path):
        p = _write_elf(tmp_path)
        r = ar.DeepElfParser(str(p)).parse()
        for key in ("path", "size_bytes", "class", "endian", "header",
                    "sections", "phdrs", "dynsyms", "symtab",
                    "imports", "exports", "dynamic", "dso_deps",
                    "notes", "relocations", "plt_stubs",
                    "section_count", "symbol_count",
                    "import_count", "export_count"):
            assert key in r, f"Missing key: {key}"

    def test_parse_real_elf_ls(self):
        """Parse /bin/ls — a real stripped ELF available everywhere."""
        ls = Path("/bin/ls")
        if not ls.exists():
            pytest.skip("/bin/ls not found")
        r = ar.DeepElfParser(str(ls)).parse()
        assert r["class"] in ("64-bit", "32-bit")
        assert r["section_count"] > 0
        assert r["header"]["e_machine"] in ("x86-64", "AArch64", "ARM")

    def test_parse_real_elf_imports(self):
        ls = Path("/bin/ls")
        if not ls.exists():
            pytest.skip("/bin/ls not found")
        r = ar.DeepElfParser(str(ls)).parse()
        # /bin/ls imports from libc — must have at least one import
        assert r["import_count"] > 0
        names = [s["name"] for s in r["imports"]]
        # At minimum, malloc or printf or similar libc symbol
        assert any(n for n in names if n)

    def test_parse_real_elf_dso_deps(self):
        ls = Path("/bin/ls")
        if not ls.exists():
            pytest.skip("/bin/ls not found")
        r = ar.DeepElfParser(str(ls)).parse()
        assert len(r["dso_deps"]) >= 1
        assert any("libc" in d for d in r["dso_deps"])

    def test_parse_real_elf_security_hardening(self):
        ls = Path("/bin/ls")
        if not ls.exists():
            pytest.skip("/bin/ls not found")
        r = ar.DeepElfParser(str(ls)).parse()
        # /bin/ls on modern Ubuntu is always PIE
        assert r["header"]["is_pie"] is True

    def test_strtab_lookup_empty(self):
        assert ar.DeepElfParser._strtab_lookup(b"", 0) == ""

    def test_strtab_lookup_normal(self):
        strtab = b"\x00hello\x00world\x00"
        assert ar.DeepElfParser._strtab_lookup(strtab, 1) == "hello"
        assert ar.DeepElfParser._strtab_lookup(strtab, 7) == "world"

    def test_strtab_lookup_out_of_range(self):
        strtab = b"\x00hi\x00"
        assert ar.DeepElfParser._strtab_lookup(strtab, 999) == ""

    def test_decode_flags(self):
        # WRITE=1, ALLOC=2, EXECINSTR=4
        flags = ar.DeepElfParser._decode_flags(0x3, ar._SHF)   # WRITE | ALLOC
        assert "WRITE" in flags
        assert "ALLOC" in flags
        assert "EXECINSTR" not in flags


# ===========================================================================
# ElfUnderstanding tests
# ===========================================================================

class TestElfUnderstanding:
    def _minimal_parse(self, imports=None, phdrs=None, dynamic=None):
        return {
            "header":   {"e_type": "ET_DYN", "is_pie": True},
            "phdrs":    phdrs or [],
            "sections": [],
            "imports":  [{"name": n, "bind": "GLOBAL"} for n in (imports or [])],
            "exports":  [],
            "all_symbols": [],
            "dynamic":  dynamic or [],
            "dso_deps": [],
            "import_count": len(imports or []),
            "export_count": 0,
        }

    def test_understand_returns_required_keys(self):
        parse = self._minimal_parse()
        u = ar.ElfUnderstanding(parse).understand()
        for key in ("purpose", "binary_type", "algorithms", "security",
                    "init_sequence", "env_config", "library_usage",
                    "execution_flow"):
            assert key in u

    def test_security_no_hardening(self):
        parse = self._minimal_parse()
        u = ar.ElfUnderstanding(parse).understand()
        sec = u["security"]
        assert sec["hardening_grade"] in ("F", "D", "C")

    def test_security_full_hardening(self):
        phdrs = [
            {"type": "DYNAMIC",    "executable": False, "writable": False, "readable": True},
            {"type": "GNU_RELRO",  "executable": False, "writable": False, "readable": True},
            {"type": "GNU_STACK",  "executable": False, "writable": True,  "readable": True},
        ]
        imports = ["__stack_chk_fail", "memcpy_chk", "printf_chk"]
        parse = self._minimal_parse(imports=imports, phdrs=phdrs)
        parse["header"]["is_pie"] = True
        u = ar.ElfUnderstanding(parse).understand()
        sec = u["security"]
        assert sec["stack_canary"] is True
        assert sec["fortify_source"] is True
        assert sec["pie"] is True
        assert sec["relro"] is True
        assert sec["nx_stack"] is True
        assert sec["hardening_grade"] == "A+"

    def test_algorithm_detection_pcre2(self):
        parse = self._minimal_parse(imports=["pcre2_match_8", "pcre2_compile_8"])
        u = ar.ElfUnderstanding(parse).understand()
        assert any("PCRE2" in a for a in u["algorithms"])

    def test_algorithm_detection_pthread(self):
        parse = self._minimal_parse(imports=["pthread_create", "pthread_join"])
        u = ar.ElfUnderstanding(parse).understand()
        assert any("thread" in a.lower() for a in u["algorithms"])

    def test_binary_type_pie(self):
        parse = self._minimal_parse(
            phdrs=[{"type": "INTERP", "executable": False,
                    "writable": False, "readable": True}]
        )
        parse["header"]["is_pie"] = True
        u = ar.ElfUnderstanding(parse).understand()
        bt = u["binary_type"]
        assert bt["is_pie"] is True
        assert bt["needs_interp"] is True

    def test_dangerous_functions_flagged(self):
        parse = self._minimal_parse(imports=["gets", "strcpy", "sprintf"])
        u = ar.ElfUnderstanding(parse).understand()
        sec = u["security"]
        assert "gets" in sec["dangerous_funcs"]
        assert "strcpy" in sec["dangerous_funcs"]

    def test_real_ls_understanding(self):
        ls = Path("/bin/ls")
        if not ls.exists():
            pytest.skip("/bin/ls not found")
        parse = ar.DeepElfParser(str(ls)).parse()
        u = ar.ElfUnderstanding(parse).understand()
        assert u["binary_type"]["is_pie"] is True
        sec = u["security"]
        # Modern /bin/ls always has at least PIE + NX stack
        assert sec["hardening_score"] >= 2


# ===========================================================================
# ProgressiveScan tests
# ===========================================================================

class TestProgressiveScan:
    def test_rejects_non_elf(self, tmp_path):
        p = tmp_path / "notelf"
        p.write_bytes(b"hello")
        with pytest.raises(ValueError):
            ar.ProgressiveScan(str(p))

    def test_rejects_missing(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            ar.ProgressiveScan(str(tmp_path / "missing"))

    def test_scan_depth1_ls(self):
        ls = Path("/bin/ls")
        if not ls.exists():
            pytest.skip("/bin/ls not found")
        updates = list(ar.ProgressiveScan(str(ls)).scan(max_depth=1))
        assert len(updates) == 1
        u = updates[0]
        assert u["depth"] == 1
        assert "64-bit" in u["summary"] or "32-bit" in u["summary"]
        assert u["progress"] == pytest.approx(1.0)

    def test_scan_depth2_ls(self):
        ls = Path("/bin/ls")
        if not ls.exists():
            pytest.skip("/bin/ls not found")
        updates = list(ar.ProgressiveScan(str(ls)).scan(max_depth=2))
        assert len(updates) == 2
        d2 = updates[1]
        assert "sections" in d2["summary"] or "section" in d2["summary"].lower()

    def test_scan_depth3_language(self):
        ls = Path("/bin/ls")
        if not ls.exists():
            pytest.skip("/bin/ls not found")
        updates = list(ar.ProgressiveScan(str(ls)).scan(max_depth=3))
        assert len(updates) == 3
        d3 = updates[2]
        assert "language=" in d3["summary"]

    def test_scan_depth4_deep(self):
        ls = Path("/bin/ls")
        if not ls.exists():
            pytest.skip("/bin/ls not found")
        updates = list(ar.ProgressiveScan(str(ls)).scan(max_depth=4))
        assert len(updates) == 4
        d4 = updates[3]
        assert "imports" in d4["summary"]
        assert "hardening=" in d4["summary"]

    def test_scan_depth5_understanding(self):
        ls = Path("/bin/ls")
        if not ls.exists():
            pytest.skip("/bin/ls not found")
        updates = list(ar.ProgressiveScan(str(ls)).scan(max_depth=5))
        assert len(updates) == 5
        d5 = updates[4]
        assert "purpose=" in d5["summary"]

    def test_run_returns_dict(self):
        ls = Path("/bin/ls")
        if not ls.exists():
            pytest.skip("/bin/ls not found")
        result = ar.ProgressiveScan(str(ls)).run(depth=2)
        assert isinstance(result, dict)
        assert "binary" in result

    def test_depth_labels_complete(self):
        for d in range(1, 7):
            assert d in ar.ProgressiveScan._DEPTH_LABELS

    def test_max_depth_clamped(self):
        ls = Path("/bin/ls")
        if not ls.exists():
            pytest.skip("/bin/ls not found")
        # max_depth=0 should clamp to 1
        updates = list(ar.ProgressiveScan(str(ls)).scan(max_depth=0))
        assert len(updates) == 1


# ===========================================================================
# BinaryXRay / VirtualUnwrapper / AIPatternMatcher integration
# ===========================================================================

class TestBinaryXRay:
    def test_xray_ls_scan_keys(self):
        ls = Path("/bin/ls")
        if not ls.exists():
            pytest.skip()
        scan = ar.BinaryXRay(str(ls)).scan()
        assert "layers" in scan
        for layer in ("skeleton", "symbols", "strings", "callgraph",
                       "data", "build"):
            assert layer in scan["layers"]

    def test_xray_language_rust(self, tmp_path):
        rg = Path("/tmp/rg_extract/usr/bin/rg")
        if not rg.exists():
            pytest.skip("ripgrep ELF not available")
        scan = ar.BinaryXRay(str(rg)).scan()
        assert scan["layers"]["symbols"]["language"] == "rust"

    def test_xray_source_paths_rust(self):
        rg = Path("/tmp/rg_extract/usr/bin/rg")
        if not rg.exists():
            pytest.skip()
        scan = ar.BinaryXRay(str(rg)).scan()
        syms = scan["layers"]["symbols"]
        assert len(syms.get("string_source_files", [])) > 10

    def test_safe_filename_normal(self):
        fname = ar.ScrollAssembler._safe_filename("foo::bar", ".rs")
        assert fname.endswith(".rs")
        assert len(fname) <= 80

    def test_safe_filename_long(self):
        long_name = "a" * 200
        fname = ar.ScrollAssembler._safe_filename(long_name, ".rs")
        assert len(fname) <= 80
        assert fname.endswith(".rs")

    def test_safe_filename_special_chars(self):
        fname = ar.ScrollAssembler._safe_filename("hello/world::test<T>", ".go")
        assert "/" not in fname
        assert "<" not in fname
        assert fname.endswith(".go")


# ===========================================================================
# GeminiProgramFixer tests
# ===========================================================================

class TestGeminiProgramFixer:
    # ── API key helpers ────────────────────────────────────────────────

    def test_load_api_key_from_env(self, monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "test-key-abc")
        assert gcf._load_api_key() == "test-key-abc"

    def test_load_api_key_missing(self, monkeypatch, tmp_path):
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.setattr(gcf, "_KEY_FILE", tmp_path / "no_key")
        assert gcf._load_api_key() is None

    def test_save_and_load_key(self, tmp_path, monkeypatch):
        key_file = tmp_path / "key"
        monkeypatch.setattr(gcf, "_KEY_FILE", key_file)
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        gcf._save_api_key("my-saved-key")
        assert gcf._load_api_key() == "my-saved-key"
        assert oct(key_file.stat().st_mode)[-3:] == "600"

    # ── Language detection ─────────────────────────────────────────────

    def test_detect_python(self):
        assert gcf.GeminiProgramFixer._detect_language(Path("x.py")) == "python"

    def test_detect_rust(self):
        assert gcf.GeminiProgramFixer._detect_language(Path("x.rs")) == "rust"

    def test_detect_go(self):
        assert gcf.GeminiProgramFixer._detect_language(Path("x.go")) == "go"

    def test_detect_unknown(self):
        assert gcf.GeminiProgramFixer._detect_language(Path("x.xyz")) == "text"

    # ── Pattern-based fixes ────────────────────────────────────────────

    def test_pattern_fix_indentation(self):
        result = gcf.GeminiProgramFixer._fix_with_patterns(
            "\tdef foo():\n\t\tpass\n",
            "IndentationError: unexpected indent",
            "python",
        )
        assert result is not None
        assert "    " in result["fixed_code"]    # tabs → spaces
        assert result["explanation"]

    def test_pattern_fix_unicode(self):
        code = 'with open("file.txt") as f:\n    data = f.read()\n'
        result = gcf.GeminiProgramFixer._fix_with_patterns(
            code, "UnicodeDecodeError: 'utf-8' codec can't decode", "python"
        )
        assert result is not None
        assert "utf-8" in result["fixed_code"]

    def test_pattern_fix_gemini_auth(self):
        code = "key = GEMINI_KEY\n"
        result = gcf.GeminiProgramFixer._fix_with_patterns(
            code, "GEMINI_API_KEY not set", "python"
        )
        assert result is not None
        assert "GEMINI_API_KEY" in result["fixed_code"]

    def test_pattern_fix_unknown_error(self):
        result = gcf.GeminiProgramFixer._fix_with_patterns(
            "x = 1\n", "some totally unknown error xyz123", "python"
        )
        assert result is None

    def test_pattern_fix_lookup(self):
        assert gcf._pattern_fix("ModuleNotFoundError: No module named 'requests'") is not None
        assert gcf._pattern_fix("something completely unknown xyz") is None

    # ── fix_file no-key path ───────────────────────────────────────────

    def test_fix_file_no_key_no_error(self, tmp_path, monkeypatch):
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.setattr(gcf, "_KEY_FILE", tmp_path / "no_key")
        src = tmp_path / "bad.py"
        src.write_text("x = 1\n")
        fixer = gcf.GeminiProgramFixer(api_key=None)
        result = fixer.fix_file(str(src), error_msg="")
        assert result["method"] == "none"
        assert "GEMINI_API_KEY" in result["explanation"]

    def test_fix_file_pattern_fallback(self, tmp_path, monkeypatch):
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.setattr(gcf, "_KEY_FILE", tmp_path / "no_key")
        src = tmp_path / "bad.py"
        src.write_text("\tdef foo():\n\t\tpass\n")
        fixer = gcf.GeminiProgramFixer(api_key=None)
        result = fixer.fix_file(str(src),
                                error_msg="IndentationError: unexpected indent")
        assert result["method"] == "pattern"
        assert "    " in result["fixed_code"]

    def test_fix_file_missing(self):
        fixer = gcf.GeminiProgramFixer(api_key=None)
        with pytest.raises(FileNotFoundError):
            fixer.fix_file("/nonexistent/missing.py")

    def test_fix_file_apply(self, tmp_path, monkeypatch):
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.setattr(gcf, "_KEY_FILE", tmp_path / "no_key")
        src = tmp_path / "bad.py"
        src.write_text("\tdef foo():\n\t\tpass\n")
        fixer = gcf.GeminiProgramFixer(api_key=None)
        result = fixer.fix_file(str(src),
                                error_msg="IndentationError: unexpected indent",
                                apply=True)
        assert result["output_file"] is not None
        fixed_path = Path(result["output_file"])
        assert fixed_path.exists()
        assert "    " in fixed_path.read_text()

    # ── diff output ────────────────────────────────────────────────────

    def test_make_diff_changed(self):
        diff = gcf.GeminiProgramFixer._make_diff("a\nb\n", "a\nc\n", "x.py")
        assert "-b" in diff
        assert "+c" in diff

    def test_make_diff_unchanged(self):
        diff = gcf.GeminiProgramFixer._make_diff("same\n", "same\n", "x.py")
        assert diff == "(no changes)"

    # ── Gemini response parser ─────────────────────────────────────────

    def test_parse_gemini_response_full(self):
        response = (
            "EXPLANATION:\nThe variable was undefined.\n\n"
            "FIXED_CODE:\n```python\nx = 1\nprint(x)\n```"
        )
        fixer = gcf.GeminiProgramFixer(api_key="fake")
        result = fixer._parse_gemini_response(response, "original")
        assert "undefined" in result["explanation"]
        assert "print(x)" in result["fixed_code"]

    def test_parse_gemini_response_no_fence(self):
        response = "EXPLANATION:\nSomething fixed.\nFIXED_CODE:\nfixed code here"
        fixer = gcf.GeminiProgramFixer(api_key="fake")
        result = fixer._parse_gemini_response(response, "original")
        assert result["fixed_code"] == "original"  # fallback to original

    # ── check_auth no-network ─────────────────────────────────────────

    def test_check_auth_no_key(self, tmp_path, monkeypatch):
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.setattr(gcf, "_KEY_FILE", tmp_path / "no_key")
        fixer = gcf.GeminiProgramFixer(api_key=None)
        status = fixer.check_auth()
        assert status["status"] == "no_key"
        assert "aistudio.google.com" in status["message"]

    # ── CLI smoke ──────────────────────────────────────────────────────

    def test_cli_no_args(self):
        cli = gcf.GeminiCodeFixerCLI()
        rc = cli.run([])
        assert rc == 1

    def test_cli_fix_missing_file(self):
        cli = gcf.GeminiCodeFixerCLI()
        rc = cli.run(["--fix", "/nonexistent/file.py"])
        assert rc == 1

    def test_cli_fix_json_output(self, tmp_path, monkeypatch):
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.setattr(gcf, "_KEY_FILE", tmp_path / "no_key")
        src = tmp_path / "x.py"
        src.write_text("x = 1\n")
        cli = gcf.GeminiCodeFixerCLI()
        import io
        out = io.StringIO()
        with patch("sys.stdout", out):
            rc = cli.run(["--fix", str(src), "--json"])
        assert rc == 0
        data = json.loads(out.getvalue())
        assert "file" in data
        assert "method" in data


# ===========================================================================
# kimi_forge_unified tool routing
# ===========================================================================

class TestKimiForgeUnified:
    def test_ai_reconstructor_registered(self):
        import kimi_forge_unified as kfu
        tools = kfu.ForgeToolRegistry().tools
        assert "ai_reconstructor" in tools
        caps = tools["ai_reconstructor"]["capabilities"]
        assert "elf_xray" in caps
        assert "progressive_scan" in caps

    def test_gemini_program_fixer_registered(self):
        import kimi_forge_unified as kfu
        tools = kfu.ForgeToolRegistry().tools
        assert "gemini_program_fixer" in tools
        caps = tools["gemini_program_fixer"]["capabilities"]
        assert "code_fix" in caps
        assert "pattern_fix" in caps

    def test_keyword_routing_xray(self):
        import kimi_forge_unified as kfu
        model = kfu.KimiK2Model()
        calls = model._select_tools("please xray this elf binary for me")
        names = [c.tool_name for c in calls]
        assert "ai_reconstructor" in names

    def test_keyword_routing_fix(self):
        import kimi_forge_unified as kfu
        model = kfu.KimiK2Model()
        calls = model._select_tools("fix my broken python script please")
        names = [c.tool_name for c in calls]
        assert "gemini_program_fixer" in names

    def test_keyword_routing_scroll(self):
        import kimi_forge_unified as kfu
        model = kfu.KimiK2Model()
        calls = model._select_tools("reconstruct binary like the herculaneum scroll")
        names = [c.tool_name for c in calls]
        assert "ai_reconstructor" in names

    def test_keyword_routing_gemini_auth(self):
        import kimi_forge_unified as kfu
        model = kfu.KimiK2Model()
        calls = model._select_tools("gemini cli not signing in")
        names = [c.tool_name for c in calls]
        assert "gemini_auth_fixer" in names

    def test_all_tools_have_implementation(self):
        import kimi_forge_unified as kfu
        for name, tool in kfu.ForgeToolRegistry().tools.items():
            # Skip the special meta-entry that aggregates all tools
            if name == "all_forge_tools":
                continue
            assert "implementation" in tool, f"Tool {name} missing 'implementation'"
            assert "description" in tool,    f"Tool {name} missing 'description'"
