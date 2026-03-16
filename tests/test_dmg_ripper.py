"""
Tests for dmg_ripper.py — MachoAnalyzer, DmgRipper, LinuxPortingScaffold

These tests:
  • Run fully on Linux — Mach-O binaries are synthesised in memory.
  • Never require a real macOS system, DMG file, or otool installation.
  • Build minimal but structurally valid Mach-O files for the parser tests.
  • Test DmgRipper helpers (is_macho, collect_macho, collect_sources,
    detect_app_bundle, parse_plist, build_summary) without extraction.
  • Test LinuxPortingScaffold with a fabricated rip report.
"""

from __future__ import annotations

import json
import os
import struct
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from dmg_ripper import (
    MACHO_MAGIC_32,
    MACHO_MAGIC_64,
    MACHO_MAGIC_FAT,
    MACHO_MAGIC_32_BE,
    MACHO_MAGIC_64_BE,
    _ALL_MACHO_MAGICS,
    _FRAMEWORK_MAP,
    _LANG_FINGERPRINTS,
    MachoAnalyzer,
    DmgRipper,
    LinuxPortingScaffold,
)


# ---------------------------------------------------------------------------
# Helpers — minimal Mach-O binaries
# ---------------------------------------------------------------------------

def _write_macho64(path: Path) -> None:
    """Write a minimal 64-bit Mach-O header (little-endian, x86-64)."""
    magic    = MACHO_MAGIC_64           # 0xFEEDFACF LE
    cputype  = 0x01000007               # CPU_TYPE_X86_64
    cpusubtype = 0x00000003
    filetype = 0x00000002               # MH_EXECUTE
    ncmds    = 0
    sizeofcmds = 0
    flags    = 0
    reserved = 0
    header = struct.pack("<IIIIIIII",
                         magic, cputype, cpusubtype, filetype,
                         ncmds, sizeofcmds, flags, reserved)
    path.write_bytes(header)


def _write_macho32(path: Path) -> None:
    """Write a minimal 32-bit Mach-O header (little-endian, x86)."""
    magic    = MACHO_MAGIC_32           # 0xFEEDFACE LE
    cputype  = 0x00000007               # CPU_TYPE_X86
    cpusubtype = 0x00000003
    filetype = 0x00000002               # MH_EXECUTE
    ncmds    = 0
    sizeofcmds = 0
    flags    = 0
    header = struct.pack("<IIIIIII",
                         magic, cputype, cpusubtype, filetype,
                         ncmds, sizeofcmds, flags)
    path.write_bytes(header)


def _write_non_macho(path: Path, content: bytes = b"not a macho file") -> None:
    path.write_bytes(content)


def _make_fake_rip_report(
    app_name: str = "TestApp",
    app_version: str = "1.0.0",
    language: str = "Rust",
    frameworks: List[str] = None,
    linux_mapping: List[Dict] = None,
) -> Dict[str, Any]:
    """Build a minimal fake DmgRipper.rip() report for scaffold tests."""
    if frameworks is None:
        frameworks = ["Metal", "AppKit"]
    if linux_mapping is None:
        linux_mapping = [
            {"macos": "Metal",   "linux_crate": "wgpu",
             "linux_dep": 'wgpu = "0.20"', "note": ""},
            {"macos": "AppKit",  "linux_crate": "winit + softbuffer",
             "linux_dep": 'winit = "0.29"\nsoftbuffer = "0.4"', "note": ""},
        ]
    return {
        "dmg_path": "/fake/App.dmg",
        "output_dir": "/fake/out",
        "app_name": app_name,
        "app_version": app_version,
        "extracted_files": 0,
        "macho_files": [
            {
                "path": "/fake/TestApp",
                "size_bytes": 1024,
                "sha256": "a" * 64,
                "macho_header": {"is_fat": False, "is_64bit": True,
                                  "cpu": "x86-64", "file_type": "MH_EXECUTE"},
                "frameworks": frameworks,
                "dylibs": [],
                "linux_mapping": linux_mapping,
                "language": language,
                "stripped": False,
                "build_uuid": None,
            }
        ],
        "source_files": {},
        "summary": {
            "app_name": app_name,
            "app_version": app_version,
            "macho_count": 1,
            "error_count": 0,
            "fat_binaries": 0,
            "stripped_binaries": 0,
            "dominant_language": language,
            "language_breakdown": {language: 1},
            "macos_frameworks": {fw: 1 for fw in frameworks},
            "linux_deps_needed": ["wgpu", "winit"],
            "source_file_categories": {},
            "total_source_artefacts": 0,
        },
    }


# ---------------------------------------------------------------------------
# Mach-O constants
# ---------------------------------------------------------------------------

class TestMachoConstants:
    def test_magic_64_correct(self):
        assert MACHO_MAGIC_64 == 0xFEEDFACF

    def test_magic_32_correct(self):
        assert MACHO_MAGIC_32 == 0xFEEDFACE

    def test_magic_fat_correct(self):
        assert MACHO_MAGIC_FAT == 0xCAFEBABE

    def test_all_magics_contains_known_values(self):
        for magic in (MACHO_MAGIC_32, MACHO_MAGIC_64, MACHO_MAGIC_FAT,
                      MACHO_MAGIC_32_BE, MACHO_MAGIC_64_BE):
            assert magic in _ALL_MACHO_MAGICS

    def test_framework_map_has_metal(self):
        names = [e["macos"] for e in _FRAMEWORK_MAP]
        assert "Metal" in names

    def test_framework_map_has_appkit(self):
        names = [e["macos"] for e in _FRAMEWORK_MAP]
        assert "AppKit" in names

    def test_framework_map_entries_have_required_keys(self):
        for entry in _FRAMEWORK_MAP:
            for key in ("macos", "linux_crate", "linux_dep", "note"):
                assert key in entry, f"missing key {key!r} in {entry}"

    def test_lang_fingerprints_are_list(self):
        assert isinstance(_LANG_FINGERPRINTS, list)
        assert len(_LANG_FINGERPRINTS) > 0

    def test_lang_fingerprints_have_required_keys(self):
        for fp in _LANG_FINGERPRINTS:
            for key in ("language", "symbols", "strings"):
                assert key in fp


# ---------------------------------------------------------------------------
# MachoAnalyzer — unit tests
# ---------------------------------------------------------------------------

class TestMachoAnalyzer:
    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            MachoAnalyzer(str(tmp_path / "ghost.bin")).analyze()

    def test_non_macho_raises(self, tmp_path):
        bad = tmp_path / "not_macho.bin"
        _write_non_macho(bad)
        with pytest.raises(ValueError, match="Not a Mach-O"):
            MachoAnalyzer(str(bad)).analyze()

    def test_too_small_file_raises(self, tmp_path):
        tiny = tmp_path / "tiny.bin"
        tiny.write_bytes(b"\xFF\xFF")  # less than 4 bytes of magic
        with pytest.raises(ValueError):
            MachoAnalyzer(str(tiny)).analyze()

    def test_analyze_64bit_returns_required_keys(self, tmp_path):
        m = tmp_path / "app64"
        _write_macho64(m)
        result = MachoAnalyzer(str(m)).analyze()
        for key in ("path", "size_bytes", "sha256", "macho_header",
                    "frameworks", "dylibs", "linux_mapping",
                    "language", "stripped", "build_uuid"):
            assert key in result, f"missing key: {key}"

    def test_analyze_64bit_path_is_string(self, tmp_path):
        m = tmp_path / "app64"
        _write_macho64(m)
        result = MachoAnalyzer(str(m)).analyze()
        assert isinstance(result["path"], str)

    def test_analyze_64bit_size_positive(self, tmp_path):
        m = tmp_path / "app64"
        _write_macho64(m)
        result = MachoAnalyzer(str(m)).analyze()
        assert result["size_bytes"] > 0

    def test_analyze_64bit_sha256_valid_hex(self, tmp_path):
        import hashlib
        m = tmp_path / "app64"
        _write_macho64(m)
        result = MachoAnalyzer(str(m)).analyze()
        sha = result["sha256"]
        assert len(sha) == 64
        int(sha, 16)  # must be valid hex

    def test_analyze_header_not_fat(self, tmp_path):
        m = tmp_path / "app64"
        _write_macho64(m)
        header = MachoAnalyzer(str(m)).analyze()["macho_header"]
        assert header.get("is_fat") is False

    def test_analyze_header_64bit(self, tmp_path):
        m = tmp_path / "app64"
        _write_macho64(m)
        header = MachoAnalyzer(str(m)).analyze()["macho_header"]
        assert header.get("is_64bit") is True

    def test_analyze_header_cpu_x86_64(self, tmp_path):
        m = tmp_path / "app64"
        _write_macho64(m)
        header = MachoAnalyzer(str(m)).analyze()["macho_header"]
        assert "x86" in header.get("cpu", "").lower() or "64" in header.get("cpu", "")

    def test_analyze_32bit_returns_required_keys(self, tmp_path):
        m = tmp_path / "app32"
        _write_macho32(m)
        result = MachoAnalyzer(str(m)).analyze()
        for key in ("path", "size_bytes", "macho_header", "frameworks",
                    "dylibs", "linux_mapping", "language"):
            assert key in result

    def test_analyze_32bit_not_64bit(self, tmp_path):
        m = tmp_path / "app32"
        _write_macho32(m)
        header = MachoAnalyzer(str(m)).analyze()["macho_header"]
        assert header.get("is_64bit") is False

    def test_detect_frameworks_from_dylibs(self):
        dylibs = [
            "/System/Library/Frameworks/Metal.framework/Versions/A/Metal",
            "/System/Library/Frameworks/AppKit.framework/Versions/A/AppKit",
        ]
        frameworks = MachoAnalyzer._detect_frameworks(dylibs)
        assert "Metal" in frameworks
        assert "AppKit" in frameworks

    def test_detect_frameworks_swift_runtime(self):
        dylibs = ["/usr/lib/swift/libswiftCore.dylib"]
        frameworks = MachoAnalyzer._detect_frameworks(dylibs)
        assert any("swift" in f.lower() for f in frameworks)

    def test_detect_frameworks_empty(self):
        assert MachoAnalyzer._detect_frameworks([]) == []

    def test_map_to_linux_metal(self):
        mapping = MachoAnalyzer._map_to_linux(["Metal"])
        assert any(e["linux_crate"] == "wgpu" for e in mapping)

    def test_map_to_linux_appkit(self):
        mapping = MachoAnalyzer._map_to_linux(["AppKit"])
        assert any("winit" in e["linux_crate"] for e in mapping)

    def test_map_to_linux_unknown_framework(self):
        # Unknown frameworks return empty mapping
        mapping = MachoAnalyzer._map_to_linux(["SomeFakeFrameworkXYZ"])
        assert mapping == []

    def test_map_to_linux_empty(self):
        assert MachoAnalyzer._map_to_linux([]) == []

    def test_frameworks_list(self, tmp_path):
        m = tmp_path / "app"
        _write_macho64(m)
        fws = MachoAnalyzer(str(m)).analyze()["frameworks"]
        assert isinstance(fws, list)

    def test_linux_mapping_list(self, tmp_path):
        m = tmp_path / "app"
        _write_macho64(m)
        mapping = MachoAnalyzer(str(m)).analyze()["linux_mapping"]
        assert isinstance(mapping, list)

    def test_dylibs_list(self, tmp_path):
        m = tmp_path / "app"
        _write_macho64(m)
        dylibs = MachoAnalyzer(str(m)).analyze()["dylibs"]
        assert isinstance(dylibs, list)


# ---------------------------------------------------------------------------
# DmgRipper helpers — static methods, no real DMG needed
# ---------------------------------------------------------------------------

class TestDmgRipperHelpers:
    def test_is_macho_64(self, tmp_path):
        m = tmp_path / "app"
        _write_macho64(m)
        assert DmgRipper._is_macho(str(m))

    def test_is_macho_32(self, tmp_path):
        m = tmp_path / "app32"
        _write_macho32(m)
        assert DmgRipper._is_macho(str(m))

    def test_is_macho_not_macho(self, tmp_path):
        f = tmp_path / "text.txt"
        f.write_bytes(b"hello world")
        assert not DmgRipper._is_macho(str(f))

    def test_is_macho_missing_file(self, tmp_path):
        assert not DmgRipper._is_macho(str(tmp_path / "ghost"))

    def test_is_macho_too_small(self, tmp_path):
        f = tmp_path / "tiny.bin"
        f.write_bytes(b"\xCF")
        assert not DmgRipper._is_macho(str(f))

    def test_collect_macho_copies_binaries(self, tmp_path):
        macho_dir = tmp_path / "macho"
        macho_dir.mkdir()
        src_dir = tmp_path / "extracted"
        src_dir.mkdir()

        m = src_dir / "app_binary"
        _write_macho64(m)
        txt = src_dir / "readme.txt"
        _write_non_macho(txt)

        ripper = DmgRipper(str(tmp_path / "fake.dmg"), str(tmp_path / "out"))
        preserved = ripper._collect_macho([str(m), str(txt)], macho_dir)

        assert len(preserved) == 1
        assert Path(preserved[0]).exists()

    def test_collect_macho_deduplicates_names(self, tmp_path):
        macho_dir = tmp_path / "macho"
        macho_dir.mkdir()

        paths = []
        for i in range(3):
            d = tmp_path / f"dir{i}"
            d.mkdir()
            p = d / "samename"
            _write_macho64(p)
            paths.append(str(p))

        ripper = DmgRipper(str(tmp_path / "fake.dmg"), str(tmp_path / "out"))
        preserved = ripper._collect_macho(paths, macho_dir)
        assert len(preserved) == 3
        names = [Path(p).name for p in preserved]
        assert len(set(names)) == 3

    def test_collect_sources_categorises_by_extension(self, tmp_path):
        src_dir = tmp_path / "extracted"
        src_dir.mkdir()
        (src_dir / "main.swift").write_text("let x = 1", encoding="utf-8")
        (src_dir / "Info.plist").write_text("<plist/>", encoding="utf-8")
        (src_dir / "config.json").write_text("{}", encoding="utf-8")
        # Mach-O should be excluded
        m = src_dir / "binary"
        _write_macho64(m)

        sources_dir = tmp_path / "sources"
        sources_dir.mkdir()

        ripper = DmgRipper(str(tmp_path / "fake.dmg"), str(tmp_path / "out"))
        all_files = [str(f) for f in src_dir.iterdir()]
        result = ripper._collect_sources(all_files, sources_dir)

        all_names = [Path(p).name
                     for files in result.values() for p in files]
        assert "binary" not in all_names
        assert "swift_source" in result
        assert "plists" in result

    def test_collect_sources_unknown_extension_other_files(self, tmp_path):
        src_dir = tmp_path / "extracted"
        src_dir.mkdir()
        (src_dir / "mystery.xyz9999").write_text("data", encoding="utf-8")

        sources_dir = tmp_path / "sources"
        sources_dir.mkdir()

        ripper = DmgRipper(str(tmp_path / "fake.dmg"), str(tmp_path / "out"))
        result = ripper._collect_sources(
            [str(src_dir / "mystery.xyz9999")], sources_dir
        )
        assert "other_files" in result

    def test_parse_plist_text_xml_name_and_version(self, tmp_path):
        plist = tmp_path / "Info.plist"
        plist.write_text("""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
        "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>TestApp</string>
    <key>CFBundleShortVersionString</key>
    <string>2.3.4</string>
</dict>
</plist>
""", encoding="utf-8")
        name, version = DmgRipper._parse_plist(plist)
        assert name == "TestApp"
        assert version == "2.3.4"

    def test_parse_plist_missing_keys_returns_unknown(self, tmp_path):
        plist = tmp_path / "Info.plist"
        plist.write_text("<plist><dict></dict></plist>", encoding="utf-8")
        name, version = DmgRipper._parse_plist(plist)
        assert name == "unknown"
        assert version == "unknown"

    def test_detect_app_bundle_finds_app_dir(self, tmp_path):
        app_dir = tmp_path / "MyApp.app"
        app_dir.mkdir()
        (app_dir / "Contents").mkdir()

        name, version = DmgRipper._detect_app_bundle(tmp_path)
        assert name == "MyApp"

    def test_detect_app_bundle_reads_plist(self, tmp_path):
        app_dir = tmp_path / "SomeApp.app" / "Contents"
        app_dir.mkdir(parents=True)
        plist = app_dir / "Info.plist"
        plist.write_text("""<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>SomeApp</string>
    <key>CFBundleShortVersionString</key>
    <string>3.0</string>
</dict>
</plist>""", encoding="utf-8")

        name, version = DmgRipper._detect_app_bundle(tmp_path)
        assert name == "SomeApp"
        assert version == "3.0"

    def test_build_summary_empty(self):
        summary = DmgRipper._build_summary("MyApp", "1.0", [], {})
        assert summary["app_name"] == "MyApp"
        assert summary["app_version"] == "1.0"
        assert summary["macho_count"] == 0
        assert summary["dominant_language"] == "unknown"

    def test_build_summary_language_breakdown(self):
        analyses = [
            {"path": "/a", "language": "Rust", "frameworks": ["Metal"],
             "linux_mapping": [{"linux_dep": "wgpu"}],
             "stripped": False, "macho_header": {"is_fat": False}},
            {"path": "/b", "language": "Rust", "frameworks": [],
             "linux_mapping": [],
             "stripped": True, "macho_header": {"is_fat": True}},
        ]
        summary = DmgRipper._build_summary("App", "1.0", analyses, {})
        assert summary["dominant_language"] == "Rust"
        assert summary["language_breakdown"]["Rust"] == 2
        assert summary["stripped_binaries"] == 1
        assert summary["fat_binaries"] == 1

    def test_build_summary_error_counted(self):
        analyses = [{"path": "/bad", "error": "parse failed"}]
        summary = DmgRipper._build_summary("App", "1.0", analyses, {})
        assert summary["error_count"] == 1

    def test_build_summary_framework_breakdown(self):
        analyses = [
            {"path": "/a", "language": "Rust", "frameworks": ["Metal", "AppKit"],
             "linux_mapping": [], "stripped": False,
             "macho_header": {"is_fat": False}},
        ]
        summary = DmgRipper._build_summary("App", "2.0", analyses, {})
        assert "Metal" in summary["macos_frameworks"]
        assert "AppKit" in summary["macos_frameworks"]

    def test_build_summary_source_categories(self):
        source_files = {
            "swift_source": ["/a.swift", "/b.swift"],
            "plists": ["/Info.plist"],
        }
        summary = DmgRipper._build_summary("App", "1.0", [], source_files)
        assert summary["source_file_categories"]["swift_source"] == 2
        assert summary["source_file_categories"]["plists"] == 1
        assert summary["total_source_artefacts"] == 3

    def test_rip_raises_for_missing_dmg(self, tmp_path):
        with pytest.raises(FileNotFoundError, match="DMG not found"):
            DmgRipper(str(tmp_path / "ghost.dmg"), str(tmp_path / "out")).rip()

    def test_rip_with_no_extraction_tools_produces_report(self, tmp_path):
        """
        When no extraction tools are available, rip() should still write a
        report JSON with an empty extracted list.
        """
        dmg = tmp_path / "fake.dmg"
        dmg.write_bytes(b"\x00" * 100)
        out_dir = tmp_path / "out"

        with patch.object(DmgRipper, "_extract", return_value=[]):
            report = DmgRipper(str(dmg), str(out_dir)).rip()

        assert "macho_files" in report
        assert "source_files" in report
        report_json = out_dir / "analysis_report.json"
        assert report_json.exists()

    def test_source_categories_dict_coverage(self):
        cats = DmgRipper._SOURCE_CATEGORIES
        for ext in (".swift", ".m", ".plist", ".strings", ".storyboard",
                    ".json", ".md", ".entitlements"):
            assert ext in cats, f"extension {ext!r} not in _SOURCE_CATEGORIES"


# ---------------------------------------------------------------------------
# LinuxPortingScaffold — scaffold generation
# ---------------------------------------------------------------------------

class TestLinuxPortingScaffold:
    def test_generate_rust_creates_cargo_toml(self, tmp_path):
        report = _make_fake_rip_report(language="Rust")
        result = LinuxPortingScaffold(report).generate(str(tmp_path / "port"))
        created = result["files_created"]
        names = [Path(f).name for f in created]
        assert "Cargo.toml" in names

    def test_generate_rust_creates_main_rs(self, tmp_path):
        report = _make_fake_rip_report(language="Rust")
        result = LinuxPortingScaffold(report).generate(str(tmp_path / "port"))
        names = [Path(f).name for f in result["files_created"]]
        assert "main.rs" in names

    def test_generate_writes_porting_notes(self, tmp_path):
        report = _make_fake_rip_report()
        result = LinuxPortingScaffold(report).generate(str(tmp_path / "port"))
        names = [Path(f).name for f in result["files_created"]]
        assert "PORTING_NOTES.md" in names

    def test_generate_writes_readme(self, tmp_path):
        report = _make_fake_rip_report()
        result = LinuxPortingScaffold(report).generate(str(tmp_path / "port"))
        names = [Path(f).name for f in result["files_created"]]
        assert "README.md" in names

    def test_generate_writes_reconstruction_notes(self, tmp_path):
        report = _make_fake_rip_report()
        result = LinuxPortingScaffold(report).generate(str(tmp_path / "port"))
        names = [Path(f).name for f in result["files_created"]]
        assert "RECONSTRUCTION_NOTES.md" in names

    def test_generate_returns_required_keys(self, tmp_path):
        report = _make_fake_rip_report()
        result = LinuxPortingScaffold(report).generate(str(tmp_path / "port"))
        for key in ("output_dir", "app_name", "dominant_language",
                    "files_created", "system_packages"):
            assert key in result

    def test_generate_app_name_in_result(self, tmp_path):
        report = _make_fake_rip_report(app_name="MyApp")
        result = LinuxPortingScaffold(report).generate(str(tmp_path / "port"))
        assert result["app_name"] == "MyApp"

    def test_generate_language_in_result(self, tmp_path):
        report = _make_fake_rip_report(language="Rust")
        result = LinuxPortingScaffold(report).generate(str(tmp_path / "port"))
        assert result["dominant_language"] == "Rust"

    def test_generate_files_created_non_empty(self, tmp_path):
        report = _make_fake_rip_report()
        result = LinuxPortingScaffold(report).generate(str(tmp_path / "port"))
        assert len(result["files_created"]) > 0

    def test_generate_go_scaffold(self, tmp_path):
        report = _make_fake_rip_report(language="Go")
        result = LinuxPortingScaffold(report).generate(str(tmp_path / "port"))
        names = [Path(f).name for f in result["files_created"]]
        assert "go.mod" in names

    def test_generate_ci_workflow_file(self, tmp_path):
        report = _make_fake_rip_report()
        result = LinuxPortingScaffold(report).generate(str(tmp_path / "port"))
        # CI workflow should be somewhere in .github/workflows
        workflow_files = [f for f in result["files_created"]
                          if "workflow" in Path(f).name.lower()
                          or f.endswith(".yml")]
        assert len(workflow_files) >= 1

    def test_cargo_toml_contains_app_name(self, tmp_path):
        report = _make_fake_rip_report(app_name="WarpTerminal")
        out = tmp_path / "port"
        LinuxPortingScaffold(report).generate(str(out))
        cargo = (out / "Cargo.toml").read_text(encoding="utf-8")
        assert "warp" in cargo.lower() or "warp-terminal" in cargo.lower()

    def test_cargo_toml_contains_wgpu_dep(self, tmp_path):
        report = _make_fake_rip_report(
            language="Rust",
            frameworks=["Metal"],
            linux_mapping=[
                {"macos": "Metal", "linux_crate": "wgpu",
                 "linux_dep": 'wgpu = "0.20"', "note": ""}
            ],
        )
        out = tmp_path / "port"
        LinuxPortingScaffold(report).generate(str(out))
        cargo = (out / "Cargo.toml").read_text(encoding="utf-8")
        assert "wgpu" in cargo

    def test_system_packages_dict(self, tmp_path):
        pkgs = LinuxPortingScaffold._SYSTEM_PKGS
        assert "wgpu" in pkgs
        assert "winit" in pkgs
        assert isinstance(pkgs["wgpu"], list)

    def test_collect_all_mappings_deduplicates(self):
        mapping = [
            {"macos": "Metal",  "linux_crate": "wgpu",
             "linux_dep": 'wgpu = "0.20"', "note": ""},
        ]
        report = _make_fake_rip_report(
            linux_mapping=mapping,
        )
        # Duplicate entries in multiple binaries
        report["macho_files"] = [
            {**report["macho_files"][0], "linux_mapping": mapping},
            {**report["macho_files"][0], "linux_mapping": mapping},
        ]
        scaffold = LinuxPortingScaffold(report)
        # No crashes — deduplication should be handled
        assert scaffold.all_mappings is not None

    def test_required_system_packages_returns_list(self):
        report = _make_fake_rip_report()
        scaffold = LinuxPortingScaffold(report)
        pkgs = scaffold._required_system_packages()
        assert isinstance(pkgs, list)
