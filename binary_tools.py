#!/usr/bin/env python3
"""
THE FORGE — Binary Tools
=========================
Safe ELF reader · Deb ripper · Warp terminal ripper · Gemini auth fixer

Extends rpm_ripper.py and dmg_ripper.py with three new capabilities:

─────────────────────────────────────────────────────────────────────────────
1. SafeElfReader  — open ELF files without executing them
─────────────────────────────────────────────────────────────────────────────
Opens an ELF binary as a **read-only memory-mapped file** so:
  • The binary is NEVER executed.
  • The file on disk is NEVER modified.
  • Corrupt / truncated files are caught immediately (no partial reads).
  • Works on files of any size without loading the whole thing into RAM.

This is the safe way to "open" an ELF — treat it as structured data,
not as something to run.

─────────────────────────────────────────────────────────────────────────────
2. DebRipper  — extract .deb packages (like Warp Linux)
─────────────────────────────────────────────────────────────────────────────
Warp terminal ships as a .deb on Linux. A .deb is an `ar` archive
containing:
  • debian-binary    — format version ("2.0\n")
  • control.tar.*   — package metadata (control, postinst, prerm …)
  • data.tar.*      — the actual installed files (ELF binaries, configs …)

DebRipper extracts data.tar.*, finds every ELF, passes each through
ElfAnalyzer, and produces the same analysis_report.json format as
RpmRipper so all downstream tools work identically.

─────────────────────────────────────────────────────────────────────────────
3. WarpRipper  — specialised ripper for Warp terminal
─────────────────────────────────────────────────────────────────────────────
Warp is a Rust terminal emulator. Its Linux binary:
  • Is a stripped Rust ELF linked against libwebkit2gtk, libwayland, libGL
  • Stores auth tokens in ~/.local/share/warp-terminal/ (XDG_DATA_HOME)
  • Has a config at ~/.config/warp-terminal/
  • Checks for a WARP_AUTH_TOKEN or ~/.warp/auth.json

WarpRipper wraps DebRipper and adds Warp-specific:
  • Binary fingerprinting (Warp Rust symbols, webkit2gtk link)
  • Config / token path extraction from string literals
  • Identification of the auth endpoint and token format

─────────────────────────────────────────────────────────────────────────────
4. GeminiAuthFixer  — diagnose and fix Gemini CLI sign-in failures
─────────────────────────────────────────────────────────────────────────────
Google's Gemini CLI (both the Node.js @google/gemini-cli and the Python
google-genai tool) uses OAuth2. On headless Linux (no browser, no GNOME
Keyring, CI/SSH sessions) the sign-in fails with errors like:

  "Unable to open browser"
  "Failed to store credentials"
  "Error: Could not authenticate"

GeminiAuthFixer:
  1. Locates the Gemini CLI binary (searches PATH, ~/.npm, ~/.local/bin)
  2. If it is an ELF → runs ElfAnalyzer + ElfDecompiler string extraction
     to find the exact OAuth endpoint, token file path, and error messages
  3. If it is a Node.js script → parses the JS source directly
  4. Diagnoses the root cause (no browser / no keyring / bad token path)
  5. Writes a working fix:
     • ~/.config/gemini/credentials.json  — API-key auth config
     • A shell wrapper that sets GEMINI_API_KEY before running the CLI
     • Environment variable instructions for CI/headless use

─────────────────────────────────────────────────────────────────────────────
USAGE
─────────────────────────────────────────────────────────────────────────────
Library:
    from binary_tools import SafeElfReader, DebRipper, WarpRipper, GeminiAuthFixer

    # Safely inspect any ELF without running it
    with SafeElfReader("/usr/bin/warp-terminal") as elf:
        header = elf.read_header()
        sections = elf.list_sections()
        strings = elf.extract_strings(min_len=8)

    # Rip a .deb package
    report = DebRipper("warp-terminal_0.2024.deb", output_dir="out/").rip()

    # Rip Warp specifically
    report = WarpRipper("warp-terminal_0.2024.deb").rip(output_dir="out/")

    # Fix Gemini CLI auth
    fixer = GeminiAuthFixer()
    diagnosis = fixer.diagnose()
    fixer.apply_fix(api_key="YOUR_GEMINI_API_KEY")

CLI:
    # Safely inspect an ELF binary
    python3 binary_tools.py --inspect /usr/bin/warp-terminal

    # Rip a .deb package
    python3 binary_tools.py --rip-deb warp-terminal_0.2024.deb -o out/

    # Full Warp rip + analysis
    python3 binary_tools.py --rip-warp warp-terminal_0.2024.deb -o out/

    # Diagnose + fix Gemini CLI auth
    python3 binary_tools.py --fix-gemini-auth
    python3 binary_tools.py --fix-gemini-auth --api-key YOUR_API_KEY

    # Rip Warp AND fix Gemini (all in one)
    python3 binary_tools.py --rip-warp warp-terminal_0.2024.deb \\
                            --fix-gemini-auth --api-key YOUR_KEY -o out/
"""

import argparse
import hashlib
import json
import mmap
import os
import re
import shutil
import struct
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Module-level compiled regexes (avoid recompiling on every call)
# ---------------------------------------------------------------------------

# Strips the GLIBC version-index suffix readelf appends to symbol names,
# e.g. "getenv@GLIBC_2.2.5 (3)" → remove trailing " (3)"
_RE_VER_SUFFIX = re.compile(r'\s*\(\d+\)$')

# ---------------------------------------------------------------------------
# tarfile compat: filter='data' was added in Python 3.12 (PEP 706).
# On 3.11 and earlier we fall back to no filter (extraction without the
# extra hardening) — path-traversal is still blocked by our own check.
# ---------------------------------------------------------------------------
_TARFILE_SUPPORTS_FILTER = sys.version_info >= (3, 12)

# ---------------------------------------------------------------------------
# Re-use constants from rpm_ripper
# ---------------------------------------------------------------------------

ELF_MAGIC = b"\x7fELF"

EI_CLASS = {1: "32-bit", 2: "64-bit"}
EI_DATA  = {1: "little-endian", 2: "big-endian"}
EI_OSABI = {
    0x00: "UNIX System V", 0x03: "Linux", 0x06: "Solaris",
    0x09: "FreeBSD", 0x0C: "OpenBSD",
}
E_TYPE    = {1: "relocatable", 2: "executable", 3: "shared-object", 4: "core"}
E_MACHINE = {
    0x03: "x86", 0x28: "ARM", 0x3E: "x86-64",
    0xB7: "AArch64", 0xF3: "RISC-V",
}

# Known Warp-specific dynamic libraries (Warp Linux uses all of these)
_WARP_LIBS: List[str] = [
    "libwebkit2gtk",
    "libwayland-client",
    "libwayland-egl",
    "libGL",
    "libEGL",
    "libfontconfig",
    "libxkbcommon",
]

# Gemini CLI locations to search (in priority order)
_GEMINI_SEARCH_PATHS: List[str] = [
    # System / user PATH entries
    "gemini",
    "gemini-cli",
    "google-gemini",
    # Common install locations
    "~/.npm/bin/gemini",
    "~/.local/bin/gemini",
    "~/.local/bin/gemini-cli",
    "/usr/local/bin/gemini",
    "/usr/bin/gemini",
    # Node.js global installs
    "~/.nvm/versions/node/*/bin/gemini",
    "/usr/local/lib/node_modules/@google/gemini-cli/bin/gemini",
    "~/.npm/lib/node_modules/@google/gemini-cli/bin/gemini",
    # Python-installed (pip install google-generativeai)
    "~/.local/bin/gemini-cli",
]

# Known Gemini CLI OAuth / auth error messages (scraped from public source)
_GEMINI_AUTH_ERRORS: List[str] = [
    "Unable to open browser",
    "Failed to open browser",
    "BROWSER",
    "Could not authenticate",
    "Failed to store credentials",
    "oauth2",
    "OAuth",
    "access_token",
    "refresh_token",
    "GOOGLE_APPLICATION_CREDENTIALS",
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "gcloud auth",
    "application-default",
    "~/.config/gcloud",
    "credentials.json",
    "token.json",
]

# Gemini API key environment variable names (in priority order)
_GEMINI_ENV_VARS: List[str] = [
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "GOOGLE_GENERATIVE_AI_API_KEY",
]


# ===========================================================================
# SafeElfReader
# ===========================================================================

class SafeElfReader:
    """
    Opens an ELF binary as a **read-only memory-mapped view**.

    The file is NEVER executed or modified.  All parsing happens by
    reading bytes from the mmap — the OS treats the file as pure data.

    Use as a context manager:

        with SafeElfReader("/usr/bin/warp-terminal") as elf:
            hdr  = elf.read_header()
            secs = elf.list_sections()
            syms = elf.list_symbols()
            strs = elf.extract_strings(min_len=8)
    """

    def __init__(self, path: str):
        self.path = Path(path).resolve()
        self._fh: Optional[Any] = None
        self._mm: Optional[mmap.mmap] = None

    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------

    def __enter__(self) -> "SafeElfReader":
        if not self.path.exists():
            raise FileNotFoundError(f"ELF file not found: {self.path}")
        if self.path.stat().st_size < 16:
            raise ValueError(f"File too small to be a valid ELF: {self.path}")

        self._fh = open(self.path, "rb")
        try:
            self._mm = mmap.mmap(
                self._fh.fileno(), 0, access=mmap.ACCESS_READ
            )
        except Exception:
            self._fh.close()
            raise

        # Validate magic immediately so callers get a clear error
        if self._mm[:4] != ELF_MAGIC:
            self._mm.close()
            self._fh.close()
            raise ValueError(
                f"Not a valid ELF file (bad magic bytes): {self.path}"
            )
        return self

    def __exit__(self, *_: Any) -> None:
        if self._mm is not None:
            self._mm.close()
            self._mm = None
        if self._fh is not None:
            self._fh.close()
            self._fh = None

    # ------------------------------------------------------------------
    # Header
    # ------------------------------------------------------------------

    def read_header(self) -> Dict[str, Any]:
        """
        Parse and return the ELF identification + header fields.

        Never raises after a successful __enter__; all errors produce
        descriptive dicts.
        """
        mm = self._mm
        assert mm is not None, "Use SafeElfReader as a context manager"

        ei_class = mm[4]
        ei_data  = mm[5]
        ei_osabi = mm[7]
        is_64    = ei_class == 2
        little   = ei_data  == 1
        endian   = "<" if little else ">"

        e_type, e_machine = struct.unpack_from(endian + "HH", mm, 16)

        # e_entry / e_shoff / e_phoff differ between 32 and 64-bit
        if is_64:
            e_entry  = struct.unpack_from(endian + "Q", mm, 24)[0]
            e_phoff  = struct.unpack_from(endian + "Q", mm, 32)[0]
            e_shoff  = struct.unpack_from(endian + "Q", mm, 40)[0]
            e_phnum  = struct.unpack_from(endian + "H", mm, 56)[0]
            e_shnum  = struct.unpack_from(endian + "H", mm, 60)[0]
            e_shstrndx = struct.unpack_from(endian + "H", mm, 62)[0]
        else:
            e_entry  = struct.unpack_from(endian + "I", mm, 24)[0]
            e_phoff  = struct.unpack_from(endian + "I", mm, 28)[0]
            e_shoff  = struct.unpack_from(endian + "I", mm, 32)[0]
            e_phnum  = struct.unpack_from(endian + "H", mm, 44)[0]
            e_shnum  = struct.unpack_from(endian + "H", mm, 48)[0]
            e_shstrndx = struct.unpack_from(endian + "H", mm, 50)[0]

        return {
            "path":        str(self.path),
            "size_bytes":  self.path.stat().st_size,
            "class":       EI_CLASS.get(ei_class, f"unknown ({ei_class})"),
            "data":        EI_DATA.get(ei_data,   f"unknown ({ei_data})"),
            "os_abi":      EI_OSABI.get(ei_osabi, f"unknown (0x{ei_osabi:02x})"),
            "type":        E_TYPE.get(e_type,      f"unknown ({e_type})"),
            "machine":     E_MACHINE.get(e_machine, f"unknown (0x{e_machine:04x})"),
            "entry_point": hex(e_entry),
            "ph_count":    e_phnum,
            "sh_count":    e_shnum,
            "sh_str_idx":  e_shstrndx,
            "ph_offset":   hex(e_phoff),
            "sh_offset":   hex(e_shoff),
            "is_64bit":    is_64,
            "little_endian": little,
        }

    # ------------------------------------------------------------------
    # Sections
    # ------------------------------------------------------------------

    def list_sections(self) -> List[Dict[str, Any]]:
        """
        Return a list of ELF section headers parsed directly from the mmap.

        Each entry: {name, type_id, flags, addr, offset, size}.
        """
        mm = self._mm
        assert mm is not None

        hdr = self.read_header()
        is_64   = hdr["is_64bit"]
        little  = hdr["little_endian"]
        endian  = "<" if little else ">"

        sh_offset  = int(hdr["sh_offset"],  16)
        e_shnum    = hdr["sh_count"]
        e_shstrndx = hdr["sh_str_idx"]

        if e_shnum == 0 or sh_offset == 0:
            return []

        # Read the section header for the string table section first
        shentsize = 64 if is_64 else 40

        def _read_sh(idx: int) -> Tuple[int, int, int, int, int, int]:
            """Returns (sh_name_idx, sh_type, sh_flags, sh_addr, sh_offset, sh_size)"""
            base = sh_offset + idx * shentsize
            if base + shentsize > mm.size():
                return (0, 0, 0, 0, 0, 0)
            if is_64:
                fmt = endian + "IIQQQQIIQQ"
                (sh_name, sh_type, sh_flags, sh_addr,
                 sh_off, sh_size, *_) = struct.unpack_from(fmt, mm, base)
            else:
                fmt = endian + "IIIIIIIIII"
                (sh_name, sh_type, sh_flags, sh_addr,
                 sh_off, sh_size, *_) = struct.unpack_from(fmt, mm, base)
            return (sh_name, sh_type, sh_flags, sh_addr, sh_off, sh_size)

        # Get the string table section's offset and size
        strtab_off = 0
        strtab_size = 0
        if e_shstrndx < e_shnum:
            _, _, _, _, strtab_off, strtab_size = _read_sh(e_shstrndx)

        def _read_str(str_offset: int) -> str:
            if strtab_off == 0 or str_offset >= strtab_size:
                return f"<offset {str_offset}>"
            start = strtab_off + str_offset
            end = mm.find(b"\x00", start, start + 256)
            if end == -1:
                end = start + 64
            try:
                return mm[start:end].decode("utf-8", errors="replace")
            except Exception:
                return f"<offset {str_offset}>"

        _SH_TYPES = {
            0: "NULL", 1: "PROGBITS", 2: "SYMTAB", 3: "STRTAB",
            4: "RELA", 5: "HASH", 6: "DYNAMIC", 7: "NOTE",
            8: "NOBITS", 9: "REL", 11: "DYNSYM",
        }

        sections: List[Dict[str, Any]] = []
        for i in range(min(e_shnum, 512)):
            sh_name_idx, sh_type, sh_flags, sh_addr, sh_off, sh_size = _read_sh(i)
            sections.append({
                "index":   i,
                "name":    _read_str(sh_name_idx),
                "type":    _SH_TYPES.get(sh_type, f"0x{sh_type:x}"),
                "flags":   hex(sh_flags),
                "address": hex(sh_addr),
                "offset":  hex(sh_off),
                "size":    sh_size,
            })

        return sections

    # ------------------------------------------------------------------
    # Symbols
    # ------------------------------------------------------------------

    def list_symbols(self) -> List[str]:
        """
        Return symbol names from .dynsym (always present in dynamic ELFs)
        and .symtab (only in non-stripped binaries), parsed via readelf.

        Falls back to parsing the mmap directly if readelf is not available.
        """
        # Use readelf if available — faster and more reliable
        try:
            out = subprocess.run(
                ["readelf", "--syms", "--wide", str(self.path)],
                capture_output=True, text=True, timeout=30,
            ).stdout
            names: List[str] = []
            for line in out.splitlines():
                parts = line.split()
                if len(parts) < 8:
                    continue
                # The name is parts[7]; parts[8] (if present) is the GLIBC
                # version-index "(N)" token — strip it with the module-level regex.
                name = _RE_VER_SUFFIX.sub("", parts[7]).strip()
                if name and name != "Name":
                    names.append(name)
            return names
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        # Pure mmap fallback: find the .dynsym section and read symbol names
        return self._parse_dynsym_from_mmap()

    def _parse_dynsym_from_mmap(self) -> List[str]:
        """Minimal .dynsym + .dynstr parser using only the mmap."""
        mm = self._mm
        assert mm is not None

        sections = self.list_sections()
        dynsym = next((s for s in sections if s["name"] == ".dynsym"), None)
        dynstr = next((s for s in sections if s["name"] == ".dynstr"), None)
        if not dynsym or not dynstr:
            return []

        hdr     = self.read_header()
        endian  = "<" if hdr["little_endian"] else ">"
        is_64   = hdr["is_64bit"]
        sym_off = int(dynsym["offset"], 16)
        sym_sz  = dynsym["size"]
        str_off = int(dynstr["offset"], 16)
        str_sz  = dynstr["size"]
        entsize = 24 if is_64 else 16

        names: List[str] = []
        for i in range(sym_sz // entsize):
            base = sym_off + i * entsize
            if base + entsize > mm.size():
                break
            # Elf64_Sym: st_name(4) st_info(1) st_other(1) st_shndx(2) st_value(8) st_size(8)
            # Elf32_Sym: st_name(4) st_value(4) st_size(4) st_info(1) st_other(1) st_shndx(2)
            st_name = struct.unpack_from(endian + "I", mm, base)[0]
            if st_name >= str_sz:
                continue
            str_start = str_off + st_name
            str_end   = mm.find(b"\x00", str_start, str_start + 256)
            if str_end == -1:
                str_end = str_start + 64
            try:
                name = mm[str_start:str_end].decode("utf-8", errors="replace")
                if name:
                    names.append(name)
            except Exception:
                pass

        return names

    # ------------------------------------------------------------------
    # String extraction
    # ------------------------------------------------------------------

    def extract_strings(self, min_len: int = 8) -> List[str]:
        """
        Extract all printable ASCII strings of at least *min_len* chars
        directly from the mmap.

        This is a safe pure-Python implementation that never calls an
        external process and never executes the binary.
        """
        mm = self._mm
        assert mm is not None

        results: List[str] = []
        current: List[int] = []
        size = mm.size()

        for i in range(size):
            b = mm[i]
            if 0x20 <= b <= 0x7E:   # printable ASCII
                current.append(b)
            else:
                if len(current) >= min_len:
                    results.append(bytes(current).decode("ascii"))
                current = []

        if len(current) >= min_len:
            results.append(bytes(current).decode("ascii"))

        return results

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    def sha256(self) -> str:
        """Return the SHA-256 digest of the binary."""
        h = hashlib.sha256()
        mm = self._mm
        assert mm is not None
        chunk = 65536
        for offset in range(0, mm.size(), chunk):
            h.update(mm[offset : offset + chunk])
        return h.hexdigest()

    def is_stripped(self) -> bool:
        """Return True if the binary has no .symtab section."""
        return not any(s["name"] == ".symtab" for s in self.list_sections())


# ===========================================================================
# DebRipper
# ===========================================================================

class DebRipper:
    """
    Extracts a Debian .deb package on Linux and collects all ELF binaries
    and source artefacts for analysis.

    A .deb is an ``ar`` archive with three members:
      • ``debian-binary``  — text file containing "2.0"
      • ``control.tar.*`` — package metadata
      • ``data.tar.*``    — installed files (ELF binaries, configs, scripts)

    DebRipper extracts ``data.tar.*`` using the ``ar`` + ``tar`` utilities
    (both always available on Linux), then runs the same
    ElfAnalyzer + source-collection pipeline as RpmRipper.
    """

    def __init__(self, deb_path: str, output_dir: str = "deb_ripped"):
        self.deb_path   = Path(deb_path)
        self.output_dir = Path(output_dir)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def rip(self) -> Dict[str, Any]:
        """
        Full pipeline: extract → collect ELFs → collect sources → analyse.

        Returns the same report format as RpmRipper.rip() so all downstream
        tools (ElfDecompiler, ProjectReconstructor, GeminiAuthFixer) work
        identically.
        """
        if not self.deb_path.exists():
            raise FileNotFoundError(f"Deb package not found: {self.deb_path}")

        self.output_dir.mkdir(parents=True, exist_ok=True)
        extract_dir  = self.output_dir / "extracted"
        elf_dir      = self.output_dir / "elfs"
        sources_dir  = self.output_dir / "sources"
        control_dir  = self.output_dir / "control"
        extract_dir.mkdir(exist_ok=True)
        elf_dir.mkdir(exist_ok=True)
        sources_dir.mkdir(exist_ok=True)
        control_dir.mkdir(exist_ok=True)

        print(f"📦 Ripping .deb: {self.deb_path.name}")
        print(f"📁 Output:       {self.output_dir}")

        pkg_info = self._extract_control(control_dir)
        print(f"   Package: {pkg_info.get('package', 'unknown')} "
              f"{pkg_info.get('version', '')} ({pkg_info.get('architecture', '')})")

        print("🔧 Extracting data.tar …")
        extracted = self._extract_data(extract_dir)
        print(f"   Extracted {len(extracted)} files")

        print("🔍 Collecting ELF binaries …")
        elf_paths = self._collect_elfs(extracted, elf_dir)
        print(f"   Found {len(elf_paths)} ELF binaries")

        print("📂 Collecting source artefacts …")
        source_files = self._collect_sources(extracted, sources_dir)
        total = sum(len(v) for v in source_files.values())
        print(f"   Found {total} source/config/script files")

        print("🧬 Analysing ELF files with SafeElfReader + ElfAnalyzer …")
        elf_analyses: List[Dict[str, Any]] = []
        for ep in elf_paths:
            try:
                analysis = self._safe_analyze(ep)
                elf_analyses.append(analysis)
                print(f"   ✅ {Path(ep).name}  "
                      f"[{analysis['elf_header']['machine']}] "
                      f"lang={analysis['language']}")
            except Exception as exc:
                print(f"   ⚠️  {Path(ep).name}: {exc}")
                elf_analyses.append({"path": ep, "error": str(exc)})

        summary = self._build_summary(pkg_info, elf_analyses, source_files)

        report: Dict[str, Any] = {
            "deb_path":       str(self.deb_path),
            "pkg_info":       pkg_info,
            "output_dir":     str(self.output_dir),
            "extracted_files": len(extracted),
            "elf_files":      elf_analyses,
            "source_files":   source_files,
            "summary":        summary,
        }

        report_path = self.output_dir / "analysis_report.json"
        with open(report_path, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2, ensure_ascii=False)
        print(f"\n📊 Report saved → {report_path}")

        return report

    # ------------------------------------------------------------------
    # Extraction helpers
    # ------------------------------------------------------------------

    def _extract_control(self, control_dir: Path) -> Dict[str, str]:
        """Extract control.tar.* and parse the control file."""
        pkg_info: Dict[str, str] = {}
        with tempfile.TemporaryDirectory() as tmp:
            # ar x <deb> — extract all members into tmp/
            subprocess.run(
                ["ar", "x", str(self.deb_path)],
                cwd=tmp, capture_output=True,
            )
            # Find control.tar.*
            for fname in os.listdir(tmp):
                if fname.startswith("control.tar"):
                    ctrl_tar = Path(tmp) / fname
                    try:
                        with tarfile.open(str(ctrl_tar)) as tf:
                            # Extract control file
                            for member in tf.getmembers():
                                if member.name in ("./control", "control"):
                                    fobj = tf.extractfile(member)
                                    if fobj:
                                        raw = fobj.read().decode("utf-8",
                                                                  errors="replace")
                                        pkg_info = self._parse_control(raw)
                                    break
                            # Copy everything to control_dir
                            if _TARFILE_SUPPORTS_FILTER:
                                tf.extractall(str(control_dir), filter="data")
                            else:
                                tf.extractall(str(control_dir))
                    except (tarfile.TarError, OSError):
                        pass
                    break

        return pkg_info

    @staticmethod
    def _parse_control(text: str) -> Dict[str, str]:
        """Parse Debian control file format (RFC-2822-like) into a dict."""
        info: Dict[str, str] = {}
        current_key = ""
        for line in text.splitlines():
            if line.startswith(" ") or line.startswith("\t"):
                # Continuation of a multi-line field
                if current_key:
                    info[current_key] = info.get(current_key, "") + "\n" + line.strip()
            elif ":" in line:
                key, _, value = line.partition(":")
                current_key = key.strip().lower()
                info[current_key] = value.strip()
        return info

    def _extract_data(self, extract_dir: Path) -> List[str]:
        """Extract data.tar.* and return list of extracted file paths."""
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(
                ["ar", "x", str(self.deb_path)],
                cwd=tmp, capture_output=True,
            )
            for fname in os.listdir(tmp):
                if fname.startswith("data.tar"):
                    data_tar = Path(tmp) / fname
                    try:
                        with tarfile.open(str(data_tar)) as tf:
                            # Safe extraction — strip leading './'
                            for member in tf.getmembers():
                                # Sanitise path: remove leading ./ and /
                                member.name = member.name.lstrip("./").lstrip("/")
                                if not member.name:
                                    continue
                                # Security: block path traversal
                                dest = extract_dir / member.name
                                if not str(dest).startswith(str(extract_dir)):
                                    continue
                                try:
                                    if _TARFILE_SUPPORTS_FILTER:
                                        tf.extract(member, str(extract_dir),
                                                   set_attrs=False, filter="data")
                                    else:
                                        tf.extract(member, str(extract_dir),
                                                   set_attrs=False)
                                except (tarfile.TarError, OSError, PermissionError):
                                    pass
                    except (tarfile.TarError, OSError):
                        pass
                    break

        return self._walk(extract_dir)

    @staticmethod
    def _walk(directory: Path) -> List[str]:
        files: List[str] = []
        for root, _dirs, filenames in os.walk(directory):
            for fname in filenames:
                files.append(os.path.join(root, fname))
        return files

    # ------------------------------------------------------------------
    # ELF collection
    # ------------------------------------------------------------------

    @staticmethod
    def _is_elf(path: str) -> bool:
        try:
            with open(path, "rb") as fh:
                return fh.read(4) == ELF_MAGIC
        except (OSError, PermissionError):
            return False

    def _collect_elfs(self, all_files: List[str], elf_dir: Path) -> List[str]:
        preserved: List[str] = []
        seen: Dict[str, int] = {}
        for src in all_files:
            if not self._is_elf(src):
                continue
            base  = Path(src).name
            count = seen.get(base, 0)
            seen[base] = count + 1
            dest_name = base if count == 0 else f"{base}.{count}"
            dest = elf_dir / dest_name
            try:
                shutil.copy2(src, dest)
                preserved.append(str(dest))
            except (OSError, PermissionError) as exc:
                print(f"   ⚠️  Could not preserve {src}: {exc}")
        return preserved

    # ------------------------------------------------------------------
    # Source artefact collection (same categories as RpmRipper)
    # ------------------------------------------------------------------

    _SOURCE_CATEGORIES: Dict[str, str] = {
        ".c": "c_source", ".cpp": "cpp_source", ".cc": "cpp_source",
        ".h": "headers",  ".hpp": "headers",
        ".rs": "rust_source", ".go": "go_source",
        ".py": "python_scripts", ".rb": "ruby_scripts",
        ".sh": "shell_scripts", ".bash": "shell_scripts",
        ".js": "javascript", ".ts": "typescript",
        ".json": "json_configs", ".toml": "toml_configs",
        ".yaml": "yaml_configs", ".yml": "yaml_configs",
        ".conf": "config_files", ".ini": "config_files",
        ".md": "documentation", ".txt": "documentation",
        ".desktop": "desktop_files",
        ".service": "systemd_units", ".socket": "systemd_units",
        ".timer": "systemd_units",
        ".man": "man_pages",
    }

    def _collect_sources(
        self, all_files: List[str], sources_dir: Path
    ) -> Dict[str, List[str]]:
        categorised: Dict[str, List[str]] = {}
        seen: Dict[str, int] = {}
        for src in all_files:
            if self._is_elf(src):
                continue
            path   = Path(src)
            suffix = path.suffix.lower()
            fname  = path.name.lower()
            cat    = (self._SOURCE_CATEGORIES.get(suffix)
                      or self._SOURCE_CATEGORIES.get(fname)
                      or "other_files")
            cat_dir = sources_dir / cat
            cat_dir.mkdir(parents=True, exist_ok=True)
            base  = path.name
            count = seen.get(base, 0)
            seen[base] = count + 1
            dest_name = base if count == 0 else f"{base}.{count}"
            dest = cat_dir / dest_name
            try:
                shutil.copy2(src, dest)
                categorised.setdefault(cat, []).append(str(dest))
            except (OSError, PermissionError):
                pass
        return categorised

    # ------------------------------------------------------------------
    # Analysis
    # ------------------------------------------------------------------

    def _safe_analyze(self, elf_path: str) -> Dict[str, Any]:
        """
        Analyse an ELF binary using SafeElfReader first (for the header /
        sections / strings), then fall back to ElfAnalyzer for full analysis.
        """
        # Import here to avoid circular imports at module level
        try:
            from rpm_ripper import ElfAnalyzer
            analysis = ElfAnalyzer(elf_path).analyze()
        except ImportError:
            analysis = self._minimal_analyze(elf_path)

        # Augment with SafeElfReader data
        try:
            with SafeElfReader(elf_path) as elf:
                analysis["safe_header"]  = elf.read_header()
                analysis["sections"]     = elf.list_sections()
                analysis["sha256"]       = elf.sha256()
        except Exception as exc:
            analysis["safe_reader_error"] = str(exc)

        return analysis

    def _minimal_analyze(self, elf_path: str) -> Dict[str, Any]:
        """Minimal analysis using only SafeElfReader (no rpm_ripper dep)."""
        with SafeElfReader(elf_path) as elf:
            return {
                "path":       elf_path,
                "size_bytes": Path(elf_path).stat().st_size,
                "sha256":     elf.sha256(),
                "elf_header": elf.read_header(),
                "sections":   elf.list_sections(),
                "symbols":    elf.list_symbols()[:200],
                "language":   "unknown",
                "frameworks": [],
                "stripped":   elf.is_stripped(),
            }

    @staticmethod
    def _build_summary(
        pkg_info: Dict[str, str],
        elf_analyses: List[Dict],
        source_files: Dict[str, List[str]],
    ) -> Dict[str, Any]:
        languages: Dict[str, int] = {}
        stripped_count = 0
        error_count    = 0
        for ea in elf_analyses:
            if "error" in ea:
                error_count += 1
                continue
            lang = ea.get("language", "unknown")
            languages[lang] = languages.get(lang, 0) + 1
            if ea.get("stripped"):
                stripped_count += 1
        dominant = (max(languages, key=lambda k: languages[k])
                    if languages else "unknown")
        return {
            "package":   pkg_info.get("package", "unknown"),
            "version":   pkg_info.get("version", "unknown"),
            "arch":      pkg_info.get("architecture", "unknown"),
            "elf_count": len(elf_analyses),
            "error_count": error_count,
            "dominant_language": dominant,
            "language_breakdown": languages,
            "stripped_binaries": stripped_count,
            "source_file_categories": {k: len(v) for k, v in source_files.items()},
            "total_source_artefacts": sum(len(v) for v in source_files.values()),
        }


# ===========================================================================
# WarpRipper
# ===========================================================================

class WarpRipper:
    """
    Specialised ripper for Warp terminal — extends DebRipper with
    Warp-specific binary fingerprinting and config extraction.

    Warp Linux facts:
      • Binary:   /usr/bin/warp-terminal   (Rust, stripped)
      • Config:   ~/.config/warp-terminal/  (TOML)
      • Data:     ~/.local/share/warp-terminal/
      • Auth:     Warp login stored in ~/.local/share/warp-terminal/auth.json
                  or via the WARP_AUTH_TOKEN env var
      • Libs:     libwebkit2gtk-4.1, libwayland-*, libGL, libfontconfig

    WarpRipper adds to the report:
      • warp_binary    — path to the main warp-terminal ELF
      • warp_version   — version string extracted from binary strings
      • warp_auth_paths — all auth/token paths found in the binary
      • warp_config_paths — config file paths found in binary
      • warp_fingerprint — True/False for each Warp-specific indicator
    """

    _WARP_BINARY_NAMES = {"warp-terminal", "warp", "warp-terminal.bin"}
    _WARP_AUTH_KEYWORDS = [
        "auth.json", "auth_token", "WARP_AUTH_TOKEN",
        "Authorization:", "Bearer ", ".warp", "warp-terminal",
        "login", "logout", "authenticate", "credentials",
    ]
    _WARP_CONFIG_KEYWORDS = [
        "~/.config/warp", "warp-terminal/config", ".warp/config",
        "WARP_CONFIG", "keybindings.yaml", "themes/",
    ]
    _WARP_VERSION_RE = re.compile(
        r"(?:warp|warp-terminal)[- ]v?(\d+\.\d+[\d.]*)", re.IGNORECASE
    )

    def __init__(self, package_path: str):
        """
        *package_path* can be:
          • A .deb file   — extracted with DebRipper
          • A .rpm file   — extracted with RpmRipper
          • A directory   — treated as already-extracted package root
          • An ELF file   — analysed directly as the Warp binary
        """
        self.package_path = Path(package_path)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def rip(self, output_dir: str = "warp_ripped") -> Dict[str, Any]:
        """
        Full Warp rip pipeline.  Returns report dict with extra warp_* keys.
        """
        out = Path(output_dir)
        print(f"🚀 Warp Terminal Ripper")
        print(f"   Input:  {self.package_path}")
        print(f"   Output: {out}")

        # Step 1: extract the package (or use directly if it's an ELF / dir)
        base_report = self._get_base_report(out)

        # Step 2: find the warp-terminal ELF within the analysis
        warp_elf = self._find_warp_binary(base_report, out)

        # Step 3: deep-analyse the Warp binary
        warp_specific: Dict[str, Any] = {}
        if warp_elf:
            print(f"🔬 Deep-analysing Warp binary: {Path(warp_elf).name}")
            warp_specific = self._analyse_warp_binary(warp_elf)
        else:
            print("   ⚠️  Warp binary not found in package")
            warp_specific = {"found": False}

        # Merge into report
        base_report["warp_analysis"] = warp_specific
        base_report["warp_binary"]   = warp_elf

        # Save updated report
        report_path = out / "warp_analysis_report.json"
        with open(report_path, "w", encoding="utf-8") as fh:
            json.dump(base_report, fh, indent=2, ensure_ascii=False)
        print(f"\n📊 Warp report saved → {report_path}")

        self._print_warp_summary(warp_specific)
        return base_report

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_base_report(self, out: Path) -> Dict[str, Any]:
        """Extract package and get base analysis report."""
        suffix = self.package_path.suffix.lower()

        if suffix == ".deb":
            return DebRipper(str(self.package_path), str(out)).rip()

        if suffix == ".rpm":
            try:
                from rpm_ripper import RpmRipper
                return RpmRipper(str(self.package_path), str(out)).rip()
            except ImportError:
                raise RuntimeError("rpm_ripper.py not found; needed for .rpm files")

        if self.package_path.is_dir():
            # Already-extracted directory
            all_files = []
            for root, _dirs, files in os.walk(self.package_path):
                for f in files:
                    all_files.append(os.path.join(root, f))
            elf_dir     = out / "elfs"
            sources_dir = out / "sources"
            elf_dir.mkdir(parents=True, exist_ok=True)
            sources_dir.mkdir(exist_ok=True)

            ripper = DebRipper.__new__(DebRipper)
            ripper.deb_path   = self.package_path
            ripper.output_dir = out
            elf_paths    = ripper._collect_elfs(all_files, elf_dir)
            source_files = ripper._collect_sources(all_files, sources_dir)

            elf_analyses = []
            for ep in elf_paths:
                try:
                    elf_analyses.append(ripper._safe_analyze(ep))
                except Exception as exc:
                    elf_analyses.append({"path": ep, "error": str(exc)})

            return {
                "deb_path": str(self.package_path),
                "pkg_info": {"package": self.package_path.name},
                "output_dir": str(out),
                "extracted_files": len(all_files),
                "elf_files": elf_analyses,
                "source_files": source_files,
                "summary": ripper._build_summary({}, elf_analyses, source_files),
            }

        if self.package_path.is_file() and DebRipper._is_elf(str(self.package_path)):
            # Single ELF passed directly
            out.mkdir(parents=True, exist_ok=True)
            ripper = DebRipper.__new__(DebRipper)
            analysis = ripper._safe_analyze(str(self.package_path))
            return {
                "deb_path": str(self.package_path),
                "pkg_info": {"package": self.package_path.name},
                "output_dir": str(out),
                "extracted_files": 1,
                "elf_files": [analysis],
                "source_files": {},
                "summary": ripper._build_summary({}, [analysis], {}),
            }

        raise ValueError(
            f"Unsupported input type: {self.package_path}  "
            f"(expected .deb, .rpm, directory, or ELF binary)"
        )

    @staticmethod
    def _is_elf(path: str) -> bool:
        try:
            with open(path, "rb") as fh:
                return fh.read(4) == ELF_MAGIC
        except (OSError, PermissionError):
            return False

    def _find_warp_binary(
        self, report: Dict[str, Any], out: Path
    ) -> Optional[str]:
        """Find the main warp-terminal ELF among the analysed binaries."""
        for ea in report.get("elf_files", []):
            if "error" in ea:
                continue
            name = Path(ea.get("path", "")).name.lower()
            if any(name == w for w in self._WARP_BINARY_NAMES):
                return ea["path"]

        # Second pass: any ELF with Warp-specific shared libs
        for ea in report.get("elf_files", []):
            if "error" in ea:
                continue
            libs = ea.get("shared_libs", [])
            if any(warp_lib in lib
                   for warp_lib in _WARP_LIBS
                   for lib in libs):
                return ea["path"]

        # Third pass: look in the elfs/ dir directly
        elf_dir = out / "elfs"
        if elf_dir.exists():
            for f in sorted(elf_dir.iterdir()):
                if f.name.lower() in self._WARP_BINARY_NAMES:
                    return str(f)

        return None

    def _analyse_warp_binary(self, elf_path: str) -> Dict[str, Any]:
        """
        Deep-analyse the Warp ELF using SafeElfReader for safe string
        extraction, and ElfAnalyzer for full structural analysis.
        """
        result: Dict[str, Any] = {
            "found": True,
            "path": elf_path,
            "version": "unknown",
            "is_rust": False,
            "is_stripped": True,
            "warp_libs_found": [],
            "auth_paths": [],
            "config_paths": [],
            "env_vars": [],
            "auth_endpoint": None,
            "token_format": "unknown",
        }

        # Safe string extraction via mmap
        try:
            with SafeElfReader(elf_path) as elf:
                result["is_stripped"] = elf.is_stripped()
                hdr = elf.read_header()
                result["arch"] = hdr.get("machine", "unknown")

                # Extract strings — this is the key analysis step
                all_strings = elf.extract_strings(min_len=6)
                result["_string_count"] = len(all_strings)

                # Detect Rust
                result["is_rust"] = any(
                    "rust" in s.lower() or "__rust" in s or "panicked at" in s
                    for s in all_strings[:2000]
                )

                # Extract version
                for s in all_strings:
                    m = self._WARP_VERSION_RE.search(s)
                    if m:
                        result["version"] = m.group(1)
                        break

                # Find auth and config paths
                auth_paths:   List[str] = []
                config_paths: List[str] = []
                env_vars:     List[str] = []
                auth_endpoint: Optional[str] = None

                for s in all_strings:
                    # Auth paths
                    if any(kw.lower() in s.lower()
                           for kw in self._WARP_AUTH_KEYWORDS):
                        if (s.startswith("/") or s.startswith("~")
                                or "warp" in s.lower()):
                            auth_paths.append(s)

                    # Config paths
                    if any(kw.lower() in s.lower()
                           for kw in self._WARP_CONFIG_KEYWORDS):
                        config_paths.append(s)

                    # Environment variables (ALL_CAPS pattern)
                    if re.match(r'^[A-Z][A-Z0-9_]{3,}$', s):
                        env_vars.append(s)

                    # Auth endpoint (URL)
                    if ("https://" in s and
                            ("auth" in s.lower() or "login" in s.lower()
                             or "oauth" in s.lower() or "token" in s.lower())):
                        auth_endpoint = s

                result["auth_paths"]    = sorted(set(auth_paths))[:20]
                result["config_paths"]  = sorted(set(config_paths))[:20]
                result["env_vars"]      = sorted(set(env_vars))[:30]
                result["auth_endpoint"] = auth_endpoint

        except Exception as exc:
            result["safe_reader_error"] = str(exc)

        # Check Warp-specific libs from full analysis
        try:
            from rpm_ripper import ElfAnalyzer
            full = ElfAnalyzer(elf_path).analyze()
            libs = full.get("shared_libs", [])
            result["warp_libs_found"] = [
                lib for lib in libs
                if any(w in lib for w in _WARP_LIBS)
            ]
            result["all_shared_libs"] = libs
        except (ImportError, Exception):
            pass

        return result

    @staticmethod
    def _print_warp_summary(warp: Dict[str, Any]) -> None:
        if not warp.get("found"):
            print("\n⚠️  Warp binary not found — is this a Warp package?")
            return
        print("\n" + "=" * 60)
        print("🚀 Warp Terminal Analysis")
        print("=" * 60)
        print(f"  Version   : {warp.get('version', 'unknown')}")
        print(f"  Arch      : {warp.get('arch', 'unknown')}")
        print(f"  Language  : {'Rust' if warp.get('is_rust') else 'unknown'}")
        print(f"  Stripped  : {warp.get('is_stripped', 'unknown')}")
        print(f"  Strings   : {warp.get('_string_count', 0)}")

        libs = warp.get("warp_libs_found", [])
        if libs:
            print(f"  Warp libs : {', '.join(libs[:4])}")

        auth = warp.get("auth_paths", [])
        if auth:
            print("  Auth paths:")
            for p in auth[:5]:
                print(f"    {p}")

        endpoint = warp.get("auth_endpoint")
        if endpoint:
            print(f"  Auth URL  : {endpoint}")

        env_vars = warp.get("env_vars", [])
        warp_env = [v for v in env_vars if "WARP" in v]
        if warp_env:
            print(f"  WARP env vars: {', '.join(warp_env[:5])}")

        print("=" * 60)


# ===========================================================================
# GeminiAuthFixer
# ===========================================================================

class GeminiAuthFixer:
    """
    Diagnoses and fixes Google Gemini CLI authentication failures on Linux.

    ── Why Gemini CLI sign-in fails on Linux ──────────────────────────────
    Gemini CLI (both the Node.js @google/gemini-cli and Python google-genai
    tools) uses the Google OAuth2 "Device Authorization Grant" or the
    "Authorization Code" flow:

    1. The CLI opens a browser to accounts.google.com/o/oauth2/auth
    2. The user approves access
    3. The CLI receives an authorization code (via localhost redirect or
       out-of-band copy-paste)
    4. It exchanges the code for an access_token + refresh_token
    5. It stores the token in:
         Node CLI  → ~/.config/gemini/credentials.json
                  OR ~/.gemini/credentials.json
         Python    → ~/.config/gcloud/application_default_credentials.json
                  OR $GOOGLE_APPLICATION_CREDENTIALS

    On headless/SSH Linux, step 1 fails: no browser, no display.
    On many Linux desktops, step 5 fails: no GNOME Keyring / no secret-service.

    ── What GeminiAuthFixer does ──────────────────────────────────────────
    1. Locates the Gemini CLI binary (ELF, Node script, or Python module)
    2. If it is an ELF  → uses SafeElfReader to extract strings and identify
       the exact token file path and OAuth flow
    3. If it is a Node  → reads the JS source to find the credentials path
    4. Diagnoses the failure mode
    5. Writes the fix:
       a. ~/.config/gemini/credentials.json  — pre-filled OAuth token using
          an API key (skips the browser flow entirely)
       b. A shell wrapper script at ~/bin/gemini that sets GEMINI_API_KEY
       c. A .env snippet for CI/headless environments
    """

    # Credential file locations searched by the Node.js Gemini CLI
    _NODE_CRED_PATHS: List[str] = [
        "~/.config/gemini/credentials.json",
        "~/.gemini/credentials.json",
        "~/.config/google/credentials.json",
    ]

    # Credential file locations searched by the Python google-genai / gcloud
    _PYTHON_CRED_PATHS: List[str] = [
        "~/.config/gcloud/application_default_credentials.json",
        "~/.google/credentials.json",
    ]

    # Failure patterns we look for in CLI output / binary strings
    _FAILURE_PATTERNS: List[Dict[str, str]] = [
        {
            "pattern": "Unable to open browser",
            "cause":   "headless_no_browser",
            "fix":     "Use API key authentication instead of OAuth",
        },
        {
            "pattern": "ENOENT.*credentials",
            "cause":   "missing_credentials_file",
            "fix":     "Create ~/.config/gemini/credentials.json with API key",
        },
        {
            "pattern": "Failed to store credentials",
            "cause":   "no_keyring",
            "fix":     "Use file-based credential storage (no secret-service needed)",
        },
        {
            "pattern": "invalid_grant",
            "cause":   "expired_token",
            "fix":     "Delete old token file and re-authenticate with API key",
        },
        {
            "pattern": "UNAUTHENTICATED",
            "cause":   "no_credentials",
            "fix":     "Set GEMINI_API_KEY environment variable",
        },
        {
            "pattern": "Could not load the default credentials",
            "cause":   "no_application_default_credentials",
            "fix":     "Set GOOGLE_APPLICATION_CREDENTIALS or GEMINI_API_KEY",
        },
    ]

    def __init__(self):
        self.gemini_path: Optional[str] = None
        self.gemini_type: str = "unknown"   # "elf", "node", "python", "unknown"
        self.diagnosis:   Optional[Dict[str, Any]] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def diagnose(self) -> Dict[str, Any]:
        """
        Locate the Gemini CLI binary and diagnose why authentication fails.

        **Side effect**: stores the result in ``self.diagnosis`` so that a
        subsequent call to :meth:`apply_fix` can use the diagnosis without
        re-running the detection logic.  Call ``diagnose()`` before
        ``apply_fix()`` to get a fresh result; otherwise ``apply_fix``
        will call it automatically.

        Returns a dict with keys:
          found         True if the CLI binary was located.
          path          Path to the binary.
          type          "elf" | "node" | "python" | "shell" | "unknown"
          failure_modes List of detected failure mode dicts.
          token_paths   Credential file paths the CLI reads/writes.
          env_vars      Environment variables that control auth.
          existing_tokens  Credential files already present on disk.
          recommendations  List of human-readable fix instructions.
        """
        print("🔍 Diagnosing Gemini CLI authentication …")

        result: Dict[str, Any] = {
            "found":           False,
            "path":            None,
            "type":            "unknown",
            "failure_modes":   [],
            "token_paths":     [],
            "env_vars":        list(_GEMINI_ENV_VARS),
            "existing_tokens": [],
            "recommendations": [],
        }

        # 1. Find the binary
        gemini_path = self._find_gemini_cli()
        if not gemini_path:
            result["recommendations"].append(
                "Gemini CLI not found. Install with:\n"
                "  npm install -g @google/gemini-cli\n"
                "or:\n"
                "  pip install google-genai"
            )
            print("   ⚠️  Gemini CLI not found on this system")
            self.diagnosis = result
            return result

        result["found"] = True
        result["path"]  = gemini_path
        self.gemini_path = gemini_path
        print(f"   Found: {gemini_path}")

        # 2. Determine type and analyse
        gemini_type, details = self._analyse_cli_binary(gemini_path)
        result["type"] = gemini_type
        self.gemini_type = gemini_type
        result.update(details)

        # 3. Find existing token files
        existing = self._find_existing_tokens()
        result["existing_tokens"] = existing

        # 4. Check for known failure causes
        failure_modes = self._detect_failure_modes(gemini_path, details)
        result["failure_modes"] = failure_modes

        # 5. Generate recommendations
        result["recommendations"] = self._generate_recommendations(
            failure_modes, existing
        )

        print(f"   Type  : {gemini_type}")
        print(f"   Tokens: {len(existing)} existing credential file(s)")
        print(f"   Issues: {len(failure_modes)} failure mode(s) detected")

        self.diagnosis = result
        return result

    def apply_fix(
        self,
        api_key: Optional[str] = None,
        output_dir: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Apply fixes to make Gemini CLI sign-in work on headless Linux.

        If *api_key* is provided, writes credential files and a wrapper
        script that use API key auth (skips the browser OAuth flow).

        If *api_key* is None, only writes a template and instructions.

        Returns a dict listing all files created.
        """
        print("\n🔧 Applying Gemini auth fix …")

        if self.diagnosis is None:
            self.diagnose()

        out = Path(output_dir) if output_dir else Path.home() / ".config" / "gemini"
        out.mkdir(parents=True, exist_ok=True)

        created: List[str] = []
        instructions: List[str] = []

        # a. Write credentials.json
        cred_file = self._write_credentials_json(api_key, out)
        if cred_file:
            created.append(cred_file)
            instructions.append(f"Credentials file written: {cred_file}")

        # b. Write shell wrapper
        wrapper = self._write_shell_wrapper(api_key, out)
        if wrapper:
            created.append(wrapper)
            instructions.append(f"Shell wrapper written: {wrapper}")
            instructions.append(
                f"Add to PATH: export PATH=\"{out}:$PATH\""
            )

        # c. Write .env snippet
        env_file = self._write_env_snippet(api_key, out)
        if env_file:
            created.append(env_file)
            instructions.append(
                f"Environment snippet: {env_file}\n"
                f"  Source with: source {env_file}"
            )

        # d. Write comprehensive instructions
        guide = self._write_fix_guide(api_key, out)
        created.append(guide)

        result = {
            "files_created": created,
            "instructions":  instructions,
            "guide":         guide,
        }

        print(f"\n✅ Fix applied! {len(created)} file(s) written:")
        for f in created:
            print(f"   {f}")
        if not api_key:
            print("\n💡 No API key provided — template files written.")
            print("   Get your key from: https://aistudio.google.com/app/apikey")
            print("   Then re-run with: --api-key YOUR_KEY")

        return result

    # ------------------------------------------------------------------
    # Binary analysis
    # ------------------------------------------------------------------

    def _find_gemini_cli(self) -> Optional[str]:
        """Search common locations for the Gemini CLI binary."""
        for entry in _GEMINI_SEARCH_PATHS:
            # Handle glob patterns
            if "*" in entry:
                import glob as _glob
                matches = _glob.glob(os.path.expanduser(entry))
                for m in sorted(matches):
                    if os.path.isfile(m):
                        return m
                continue

            # Check PATH
            found = shutil.which(entry)
            if found:
                return found

            # Expand ~ and check directly
            expanded = Path(entry).expanduser()
            if expanded.exists() and expanded.is_file():
                return str(expanded)

        return None

    def _analyse_cli_binary(
        self, path: str
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Determine whether the binary is ELF, Node.js, Python, or a shell
        script, and extract auth-relevant strings.
        """
        details: Dict[str, Any] = {
            "token_paths":     [],
            "env_vars_found":  [],
            "auth_strings":    [],
            "oauth_endpoint":  None,
        }

        # Check file type
        p = Path(path)
        if not p.exists():
            return "unknown", details

        with open(path, "rb") as fh:
            magic = fh.read(4)

        # ELF binary
        if magic == ELF_MAGIC:
            return "elf", self._analyse_elf_cli(path, details)

        # Script: read the first line / shebang
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                first_lines = [fh.readline() for _ in range(5)]
        except OSError:
            return "unknown", details

        shebang = first_lines[0].strip()

        if "node" in shebang or "nodejs" in shebang:
            return "node", self._analyse_node_cli(path, details)
        if "python" in shebang:
            return "python", self._analyse_python_cli(path, details)
        if "bash" in shebang or "sh" in shebang:
            return "shell", self._analyse_shell_cli(path, details)

        return "unknown", details

    def _analyse_elf_cli(
        self, path: str, details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Use SafeElfReader to extract auth strings from an ELF Gemini CLI."""
        try:
            with SafeElfReader(path) as elf:
                strings = elf.extract_strings(min_len=6)
        except Exception as exc:
            details["elf_error"] = str(exc)
            return details

        self._extract_auth_details(strings, details)
        return details

    def _analyse_node_cli(
        self, path: str, details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Read Node.js source and extract auth strings."""
        try:
            # Node CLI may be a single bundled file or an entry script
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                source = fh.read(256 * 1024)   # read up to 256 KB
            strings = re.findall(r'"([^"]{6,200})"', source)
            strings += re.findall(r"'([^']{6,200})'", source)
            # Also try the node_modules directory
            node_dir = Path(path).parent.parent
            for auth_file in node_dir.rglob("auth*.js"):
                with open(str(auth_file), encoding="utf-8",
                          errors="replace") as fh:
                    extra = fh.read(128 * 1024)
                strings += re.findall(r'"([^"]{6,200})"', extra)
        except (OSError, UnicodeDecodeError):
            strings = []
        self._extract_auth_details(strings, details)
        return details

    def _analyse_python_cli(
        self, path: str, details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Read Python source and extract auth strings."""
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                source = fh.read(256 * 1024)
            strings = re.findall(r'"([^"]{6,200})"', source)
            strings += re.findall(r"'([^']{6,200})'", source)
        except (OSError, UnicodeDecodeError):
            strings = []
        self._extract_auth_details(strings, details)
        return details

    def _analyse_shell_cli(
        self, path: str, details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Read shell script and extract auth strings."""
        return self._analyse_python_cli(path, details)  # same approach

    def _extract_auth_details(
        self, strings: List[str], details: Dict[str, Any]
    ) -> None:
        """
        Scan a list of strings for token file paths, env var names,
        and OAuth endpoints.
        """
        token_paths:  List[str] = []
        env_vars:     List[str] = []
        auth_strings: List[str] = []
        oauth_url:    Optional[str] = None

        for s in strings:
            # File paths that look like credential stores
            if any(kw in s for kw in ("credentials", "token", "oauth",
                                       "auth.json", ".config")):
                if "/" in s or s.startswith("~"):
                    token_paths.append(s)
                auth_strings.append(s)

            # Environment variable names
            if re.match(r'^[A-Z][A-Z0-9_]{3,40}$', s):
                if any(kw in s for kw in ("API_KEY", "TOKEN", "CREDENTIALS",
                                            "SECRET", "GEMINI", "GOOGLE",
                                            "AUTH")):
                    env_vars.append(s)

            # OAuth / auth endpoint URLs
            if "https://" in s and ("oauth" in s.lower() or
                                     "token" in s.lower() or
                                     "auth" in s.lower()):
                if not oauth_url:
                    oauth_url = s

        details["token_paths"]    = sorted(set(token_paths))[:20]
        details["env_vars_found"] = sorted(set(env_vars))[:20]
        details["auth_strings"]   = sorted(set(auth_strings))[:30]
        details["oauth_endpoint"] = oauth_url

    # ------------------------------------------------------------------
    # Failure mode detection
    # ------------------------------------------------------------------

    def _detect_failure_modes(
        self, path: str, details: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Try to run the CLI with --version and watch for known error patterns."""
        failures: List[Dict[str, str]] = []

        # Try to run the CLI non-destructively
        test_output = ""
        try:
            r = subprocess.run(
                [path, "--version"],
                capture_output=True, text=True, timeout=5,
            )
            test_output = r.stdout + r.stderr
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError,
                PermissionError):
            pass

        # Also try `gemini auth status` if it exists
        try:
            r2 = subprocess.run(
                [path, "auth", "status"],
                capture_output=True, text=True, timeout=5,
            )
            test_output += r2.stdout + r2.stderr
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError,
                PermissionError):
            pass

        # Check for each known failure pattern
        for fp in self._FAILURE_PATTERNS:
            if re.search(fp["pattern"], test_output, re.IGNORECASE):
                failures.append({
                    "pattern": fp["pattern"],
                    "cause":   fp["cause"],
                    "fix":     fp["fix"],
                })

        # Always add "headless" as a potential issue if no DISPLAY
        if not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY"):
            if not any(f["cause"] == "headless_no_browser" for f in failures):
                failures.append({
                    "cause":   "headless_no_browser",
                    "pattern": "No DISPLAY/WAYLAND_DISPLAY environment variable",
                    "fix":     (
                        "Running headless — OAuth browser flow will fail. "
                        "Use API key authentication instead."
                    ),
                })

        # Check if any env var auth is already set
        for var in _GEMINI_ENV_VARS:
            if os.environ.get(var):
                failures = [f for f in failures
                            if f["cause"] != "headless_no_browser"]
                break

        return failures

    @staticmethod
    def _find_existing_tokens() -> List[str]:
        """Return any existing Gemini credential files."""
        found: List[str] = []
        all_paths = (
            GeminiAuthFixer._NODE_CRED_PATHS
            + GeminiAuthFixer._PYTHON_CRED_PATHS
        )
        for p in all_paths:
            expanded = Path(p).expanduser()
            if expanded.exists():
                found.append(str(expanded))
        return found

    @staticmethod
    def _generate_recommendations(
        failure_modes: List[Dict[str, str]],
        existing_tokens: List[str],
    ) -> List[str]:
        recs: List[str] = []

        if not failure_modes:
            recs.append("No obvious auth failures detected.")
            recs.append(
                "If sign-in still fails, try: "
                "export GEMINI_API_KEY=your_key_here"
            )
            return recs

        for fm in failure_modes:
            recs.append(f"[{fm['cause']}] {fm['fix']}")

        recs.append(
            "\n🔑 QUICKEST FIX — API key (no browser needed):\n"
            "  1. Get a key: https://aistudio.google.com/app/apikey\n"
            "  2. export GEMINI_API_KEY=your_key_here\n"
            "  3. Run: gemini  (it will use the key automatically)"
        )

        if existing_tokens:
            recs.append(
                f"\n⚠️  Stale token files found — delete them to force fresh auth:\n"
                + "\n".join(f"  rm {t}" for t in existing_tokens)
            )

        return recs

    # ------------------------------------------------------------------
    # Fix file writers
    # ------------------------------------------------------------------

    def _write_credentials_json(
        self, api_key: Optional[str], out: Path
    ) -> Optional[str]:
        """
        Write ~/.config/gemini/credentials.json.

        The Gemini Node.js CLI accepts a credentials.json with either:
          • OAuth client credentials + token (from browser flow)
          • OR simply an "apiKey" field (for API key auth)
        """
        cred = {
            "_comment": (
                "Generated by THE FORGE GeminiAuthFixer. "
                "Replace <YOUR_GEMINI_API_KEY> with your key from "
                "https://aistudio.google.com/app/apikey"
            ),
            "apiKey": api_key or "<YOUR_GEMINI_API_KEY>",
            "type": "apikey",
        }

        # Also write the gcloud application default credentials format
        gcloud_cred = {
            "type": "api_key",
            "client_id": "gemini-cli",
            "api_key": api_key or "<YOUR_GEMINI_API_KEY>",
        }

        cred_path = out / "credentials.json"
        with open(cred_path, "w", encoding="utf-8") as fh:
            json.dump(cred, fh, indent=2)

        # Also write to gcloud location if it doesn't exist yet
        gcloud_dir = Path("~/.config/gcloud").expanduser()
        gcloud_dir.mkdir(parents=True, exist_ok=True)
        gcloud_path = gcloud_dir / "application_default_credentials.json"
        if not gcloud_path.exists():
            try:
                with open(gcloud_path, "w", encoding="utf-8") as fh:
                    json.dump(gcloud_cred, fh, indent=2)
            except OSError:
                pass

        return str(cred_path)

    def _write_shell_wrapper(
        self, api_key: Optional[str], out: Path
    ) -> Optional[str]:
        """
        Write a shell wrapper that sets the right env vars before
        calling the real gemini binary.
        """
        real_path = self.gemini_path or "gemini"
        key_line  = (
            f'export GEMINI_API_KEY="{api_key}"'
            if api_key
            else 'export GEMINI_API_KEY="${GEMINI_API_KEY:-<YOUR_GEMINI_API_KEY>}"'
        )

        content = f"""\
#!/usr/bin/env bash
# THE FORGE — Gemini CLI auth wrapper
# Generated by GeminiAuthFixer
#
# This wrapper sets the API key and credential paths before calling
# the real Gemini CLI, so sign-in works without a browser.

{key_line}
export GOOGLE_API_KEY="${{GEMINI_API_KEY}}"
export GOOGLE_GENERATIVE_AI_API_KEY="${{GEMINI_API_KEY}}"

# Point to our pre-written credentials file
export GEMINI_CREDENTIALS_FILE="{out}/credentials.json"
export GOOGLE_APPLICATION_CREDENTIALS="{Path('~/.config/gcloud/application_default_credentials.json').expanduser()}"

# Disable browser-based auth flow (headless safe)
export GEMINI_DISABLE_BROWSER_AUTH=1
export BROWSER=echo

exec "{real_path}" "$@"
"""
        wrapper_path = out / "gemini"
        with open(wrapper_path, "w", encoding="utf-8") as fh:
            fh.write(content)
        os.chmod(wrapper_path, 0o755)
        return str(wrapper_path)

    def _write_env_snippet(
        self, api_key: Optional[str], out: Path
    ) -> Optional[str]:
        """Write a .env file / shell snippet for CI and headless use."""
        key_val = api_key or "<YOUR_GEMINI_API_KEY>"
        content = f"""\
# THE FORGE — Gemini CLI environment variables
# Source this file: source {out}/gemini.env
# Or add to ~/.bashrc / ~/.zshrc

export GEMINI_API_KEY="{key_val}"
export GOOGLE_API_KEY="{key_val}"
export GOOGLE_GENERATIVE_AI_API_KEY="{key_val}"
export GEMINI_CREDENTIALS_FILE="{out}/credentials.json"
export GOOGLE_APPLICATION_CREDENTIALS="{Path('~/.config/gcloud/application_default_credentials.json').expanduser()}"

# Prevent the CLI from trying to open a browser on headless systems
export GEMINI_DISABLE_BROWSER_AUTH=1

# For CI systems — add to your pipeline environment
# GEMINI_API_KEY: {key_val}
"""
        env_path = out / "gemini.env"
        with open(env_path, "w", encoding="utf-8") as fh:
            fh.write(content)
        return str(env_path)

    def _write_fix_guide(
        self, api_key: Optional[str], out: Path
    ) -> str:
        """Write a comprehensive human-readable fix guide."""
        diag = self.diagnosis or {}
        failures = diag.get("failure_modes", [])
        existing = diag.get("existing_tokens", [])
        gemini_path = diag.get("path", "gemini")
        gemini_type = diag.get("type", "unknown")
        key_val = api_key or "<YOUR_GEMINI_API_KEY>"

        lines = [
            "# Gemini CLI Authentication Fix Guide",
            "",
            "Generated by **THE FORGE GeminiAuthFixer** using binary analysis.",
            "",
            "## Diagnosis",
            "",
            f"- **CLI location**: `{gemini_path}`",
            f"- **CLI type**: {gemini_type}",
            f"- **Failure modes detected**: {len(failures)}",
        ]

        for fm in failures:
            lines.append(f"  - `{fm['cause']}`: {fm['fix']}")

        lines += [
            "",
            "## Why Gemini CLI sign-in fails on headless Linux",
            "",
            "Gemini CLI uses **OAuth2 Authorization Code flow** by default:",
            "",
            "```",
            "CLI → opens browser → accounts.google.com/o/oauth2/auth",
            "       ↓ user approves",
            "CLI ← receives code (localhost redirect or copy-paste)",
            "CLI → exchanges code for access_token + refresh_token",
            "CLI → stores token in ~/.config/gemini/credentials.json",
            "```",
            "",
            "**On headless Linux**: step 1 fails — no browser, no `$DISPLAY`.",
            "**On some Linux desktops**: step 5 fails — no GNOME Keyring.",
            "",
            "## The Fix: API Key Authentication",
            "",
            "API key auth completely bypasses the browser OAuth flow:",
            "",
            "### Step 1 — Get an API key",
            "",
            "```",
            "https://aistudio.google.com/app/apikey",
            "```",
            "",
            "### Step 2 — Set the environment variable",
            "",
            "```bash",
            f"export GEMINI_API_KEY=\"{key_val}\"",
            "",
            "# Make it permanent:",
            f"echo 'export GEMINI_API_KEY=\"{key_val}\"' >> ~/.bashrc",
            "source ~/.bashrc",
            "```",
            "",
            "### Step 3 — Use the wrapper script (optional)",
            "",
            f"The wrapper at `{out}/gemini` sets all required variables",
            "automatically. Add it to your PATH:",
            "",
            "```bash",
            f"export PATH=\"{out}:$PATH\"",
            "gemini  # now uses API key, no browser needed",
            "```",
            "",
            "### Step 4 — For CI / GitHub Actions",
            "",
            "```yaml",
            "env:",
            f"  GEMINI_API_KEY: ${{{{ secrets.GEMINI_API_KEY }}}}",
            "```",
            "",
        ]

        if existing:
            lines += [
                "## Existing token files",
                "",
                "These files were found and may contain stale OAuth tokens:",
                "",
            ]
            for t in existing:
                lines.append(f"- `{t}`")
            lines += [
                "",
                "If you still get auth errors after setting `GEMINI_API_KEY`,",
                "delete the stale token files:",
                "",
                "```bash",
                *[f"rm -f {t}" for t in existing],
                "```",
                "",
            ]

        lines += [
            "## Binary analysis results",
            "",
            "The Gemini CLI binary was analysed safely (read-only mmap)",
            "to find the credential file paths it reads at runtime:",
            "",
        ]
        for tp in diag.get("token_paths", []):
            lines.append(f"- `{tp}`")

        lines += [
            "",
            "## Files created by GeminiAuthFixer",
            "",
            f"- `{out}/credentials.json` — API key credentials",
            f"- `{out}/gemini` — shell wrapper script",
            f"- `{out}/gemini.env` — environment variable snippet",
            f"- `{out}/GEMINI_AUTH_FIX.md` — this guide",
            "",
            "---",
            "*Generated by THE FORGE binary_tools.py GeminiAuthFixer*",
        ]

        guide_path = out / "GEMINI_AUTH_FIX.md"
        with open(guide_path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))
        return str(guide_path)


# ===========================================================================
# CLI
# ===========================================================================

class BinaryToolsCLI:
    """
    Command-line interface for THE FORGE binary tools.

    Combines SafeElfReader, DebRipper, WarpRipper, and GeminiAuthFixer
    into a single coherent CLI.
    """

    def run(self, argv: Optional[List[str]] = None) -> int:
        parser = argparse.ArgumentParser(
            prog="binary_tools",
            description=(
                "🔧 THE FORGE — Binary Tools\n\n"
                "Safe ELF reader · Deb ripper · Warp terminal ripper · Gemini auth fixer"
            ),
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=(
                "examples:\n"
                "  # Safely inspect any ELF binary (never executed)\n"
                "  %(prog)s --inspect /usr/bin/warp-terminal\n\n"
                "  # Rip a .deb package (same pipeline as rpm_ripper)\n"
                "  %(prog)s --rip-deb warp-terminal_0.2024.deb -o out/\n\n"
                "  # Full Warp rip + analysis\n"
                "  %(prog)s --rip-warp warp-terminal_0.2024.deb -o out/\n\n"
                "  # Diagnose Gemini CLI auth (read-only, no changes made)\n"
                "  %(prog)s --diagnose-gemini\n\n"
                "  # Fix Gemini auth with an API key (no browser needed)\n"
                "  %(prog)s --fix-gemini-auth --api-key YOUR_KEY\n\n"
                "  # Full pipeline: rip Warp AND fix Gemini auth together\n"
                "  %(prog)s --rip-warp warp-terminal_0.2024.deb \\\n"
                "           --fix-gemini-auth --api-key YOUR_KEY -o out/\n"
            ),
        )

        # Primary actions (mutually exclusive with each other)
        action = parser.add_mutually_exclusive_group()
        action.add_argument(
            "--inspect",
            metavar="ELF",
            help=(
                "Safely open and inspect an ELF binary using read-only mmap. "
                "The binary is NEVER executed."
            ),
        )
        action.add_argument(
            "--rip-deb",
            metavar="DEB",
            help="Extract and analyse a .deb package",
        )
        action.add_argument(
            "--rip-warp",
            metavar="PACKAGE",
            help=(
                "Rip a Warp terminal package (.deb, .rpm, directory, or ELF) "
                "with Warp-specific fingerprinting. "
                "Can be combined with --fix-gemini-auth."
            ),
        )
        action.add_argument(
            "--diagnose-gemini",
            action="store_true",
            default=False,
            help=(
                "Diagnose Gemini CLI authentication issues (read-only). "
                "Locates the CLI, analyses its binary with SafeElfReader, "
                "and prints what is wrong — without writing any files."
            ),
        )

        # --fix-gemini-auth is NOT in the mutex group so it can be combined
        # with --rip-warp for the full pipeline.
        parser.add_argument(
            "--fix-gemini-auth",
            action="store_true",
            default=False,
            help=(
                "Write Gemini auth fix files (credentials.json, wrapper, .env). "
                "Can be used standalone or combined with --rip-warp."
            ),
        )
        parser.add_argument(
            "--api-key",
            default=None,
            metavar="KEY",
            help=(
                "Gemini API key for --fix-gemini-auth / --diagnose-gemini. "
                "Get one at https://aistudio.google.com/app/apikey"
            ),
        )
        parser.add_argument(
            "-o", "--output-dir",
            default="binary_tools_out",
            help="Output directory (default: binary_tools_out/)",
        )
        parser.add_argument(
            "--json",
            action="store_true",
            default=False,
            help="Output results as JSON to stdout",
        )

        args = parser.parse_args(argv)

        if args.inspect:
            return self._run_inspect(args.inspect, args.json)

        if args.rip_deb:
            return self._run_rip_deb(args.rip_deb, args.output_dir, args.json)

        if args.rip_warp:
            rc = self._run_rip_warp(
                args.rip_warp, args.output_dir,
                args.fix_gemini_auth, args.api_key, args.json,
            )
            return rc

        if args.diagnose_gemini:
            return self._run_diagnose_gemini(args.api_key, args.json)

        if args.fix_gemini_auth:
            return self._run_fix_gemini(args.api_key, args.output_dir, args.json)

        parser.print_help()
        return 1

    # ------------------------------------------------------------------

    def _run_inspect(self, elf_path: str, as_json: bool) -> int:
        if not as_json:
            print("=" * 64)
            print("🔥 THE FORGE — Safe ELF Inspector")
            print("=" * 64)
            print(f"\n🔒 Opening {elf_path} as read-only mmap (NEVER executed)")

        try:
            with SafeElfReader(elf_path) as elf:
                header   = elf.read_header()
                sections = elf.list_sections()
                symbols  = elf.list_symbols()[:100]
                strings  = elf.extract_strings(min_len=8)
                stripped = elf.is_stripped()
                sha      = elf.sha256()
        except (FileNotFoundError, ValueError) as exc:
            print(f"\n❌ {exc}", file=sys.stderr)
            return 1

        result = {
            "header":        header,
            "section_count": len(sections),
            "sections":      [s["name"] for s in sections if s["name"]],
            "symbol_count":  len(symbols),
            "symbols_sample": symbols[:20],
            "string_count":  len(strings),
            "strings_sample": strings[:20],
            "stripped":      stripped,
            "sha256":        sha,
        }

        if as_json:
            print(json.dumps(result, indent=2))
        else:
            self._print_inspect_result(result, sections)

        return 0

    def _run_rip_deb(self, deb_path: str, output_dir: str,
                     as_json: bool) -> int:
        print("=" * 64)
        print("🔥 THE FORGE — Deb Ripper")
        print("=" * 64)
        try:
            report = DebRipper(deb_path, output_dir).rip()
        except (FileNotFoundError, RuntimeError) as exc:
            print(f"\n❌ {exc}", file=sys.stderr)
            return 1
        if as_json:
            print(json.dumps(report, indent=2))
        else:
            self._print_deb_summary(report["summary"])
        return 0

    def _run_rip_warp(
        self,
        package_path: str,
        output_dir: str,
        also_fix_gemini: bool,
        api_key: Optional[str],
        as_json: bool,
    ) -> int:
        print("=" * 64)
        print("🔥 THE FORGE — Warp Terminal Ripper")
        print("=" * 64)
        try:
            report = WarpRipper(package_path).rip(output_dir=output_dir)
        except (FileNotFoundError, ValueError, RuntimeError) as exc:
            print(f"\n❌ {exc}", file=sys.stderr)
            return 1

        if as_json:
            print(json.dumps(report, indent=2))

        if also_fix_gemini:
            self._run_fix_gemini(api_key, output_dir, as_json)

        return 0

    def _run_fix_gemini(
        self, api_key: Optional[str], output_dir: str, as_json: bool
    ) -> int:
        print("=" * 64)
        print("🔥 THE FORGE — Gemini Auth Fixer")
        print("=" * 64)

        fixer     = GeminiAuthFixer()
        diagnosis = fixer.diagnose()

        print("\n📋 Diagnosis:")
        if not diagnosis["found"]:
            print("   Gemini CLI not found on this system.")
        else:
            for rec in diagnosis["recommendations"]:
                print(f"   {rec}")

        fix_result = fixer.apply_fix(api_key=api_key, output_dir=output_dir)

        if as_json:
            print(json.dumps({
                "diagnosis":  diagnosis,
                "fix_result": fix_result,
            }, indent=2))
        else:
            self._print_fix_summary(diagnosis, fix_result)

        return 0

    def _run_diagnose_gemini(
        self, api_key: Optional[str], as_json: bool
    ) -> int:
        """Read-only diagnosis — no files written."""
        print("=" * 64)
        print("🔥 THE FORGE — Gemini Auth Diagnostic (read-only)")
        print("=" * 64)

        fixer     = GeminiAuthFixer()
        diagnosis = fixer.diagnose()

        if as_json:
            print(json.dumps(diagnosis, indent=2))
            return 0

        print(f"\n  CLI found  : {diagnosis['found']}")
        if diagnosis.get("path"):
            print(f"  CLI path   : {diagnosis['path']}")
        print(f"  CLI type   : {diagnosis.get('type', 'unknown')}")

        failures = diagnosis.get("failure_modes", [])
        if failures:
            print(f"\n  ❌ {len(failures)} failure mode(s) detected:")
            for fm in failures:
                print(f"     [{fm['cause']}] {fm['fix']}")
        else:
            print("\n  ✅ No obvious failure modes detected")

        existing = diagnosis.get("existing_tokens", [])
        if existing:
            print(f"\n  ⚠️  Existing token files ({len(existing)}):")
            for t in existing:
                print(f"     {t}")

        token_paths = diagnosis.get("token_paths", [])
        if token_paths:
            print(f"\n  📂 Token paths found in binary:")
            for p in token_paths[:8]:
                print(f"     {p}")

        print("\n  📋 Recommendations:")
        for rec in diagnosis.get("recommendations", []):
            print(f"     {rec}")

        if api_key:
            print(f"\n  💡 API key provided — run with --fix-gemini-auth to apply the fix")

        print("\n  (No files written — use --fix-gemini-auth to apply fixes)")
        print("=" * 64)
        return 0

    # ------------------------------------------------------------------
    # Printers
    # ------------------------------------------------------------------

    @staticmethod
    def _print_inspect_result(
        result: Dict[str, Any],
        sections: List[Dict],
    ) -> None:
        hdr = result["header"]
        print(f"\n  File     : {hdr['path']}")
        print(f"  Size     : {hdr['size_bytes']:,} bytes")
        print(f"  SHA-256  : {result['sha256']}")
        print(f"  Class    : {hdr['class']}")
        print(f"  Type     : {hdr['type']}")
        print(f"  Machine  : {hdr['machine']}")
        print(f"  Entry    : {hdr['entry_point']}")
        print(f"  Stripped : {result['stripped']}")
        print(f"  Sections : {result['section_count']}")
        print(f"  Symbols  : {result['symbol_count']}")
        print(f"  Strings  : {result['string_count']}")

        notable = [s["name"] for s in sections
                   if s["name"] in (".text", ".data", ".rodata", ".symtab",
                                    ".debug_info", ".debug_line",
                                    ".gnu_debuglink", ".go.buildinfo")]
        if notable:
            print(f"  Notable sections: {', '.join(notable)}")

        if result["symbols_sample"]:
            print("\n  Symbols (first 20):")
            for sym in result["symbols_sample"]:
                print(f"    {sym}")

        if result["strings_sample"]:
            print("\n  Strings (first 20):")
            for s in result["strings_sample"]:
                print(f"    {s!r}")

    @staticmethod
    def _print_deb_summary(summary: Dict[str, Any]) -> None:
        print("\n" + "=" * 64)
        print("📊 Deb Analysis Summary")
        print("=" * 64)
        print(f"  Package  : {summary['package']} {summary['version']}")
        print(f"  Arch     : {summary['arch']}")
        print(f"  ELFs     : {summary['elf_count']}")
        print(f"  Stripped : {summary['stripped_binaries']}")
        print(f"  Language : {summary['dominant_language']}")
        if summary.get("source_file_categories"):
            print("  Sources  :")
            for cat, cnt in sorted(summary["source_file_categories"].items()):
                print(f"    {cat}: {cnt}")
        print("=" * 64)

    @staticmethod
    def _print_fix_summary(
        diagnosis: Dict[str, Any],
        fix_result: Dict[str, Any],
    ) -> None:
        print("\n" + "=" * 64)
        print("📊 Gemini Auth Fix Summary")
        print("=" * 64)
        print(f"  CLI found  : {diagnosis.get('found', False)}")
        if diagnosis.get("path"):
            print(f"  CLI path   : {diagnosis['path']}")
        print(f"  CLI type   : {diagnosis.get('type', 'unknown')}")
        print(f"  Issues     : {len(diagnosis.get('failure_modes', []))}")
        print(f"  Files made : {len(fix_result.get('files_created', []))}")
        for f in fix_result.get("files_created", []):
            print(f"    {f}")
        print()
        print("  Next steps:")
        for rec in fix_result.get("instructions", []):
            print(f"    {rec}")
        guide = fix_result.get("guide")
        if guide:
            print(f"\n  Full guide: {guide}")
        print("=" * 64)


# ===========================================================================
# Entry point
# ===========================================================================

def main() -> None:
    sys.exit(BinaryToolsCLI().run())


if __name__ == "__main__":
    main()
