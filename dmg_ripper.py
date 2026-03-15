#!/usr/bin/env python3
"""
DMG Ripper, Mach-O Analyzer & Linux Porter
============================================
Part of THE FORGE toolkit.

─────────────────────────────────────────────────────────────────────────────
WHAT THIS DOES
─────────────────────────────────────────────────────────────────────────────
1. Extracts a macOS DMG disk image on Linux (no Mac needed).
2. Finds all Mach-O binaries (the macOS equivalent of ELF files).
3. Analyses each binary: architecture, language runtime, shared frameworks.
4. Generates a complete Linux porting scaffold — the build files, dependency
   mappings, and stub source files needed to rebuild the app on Linux.

Example target: Warp terminal (https://www.warp.dev/terminal)
  • Rust binary
  • Metal GPU rendering → ported to wgpu (already cross-platform)
  • AppKit / NSWindow   → ported to winit + glutin
  • WebKit (macOS)      → ported to webkit2gtk
  • CoreText            → ported to fontconfig + cosmic-text
  Note: Warp officially released a Linux version in 2024. This tool
  produces the porting scaffold regardless, and notes when an official
  Linux release already exists.

─────────────────────────────────────────────────────────────────────────────
WHAT IS A MACH-O BINARY?
─────────────────────────────────────────────────────────────────────────────
Mach-O (Mach Object) is the macOS / iOS equivalent of Linux ELF. Like ELF:
  • It is a COMPILED BINARY — not source code.
  • It starts with a magic number (0xFEEDFACF for 64-bit).
  • It has load commands listing shared frameworks (like ELF's .dynamic).
  • It can be a "fat binary" (universal) containing slices for multiple
    CPU architectures (x86_64 + arm64).
  • It can carry DWARF debug info (same format as Linux ELF).
Source recovery from Mach-O follows the same layered approach as ELF:
DWARF → symbols → strings → disassembly (otool/objdump) → Ghidra.

─────────────────────────────────────────────────────────────────────────────
PLATFORM API MAPPING  (macOS → Linux)
─────────────────────────────────────────────────────────────────────────────
macOS framework         Linux replacement
─────────────────────   ──────────────────────────────────────────────────
Metal                   wgpu / Vulkan / ash / OpenGL (glium/glutin)
AppKit / NSWindow       winit + softbuffer  OR  gtk-rs / iced / egui
CoreText / CoreGraphics cosmic-text + fontconfig + freetype-rs
WebKit (WKWebView)      webkit2gtk-rs  (WebKit2GTK)
AVFoundation            GStreamer (gstreamer-rs bindings)
CoreAudio               cpal  (cross-platform audio — ALSA/PipeWire)
Security.framework      rustls  OR  openssl (openssl-sys)
CoreFoundation          std  (Rust standard library covers most of this)
Grand Central Dispatch  tokio / rayon
XPC / launchd           zbus (D-Bus)  OR  Unix sockets
Keychain Services       secret-service (libsecret / gnome-keyring)
CoreLocation            geoclue2 via D-Bus
Accessibility (AX)      atspi2 (AT-SPI)
IOKit                   udev-rs / sysfs
NSUserDefaults          dirs-rs + serde + TOML/JSON config files
Sparkle (auto-update)   self_update crate

─────────────────────────────────────────────────────────────────────────────
USAGE
─────────────────────────────────────────────────────────────────────────────
Library:
    from dmg_ripper import DmgRipper, MachoAnalyzer, LinuxPortingScaffold

    report = DmgRipper("Warp.dmg", output_dir="out/").rip()
    scaffold = LinuxPortingScaffold(report).generate(output_dir="linux_port/")

CLI:
    # Rip a DMG and analyse all Mach-O binaries
    python3 dmg_ripper.py Warp.dmg -o out/

    # Analyse a single Mach-O binary you already have
    python3 dmg_ripper.py --analyze-only out/macho/warp

    # Full pipeline: rip + analyse + generate Linux porting scaffold
    python3 dmg_ripper.py Warp.dmg -o out/ --port-to-linux linux_port/

    # Analyse then port without re-ripping (use existing rip report)
    python3 dmg_ripper.py --port-from-report out/analysis_report.json \\
                          --port-to-linux linux_port/
"""

import argparse
import hashlib
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Mach-O constants
# ---------------------------------------------------------------------------

# Magic numbers (little-endian on x86/arm)
MACHO_MAGIC_32     = 0xFEEDFACE   # 32-bit, native-endian
MACHO_MAGIC_64     = 0xFEEDFACF   # 64-bit, native-endian
MACHO_MAGIC_FAT    = 0xCAFEBABE   # Universal / fat binary
MACHO_MAGIC_32_BE  = 0xCEFAEDFE  # 32-bit, big-endian (PPC)
MACHO_MAGIC_64_BE  = 0xCFFAEDFE  # 64-bit, big-endian

_ALL_MACHO_MAGICS = {
    MACHO_MAGIC_32, MACHO_MAGIC_64, MACHO_MAGIC_FAT,
    MACHO_MAGIC_32_BE, MACHO_MAGIC_64_BE,
}

# CPU types
_CPU_TYPE: Dict[int, str] = {
    0x00000007: "x86",
    0x01000007: "x86-64",
    0x0000000C: "ARM",
    0x0100000C: "AArch64 (Apple Silicon)",
    0x00000012: "PowerPC",
    0x01000012: "PowerPC-64",
}

# File types
_FILE_TYPE: Dict[int, str] = {
    0x1: "object",
    0x2: "executable",
    0x6: "dylib (shared library)",
    0x8: "bundle (plugin)",
    0xA: "dylinker",
    0xB: "bundle (kernel extension)",
}

# Load command types we care about
LC_LOAD_DYLIB         = 0xC   # imported shared library
LC_RPATH              = 0x1C  # runtime search path
LC_ID_DYLIB           = 0xD   # this binary's dylib identity
LC_BUILD_VERSION      = 0x32  # min OS version
LC_SOURCE_VERSION     = 0x2A  # source version tag
LC_UUID               = 0x1B  # UUID (like GNU build-id)

# Known macOS frameworks and their Linux equivalents
_FRAMEWORK_MAP: List[Dict[str, str]] = [
    {
        "macos": "Metal",
        "linux_crate": "wgpu",
        "linux_dep": 'wgpu = "0.20"',
        "note": "wgpu is already cross-platform (Vulkan/OpenGL/Metal). "
                "Replace MTLDevice, MTLCommandQueue etc. with wgpu Device, Queue.",
    },
    {
        "macos": "AppKit",
        "linux_crate": "winit + softbuffer",
        "linux_dep": 'winit = "0.29"\nsoftbuffer = "0.4"',
        "note": "Replace NSWindow/NSView with winit Window. "
                "Use softbuffer for 2D rendering or wgpu for GPU.",
    },
    {
        "macos": "CoreText",
        "linux_crate": "cosmic-text + fontconfig",
        "linux_dep": 'cosmic-text = "0.12"\nfontconfig = "0.5"',
        "note": "cosmic-text handles font shaping + layout cross-platform. "
                "Use fontconfig-rs to enumerate system fonts.",
    },
    {
        "macos": "WebKit",
        "linux_crate": "webkit2gtk",
        "linux_dep": 'webkit2gtk = { version = "2", features = ["v2_40"] }',
        "note": "webkit2gtk provides WKWebView equivalent on Linux. "
                "Requires libwebkit2gtk-4.1-dev system package.",
    },
    {
        "macos": "CoreAudio",
        "linux_crate": "cpal",
        "linux_dep": 'cpal = "0.15"',
        "note": "cpal abstracts ALSA/PipeWire/JACK on Linux transparently.",
    },
    {
        "macos": "AVFoundation",
        "linux_crate": "gstreamer",
        "linux_dep": 'gstreamer = "0.22"\ngstreamer-app = "0.22"',
        "note": "GStreamer covers audio/video capture and playback on Linux.",
    },
    {
        "macos": "Security",
        "linux_crate": "rustls",
        "linux_dep": 'rustls = "0.23"\nrustls-native-certs = "0.7"',
        "note": "rustls is a pure-Rust TLS stack that works identically on Linux.",
    },
    {
        "macos": "CoreFoundation",
        "linux_crate": "(std)",
        "linux_dep": "# CoreFoundation is mostly covered by Rust std.",
        "note": "CFString → std::str, CFData → Vec<u8>, CFRunLoop → tokio runtime.",
    },
    {
        "macos": "CoreGraphics",
        "linux_crate": "tiny-skia",
        "linux_dep": 'tiny-skia = "0.11"',
        "note": "tiny-skia provides a pure-Rust 2D rasteriser (Skia-compatible API).",
    },
    {
        "macos": "IOKit",
        "linux_crate": "udev",
        "linux_dep": 'udev = "0.8"',
        "note": "udev-rs gives access to Linux device events (USB, input, etc.).",
    },
    {
        "macos": "XPC",
        "linux_crate": "zbus",
        "linux_dep": 'zbus = "4"',
        "note": "zbus implements D-Bus in pure Rust; use for IPC between processes.",
    },
    {
        "macos": "Keychain",
        "linux_crate": "secret-service",
        "linux_dep": 'secret-service = "3"',
        "note": "secret-service talks to libsecret / GNOME Keyring / KWallet.",
    },
    {
        "macos": "Accessibility",
        "linux_crate": "atspi",
        "linux_dep": 'atspi = "0.19"',
        "note": "atspi implements AT-SPI2 (Linux accessibility bus) in Rust.",
    },
]

# Language fingerprints in Mach-O symbol names
_LANG_FINGERPRINTS: List[Dict[str, Any]] = [
    {
        "language": "Rust",
        "symbols": ["__rust_alloc", "rust_begin_unwind", "_ZN4core", "__rust_dealloc"],
        "strings": ["panicked at", "rust_panic_handler"],
    },
    {
        "language": "Go",
        "symbols": ["runtime.main", "runtime.goexit", "main.main"],
        "strings": ["go:buildid", "runtime.main"],
    },
    {
        "language": "Swift",
        "symbols": ["_swift_allocObject", "_swift_release", "$s"],
        "strings": ["Swift runtime", "_TtC"],
    },
    {
        "language": "Objective-C",
        "symbols": ["_objc_msgSend", "_NSLog", "_CFRelease"],
        "strings": [],
    },
    {
        "language": "Python (C extension)",
        "symbols": ["PyInit_", "Py_InitModule"],
        "strings": [],
    },
]


# ---------------------------------------------------------------------------
# MachoAnalyzer
# ---------------------------------------------------------------------------

class MachoAnalyzer:
    """
    Analyses a single Mach-O binary (macOS/iOS executable or dylib).

    Parses the Mach-O header, extracts load commands to find imported
    frameworks, detects the language runtime, and fingerprints the
    platform APIs used — mapping each to its Linux equivalent.
    """

    def __init__(self, path: str):
        self.path = Path(path)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze(self) -> Dict[str, Any]:
        """
        Return a structured analysis dict for the Mach-O binary.

        Keys
        ----
        path            Absolute path.
        size_bytes      File size.
        sha256          SHA-256 digest.
        macho_header    Parsed header: arch, file_type, is_fat, slices.
        frameworks      macOS frameworks imported (e.g. Metal, AppKit).
        dylibs          Raw list of LC_LOAD_DYLIB entries.
        linux_mapping   List of {macos, linux_crate, linux_dep, note} dicts.
        language        Detected language runtime.
        stripped        True if no symbol table.
        build_uuid      Mach-O UUID (like GNU build-id).
        """
        if not self.path.exists():
            raise FileNotFoundError(f"Mach-O file not found: {self.path}")

        with open(self.path, "rb") as fh:
            raw_header = fh.read(8)

        if len(raw_header) < 4:
            raise ValueError(f"File too small to be Mach-O: {self.path}")

        magic = struct.unpack_from("<I", raw_header)[0]
        if magic not in _ALL_MACHO_MAGICS:
            raise ValueError(f"Not a Mach-O binary (magic=0x{magic:08x}): {self.path}")

        result: Dict[str, Any] = {
            "path": str(self.path),
            "size_bytes": self.path.stat().st_size,
            "sha256": self._sha256(),
            "macho_header": self._parse_header(magic),
            "dylibs": self._get_dylibs(),
            "frameworks": [],
            "linux_mapping": [],
            "language": "unknown",
            "stripped": self._is_stripped(),
            "build_uuid": self._get_uuid(),
        }

        result["frameworks"] = self._detect_frameworks(result["dylibs"])
        result["linux_mapping"] = self._map_to_linux(result["frameworks"])
        result["language"] = self._detect_language()
        return result

    # ------------------------------------------------------------------
    # Parsing helpers
    # ------------------------------------------------------------------

    def _sha256(self) -> str:
        h = hashlib.sha256()
        with open(self.path, "rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

    def _parse_header(self, magic: int) -> Dict[str, Any]:
        """Parse the Mach-O header fields."""
        is_fat = magic == MACHO_MAGIC_FAT
        is_be = magic in (MACHO_MAGIC_32_BE, MACHO_MAGIC_64_BE)
        endian = ">" if is_be else "<"
        is_64 = magic in (MACHO_MAGIC_64, MACHO_MAGIC_64_BE)

        with open(self.path, "rb") as fh:
            data = fh.read(28)

        if is_fat:
            # fat_header: magic(4) + nfat_arch(4)
            nfat = struct.unpack_from(">I", data, 4)[0]
            slices = self._parse_fat_slices(nfat)
            return {"is_fat": True, "slices": slices}

        # mach_header: magic(4) cputype(4) cpusubtype(4) filetype(4) ...
        cputype  = struct.unpack_from(endian + "i", data, 4)[0]
        filetype = struct.unpack_from(endian + "I", data, 12)[0]
        return {
            "is_fat": False,
            "is_64bit": is_64,
            "cpu": _CPU_TYPE.get(cputype & 0x01FFFFFF,
                                  f"unknown (0x{cputype:08x})"),
            "file_type": _FILE_TYPE.get(filetype, f"unknown ({filetype})"),
        }

    def _parse_fat_slices(self, nfat: int) -> List[Dict[str, str]]:
        """Parse fat_arch structs to list the architectures in a universal binary."""
        slices = []
        with open(self.path, "rb") as fh:
            fh.seek(8)  # skip magic + nfat_arch
            for _ in range(min(nfat, 8)):
                raw = fh.read(20)
                if len(raw) < 20:
                    break
                cputype = struct.unpack_from(">i", raw, 0)[0]
                slices.append({
                    "cpu": _CPU_TYPE.get(cputype & 0x01FFFFFF,
                                          f"unknown (0x{cputype:08x})"),
                })
        return slices

    def _run(self, *args: str) -> str:
        """Run a command; return stdout or empty string on error."""
        try:
            proc = subprocess.run(
                list(args), capture_output=True, text=True, timeout=60
            )
            return proc.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return ""

    def _get_dylibs(self) -> List[str]:
        """
        Return imported dylib paths from LC_LOAD_DYLIB load commands.

        Tries ``otool -L`` (macOS) first, falls back to parsing the
        binary header directly so this works on Linux.
        """
        if shutil.which("otool"):
            out = self._run("otool", "-L", str(self.path))
            libs: List[str] = []
            for line in out.splitlines()[1:]:
                line = line.strip()
                if line and not line.startswith("Archive"):
                    # Format: /path/to/lib.dylib (compatibility version ...)
                    lib_path = line.split("(")[0].strip()
                    if lib_path:
                        libs.append(lib_path)
            return libs

        # Linux fallback: parse load commands with struct
        return self._parse_load_dylibs()

    def _parse_load_dylibs(self) -> List[str]:
        """Parse LC_LOAD_DYLIB entries directly from the binary."""
        libs: List[str] = []
        try:
            with open(self.path, "rb") as fh:
                data = fh.read()

            magic = struct.unpack_from("<I", data)[0]
            if magic == MACHO_MAGIC_FAT:
                # For fat binaries, just scan the first slice offset
                nfat = struct.unpack_from(">I", data, 4)[0]
                if nfat > 0:
                    offset = struct.unpack_from(">I", data, 20)[0]
                    data = data[offset:]
                    magic = struct.unpack_from("<I", data)[0]

            is_be = magic in (MACHO_MAGIC_32_BE, MACHO_MAGIC_64_BE)
            endian = ">" if is_be else "<"
            is_64 = magic in (MACHO_MAGIC_64, MACHO_MAGIC_64_BE)
            hdr_size = 32 if is_64 else 28
            ncmds = struct.unpack_from(endian + "I", data, 16)[0]

            offset = hdr_size
            for _ in range(min(ncmds, 512)):
                if offset + 8 > len(data):
                    break
                cmd, cmdsize = struct.unpack_from(endian + "II", data, offset)
                if cmdsize < 8:
                    break
                if cmd == LC_LOAD_DYLIB:
                    # dylib struct: name_offset(4) timestamp(4) current(4) compat(4)
                    name_off = struct.unpack_from(endian + "I", data, offset + 8)[0]
                    str_start = offset + name_off
                    str_end = offset + cmdsize
                    raw = data[str_start:str_end]
                    lib_name = raw.split(b"\x00")[0].decode("utf-8", errors="replace")
                    if lib_name:
                        libs.append(lib_name)
                offset += cmdsize
        except (struct.error, IndexError, OSError):
            pass
        return libs

    def _is_stripped(self) -> bool:
        """Return True if the binary has no symbol table (nm returns nothing)."""
        out = self._run("nm", str(self.path))
        return not bool(out.strip())

    def _get_uuid(self) -> Optional[str]:
        """Return the Mach-O UUID from LC_UUID."""
        if shutil.which("otool"):
            out = self._run("otool", "-l", str(self.path))
            for i, line in enumerate(out.splitlines()):
                if "LC_UUID" in line:
                    for j in range(i, min(i + 5, len(out.splitlines()))):
                        next_line = out.splitlines()[j]
                        if "uuid" in next_line.lower():
                            return next_line.split()[-1].strip()
        return None

    # ------------------------------------------------------------------
    # Detection helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _detect_frameworks(dylibs: List[str]) -> List[str]:
        """Extract framework names from dylib paths."""
        frameworks: List[str] = []
        for lib in dylibs:
            # e.g. /System/Library/Frameworks/Metal.framework/Versions/A/Metal
            if ".framework/" in lib:
                name = lib.split(".framework/")[0].rsplit("/", 1)[-1]
                if name not in frameworks:
                    frameworks.append(name)
            # Also look for /usr/lib/swift/ entries
            elif "/swift/" in lib.lower():
                if "Swift runtime" not in frameworks:
                    frameworks.append("Swift runtime")
        return frameworks

    @staticmethod
    def _map_to_linux(frameworks: List[str]) -> List[Dict[str, str]]:
        """Return Linux mapping entries for each detected macOS framework."""
        mapping = []
        for fw in frameworks:
            for entry in _FRAMEWORK_MAP:
                if entry["macos"].lower() == fw.lower() or \
                   fw.lower() in entry["macos"].lower():
                    mapping.append(entry)
                    break
        return mapping

    def _detect_language(self) -> str:
        """Fingerprint language from symbol names and string literals."""
        syms_out = self._run("nm", "--demangle", str(self.path))
        if not syms_out:
            syms_out = ""
        strs_out = self._run("strings", "-n", "8", str(self.path))
        strs = set(strs_out.splitlines()[:2000])

        for fp in _LANG_FINGERPRINTS:
            for sym in fp["symbols"]:
                if sym in syms_out:
                    return fp["language"]
            for needle in fp["strings"]:
                if any(needle in s for s in strs):
                    return fp["language"]

        # Fallback: linked against libc++ → C++, else C
        dylibs = self._get_dylibs()
        if any("libc++" in d or "libstdc++" in d for d in dylibs):
            return "C++"
        return "C/Objective-C"


# ---------------------------------------------------------------------------
# DmgRipper
# ---------------------------------------------------------------------------

class DmgRipper:
    """
    Extracts a macOS DMG disk image on Linux and collects all Mach-O binaries
    and source artefacts (scripts, configs, resources) for analysis.

    Extraction strategy (tried in order):
      1. ``dmg2img`` → converts compressed DMG to a raw HFS+/APFS image,
         then mounts with the loop device (requires sudo) or extracts with
         ``7z x``.
      2. ``7z x`` directly on the DMG — works for many DMG formats
         (UDIF/zlib/bzip2 compressed).
      3. Heuristic scan — walk the raw file looking for embedded ZIP/tar
         archives (some DMGs are just renamed ZIPs).
    """

    def __init__(self, dmg_path: str, output_dir: str = "dmg_ripped"):
        self.dmg_path = Path(dmg_path)
        self.output_dir = Path(output_dir)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def rip(self) -> Dict[str, Any]:
        """
        Full pipeline: extract → collect Mach-O → collect sources → analyse.

        Returns
        -------
        dict with keys:
            dmg_path        Source DMG path.
            output_dir      Output directory.
            app_name        Detected application name (from .app bundle).
            app_version     Detected version (from Info.plist).
            extracted_files Total extracted file count.
            macho_files     List of per-binary analysis dicts.
            source_files    Dict category → list of paths.
            summary         High-level summary.
        """
        if not self.dmg_path.exists():
            raise FileNotFoundError(f"DMG not found: {self.dmg_path}")

        self.output_dir.mkdir(parents=True, exist_ok=True)
        extract_dir  = self.output_dir / "extracted"
        macho_dir    = self.output_dir / "macho"
        sources_dir  = self.output_dir / "sources"
        extract_dir.mkdir(exist_ok=True)
        macho_dir.mkdir(exist_ok=True)
        sources_dir.mkdir(exist_ok=True)

        print(f"💿 Ripping DMG: {self.dmg_path.name}")
        print(f"📁 Output:      {self.output_dir}")

        print("🔧 Extracting DMG contents …")
        extracted = self._extract(extract_dir)
        print(f"   Extracted {len(extracted)} files")
        if not extracted:
            print("   ⚠️  No files extracted — DMG may need a macOS system to mount.")
            print("   Tip: Copy the DMG contents manually into:")
            print(f"        {extract_dir}")

        app_name, app_version = self._detect_app_bundle(extract_dir)
        print(f"   App bundle: {app_name}  version {app_version}")

        print("🔍 Collecting Mach-O binaries …")
        macho_paths = self._collect_macho(extracted, macho_dir)
        print(f"   Found {len(macho_paths)} Mach-O binaries")

        print("📂 Collecting source artefacts …")
        source_files = self._collect_sources(extracted, sources_dir)
        total = sum(len(v) for v in source_files.values())
        print(f"   Found {total} artefacts across {len(source_files)} categories")

        print("🧬 Analysing Mach-O binaries …")
        macho_analyses: List[Dict[str, Any]] = []
        for mp in macho_paths:
            try:
                analysis = MachoAnalyzer(mp).analyze()
                macho_analyses.append(analysis)
                print(f"   ✅ {Path(mp).name}  "
                      f"lang={analysis['language']}  "
                      f"frameworks={analysis['frameworks']}")
            except Exception as exc:
                print(f"   ⚠️  {Path(mp).name}: {exc}")
                macho_analyses.append({"path": mp, "error": str(exc)})

        summary = self._build_summary(
            app_name, app_version, macho_analyses, source_files
        )

        report: Dict[str, Any] = {
            "dmg_path": str(self.dmg_path),
            "output_dir": str(self.output_dir),
            "app_name": app_name,
            "app_version": app_version,
            "extracted_files": len(extracted),
            "macho_files": macho_analyses,
            "source_files": source_files,
            "summary": summary,
        }

        report_path = self.output_dir / "analysis_report.json"
        with open(report_path, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2, ensure_ascii=False)
        print(f"\n📊 Report saved → {report_path}")

        return report

    # ------------------------------------------------------------------
    # Extraction
    # ------------------------------------------------------------------

    def _extract(self, extract_dir: Path) -> List[str]:
        """Try multiple extraction strategies; return list of file paths."""

        # Strategy 1: dmg2img → then 7z on the .img
        if shutil.which("dmg2img"):
            files = self._extract_via_dmg2img(extract_dir)
            if files:
                return files

        # Strategy 2: 7z directly on the .dmg
        if shutil.which("7z"):
            files = self._extract_via_7z(str(self.dmg_path), extract_dir)
            if files:
                return files

        # Strategy 3: nothing worked
        return []

    def _extract_via_dmg2img(self, extract_dir: Path) -> List[str]:
        """Convert DMG → IMG with dmg2img, then extract IMG with 7z."""
        with tempfile.TemporaryDirectory() as tmp:
            img_path = Path(tmp) / "disk.img"
            try:
                subprocess.run(
                    ["dmg2img", "-i", str(self.dmg_path), "-o", str(img_path)],
                    capture_output=True, timeout=120,
                )
            except (subprocess.TimeoutExpired, FileNotFoundError):
                return []

            if not img_path.exists():
                return []

            return self._extract_via_7z(str(img_path), extract_dir)

    def _extract_via_7z(self, archive_path: str, extract_dir: Path) -> List[str]:
        """Extract an archive (DMG or IMG) with 7z."""
        try:
            subprocess.run(
                ["7z", "x", archive_path, f"-o{extract_dir}", "-y"],
                capture_output=True, timeout=120,
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []

        return self._walk(extract_dir)

    @staticmethod
    def _walk(directory: Path) -> List[str]:
        files: List[str] = []
        for root, _dirs, filenames in os.walk(directory):
            for fname in filenames:
                files.append(os.path.join(root, fname))
        return files

    # ------------------------------------------------------------------
    # Mach-O collection
    # ------------------------------------------------------------------

    @staticmethod
    def _is_macho(path: str) -> bool:
        try:
            with open(path, "rb") as fh:
                raw = fh.read(4)
            if len(raw) < 4:
                return False
            magic = struct.unpack_from("<I", raw)[0]
            return magic in _ALL_MACHO_MAGICS
        except (OSError, PermissionError):
            return False

    def _collect_macho(self, all_files: List[str], macho_dir: Path) -> List[str]:
        """Filter Mach-O files, copy to macho_dir, return destination paths."""
        preserved: List[str] = []
        seen: Dict[str, int] = {}

        for src in all_files:
            if not self._is_macho(src):
                continue
            base = Path(src).name
            count = seen.get(base, 0)
            seen[base] = count + 1
            dest_name = base if count == 0 else f"{base}.{count}"
            dest = macho_dir / dest_name
            try:
                shutil.copy2(src, dest)
                preserved.append(str(dest))
            except (OSError, PermissionError) as exc:
                print(f"   ⚠️  Could not preserve {src}: {exc}")
        return preserved

    # ------------------------------------------------------------------
    # Source artefact collection
    # ------------------------------------------------------------------

    # File extensions → category
    _SOURCE_CATEGORIES: Dict[str, str] = {
        # Code
        ".swift": "swift_source",
        ".m": "objc_source",
        ".mm": "objcpp_source",
        ".c": "c_source",
        ".cpp": "cpp_source",
        ".cc": "cpp_source",
        ".h": "headers",
        ".hpp": "headers",
        ".rs": "rust_source",
        ".go": "go_source",
        ".py": "python_scripts",
        ".rb": "ruby_scripts",
        ".sh": "shell_scripts",
        ".bash": "shell_scripts",
        ".zsh": "shell_scripts",
        ".js": "javascript",
        ".ts": "typescript",
        # Apple-specific data
        ".plist": "plists",
        ".strings": "localization",
        ".storyboard": "ui_storyboards",
        ".xib": "ui_xibs",
        ".xcassets": "asset_catalogs",
        ".nib": "ui_nibs",
        # Build / project
        ".xcodeproj": "xcode_project",
        ".podspec": "cocoapods_spec",
        ".xcconfig": "xcode_config",
        ".cmake": "cmake_files",
        "makefile": "makefiles",
        # Config / data
        ".json": "json_configs",
        ".toml": "toml_configs",
        ".yaml": "yaml_configs",
        ".yml": "yaml_configs",
        ".conf": "config_files",
        ".ini": "config_files",
        ".env": "env_files",
        # Docs
        ".md": "documentation",
        ".txt": "documentation",
        ".rst": "documentation",
        ".pdf": "documentation",
        # Entitlements / signing
        ".entitlements": "entitlements",
        ".mobileprovision": "provisioning_profiles",
    }

    def _collect_sources(
        self, all_files: List[str], sources_dir: Path
    ) -> Dict[str, List[str]]:
        """
        Categorise and copy all non-Mach-O artefacts from the extracted payload.
        Returns a dict of category → list of preserved destination paths.
        """
        categorised: Dict[str, List[str]] = {}
        seen: Dict[str, int] = {}

        for src in all_files:
            if self._is_macho(src):
                continue  # handled separately

            suffix = Path(src).suffix.lower()
            fname_lower = Path(src).name.lower()
            category = (
                self._SOURCE_CATEGORIES.get(suffix)
                or self._SOURCE_CATEGORIES.get(fname_lower)
                or "other_files"
            )

            cat_dir = sources_dir / category
            cat_dir.mkdir(exist_ok=True)

            base = Path(src).name
            count = seen.get(base, 0)
            seen[base] = count + 1
            dest_name = base if count == 0 else f"{base}.{count}"
            dest = cat_dir / dest_name

            try:
                shutil.copy2(src, dest)
                categorised.setdefault(category, []).append(str(dest))
            except (OSError, PermissionError):
                pass

        return categorised

    # ------------------------------------------------------------------
    # App bundle detection
    # ------------------------------------------------------------------

    @staticmethod
    def _detect_app_bundle(extract_dir: Path) -> Tuple[str, str]:
        """Find the .app bundle and read its Info.plist for name + version."""
        app_name = "unknown"
        app_version = "unknown"

        # Find Info.plist files
        for root, _dirs, files in os.walk(extract_dir):
            for fname in files:
                if fname == "Info.plist":
                    plist_path = Path(root) / fname
                    name, version = DmgRipper._parse_plist(plist_path)
                    if name != "unknown":
                        return name, version

            # Also detect .app directories
            for d in _dirs:
                if d.endswith(".app"):
                    if app_name == "unknown":
                        app_name = d[:-4]

        return app_name, app_version

    @staticmethod
    def _parse_plist(plist_path: Path) -> Tuple[str, str]:
        """
        Parse a text or binary plist to extract CFBundleName and
        CFBundleShortVersionString.  Uses ``plutil`` (macOS) or a
        pure-Python XML parser for text plists on Linux.
        """
        name = "unknown"
        version = "unknown"
        try:
            content = plist_path.read_bytes()
            # Text plist (XML)
            if b"<plist" in content:
                text = content.decode("utf-8", errors="replace")
                # Very simple key/string extractor (no full XML parse needed)
                lines = text.splitlines()
                for i, line in enumerate(lines):
                    if "CFBundleName" in line and i + 1 < len(lines):
                        val = lines[i + 1].strip()
                        if val.startswith("<string>"):
                            name = val[8:].split("</string>")[0]
                    if "CFBundleShortVersionString" in line and i + 1 < len(lines):
                        val = lines[i + 1].strip()
                        if val.startswith("<string>"):
                            version = val[8:].split("</string>")[0]
        except (OSError, UnicodeDecodeError):
            pass
        return name, version

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    @staticmethod
    def _build_summary(
        app_name: str,
        app_version: str,
        macho_analyses: List[Dict],
        source_files: Dict[str, List[str]],
    ) -> Dict[str, Any]:
        languages: Dict[str, int] = {}
        all_frameworks: Dict[str, int] = {}
        all_linux_crates: List[str] = []
        stripped_count = 0
        fat_count = 0
        error_count = 0

        for ma in macho_analyses:
            if "error" in ma:
                error_count += 1
                continue
            lang = ma.get("language", "unknown")
            languages[lang] = languages.get(lang, 0) + 1

            for fw in ma.get("frameworks", []):
                all_frameworks[fw] = all_frameworks.get(fw, 0) + 1

            for mapping in ma.get("linux_mapping", []):
                dep = mapping.get("linux_dep", "")
                if dep and dep not in all_linux_crates:
                    all_linux_crates.append(dep)

            if ma.get("stripped"):
                stripped_count += 1
            if ma.get("macho_header", {}).get("is_fat"):
                fat_count += 1

        dominant_lang = (
            max(languages, key=lambda k: languages[k]) if languages else "unknown"
        )
        total_sources = sum(len(v) for v in source_files.values())

        return {
            "app_name": app_name,
            "app_version": app_version,
            "macho_count": len(macho_analyses),
            "error_count": error_count,
            "fat_binaries": fat_count,
            "stripped_binaries": stripped_count,
            "dominant_language": dominant_lang,
            "language_breakdown": languages,
            "macos_frameworks": all_frameworks,
            "linux_deps_needed": all_linux_crates,
            "source_file_categories": {k: len(v) for k, v in source_files.items()},
            "total_source_artefacts": total_sources,
        }


# ---------------------------------------------------------------------------
# LinuxPortingScaffold
# ---------------------------------------------------------------------------

class LinuxPortingScaffold:
    """
    Generates a complete, buildable Linux project scaffold from a DMG rip
    report.

    Given the analysis of a macOS app, it produces:

    linux_port/
    ├── Cargo.toml          (or go.mod / CMakeLists.txt / Makefile)
    ├── src/
    │   └── main.rs         (stub with TODO markers for each framework)
    ├── src/platform/
    │   ├── mod.rs          (platform abstraction layer)
    │   ├── window.rs       (AppKit → winit)
    │   ├── gpu.rs          (Metal → wgpu)
    │   ├── webview.rs      (WebKit → webkit2gtk)
    │   └── audio.rs        (CoreAudio → cpal)
    ├── build.rs            (pkg-config probes for system libraries)
    ├── PORTING_NOTES.md    (per-framework migration guide)
    ├── RECONSTRUCTION_NOTES.md (what was decompiled vs real)
    └── README.md           (how to build on Linux)
    """

    # System packages required for each crate
    _SYSTEM_PKGS: Dict[str, List[str]] = {
        "wgpu":         ["libvulkan-dev", "libgl1-mesa-dev"],
        "winit":        ["libx11-dev", "libwayland-dev", "libxkbcommon-dev"],
        "webkit2gtk":   ["libwebkit2gtk-4.1-dev", "libgtk-3-dev"],
        "gstreamer":    ["libgstreamer1.0-dev", "gstreamer1.0-plugins-base"],
        "cpal":         ["libasound2-dev", "libpulse-dev"],
        "fontconfig":   ["libfontconfig1-dev"],
        "udev":         ["libudev-dev"],
        "zbus":         ["libdbus-1-dev"],
        "secret-service": ["libsecret-1-dev"],
        "atspi":        ["libatspi2.0-dev"],
    }

    def __init__(self, rip_report: Dict[str, Any]):
        self.report = rip_report
        self.app_name = rip_report.get("app_name", "ported-app")
        self.app_version = rip_report.get("app_version", "0.1.0")
        self.summary = rip_report.get("summary", {})
        self.dominant_lang = self.summary.get("dominant_language", "unknown")
        self.all_mappings = self._collect_all_mappings()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(self, output_dir: str = "linux_port") -> Dict[str, Any]:
        """
        Generate the Linux port scaffold.  Returns a dict describing
        what was created.
        """
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        name_safe = self.app_name.lower().replace(" ", "-").replace(".", "-")

        print(f"🐧 Generating Linux porting scaffold for: {self.app_name}")
        print(f"   Language: {self.dominant_lang}")
        print(f"   Frameworks to port: {list(self.summary.get('macos_frameworks', {}).keys())}")
        print(f"📁 Output: {out}")

        created: List[str] = []

        # Choose scaffold type based on language
        if "Rust" in self.dominant_lang or self.dominant_lang == "unknown":
            created += self._generate_rust_scaffold(out, name_safe)
        elif "Go" in self.dominant_lang:
            created += self._generate_go_scaffold(out, name_safe)
        elif "Swift" in self.dominant_lang or "Objective-C" in self.dominant_lang:
            created += self._generate_c_scaffold(out, name_safe)
        else:
            created += self._generate_rust_scaffold(out, name_safe)

        # Always write docs regardless of language
        created.append(self._write_porting_notes(out))
        created.append(self._write_reconstruction_notes(out))
        created.append(self._write_readme(out, name_safe))
        created.append(self._write_ci_workflow(out))

        # Copy source artefacts from the rip
        copied = self._copy_source_artefacts(out)
        created += copied

        print(f"\n✅ Generated {len(created)} files in {out}")
        for f in created:
            print(f"   {Path(f).relative_to(out)}")

        return {
            "output_dir": str(out),
            "app_name": self.app_name,
            "dominant_language": self.dominant_lang,
            "files_created": created,
            "system_packages": self._required_system_packages(),
        }

    # ------------------------------------------------------------------
    # Rust scaffold
    # ------------------------------------------------------------------

    def _generate_rust_scaffold(self, out: Path, name_safe: str) -> List[str]:
        """Generate a Cargo workspace scaffold for a Rust app."""
        created: List[str] = []
        src = out / "src"
        platform = src / "platform"
        src.mkdir(exist_ok=True)
        platform.mkdir(exist_ok=True)

        # Cargo.toml
        cargo_toml = out / "Cargo.toml"
        cargo_toml.write_text(self._rust_cargo_toml(name_safe), encoding="utf-8")
        created.append(str(cargo_toml))

        # build.rs
        build_rs = out / "build.rs"
        build_rs.write_text(self._rust_build_rs(), encoding="utf-8")
        created.append(str(build_rs))

        # src/main.rs
        main_rs = src / "main.rs"
        main_rs.write_text(self._rust_main_rs(), encoding="utf-8")
        created.append(str(main_rs))

        # src/platform/mod.rs
        mod_rs = platform / "mod.rs"
        mod_rs.write_text(self._rust_platform_mod(), encoding="utf-8")
        created.append(str(mod_rs))

        # Per-framework platform stubs
        for stub_file, stub_content in self._rust_platform_stubs().items():
            stub_path = platform / stub_file
            stub_path.write_text(stub_content, encoding="utf-8")
            created.append(str(stub_path))

        return created

    def _rust_cargo_toml(self, name_safe: str) -> str:
        macos_frameworks = self.summary.get("macos_frameworks", {})
        deps: List[str] = [
            'tokio = { version = "1", features = ["full"] }',
            'anyhow = "1"',
            'tracing = "0.1"',
            'tracing-subscriber = "0.3"',
        ]
        for mapping in self.all_mappings:
            dep = mapping.get("linux_dep", "")
            if dep and not dep.startswith("#"):
                for line in dep.splitlines():
                    if line.strip() and not line.startswith("#"):
                        if line not in deps:
                            deps.append(line.strip())

        deps_str = "\n".join(deps)
        fw_comment = ", ".join(macos_frameworks.keys()) if macos_frameworks else "none detected"

        return f"""\
[package]
name = "{name_safe}"
version = "{self.app_version}"
edition = "2021"
description = "Linux port of {self.app_name} (reconstructed from DMG analysis)"

# macOS frameworks detected: {fw_comment}
# Each has been mapped to the nearest Linux-compatible crate.
# See PORTING_NOTES.md for migration guidance per framework.

[dependencies]
{deps_str}

[profile.release]
opt-level = 3
lto = true
codegen-units = 1

# To build:
#   cargo build --release
#
# System packages required (Ubuntu/Debian):
#   sudo apt-get install {" ".join(self._required_system_packages())}
"""

    def _rust_build_rs(self) -> str:
        probes = []
        for mapping in self.all_mappings:
            crate = mapping.get("linux_crate", "")
            if "webkit2gtk" in crate:
                probes.append('    pkg_config::probe_library("webkit2gtk-4.1")'
                              '.expect("webkit2gtk-4.1 not found");')
            if "gtk" in crate:
                probes.append('    pkg_config::probe_library("gtk+-3.0")'
                              '.expect("gtk+-3.0 not found");')
            if "fontconfig" in crate:
                probes.append('    pkg_config::probe_library("fontconfig")'
                              '.expect("fontconfig not found");')

        probes_str = "\n".join(probes) if probes else \
            '    // No pkg-config probes needed for this configuration.'

        return f"""\
// build.rs — pkg-config probes for system libraries
// Generated by THE FORGE DMG Ripper
fn main() {{
{probes_str}
}}
"""

    def _rust_main_rs(self) -> str:
        return f"""\
//! {self.app_name} — Linux port
//!
//! Reconstructed from macOS DMG analysis by THE FORGE.
//! See PORTING_NOTES.md for the macOS → Linux framework mapping.

mod platform;

#[tokio::main]
async fn main() -> anyhow::Result<()> {{
    tracing_subscriber::fmt::init();
    tracing::info!("Starting {self.app_name} (Linux port)");

    // TODO: Initialise your application here.
    // The platform/ module contains stubs for each ported macOS framework.
    // Work through each TODO in platform/ to implement the Linux equivalents.
    platform::run().await
}}
"""

    def _rust_platform_mod(self) -> str:
        frameworks = list(self.summary.get("macos_frameworks", {}).keys())
        module_lines: List[str] = []
        for fw in frameworks:
            mod_name = fw.lower().replace(" ", "_").replace("/", "_")
            module_lines.append(f"pub mod {mod_name};")

        mods = "\n".join(module_lines) if module_lines else \
            "// No specific platform modules detected."

        return f"""\
//! Platform abstraction layer
//!
//! Replaces macOS-specific frameworks with Linux equivalents.
//! Detected macOS frameworks: {", ".join(frameworks) if frameworks else "none"}

{mods}

/// Main entry point called from main.rs.
pub async fn run() -> anyhow::Result<()> {{
    // TODO: Wire up the platform modules below.
    todo!("Implement platform::run() using the modules in this directory")
}}
"""

    def _rust_platform_stubs(self) -> Dict[str, str]:
        """Generate per-framework stub files."""
        stubs: Dict[str, str] = {}
        for mapping in self.all_mappings:
            macos = mapping["macos"]
            linux_crate = mapping["linux_crate"]
            note = mapping["note"]
            fname = macos.lower().replace(" ", "_").replace("/", "_") + ".rs"
            stubs[fname] = (
                f"//! {macos} → {linux_crate}\n"
                f"//!\n"
                f"//! {note}\n"
                f"//!\n"
                f"//! TODO: Implement this module using `{linux_crate}`.\n"
                f"\n"
                f"pub async fn init() -> anyhow::Result<()> {{\n"
                f"    todo!(\"Implement {macos} replacement with {linux_crate}\")\n"
                f"}}\n"
            )
        return stubs

    # ------------------------------------------------------------------
    # Go scaffold
    # ------------------------------------------------------------------

    def _generate_go_scaffold(self, out: Path, name_safe: str) -> List[str]:
        """Generate a Go module scaffold."""
        created: List[str] = []
        src = out / "cmd" / name_safe
        src.mkdir(parents=True, exist_ok=True)

        go_mod = out / "go.mod"
        go_mod.write_text(
            f"module github.com/linux-port/{name_safe}\n\ngo 1.22\n",
            encoding="utf-8",
        )
        created.append(str(go_mod))

        main_go = src / "main.go"
        main_go.write_text(
            f"// {self.app_name} — Linux port\n"
            f"// Reconstructed from macOS DMG analysis by THE FORGE.\n\n"
            f"package main\n\nfunc main() {{\n"
            f"\t// TODO: implement Linux port\n}}\n",
            encoding="utf-8",
        )
        created.append(str(main_go))
        return created

    # ------------------------------------------------------------------
    # C/ObjC scaffold
    # ------------------------------------------------------------------

    def _generate_c_scaffold(self, out: Path, name_safe: str) -> List[str]:
        """Generate a CMake scaffold for C / Objective-C / Swift apps."""
        created: List[str] = []
        src = out / "src"
        src.mkdir(exist_ok=True)

        cmake = out / "CMakeLists.txt"
        cmake.write_text(
            f"cmake_minimum_required(VERSION 3.20)\n"
            f"project({name_safe} VERSION {self.app_version})\n\n"
            f"find_package(PkgConfig REQUIRED)\n"
            + ("pkg_check_modules(GTK3 REQUIRED gtk+-3.0)\n"
               if any("AppKit" in m["macos"] for m in self.all_mappings) else "")
            + f"\nadd_executable({name_safe} src/main.c)\n",
            encoding="utf-8",
        )
        created.append(str(cmake))

        main_c = src / "main.c"
        main_c.write_text(
            f"/* {self.app_name} — Linux port */\n"
            f"/* Reconstructed from macOS DMG analysis by THE FORGE. */\n\n"
            f"int main(int argc, char **argv) {{\n"
            f"    /* TODO: implement Linux port */\n"
            f"    return 0;\n}}\n",
            encoding="utf-8",
        )
        created.append(str(main_c))
        return created

    # ------------------------------------------------------------------
    # Documentation
    # ------------------------------------------------------------------

    def _write_porting_notes(self, out: Path) -> str:
        """Write a detailed per-framework porting guide."""
        lines = [
            f"# Porting Notes: {self.app_name} → Linux",
            "",
            "Generated by **THE FORGE DMG Ripper & Linux Porter**.",
            "",
            "## Overview",
            "",
            f"- **App**: {self.app_name} {self.app_version}",
            f"- **Dominant language**: {self.dominant_lang}",
            f"- **macOS frameworks detected**: "
            + ", ".join(self.summary.get("macos_frameworks", {}).keys()),
            "",
            "## Framework Migration Guide",
            "",
        ]

        for mapping in self.all_mappings:
            lines += [
                f"### {mapping['macos']} → `{mapping['linux_crate']}`",
                "",
                f"**Cargo dependency:**",
                "```toml",
                mapping["linux_dep"],
                "```",
                "",
                f"**Migration notes:** {mapping['note']}",
                "",
            ]

        if not self.all_mappings:
            lines.append("No macOS-specific framework mappings were detected.")

        lines += [
            "## System Package Requirements",
            "",
            "Install these on Ubuntu/Debian before building:",
            "```bash",
            "sudo apt-get install " + " ".join(self._required_system_packages()),
            "```",
            "",
            "## Build Instructions",
            "",
            "```bash",
            "# Install Rust (if not already installed)",
            "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh",
            "",
            "# Install system dependencies (see above)",
            "",
            "# Build",
            "cargo build --release",
            "",
            "# Run",
            f"./target/release/{self.app_name.lower().replace(' ', '-')}",
            "```",
            "",
            "## Note on Warp Terminal",
            "",
            "If you are porting Warp (https://www.warp.dev/terminal), note that "
            "**Warp officially released a native Linux version in 2024** "
            "(Ubuntu/Debian, x86-64 and arm64). You can install it directly:",
            "```bash",
            "# Ubuntu/Debian",
            "wget https://releases.warp.dev/stable/v0.2024.07.18.08.01.stable_01/"
            "warp-terminal_0.2024.07.18.08.01.stable_01_amd64.deb",
            "sudo apt install ./warp-terminal_*.deb",
            "```",
        ]

        path = out / "PORTING_NOTES.md"
        path.write_text("\n".join(lines), encoding="utf-8")
        return str(path)

    def _write_reconstruction_notes(self, out: Path) -> str:
        """Write notes explaining what was decompiled vs what is real source."""
        macho_count = self.summary.get("macho_count", 0)
        stripped = self.summary.get("stripped_binaries", 0)

        lines = [
            f"# Reconstruction Notes: {self.app_name}",
            "",
            "## What was recovered",
            "",
            f"- **Mach-O binaries analysed**: {macho_count}",
            f"- **Stripped binaries**: {stripped} "
            "(no symbol table — function names not recoverable without DWARF)",
            f"- **Source artefacts found in DMG**: "
            + str(self.summary.get("total_source_artefacts", 0)),
            "",
            "## Accuracy warning",
            "",
            "> **Mach-O is NOT source code.**  Compilation is lossy.",
            "> Variable names, comments, and control-flow structure are gone.",
            "> The `src/platform/` stubs are *skeletons* with TODOs — they",
            "> show what each module needs to do, not how the original did it.",
            "",
            "## Source files found in the DMG",
            "",
        ]

        for category, paths in self.report.get("source_files", {}).items():
            lines.append(f"### {category} ({len(paths)} files)")
            for p in paths[:10]:
                lines.append(f"  - `{Path(p).name}`")
            if len(paths) > 10:
                lines.append(f"  - *(and {len(paths) - 10} more)*")
            lines.append("")

        path = out / "RECONSTRUCTION_NOTES.md"
        path.write_text("\n".join(lines), encoding="utf-8")
        return str(path)

    def _write_readme(self, out: Path, name_safe: str) -> str:
        """Write a top-level README for the Linux port."""
        system_pkgs = " ".join(self._required_system_packages())
        lines = [
            f"# {self.app_name} — Linux Port",
            "",
            f"> Reconstructed from macOS DMG by **THE FORGE DMG Ripper**.",
            "",
            "## Quick Start",
            "",
            "```bash",
            "# 1. Install system dependencies",
            f"sudo apt-get install {system_pkgs}",
            "",
            "# 2. Install Rust",
            "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh",
            "",
            "# 3. Build",
            "cargo build --release",
            "",
            "# 4. Run",
            f"./target/release/{name_safe}",
            "```",
            "",
            "## Project Layout",
            "",
            "```",
            "├── Cargo.toml              Build manifest",
            "├── build.rs                pkg-config probes",
            "├── src/",
            "│   ├── main.rs             Entry point",
            "│   └── platform/           macOS → Linux platform shims",
            "├── sources/                Source artefacts extracted from DMG",
            "├── PORTING_NOTES.md        Framework migration guide",
            "└── RECONSTRUCTION_NOTES.md What is decompiled vs real",
            "```",
            "",
            "## Status",
            "",
            "- [ ] Window creation (AppKit → winit)",
            "- [ ] GPU rendering (Metal → wgpu)",
            "- [ ] Text rendering (CoreText → cosmic-text)",
            "- [ ] Web view (WebKit → webkit2gtk)",
            "- [ ] Audio (CoreAudio → cpal)",
            "- [ ] IPC (XPC → zbus)",
            "- [ ] Keychain (Security → secret-service)",
            "",
            "Each item corresponds to a `TODO` in `src/platform/`.",
        ]

        path = out / "README.md"
        path.write_text("\n".join(lines), encoding="utf-8")
        return str(path)

    def _write_ci_workflow(self, out: Path) -> str:
        """Write a GitHub Actions CI workflow for Linux builds."""
        gh_dir = out / ".github" / "workflows"
        gh_dir.mkdir(parents=True, exist_ok=True)

        system_pkgs = " ".join(self._required_system_packages())
        content = f"""\
name: Linux Build

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install system dependencies
        run: sudo apt-get install -y {system_pkgs}

      - name: Install Rust
        uses: dtolnay/rust-toolchain@stable

      - name: Build
        run: cargo build --release

      - name: Test
        run: cargo test
"""
        workflow = gh_dir / "linux.yml"
        workflow.write_text(content, encoding="utf-8")
        return str(workflow)

    # ------------------------------------------------------------------
    # Copy source artefacts
    # ------------------------------------------------------------------

    def _copy_source_artefacts(self, out: Path) -> List[str]:
        """Copy source files collected during rip into the scaffold."""
        copied: List[str] = []
        src_dest = out / "sources"
        for category, paths in self.report.get("source_files", {}).items():
            cat_dir = src_dest / category
            cat_dir.mkdir(parents=True, exist_ok=True)
            for src_path in paths:
                dest = cat_dir / Path(src_path).name
                try:
                    if not dest.exists():
                        shutil.copy2(src_path, dest)
                        copied.append(str(dest))
                except (OSError, FileNotFoundError):
                    pass
        return copied

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _collect_all_mappings(self) -> List[Dict[str, str]]:
        """Deduplicate linux_mapping entries across all analysed binaries."""
        seen: set = set()
        result: List[Dict[str, str]] = []
        for binary in self.report.get("macho_files", []):
            for mapping in binary.get("linux_mapping", []):
                key = mapping.get("macos", "")
                if key and key not in seen:
                    seen.add(key)
                    result.append(mapping)
        return result

    def _required_system_packages(self) -> List[str]:
        """Return deduplicated list of system packages for all Linux crates."""
        pkgs: List[str] = []
        for mapping in self.all_mappings:
            crate_name = mapping.get("linux_crate", "").split()[0].lower()
            for key, pkg_list in self._SYSTEM_PKGS.items():
                if key in crate_name:
                    for pkg in pkg_list:
                        if pkg not in pkgs:
                            pkgs.append(pkg)
        return pkgs if pkgs else ["build-essential", "pkg-config"]


# ---------------------------------------------------------------------------
# ProjectReconstructor (RPM + DMG unified)
# ---------------------------------------------------------------------------

class ProjectReconstructor:
    """
    Unified project reconstructor that works with both RPM rip reports
    (ELF binaries, Linux) and DMG rip reports (Mach-O binaries, macOS).

    Takes the output of RpmRipper.rip() or DmgRipper.rip() and assembles
    a complete, language-appropriate open-source project skeleton with:

    - All real source files found in the package (scripts, headers, configs)
    - Decompiled function skeletons for every binary (ELF or Mach-O)
    - A buildable build file (Cargo.toml / go.mod / CMakeLists.txt / Makefile)
    - A README.md explaining the project and how to build it
    - A RECONSTRUCTION_NOTES.md explaining what is decompiled vs original

    This is the top-level "put it all back together" step.
    """

    _BUILD_FILE_GENERATORS = {
        "Rust":             "_gen_cargo_toml",
        "Go":               "_gen_go_mod",
        "C++":              "_gen_cmake",
        "C":                "_gen_cmake",
        "Swift":            "_gen_cmake",
        "Objective-C":      "_gen_cmake",
        "Python (C extension)": "_gen_pyproject",
    }

    def __init__(self, rip_report: Dict[str, Any]):
        self.report = rip_report
        # Normalise: RPM reports use "summary", both use "summary"
        self.summary = rip_report.get("summary", {})
        self.pkg_name = (
            self.summary.get("package")
            or self.summary.get("app_name")
            or "reconstructed-package"
        )
        self.version = (
            self.summary.get("version")
            or self.summary.get("app_version")
            or "0.1.0"
        )
        self.lang = self.summary.get("dominant_language", "C")
        # Binaries: ELF (rpm) or Mach-O (dmg)
        self.binaries: List[Dict] = (
            rip_report.get("elf_files") or rip_report.get("macho_files") or []
        )
        self.source_files: Dict[str, List[str]] = rip_report.get("source_files", {})

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def reconstruct(self, output_dir: str = "reconstructed") -> Dict[str, Any]:
        """
        Build the reconstructed open-source project layout.

        Returns a manifest dict listing every file created.
        """
        from rpm_ripper import ElfDecompiler  # local import avoids circular dep

        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        name_safe = self.pkg_name.lower().replace(" ", "-")

        print(f"\n🔨 Reconstructing open-source project: {self.pkg_name}")
        print(f"   Language : {self.lang}")
        print(f"   Binaries : {len(self.binaries)}")
        print(f"   Sources  : {sum(len(v) for v in self.source_files.values())}")
        print(f"   Output   : {out}")

        created: List[str] = []

        # 1. Decompile every binary and collect function skeletons
        print("\n[1/5] Decompiling binaries …")
        decompiled = self._decompile_all_binaries(out)
        created += decompiled

        # 2. Lay out real source files
        print("[2/5] Copying real source artefacts …")
        created += self._layout_sources(out)

        # 3. Generate build file
        print(f"[3/5] Generating {self.lang} build scaffold …")
        build_files = self._generate_build_scaffold(out, name_safe)
        created += build_files

        # 4. Write documentation
        print("[4/5] Writing documentation …")
        created.append(self._write_readme(out, name_safe))
        created.append(self._write_reconstruction_notes(out))
        created.append(self._write_open_source_notes(out))

        # 5. Write manifest JSON
        print("[5/5] Writing project manifest …")
        manifest = {
            "package": self.pkg_name,
            "version": self.version,
            "language": self.lang,
            "output_dir": str(out),
            "files_created": created,
            "binary_count": len(self.binaries),
            "source_categories": list(self.source_files.keys()),
        }
        manifest_path = out / "project_manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        created.append(str(manifest_path))

        print(f"\n✅ Reconstructed project ready in: {out}")
        print(f"   {len(created)} files written")
        return manifest

    # ------------------------------------------------------------------
    # Decompilation
    # ------------------------------------------------------------------

    def _decompile_all_binaries(self, out: Path) -> List[str]:
        """Run ElfDecompiler on every binary; collect all output files."""
        from rpm_ripper import ElfDecompiler

        created: List[str] = []
        decompile_dir = out / "decompiled"

        for binary in self.binaries:
            if "error" in binary:
                continue
            path = binary.get("path", "")
            if not path or not Path(path).exists():
                continue

            name = Path(path).name
            binary_out = decompile_dir / name
            try:
                result = ElfDecompiler(path).decompile(output_dir=str(binary_out))
                # Copy the function skeleton into src/
                skel = result.get("layers", {}).get("symbols", {}).get("skeleton_file")
                if skel and Path(skel).exists():
                    src_dir = out / "src"
                    src_dir.mkdir(exist_ok=True)
                    dest = src_dir / f"{name}_functions.txt"
                    shutil.copy2(skel, dest)
                    created.append(str(dest))
                print(f"   ✅ {name}")
            except Exception as exc:
                print(f"   ⚠️  {name}: {exc}")

        return created

    # ------------------------------------------------------------------
    # Source layout
    # ------------------------------------------------------------------

    def _layout_sources(self, out: Path) -> List[str]:
        """
        Copy real source files from the rip into a logical project layout.

        Category → destination directory mapping:
          *_source, headers  → src/
          shell_scripts      → scripts/
          plists, *_configs  → config/
          documentation      → docs/
          everything else    → misc/
        """
        created: List[str] = []

        _dest_map = {
            "c_source": "src", "cpp_source": "src", "rust_source": "src",
            "go_source": "src", "swift_source": "src", "objc_source": "src",
            "objcpp_source": "src", "python_scripts": "src",
            "headers": "src/include",
            "shell_scripts": "scripts",
            "json_configs": "config", "toml_configs": "config",
            "yaml_configs": "config", "config_files": "config",
            "plists": "config", "xcode_config": "config",
            "documentation": "docs", "localization": "docs",
            "javascript": "src/web", "typescript": "src/web",
        }

        for category, paths in self.source_files.items():
            dest_name = _dest_map.get(category, "misc")
            dest_dir = out / dest_name
            dest_dir.mkdir(parents=True, exist_ok=True)
            for src_path in paths:
                dest = dest_dir / Path(src_path).name
                try:
                    if not dest.exists():
                        shutil.copy2(src_path, dest)
                        created.append(str(dest))
                except (OSError, FileNotFoundError):
                    pass

        return created

    # ------------------------------------------------------------------
    # Build scaffold
    # ------------------------------------------------------------------

    def _generate_build_scaffold(self, out: Path, name_safe: str) -> List[str]:
        method_name = self._BUILD_FILE_GENERATORS.get(self.lang, "_gen_cmake")
        method = getattr(self, method_name)
        return method(out, name_safe)

    def _gen_cargo_toml(self, out: Path, name_safe: str) -> List[str]:
        frameworks = list(self.summary.get("framework_breakdown", {}).keys())
        fw_comment = (", ".join(frameworks) if frameworks
                      else "no specific frameworks detected")
        content = (
            f'[package]\n'
            f'name = "{name_safe}"\n'
            f'version = "{self.version}"\n'
            f'edition = "2021"\n'
            f'description = "Reconstructed from {self.pkg_name} package"\n'
            f'\n'
            f'# Detected frameworks: {fw_comment}\n'
            f'\n'
            f'[dependencies]\n'
            f'tokio = {{ version = "1", features = ["full"] }}\n'
            f'anyhow = "1"\n'
            f'tracing = "0.1"\n'
            f'tracing-subscriber = "0.3"\n'
            f'\n'
            f'[[bin]]\n'
            f'name = "{name_safe}"\n'
            f'path = "src/main.rs"\n'
        )
        p = out / "Cargo.toml"
        p.write_text(content, encoding="utf-8")

        main_rs = out / "src" / "main.rs"
        (out / "src").mkdir(exist_ok=True)
        if not main_rs.exists():
            main_rs.write_text(
                f"//! {self.pkg_name} — reconstructed\n\n"
                f"#[tokio::main]\nasync fn main() -> anyhow::Result<()> {{\n"
                f"    // TODO: implement from decompiled stubs in src/\n"
                f"    Ok(())\n}}\n",
                encoding="utf-8",
            )
        return [str(p), str(main_rs)]

    def _gen_go_mod(self, out: Path, name_safe: str) -> List[str]:
        p = out / "go.mod"
        p.write_text(
            f"module github.com/reconstructed/{name_safe}\n\ngo 1.22\n",
            encoding="utf-8",
        )
        main_go = out / "src" / "main.go"
        (out / "src").mkdir(exist_ok=True)
        if not main_go.exists():
            main_go.write_text(
                f"// {self.pkg_name} — reconstructed\n\n"
                f"package main\n\nfunc main() {{\n"
                f"\t// TODO: implement from decompiled stubs in src/\n}}\n",
                encoding="utf-8",
            )
        return [str(p), str(main_go)]

    def _gen_cmake(self, out: Path, name_safe: str) -> List[str]:
        content = (
            f"cmake_minimum_required(VERSION 3.20)\n"
            f"project({name_safe} VERSION {self.version})\n\n"
            f"set(CMAKE_C_STANDARD 17)\nset(CMAKE_CXX_STANDARD 20)\n\n"
            f"file(GLOB_RECURSE SOURCES src/*.c src/*.cpp)\n"
            f"add_executable({name_safe} ${{SOURCES}})\n"
        )
        p = out / "CMakeLists.txt"
        p.write_text(content, encoding="utf-8")
        return [str(p)]

    def _gen_pyproject(self, out: Path, name_safe: str) -> List[str]:
        content = (
            f'[build-system]\n'
            f'requires = ["setuptools>=68"]\n'
            f'build-backend = "setuptools.build_meta"\n\n'
            f'[project]\n'
            f'name = "{name_safe}"\n'
            f'version = "{self.version}"\n'
            f'description = "Reconstructed from {self.pkg_name}"\n'
        )
        p = out / "pyproject.toml"
        p.write_text(content, encoding="utf-8")
        return [str(p)]

    # ------------------------------------------------------------------
    # Documentation
    # ------------------------------------------------------------------

    def _write_readme(self, out: Path, name_safe: str) -> str:
        lang_build = {
            "Rust": "cargo build --release",
            "Go": "go build ./...",
        }.get(self.lang, "cmake -B build && cmake --build build")

        lines = [
            f"# {self.pkg_name} — Reconstructed Open-Source Project",
            "",
            f"> **Language**: {self.lang}  |  **Version**: {self.version}",
            "> Reconstructed from package analysis by **THE FORGE RPM/DMG Ripper**.",
            "",
            "## How to Build",
            "",
            "```bash",
            lang_build,
            "```",
            "",
            "## Project Layout",
            "",
            "```",
            "├── src/              Decompiled function skeletons + real sources",
            "├── src/include/      Header files from the package",
            "├── scripts/          Shell scripts found in the package",
            "├── config/           Config / plist files",
            "├── docs/             Documentation extracted from the package",
            "├── decompiled/       Full per-binary decompilation artefacts",
            "│   └── <binary>/",
            "│       ├── dwarf/          DWARF debug info",
            "│       ├── symbols/        Demangled symbol table + function skeleton",
            "│       ├── strings/        Categorised string literals",
            "│       └── disassembly/    Annotated objdump output",
            "├── RECONSTRUCTION_NOTES.md  Accuracy and completeness notes",
            "└── OPEN_SOURCE_NOTES.md     Licensing and open-source guidance",
            "```",
            "",
            "## Status",
            "",
            "| File | Origin |",
            "|------|--------|",
        ]

        for category, paths in self.source_files.items():
            if paths:
                lines.append(f"| `{category}/` ({len(paths)} files) | "
                              "Real file from package |")
        lines += [
            f"| `src/*_functions.txt` | Decompiled function skeleton |",
            "",
            "Items in **decompiled function skeletons** are stubs — they show "
            "what each function is called but not how it was implemented. "
            "Fill them in to produce a working open-source reimplementation.",
        ]

        path = out / "README.md"
        path.write_text("\n".join(lines), encoding="utf-8")
        return str(path)

    def _write_reconstruction_notes(self, out: Path) -> str:
        stripped = self.summary.get("stripped_binaries", 0)
        elf_count = self.summary.get("elf_count") or self.summary.get("macho_count", 0)

        lines = [
            "# Reconstruction Notes",
            "",
            "## What was decompiled (not real source code)",
            "",
            f"- **{elf_count} binaries** were analysed.",
            f"- **{stripped} were stripped** — no symbol table, "
            "so function names defaulted to addresses.",
            "- Function stubs in `src/*_functions.txt` are SKELETONS only.",
            "  They show function signatures but bodies are all `TODO`.",
            "",
            "## What IS real source code",
            "",
        ]
        for category, paths in self.source_files.items():
            if paths:
                lines.append(f"- **{category}**: {len(paths)} files — "
                              "copied verbatim from the package.")
        if not self.source_files:
            lines.append("- No source files were found in the package payload.")

        lines += [
            "",
            "## Completeness rating",
            "",
            "| Indicator | Value |",
            "|-----------|-------|",
            f"| Binaries analysed | {elf_count} |",
            f"| Stripped binaries | {stripped} |",
            f"| Source files found | "
            f"{sum(len(v) for v in self.source_files.values())} |",
            f"| Dominant language | {self.lang} |",
            "",
            "> A stripped binary with no DWARF debug info gives very little",
            "> recoverable information.  The best recovery strategy is to find",
            "> the companion source package (`.src.rpm` or upstream Git repo).",
        ]

        path = out / "RECONSTRUCTION_NOTES.md"
        path.write_text("\n".join(lines), encoding="utf-8")
        return str(path)

    def _write_open_source_notes(self, out: Path) -> str:
        lines = [
            "# Open Source Notes",
            "",
            "## Important: Legal Considerations",
            "",
            "Decompiling proprietary software and publishing the results may",
            "violate copyright law and/or the software's terms of service.",
            "This tool is intended for:",
            "",
            "- **Personal interoperability** (e.g. making a tool run on your OS)",
            "- **Security research** (vulnerability analysis)",
            "- **Learning** (understanding how binaries are structured)",
            "- **Porting open-source software** (where the licence permits it)",
            "",
            "Before publishing a reconstruction:",
            "",
            "1. Check the original software's licence.",
            "2. Check local laws on reverse engineering (EU Directive 2009/24/EC",
            "   Article 6 allows interoperability decompilation in the EU; US",
            "   DMCA has similar provisions).",
            "3. Prefer obtaining the real source from `.src.rpm`, upstream Git,",
            "   or by contacting the authors.",
            "",
            "## If the software is already open source",
            "",
            "Many RPM packages are open-source.  Check:",
            "",
            f"- `https://src.fedoraproject.org/rpms/{self.pkg_name}`",
            f"- `https://github.com/search?q={self.pkg_name}`",
            "- The `License:` tag in the RPM spec file",
            "",
            "If it is open source, simply clone the upstream repository instead",
            "of using the decompiled skeleton.",
        ]

        path = out / "OPEN_SOURCE_NOTES.md"
        path.write_text("\n".join(lines), encoding="utf-8")
        return str(path)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

class DmgRipperCLI:
    """Command-line interface for the DMG Ripper, Mach-O Analyzer & Linux Porter."""

    def run(self, argv: Optional[List[str]] = None) -> int:
        parser = argparse.ArgumentParser(
            prog="dmg_ripper",
            description=(
                "🔧 THE FORGE — DMG Ripper, Mach-O Analyzer & Linux Porter.\n\n"
                "Extracts macOS DMG disk images on Linux, analyses every Mach-O\n"
                "binary inside, and generates a complete Linux porting scaffold\n"
                "with per-framework migration guides and buildable stub code.\n\n"
                "Example:\n"
                "  python3 dmg_ripper.py Warp.dmg -o out/ --port-to-linux linux_port/\n"
                "  python3 dmg_ripper.py --analyze-only out/macho/warp\n"
                "  python3 dmg_ripper.py --reconstruct out/analysis_report.json"
            ),
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

        action = parser.add_mutually_exclusive_group()
        action.add_argument(
            "--analyze-only",
            metavar="MACHO",
            help="Analyse a single Mach-O binary (no DMG needed)",
        )
        action.add_argument(
            "--reconstruct",
            metavar="REPORT_JSON",
            help=(
                "Skip ripping; load an existing analysis_report.json and "
                "reconstruct the open-source project from it"
            ),
        )

        parser.add_argument(
            "dmg", nargs="?",
            help="Path to the .dmg file to rip",
        )
        parser.add_argument(
            "-o", "--output-dir", default="dmg_ripped",
            help="Output directory for rip artefacts (default: dmg_ripped/)",
        )
        parser.add_argument(
            "--port-to-linux", metavar="PORT_DIR", default=None,
            help="After ripping, generate a Linux porting scaffold in PORT_DIR",
        )
        parser.add_argument(
            "--full-reconstruct", metavar="RECON_DIR", default=None,
            help=(
                "After ripping, run the full ProjectReconstructor pipeline "
                "(decompile all binaries + build open-source project) in RECON_DIR"
            ),
        )

        args = parser.parse_args(argv)

        if args.analyze_only:
            return self._run_analyze_only(args.analyze_only)

        if args.reconstruct:
            return self._run_reconstruct_from_report(
                args.reconstruct,
                args.full_reconstruct or "reconstructed",
            )

        if not args.dmg:
            parser.print_help()
            return 1

        return self._run_rip(
            args.dmg,
            args.output_dir,
            args.port_to_linux,
            args.full_reconstruct,
        )

    # ------------------------------------------------------------------

    def _run_rip(
        self,
        dmg_path: str,
        output_dir: str,
        port_dir: Optional[str],
        recon_dir: Optional[str],
    ) -> int:
        print("=" * 64)
        print("🔥 THE FORGE — DMG Ripper & Mach-O Analyzer")
        print("=" * 64)
        try:
            report = DmgRipper(dmg_path, output_dir).rip()
        except (FileNotFoundError, RuntimeError) as exc:
            print(f"\n❌ Error: {exc}", file=sys.stderr)
            return 1

        self._print_summary(report["summary"])

        if port_dir:
            print(f"\n🐧 Generating Linux port scaffold → {port_dir}")
            LinuxPortingScaffold(report).generate(output_dir=port_dir)

        if recon_dir:
            print(f"\n🔨 Running full project reconstruction → {recon_dir}")
            ProjectReconstructor(report).reconstruct(output_dir=recon_dir)

        return 0

    def _run_analyze_only(self, macho_path: str) -> int:
        print("=" * 64)
        print("🔥 THE FORGE — Mach-O Analyzer")
        print("=" * 64)
        try:
            analysis = MachoAnalyzer(macho_path).analyze()
        except (FileNotFoundError, ValueError) as exc:
            print(f"\n❌ Error: {exc}", file=sys.stderr)
            return 1
        print(json.dumps(analysis, indent=2))
        return 0

    def _run_reconstruct_from_report(
        self, report_path: str, recon_dir: str
    ) -> int:
        print("=" * 64)
        print("🔥 THE FORGE — Project Reconstructor")
        print("=" * 64)
        try:
            with open(report_path, encoding="utf-8") as fh:
                report = json.load(fh)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"\n❌ Cannot load report: {exc}", file=sys.stderr)
            return 1

        # Detect whether this is a DMG or RPM report and choose reconstructor
        if "macho_files" in report:
            LinuxPortingScaffold(report).generate(output_dir=recon_dir + "_linux")
        ProjectReconstructor(report).reconstruct(output_dir=recon_dir)
        return 0

    @staticmethod
    def _print_summary(summary: Dict[str, Any]) -> None:
        print("\n" + "=" * 64)
        print("📊 Analysis Summary")
        print("=" * 64)
        print(f"  App              : {summary['app_name']} {summary['app_version']}")
        print(f"  Mach-O binaries  : {summary['macho_count']}")
        print(f"  Fat (universal)  : {summary['fat_binaries']}")
        print(f"  Stripped         : {summary['stripped_binaries']}")
        print(f"  Dominant language: {summary['dominant_language']}")

        if summary["macos_frameworks"]:
            print("  macOS frameworks :")
            for fw, count in sorted(summary["macos_frameworks"].items()):
                print(f"    {fw}: {count} binaries")

        if summary["linux_deps_needed"]:
            print("  Linux deps needed:")
            for dep in summary["linux_deps_needed"][:8]:
                first_line = dep.splitlines()[0] if dep else ""
                print(f"    {first_line}")

        if summary.get("source_file_categories"):
            print("  Source artefacts :")
            for cat, count in sorted(summary["source_file_categories"].items()):
                print(f"    {cat}: {count}")

        print("=" * 64)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    sys.exit(DmgRipperCLI().run())


if __name__ == "__main__":
    main()
