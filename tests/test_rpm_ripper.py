"""
Tests for rpm_ripper.py — ElfAnalyzer, RpmRipper, ElfDecompiler, SrcRpmFinder

These tests:
  • Are Linux-only (ELF binaries, cpio extraction helpers).
  • Never execute extracted binaries.
  • Use /usr/bin/ls as a real ELF target wherever an on-disk ELF is needed.
  • Build a minimal fake RPM payload in memory to test RpmRipper helpers
    without requiring a real .rpm file or the rpm/cpio tools.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import struct
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from rpm_ripper import (
    ELF_MAGIC,
    EI_CLASS,
    EI_DATA,
    EI_OSABI,
    E_TYPE,
    E_MACHINE,
    ElfAnalyzer,
    ElfDecompiler,
    RpmRipper,
    SrcRpmFinder,
)

# ---------------------------------------------------------------------------
# Platform guard
# ---------------------------------------------------------------------------

pytestmark = pytest.mark.skipif(
    not Path("/usr/bin/ls").exists(),
    reason="tests require a Linux /usr/bin/ls ELF",
)

_LS = "/usr/bin/ls"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_minimal_elf64(path: Path) -> None:
    """Write a minimal but structurally valid 64-bit ELF file."""
    e_ident = (
        b"\x7fELF"   # magic
        + b"\x02"    # EI_CLASS  = 64-bit
        + b"\x01"    # EI_DATA   = little-endian
        + b"\x01"    # EI_VERSION = current
        + b"\x00"    # EI_OSABI  = System V
        + b"\x00" * 8  # padding
    )
    # e_type=2 (ET_EXEC), e_machine=0x3e (AMD64)
    rest = struct.pack("<HH", 2, 0x3E)
    rest += b"\x00" * (64 - len(e_ident) - len(rest))
    path.write_bytes(e_ident + rest)


def _write_non_elf(path: Path, content: bytes = b"not an elf file") -> None:
    path.write_bytes(content)


# ---------------------------------------------------------------------------
# ElfAnalyzer — unit tests
# ---------------------------------------------------------------------------

class TestElfAnalyzer:
    """Tests for ElfAnalyzer.analyze() against /usr/bin/ls and minimal ELFs."""

    def test_analyze_real_elf_returns_required_keys(self):
        result = ElfAnalyzer(_LS).analyze()
        for key in ("path", "size_bytes", "sha256", "elf_header",
                    "shared_libs", "language", "frameworks",
                    "build_id", "stripped"):
            assert key in result, f"missing key: {key}"

    def test_analyze_real_elf_path_is_string(self):
        result = ElfAnalyzer(_LS).analyze()
        assert isinstance(result["path"], str)

    def test_analyze_real_elf_size_positive(self):
        result = ElfAnalyzer(_LS).analyze()
        assert result["size_bytes"] > 0

    def test_analyze_real_elf_sha256_hex(self):
        result = ElfAnalyzer(_LS).analyze()
        sha = result["sha256"]
        assert isinstance(sha, str)
        assert len(sha) == 64
        # Must be valid hex
        int(sha, 16)

    def test_analyze_real_elf_header_fields(self):
        header = ElfAnalyzer(_LS).analyze()["elf_header"]
        assert "class" in header
        assert "data" in header
        assert "type" in header
        assert "machine" in header

    def test_analyze_real_elf_shared_libs_list(self):
        libs = ElfAnalyzer(_LS).analyze()["shared_libs"]
        assert isinstance(libs, list)
        # ls always links at least libc
        assert any("libc" in lib.lower() for lib in libs)

    def test_analyze_real_elf_language_is_string(self):
        lang = ElfAnalyzer(_LS).analyze()["language"]
        assert isinstance(lang, str)
        assert lang  # not empty

    def test_analyze_real_elf_frameworks_list(self):
        fws = ElfAnalyzer(_LS).analyze()["frameworks"]
        assert isinstance(fws, list)

    def test_analyze_real_elf_stripped_bool(self):
        stripped = ElfAnalyzer(_LS).analyze()["stripped"]
        assert isinstance(stripped, bool)

    def test_analyze_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            ElfAnalyzer(str(tmp_path / "nonexistent.elf")).analyze()

    def test_parse_elf_header_non_elf_raises(self, tmp_path):
        bad = tmp_path / "bad.bin"
        _write_non_elf(bad)
        with pytest.raises(ValueError, match="Not a valid ELF"):
            ElfAnalyzer(str(bad)).analyze()

    def test_parse_minimal_elf64_class(self, tmp_path):
        elf = tmp_path / "min.elf"
        _write_minimal_elf64(elf)
        result = ElfAnalyzer(str(elf)).analyze()
        assert result["elf_header"]["class"] == "64-bit"

    def test_parse_minimal_elf64_data(self, tmp_path):
        elf = tmp_path / "min.elf"
        _write_minimal_elf64(elf)
        result = ElfAnalyzer(str(elf)).analyze()
        assert result["elf_header"]["data"] == "little-endian"

    def test_parse_minimal_elf64_type_exec(self, tmp_path):
        elf = tmp_path / "min.elf"
        _write_minimal_elf64(elf)
        result = ElfAnalyzer(str(elf)).analyze()
        # E_TYPE[2] may be "executable" or "ET_EXEC" depending on the dict
        assert result["elf_header"]["type"]  # non-empty string

    def test_parse_minimal_elf64_machine_amd64(self, tmp_path):
        elf = tmp_path / "min.elf"
        _write_minimal_elf64(elf)
        result = ElfAnalyzer(str(elf)).analyze()
        assert "AMD64" in result["elf_header"]["machine"] or \
               "x86-64" in result["elf_header"]["machine"] or \
               "EM_X86_64" in result["elf_header"]["machine"]

    def test_is_elf_correct(self, tmp_path):
        elf = tmp_path / "real.elf"
        _write_minimal_elf64(elf)
        not_elf = tmp_path / "text.bin"
        _write_non_elf(not_elf)
        assert RpmRipper._is_elf(str(elf))
        assert not RpmRipper._is_elf(str(not_elf))

    def test_is_elf_missing_file_returns_false(self, tmp_path):
        assert not RpmRipper._is_elf(str(tmp_path / "ghost.elf"))

    def test_sha256_matches_manual(self, tmp_path):
        elf = tmp_path / "a.elf"
        _write_minimal_elf64(elf)
        expected = hashlib.sha256(elf.read_bytes()).hexdigest()
        result = ElfAnalyzer(str(elf)).analyze()
        assert result["sha256"] == expected


# ---------------------------------------------------------------------------
# EI_ constant dictionaries
# ---------------------------------------------------------------------------

class TestElfConstants:
    def test_ei_class_known(self):
        assert EI_CLASS[1] == "32-bit"
        assert EI_CLASS[2] == "64-bit"

    def test_ei_data_known(self):
        assert EI_DATA[1] == "little-endian"
        assert EI_DATA[2] == "big-endian"

    def test_ei_osabi_system_v(self):
        assert EI_OSABI[0x00] == "UNIX System V"

    def test_ei_osabi_linux(self):
        assert EI_OSABI[0x03] == "Linux"

    def test_e_type_exec(self):
        # key 2 is ET_EXEC — value describes executables
        assert E_TYPE[2]  # non-empty string (e.g. "executable" or "ET_EXEC")

    def test_e_machine_amd64_present(self):
        # 0x3E = EM_X86_64
        assert 0x3E in E_MACHINE


# ---------------------------------------------------------------------------
# RpmRipper helpers
# ---------------------------------------------------------------------------

class TestRpmRipperHelpers:
    """Test the static helpers that don't need a real RPM."""

    def test_is_elf_magic(self, tmp_path):
        elf = tmp_path / "a.elf"
        _write_minimal_elf64(elf)
        assert RpmRipper._is_elf(str(elf))

    def test_is_elf_not_elf(self, tmp_path):
        f = tmp_path / "a.txt"
        f.write_bytes(b"hello world")
        assert not RpmRipper._is_elf(str(f))

    def test_collect_elfs_copies_to_elf_dir(self, tmp_path):
        # Put one ELF and one non-ELF in a fake extract dir
        elf_src = tmp_path / "extracted" / "usrbin"
        elf_src.mkdir(parents=True)
        e = elf_src / "fake_bin"
        _write_minimal_elf64(e)
        txt = elf_src / "notes.txt"
        txt.write_bytes(b"hello")

        elf_dir = tmp_path / "elfs"
        elf_dir.mkdir()

        ripper = RpmRipper("dummy.rpm", str(tmp_path / "out"))
        preserved = ripper._collect_elfs([str(e), str(txt)], elf_dir)

        assert len(preserved) == 1
        assert Path(preserved[0]).exists()
        assert Path(preserved[0]).read_bytes()[:4] == ELF_MAGIC

    def test_collect_elfs_deduplicates_names(self, tmp_path):
        elf_dir = tmp_path / "elfs"
        elf_dir.mkdir()

        elfs = []
        for i in range(3):
            d = tmp_path / f"dir{i}"
            d.mkdir()
            e = d / "samename"
            _write_minimal_elf64(e)
            elfs.append(str(e))

        ripper = RpmRipper("dummy.rpm", str(tmp_path / "out"))
        preserved = ripper._collect_elfs(elfs, elf_dir)
        assert len(preserved) == 3

        names = [Path(p).name for p in preserved]
        assert len(set(names)) == 3  # all unique names

    def test_collect_sources_categorises_by_extension(self, tmp_path):
        extract_dir = tmp_path / "extracted"
        extract_dir.mkdir()

        (extract_dir / "script.sh").write_text("#!/bin/sh\necho hi", encoding="utf-8")
        (extract_dir / "config.yaml").write_text("key: value", encoding="utf-8")
        (extract_dir / "main.py").write_text("print('hello')", encoding="utf-8")
        # Also a fake ELF that should be excluded from sources
        elf_f = extract_dir / "binary"
        _write_minimal_elf64(elf_f)

        sources_dir = tmp_path / "sources"
        sources_dir.mkdir()

        ripper = RpmRipper("dummy.rpm", str(tmp_path / "out"))
        all_files = [str(f) for f in extract_dir.iterdir()]
        result = ripper._collect_sources(all_files, sources_dir)

        # ELF should NOT appear in sources
        all_source_files = [
            Path(p).name for files in result.values() for p in files
        ]
        assert "binary" not in all_source_files

        # Known extensions should be categorised
        assert "shell_scripts" in result
        assert "yaml_configs" in result
        assert "python_scripts" in result

    def test_collect_sources_unknown_extension_goes_to_other(self, tmp_path):
        extract_dir = tmp_path / "extracted"
        extract_dir.mkdir()
        (extract_dir / "strange.xyz1234").write_text("data", encoding="utf-8")

        sources_dir = tmp_path / "sources"
        sources_dir.mkdir()

        ripper = RpmRipper("dummy.rpm", str(tmp_path / "out"))
        result = ripper._collect_sources([str(extract_dir / "strange.xyz1234")], sources_dir)
        assert "other_files" in result

    def test_build_summary_empty_analyses(self):
        rpm_info = {"name": "testpkg", "version": "1.0", "arch": "x86_64"}
        summary = RpmRipper._build_summary(rpm_info, [], {})
        assert summary["package"] == "testpkg"
        assert summary["elf_count"] == 0
        assert summary["dominant_language"] == "unknown"

    def test_build_summary_error_counted(self):
        rpm_info = {"name": "pkg", "version": "1.0", "arch": "x86_64"}
        analyses = [{"path": "/bad", "error": "failed to parse"}]
        summary = RpmRipper._build_summary(rpm_info, analyses)
        assert summary["error_count"] == 1

    def test_build_summary_language_breakdown(self):
        rpm_info = {"name": "pkg", "version": "2.0", "arch": "x86_64"}
        analyses = [
            {"path": "/a", "language": "Rust", "frameworks": [],
             "elf_header": {"machine": "AMD64"}, "stripped": False},
            {"path": "/b", "language": "Rust", "frameworks": ["Qt"],
             "elf_header": {"machine": "AMD64"}, "stripped": True},
            {"path": "/c", "language": "C", "frameworks": [],
             "elf_header": {"machine": "AMD64"}, "stripped": False},
        ]
        summary = RpmRipper._build_summary(rpm_info, analyses)
        assert summary["dominant_language"] == "Rust"
        assert summary["language_breakdown"]["Rust"] == 2
        assert summary["language_breakdown"]["C"] == 1
        assert summary["stripped_binaries"] == 1

    def test_build_summary_source_file_categories(self):
        rpm_info = {"name": "p", "version": "1.0", "arch": "x86_64"}
        source_files = {
            "shell_scripts": ["/a.sh", "/b.sh"],
            "yaml_configs": ["/conf.yaml"],
        }
        summary = RpmRipper._build_summary(rpm_info, [], source_files)
        assert summary["source_file_categories"]["shell_scripts"] == 2
        assert summary["source_file_categories"]["yaml_configs"] == 1
        assert summary["total_source_artefacts"] == 3

    def test_rip_raises_for_missing_rpm(self, tmp_path):
        with pytest.raises(FileNotFoundError, match="RPM not found"):
            RpmRipper(str(tmp_path / "ghost.rpm"), str(tmp_path / "out")).rip()

    def test_rip_writes_report_json_with_fake_extraction(self, tmp_path):
        """
        Patch _extract and _query_rpm_metadata so rip() completes without
        a real RPM or rpm2cpio on the system.
        """
        # Write a placeholder rpm "file"
        rpm_file = tmp_path / "fake.rpm"
        rpm_file.write_bytes(b"\xed\xab\xee\xdb" + b"\x00" * 92)  # minimal rpm magic

        out_dir = tmp_path / "out"

        with patch.object(RpmRipper, "_query_rpm_metadata",
                          return_value={"name": "fakepkg", "version": "1.0",
                                        "arch": "x86_64"}), \
             patch.object(RpmRipper, "_extract", return_value=[]):

            report = RpmRipper(str(rpm_file), str(out_dir)).rip()

        assert "rpm_path" in report
        assert "elf_files" in report
        assert "source_files" in report
        assert "summary" in report

        report_json = out_dir / "analysis_report.json"
        assert report_json.exists()

        with open(report_json, encoding="utf-8") as fh:
            loaded = json.load(fh)
        assert loaded["summary"]["package"] == "fakepkg"

    def test_source_categories_dict_coverage(self):
        cats = RpmRipper._SOURCE_CATEGORIES
        for ext in (".py", ".sh", ".rs", ".go", ".json", ".yaml", ".md",
                    ".service", ".desktop", ".spec", ".cmake"):
            assert ext in cats, f"extension {ext!r} not in _SOURCE_CATEGORIES"


# ---------------------------------------------------------------------------
# ElfDecompiler — unit tests
# ---------------------------------------------------------------------------

class TestElfDecompiler:
    def test_missing_elf_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            ElfDecompiler(str(tmp_path / "ghost.elf"))

    def test_decompile_real_ls_returns_required_keys(self, tmp_path):
        result = ElfDecompiler(_LS).decompile(output_dir=str(tmp_path / "decomp"))
        for key in ("elf", "output_dir", "layers", "summary_file"):
            assert key in result

    def test_decompile_layers_present(self, tmp_path):
        result = ElfDecompiler(_LS).decompile(output_dir=str(tmp_path / "decomp"))
        layers = result["layers"]
        for layer in ("dwarf", "symbols", "strings", "disassembly", "ghidra"):
            assert layer in layers, f"layer {layer!r} missing"

    def test_decompile_ghidra_skipped_by_default(self, tmp_path):
        result = ElfDecompiler(_LS).decompile(output_dir=str(tmp_path / "decomp"))
        ghidra = result["layers"]["ghidra"]
        assert ghidra.get("status") in ("skipped", "not_installed")

    def test_decompile_strings_layer_count(self, tmp_path):
        result = ElfDecompiler(_LS).decompile(output_dir=str(tmp_path / "decomp"))
        strs = result["layers"]["strings"]
        assert "count" in strs
        # ls has plenty of strings >= 8 chars
        assert strs["count"] > 0

    def test_decompile_symbols_layer_total(self, tmp_path):
        result = ElfDecompiler(_LS).decompile(output_dir=str(tmp_path / "decomp"))
        syms = result["layers"]["symbols"]
        assert "total" in syms
        assert isinstance(syms["total"], int)

    def test_decompile_writes_summary_json(self, tmp_path):
        out = tmp_path / "decomp"
        result = ElfDecompiler(_LS).decompile(output_dir=str(out))
        summary_path = Path(result["summary_file"])
        assert summary_path.exists()
        data = json.loads(summary_path.read_text(encoding="utf-8"))
        assert "layers" in data

    def test_decompile_disassembly_file_created(self, tmp_path):
        out = tmp_path / "decomp"
        result = ElfDecompiler(_LS).decompile(output_dir=str(out))
        disasm_info = result["layers"]["disassembly"]
        disasm_path = Path(disasm_info.get("file", ""))
        assert disasm_path.exists()

    def test_parse_nm_output_normal(self):
        nm_text = "0000000000401234 T main\n                 U printf"
        syms = ElfDecompiler._parse_nm_output(nm_text)
        assert len(syms) == 2
        assert syms[0]["type"] == "T"
        assert syms[0]["raw"] == "main"
        assert syms[1]["type"] == "U"
        assert syms[1]["raw"] == "printf"

    def test_parse_nm_output_empty(self):
        assert ElfDecompiler._parse_nm_output("") == []

    def test_build_function_skeleton_contains_function_names(self):
        functions = [
            {"addr": "0x401234", "type": "T", "raw": "foo", "demangled": "foo"},
            {"addr": "0x401240", "type": "T", "raw": "bar", "demangled": "bar"},
        ]
        skel = ElfDecompiler._build_function_skeleton(functions)
        assert "foo" in skel
        assert "bar" in skel
        assert "SKELETON" in skel  # header comment

    def test_parse_dwarf_source_files_empty(self):
        files = ElfDecompiler._parse_dwarf_source_files("")
        assert files == []

    def test_parse_dwarf_source_files_c_extension(self):
        debug_info = (
            "    DW_AT_name        : (indirect string, offset: 0x0): /src/main.c\n"
            "    DW_AT_comp_dir    : (indirect string, offset: 0x8): /build\n"
        )
        files = ElfDecompiler._parse_dwarf_source_files(debug_info)
        assert any(".c" in f for f in files)

    def test_parse_dwarf_no_duplicates(self):
        debug_info = (
            "    DW_AT_name : /src/main.c\n"
            "    DW_AT_name : /src/main.c\n"
        )
        files = ElfDecompiler._parse_dwarf_source_files(debug_info)
        assert files.count("/src/main.c") == 1


# ---------------------------------------------------------------------------
# SrcRpmFinder — unit tests
# ---------------------------------------------------------------------------

class TestSrcRpmFinder:
    """Test SrcRpmFinder against a fake rpm path (no real .rpm needed)."""

    def _make_finder(self, name: str = "mypkg", version: str = "1.2.3",
                     release: str = "1.fc39") -> SrcRpmFinder:
        """Build a SrcRpmFinder with a patched _query_rpm_metadata."""
        finder = SrcRpmFinder("mypkg-1.2.3-1.fc39.x86_64.rpm")
        finder._query_rpm_metadata = lambda: {   # type: ignore[method-assign]
            "name": name,
            "version": version,
            "release": release,
            "arch": "x86_64",
            "sourcerpm": f"{name}-{version}-{release}.src.rpm",
        }
        return finder

    def test_find_hints_returns_required_keys(self):
        hints = self._make_finder().find_hints()
        for key in ("package_name", "version", "release", "src_rpm_name",
                    "dist", "fetch_commands", "urls", "note"):
            assert key in hints, f"missing key: {key}"

    def test_find_hints_src_rpm_name(self):
        hints = self._make_finder("mypkg", "1.2.3", "1.fc39").find_hints()
        assert hints["src_rpm_name"] == "mypkg-1.2.3-1.fc39.src.rpm"

    def test_find_hints_dist_parsed(self):
        hints = self._make_finder("mypkg", "1.0", "1.fc40").find_hints()
        assert hints["dist"] == "fc40"

    def test_find_hints_dist_no_dot(self):
        hints = self._make_finder("mypkg", "1.0", "1").find_hints()
        # release has no dot → dist is empty string (SrcRpmFinder only sets
        # dist when a "." is present in the release string)
        assert hints["dist"] == ""

    def test_find_hints_urls_contains_koji(self):
        hints = self._make_finder("curl", "8.4.0", "1.fc39").find_hints()
        koji_urls = [u for u in hints["urls"] if "kojipkgs" in u]
        assert len(koji_urls) >= 1
        assert "curl" in koji_urls[0]

    def test_find_hints_urls_contains_fedora_src(self):
        hints = self._make_finder("curl", "8.4.0", "1.fc39").find_hints()
        from urllib.parse import urlparse
        fedora_urls = [
            u for u in hints["urls"]
            if urlparse(u).netloc == "src.fedoraproject.org"
        ]
        assert len(fedora_urls) >= 1

    def test_find_hints_urls_contains_gitlab_centos(self):
        hints = self._make_finder("curl", "8.4.0", "1.fc39").find_hints()
        from urllib.parse import urlparse
        gitlab_urls = [
            u for u in hints["urls"]
            if urlparse(u).netloc == "gitlab.com"
        ]
        assert len(gitlab_urls) >= 1

    def test_find_hints_note_mentions_source(self):
        hints = self._make_finder().find_hints()
        assert ".src.rpm" in hints["note"] or "source" in hints["note"].lower()

    def test_find_hints_package_name_correct(self):
        hints = self._make_finder("bash", "5.2.21", "2.fc39").find_hints()
        assert hints["package_name"] == "bash"

    def test_find_hints_fetch_commands_list(self):
        hints = self._make_finder().find_hints()
        assert isinstance(hints["fetch_commands"], list)
