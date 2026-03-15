#!/usr/bin/env python3
"""
RPM Ripper & ELF Analyzer / Decompiler
=======================================
Part of THE FORGE toolkit.

─────────────────────────────────────────────────────────────────────────────
WHAT IS AN ELF?  IS IT SOURCE CODE?
─────────────────────────────────────────────────────────────────────────────
ELF (Executable and Linkable Format) is a **compiled binary** — NOT source
code.  The pipeline looks like this:

    Source code (.c / .rs / .go / .cpp)
          │
          ▼  compiler (gcc / rustc / go build / clang)
          │
    Object files (.o)
          │
          ▼  linker (ld / lld)
          │
    ELF binary  ← this is what you get inside an RPM

Compilation is a **lossy, one-way process**.  The compiler discards:
  • All comments
  • Most variable/parameter names (unless debug symbols are present)
  • High-level control-flow structure (loops, match arms, closures)
  • Type aliases, macros, generics before monomorphisation

You **cannot recover exact source code** from a compiled ELF.  What you CAN
recover, with varying fidelity, depends on what was left behind:

┌────────────────────────┬──────────────────────────────────────────────────┐
│ What survived          │ What it gives you                                │
├────────────────────────┼──────────────────────────────────────────────────┤
│ .symtab (symbols)      │ Function names + sizes (if not stripped)         │
│ DWARF debug sections   │ Source file names, line numbers, variable types  │
│ Dynamic symbols        │ Exported/imported function names                 │
│ .rodata (strings)      │ Literal strings, error messages, URLs            │
│ Mangled C++/Rust syms  │ After demangling: class names, method signatures │
│ Go symbol table        │ Go always keeps full function names + types      │
│ .note.gnu.build-id     │ Matches binary to a debuginfo package            │
└────────────────────────┴──────────────────────────────────────────────────┘

SAFE & CLEAN APPROACHES (best → least complete)
──────────────────────────────────────────────────
1. **Fetch the .src.rpm** — The RPM ecosystem always ships a source RPM.
   This contains the ACTUAL source code.  Use --find-source or look in
   https://src.fedoraproject.org / https://kojipkgs.fedoraproject.org

2. **Extract DWARF debug info** — If the package or its -debuginfo companion
   has DWARF sections, ``addr2line`` and ``readelf --debug-dump`` reconstruct
   file/line/variable information almost perfectly.

3. **Demangle symbols** — C++ (c++filt), Rust (rustfilt / rustc --print
   symbol-names), Go (already human-readable).  Gives you class hierarchies
   and function signatures without decompiling a single byte.

4. **Disassemble with objdump / llvm-objdump** — Machine code → assembly.
   100% accurate, but requires assembly knowledge to read.

5. **Decompile with Ghidra / Binary Ninja / IDA** — Assembly → C-like
   pseudocode.  Variable names are recovered as ``local_10``, ``param_1``
   etc.  Functional but not the original source.  Pass ``--ghidra`` to
   this tool to invoke Ghidra headless if it is installed.

─────────────────────────────────────────────────────────────────────────────
USAGE
─────────────────────────────────────────────────────────────────────────────
Library:
    from rpm_ripper import RpmRipper, ElfAnalyzer, ElfDecompiler

    # Rip an RPM and analyse every ELF inside it
    report = RpmRipper("warp-terminal.rpm", output_dir="out/").rip()
    for elf in report["elf_files"]:
        print(elf["path"], elf["language"])

    # Decompile a single ELF
    decomp = ElfDecompiler("out/elfs/warp").decompile(output_dir="src_out/")

CLI:
    # Full pipeline: extract RPM → preserve ELFs → analyse → write report
    python3 rpm_ripper.py warp-terminal.rpm -o out/

    # Analyse a single ELF file you already have
    python3 rpm_ripper.py --analyze-only /usr/bin/warp-terminal

    # Decompile a single ELF → write reconstructed source skeleton
    python3 rpm_ripper.py --decompile /usr/bin/warp-terminal -o src_out/

    # Try to find the companion .src.rpm for a binary RPM
    python3 rpm_ripper.py --find-source warp-terminal-0.1-1.x86_64.rpm
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
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# ELF constants
# ---------------------------------------------------------------------------

ELF_MAGIC = b"\x7fELF"

EI_CLASS = {1: "32-bit", 2: "64-bit"}
EI_DATA = {1: "little-endian", 2: "big-endian"}
EI_OSABI = {
    0x00: "UNIX System V",
    0x03: "Linux",
    0x06: "Solaris",
    0x09: "FreeBSD",
    0x0C: "OpenBSD",
}
E_TYPE = {1: "relocatable", 2: "executable", 3: "shared-object", 4: "core"}
E_MACHINE = {
    0x03: "x86",
    0x28: "ARM",
    0x3E: "x86-64",
    0xB7: "AArch64",
    0xF3: "RISC-V",
    0x16: "PowerPC",
    0x15: "PowerPC-64",
    0x02: "SPARC",
}

# Language/framework fingerprints found in symbol tables or binary strings
_LANG_FINGERPRINTS: List[Dict[str, Any]] = [
    # Rust — mangled symbols always start with _ZN and contain "rust"
    {
        "language": "Rust",
        "symbols": ["__rust_alloc", "__rust_dealloc", "rust_begin_unwind", "_ZN4core"],
        "sections": [],
        "strings": ["rust_panic_handler", "panicked at"],
    },
    # Go — runtime symbols and a special build-id section
    {
        "language": "Go",
        "symbols": ["runtime.main", "runtime.goexit", "main.main"],
        "sections": [".go.buildinfo"],
        "strings": ["go:buildid", "runtime.main"],
    },
    # Python C-extension — PyInit_ prefix
    {
        "language": "Python (C extension)",
        "symbols": ["PyInit_", "Py_InitModule"],
        "sections": [],
        "strings": [],
    },
    # JVM / JNI
    {
        "language": "JVM (JNI)",
        "symbols": ["JNI_OnLoad", "JNI_CreateJavaVM"],
        "sections": [],
        "strings": [],
    },
]

_FRAMEWORK_FINGERPRINTS: List[Dict[str, str]] = [
    {"framework": "Qt5/Qt6", "lib_prefix": "libQt"},
    {"framework": "GTK3/GTK4", "lib_prefix": "libgtk"},
    {"framework": "SDL2", "lib_prefix": "libSDL2"},
    {"framework": "OpenGL", "lib_prefix": "libGL"},
    {"framework": "Vulkan", "lib_prefix": "libvulkan"},
    {"framework": "Tauri (WebKit)", "lib_prefix": "libwebkit2gtk"},
    {"framework": "Electron (Node)", "lib_prefix": "libnode"},
    {"framework": "CUDA", "lib_prefix": "libcuda"},
    {"framework": "OpenCL", "lib_prefix": "libOpenCL"},
]


# ---------------------------------------------------------------------------
# ElfAnalyzer
# ---------------------------------------------------------------------------

class ElfAnalyzer:
    """
    Analyzes a single ELF binary.

    Parses the ELF header, detects shared-library dependencies via the
    dynamic section / ``readelf``, and fingerprints the language runtime
    and major frameworks used.
    """

    def __init__(self, path: str):
        self.path = Path(path)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze(self) -> Dict[str, Any]:
        """
        Return a structured analysis dictionary for the ELF file.

        Keys
        ----
        path            Absolute path to the ELF binary.
        size_bytes      File size in bytes.
        sha256          SHA-256 hex digest.
        elf_header      Parsed ELF header fields.
        shared_libs     List of NEEDED shared libraries.
        language        Detected language runtime (str | "unknown").
        frameworks      List of detected frameworks.
        build_id        GNU build-id (hex string) or None.
        stripped        True if the binary has no symbol table.
        """
        if not self.path.exists():
            raise FileNotFoundError(f"ELF file not found: {self.path}")

        result: Dict[str, Any] = {
            "path": str(self.path),
            "size_bytes": self.path.stat().st_size,
            "sha256": self._sha256(),
            "elf_header": self._parse_elf_header(),
            "shared_libs": self._get_shared_libs(),
            "language": "unknown",
            "frameworks": [],
            "build_id": self._get_build_id(),
            "stripped": self._is_stripped(),
        }

        result["language"] = self._detect_language(result)
        result["frameworks"] = self._detect_frameworks(result["shared_libs"])
        return result

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _sha256(self) -> str:
        h = hashlib.sha256()
        with open(self.path, "rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

    def _parse_elf_header(self) -> Dict[str, Any]:
        """Parse the 64-byte ELF identification + header fields."""
        with open(self.path, "rb") as fh:
            raw = fh.read(64)

        if len(raw) < 16 or raw[:4] != ELF_MAGIC:
            raise ValueError(f"Not a valid ELF file: {self.path}")

        ei_class = raw[4]
        ei_data = raw[5]
        ei_osabi = raw[7]
        is_64 = ei_class == 2
        little = ei_data == 1
        endian = "<" if little else ">"

        if is_64:
            # 64-bit ELF header
            if len(raw) < 64:
                raise ValueError("ELF header truncated")
            e_type, e_machine = struct.unpack_from(endian + "HH", raw, 16)
        else:
            # 32-bit ELF header
            if len(raw) < 52:
                raise ValueError("ELF header truncated")
            e_type, e_machine = struct.unpack_from(endian + "HH", raw, 16)

        return {
            "class": EI_CLASS.get(ei_class, f"unknown ({ei_class})"),
            "data": EI_DATA.get(ei_data, f"unknown ({ei_data})"),
            "os_abi": EI_OSABI.get(ei_osabi, f"unknown (0x{ei_osabi:02x})"),
            "type": E_TYPE.get(e_type, f"unknown ({e_type})"),
            "machine": E_MACHINE.get(e_machine, f"unknown (0x{e_machine:04x})"),
        }

    def _run(self, *args: str) -> str:
        """Run a subprocess and return stdout, empty string on error."""
        try:
            proc = subprocess.run(
                list(args),
                capture_output=True,
                text=True,
                timeout=30,
            )
            return proc.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return ""

    def _get_shared_libs(self) -> List[str]:
        """Return list of NEEDED shared libraries from the dynamic section."""
        out = self._run("readelf", "-d", str(self.path))
        libs: List[str] = []
        for line in out.splitlines():
            if "(NEEDED)" in line and "Shared library:" in line:
                # Format: 0x... (NEEDED)  Shared library: [libfoo.so.1]
                start = line.rfind("[")
                end = line.rfind("]")
                if start != -1 and end != -1 and end > start:
                    libs.append(line[start + 1 : end])
        return libs

    def _get_build_id(self) -> Optional[str]:
        """Return the GNU build-id hex string if present."""
        out = self._run("readelf", "-n", str(self.path))
        for line in out.splitlines():
            if "Build ID:" in line:
                parts = line.split("Build ID:")
                if len(parts) == 2:
                    return parts[1].strip()
        return None

    def _is_stripped(self) -> bool:
        """Return True if the binary has no .symtab section."""
        out = self._run("readelf", "-S", str(self.path))
        return ".symtab" not in out

    def _get_symbol_names(self) -> List[str]:
        """Return a sample of symbol names (from dynamic + static symtab)."""
        out = self._run("readelf", "--syms", str(self.path))
        names: List[str] = []
        for line in out.splitlines():
            parts = line.split()
            if len(parts) >= 8:
                names.append(parts[-1])
        return names

    def _get_section_names(self) -> List[str]:
        """Return section names present in the binary."""
        out = self._run("readelf", "-S", str(self.path))
        names: List[str] = []
        for line in out.splitlines():
            # Lines look like:  [ 1] .interp   PROGBITS ...
            if "]" in line:
                after_bracket = line.split("]", 1)[-1].strip()
                section_name = after_bracket.split()[0] if after_bracket.split() else ""
                if section_name:
                    names.append(section_name)
        return names

    def _get_strings_sample(self) -> List[str]:
        """Return a sample of printable strings from the binary."""
        out = self._run("strings", "-n", "8", str(self.path))
        # Limit to first 2000 lines to keep analysis fast
        return out.splitlines()[:2000]

    def _detect_language(self, partial: Dict[str, Any]) -> str:
        """Fingerprint the language runtime from symbols, sections, strings."""
        symbols = self._get_symbol_names()
        sections = self._get_section_names()
        strings = self._get_strings_sample()

        sym_set = set(symbols)
        sec_set = set(sections)
        str_set = set(strings)

        for fp in _LANG_FINGERPRINTS:
            # Check symbols
            for sym in fp["symbols"]:
                if any(sym in s for s in sym_set):
                    return fp["language"]
            # Check sections
            for sec in fp["sections"]:
                if sec in sec_set:
                    return fp["language"]
            # Check strings
            for needle in fp["strings"]:
                if any(needle in s for s in str_set):
                    return fp["language"]

        # Fallback: if linked against libc++ / libstdc++ → C++, else C
        libs = partial.get("shared_libs", [])
        for lib in libs:
            if "stdc++" in lib or "libc++" in lib:
                return "C++"
        return "C"

    def _detect_frameworks(self, shared_libs: List[str]) -> List[str]:
        """Detect high-level frameworks from shared library names."""
        found: List[str] = []
        for fp in _FRAMEWORK_FINGERPRINTS:
            prefix = fp["lib_prefix"]
            if any(lib.startswith(prefix) for lib in shared_libs):
                found.append(fp["framework"])
        return found


# ---------------------------------------------------------------------------
# RpmRipper
# ---------------------------------------------------------------------------

class RpmRipper:
    """
    Rips an RPM package, preserves all ELF binaries, and analyzes them.

    Parameters
    ----------
    rpm_path    Path to the ``.rpm`` file.
    output_dir  Directory where extracted files and the ELF collection are
                written.  Created if it does not exist.
    """

    def __init__(self, rpm_path: str, output_dir: str = "rpm_ripped"):
        self.rpm_path = Path(rpm_path)
        self.output_dir = Path(output_dir)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def rip(self) -> Dict[str, Any]:
        """
        Full pipeline: extract → collect ELFs → analyze → return report.

        Returns
        -------
        dict with keys:
            rpm_path        Source RPM file path.
            rpm_info        RPM metadata from ``rpm -qip``.
            output_dir      Output directory path.
            extracted_files Total number of extracted files.
            elf_files       List of per-ELF analysis dicts.
            summary         High-level summary dict.
        """
        if not self.rpm_path.exists():
            raise FileNotFoundError(f"RPM not found: {self.rpm_path}")

        self.output_dir.mkdir(parents=True, exist_ok=True)
        extract_dir = self.output_dir / "extracted"
        elf_dir = self.output_dir / "elfs"
        extract_dir.mkdir(exist_ok=True)
        elf_dir.mkdir(exist_ok=True)

        print(f"📦 Ripping: {self.rpm_path.name}")
        print(f"📁 Output:  {self.output_dir}")

        rpm_info = self._query_rpm_metadata()
        print(f"   Package: {rpm_info.get('name', 'unknown')} "
              f"{rpm_info.get('version', '')} ({rpm_info.get('arch', '')})")

        print("🔧 Extracting RPM payload …")
        extracted = self._extract(extract_dir)
        print(f"   Extracted {len(extracted)} files")

        print("🔍 Collecting ELF binaries …")
        elf_paths = self._collect_elfs(extracted, elf_dir)
        print(f"   Found {len(elf_paths)} ELF binaries")

        print("🧬 Analyzing ELF files …")
        elf_analyses: List[Dict[str, Any]] = []
        for ep in elf_paths:
            try:
                analysis = ElfAnalyzer(ep).analyze()
                elf_analyses.append(analysis)
                print(f"   ✅ {Path(ep).name}  [{analysis['elf_header']['machine']}] "
                      f"lang={analysis['language']}")
            except Exception as exc:
                print(f"   ⚠️  {Path(ep).name}: {exc}")
                elf_analyses.append({"path": ep, "error": str(exc)})

        summary = self._build_summary(rpm_info, elf_analyses)

        report: Dict[str, Any] = {
            "rpm_path": str(self.rpm_path),
            "rpm_info": rpm_info,
            "output_dir": str(self.output_dir),
            "extracted_files": len(extracted),
            "elf_files": elf_analyses,
            "summary": summary,
        }

        report_path = self.output_dir / "analysis_report.json"
        with open(report_path, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2, ensure_ascii=False)
        print(f"\n📊 Report saved → {report_path}")

        return report

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _query_rpm_metadata(self) -> Dict[str, str]:
        """Query RPM package metadata with ``rpm -qip``."""
        fields = {
            "name": "%{NAME}",
            "version": "%{VERSION}",
            "release": "%{RELEASE}",
            "arch": "%{ARCH}",
            "summary": "%{SUMMARY}",
            "license": "%{LICENSE}",
            "url": "%{URL}",
            "buildhost": "%{BUILDHOST}",
            "packager": "%{PACKAGER}",
            "vendor": "%{VENDOR}",
            "description": "%{DESCRIPTION}",
        }
        query_fmt = "\n".join(f"{k}={v}" for k, v in fields.items())
        try:
            out = subprocess.check_output(
                ["rpm", "-qp", "--queryformat", query_fmt, str(self.rpm_path)],
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=30,
            )
            info: Dict[str, str] = {}
            for line in out.splitlines():
                if "=" in line:
                    key, _, val = line.partition("=")
                    info[key.strip()] = val.strip()
            return info
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return {"name": self.rpm_path.stem}

    def _extract(self, extract_dir: Path) -> List[str]:
        """
        Extract the RPM payload using ``rpm2cpio`` + ``cpio``.

        Returns a list of extracted file paths.
        """
        # rpm2cpio <file> | cpio -idm --quiet
        try:
            rpm2cpio = subprocess.Popen(
                ["rpm2cpio", str(self.rpm_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
            )
            cpio = subprocess.Popen(
                ["cpio", "-idm", "--quiet"],
                stdin=rpm2cpio.stdout,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=str(extract_dir),
            )
            if rpm2cpio.stdout:
                rpm2cpio.stdout.close()
            cpio.communicate(timeout=120)
            rpm2cpio.wait(timeout=10)
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(f"Extraction timed out: {exc}") from exc
        except FileNotFoundError as exc:
            raise RuntimeError(
                "rpm2cpio or cpio not found. Install rpm/cpio tools."
            ) from exc

        # Walk extracted directory and collect all file paths
        files: List[str] = []
        for root, _dirs, filenames in os.walk(extract_dir):
            for fname in filenames:
                files.append(os.path.join(root, fname))
        return files

    @staticmethod
    def _is_elf(path: str) -> bool:
        """Quick check: read first 4 bytes and compare to ELF magic."""
        try:
            with open(path, "rb") as fh:
                return fh.read(4) == ELF_MAGIC
        except (OSError, PermissionError):
            return False

    def _collect_elfs(self, all_files: List[str], elf_dir: Path) -> List[str]:
        """
        Filter ELF files, copy them to *elf_dir* preserving names, and
        return the list of destination paths.
        """
        preserved: List[str] = []
        seen_names: Dict[str, int] = {}

        for src in all_files:
            if not self._is_elf(src):
                continue

            base = Path(src).name
            # Deduplicate names by appending a counter
            count = seen_names.get(base, 0)
            seen_names[base] = count + 1
            dest_name = base if count == 0 else f"{base}.{count}"
            dest = elf_dir / dest_name

            try:
                shutil.copy2(src, dest)
                preserved.append(str(dest))
            except (OSError, PermissionError) as exc:
                print(f"   ⚠️  Could not preserve {src}: {exc}")

        return preserved

    @staticmethod
    def _build_summary(rpm_info: Dict[str, str], elf_analyses: List[Dict]) -> Dict[str, Any]:
        """Build a human-readable high-level summary."""
        languages: Dict[str, int] = {}
        frameworks: Dict[str, int] = {}
        machines: Dict[str, int] = {}
        stripped_count = 0
        error_count = 0

        for ea in elf_analyses:
            if "error" in ea:
                error_count += 1
                continue
            lang = ea.get("language", "unknown")
            languages[lang] = languages.get(lang, 0) + 1

            for fw in ea.get("frameworks", []):
                frameworks[fw] = frameworks.get(fw, 0) + 1

            machine = ea.get("elf_header", {}).get("machine", "unknown")
            machines[machine] = machines.get(machine, 0) + 1

            if ea.get("stripped"):
                stripped_count += 1

        dominant_lang = (
            max(languages, key=lambda k: languages[k]) if languages else "unknown"
        )

        return {
            "package": rpm_info.get("name", "unknown"),
            "version": rpm_info.get("version", "unknown"),
            "arch": rpm_info.get("arch", "unknown"),
            "elf_count": len(elf_analyses),
            "error_count": error_count,
            "dominant_language": dominant_lang,
            "language_breakdown": languages,
            "framework_breakdown": frameworks,
            "machine_breakdown": machines,
            "stripped_binaries": stripped_count,
        }


# ---------------------------------------------------------------------------
# ElfDecompiler
# ---------------------------------------------------------------------------

class ElfDecompiler:
    """
    Attempts to reconstruct human-readable source artefacts from a compiled
    ELF binary using a layered strategy from highest- to lowest-fidelity:

    Layer 1  — DWARF debug information (source file names, line numbers,
               type information).  Present in -debuginfo packages or when
               compiled with -g.

    Layer 2  — Symbol table demangling (C++, Rust, Go).  Even a production
               build keeps dynamic symbols and, for Go/Rust, usually the
               full symbol table.  ``c++filt`` and ``rustfilt`` (when
               available) decode mangled names into readable signatures.

    Layer 3  — String literal extraction.  Error messages, log strings, and
               path literals reveal internal structure without any
               decompilation.

    Layer 4  — Disassembly via ``objdump -d``.  Converts machine code to
               annotated assembly.  Combined with demangled symbol names the
               result is readable by anyone with moderate systems knowledge.

    Layer 5  — Ghidra headless (optional, pass ``use_ghidra=True``).
               Produces C-like decompiled pseudocode.  Requires Ghidra to
               be installed and ``analyzeHeadless`` on the PATH.

    All output is written to *output_dir* as plain text / JSON files so
    nothing is lost between sessions.
    """

    def __init__(self, elf_path: str):
        self.elf_path = Path(elf_path)
        if not self.elf_path.exists():
            raise FileNotFoundError(f"ELF not found: {self.elf_path}")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def decompile(
        self,
        output_dir: str = "decompiled",
        use_ghidra: bool = False,
    ) -> Dict[str, Any]:
        """
        Run all decompilation layers and write output files.

        Returns a dict summarising what was recovered and where it was
        written.

        Parameters
        ----------
        output_dir   Directory to write recovered artefacts into.
        use_ghidra   If True, also invoke Ghidra headless decompiler
                     (requires ``analyzeHeadless`` on the PATH).
        """
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)

        name = self.elf_path.name
        print(f"🧬 Decompiling: {name}")
        print(f"📁 Output:      {out}")

        result: Dict[str, Any] = {
            "elf": str(self.elf_path),
            "output_dir": str(out),
            "layers": {},
        }

        # Layer 1 — DWARF
        print("  [1/5] Extracting DWARF debug information …")
        dwarf = self._extract_dwarf(out)
        result["layers"]["dwarf"] = dwarf
        if dwarf.get("source_files"):
            print(f"        Found {len(dwarf['source_files'])} source file references")
        else:
            print("        No DWARF info — binary lacks debug symbols")

        # Layer 2 — Symbol demangling
        print("  [2/5] Demangling symbols …")
        syms = self._demangle_symbols(out)
        result["layers"]["symbols"] = syms
        print(f"        Recovered {syms.get('total', 0)} symbols "
              f"({syms.get('demangled', 0)} demangled)")

        # Layer 3 — String literals
        print("  [3/5] Extracting string literals …")
        strs = self._extract_strings(out)
        result["layers"]["strings"] = strs
        print(f"        Extracted {strs.get('count', 0)} strings ≥ 8 chars")

        # Layer 4 — Disassembly
        print("  [4/5] Disassembling with objdump …")
        disasm = self._disassemble(out)
        result["layers"]["disassembly"] = disasm
        print(f"        Disassembly: {disasm.get('lines', 0)} lines → "
              f"{disasm.get('file', 'N/A')}")

        # Layer 5 — Ghidra (optional)
        if use_ghidra:
            print("  [5/5] Running Ghidra headless decompiler …")
            ghidra = self._run_ghidra(out)
            result["layers"]["ghidra"] = ghidra
        else:
            result["layers"]["ghidra"] = {
                "status": "skipped",
                "note": (
                    "Pass use_ghidra=True or --ghidra CLI flag to enable Ghidra "
                    "headless decompilation.  Install from https://ghidra-sre.org"
                ),
            }
            print("  [5/5] Ghidra skipped (pass --ghidra to enable)")

        # Write summary JSON
        summary_path = out / f"{name}_decompile_summary.json"
        with open(summary_path, "w", encoding="utf-8") as fh:
            json.dump(result, fh, indent=2, ensure_ascii=False)
        print(f"\n  📄 Summary → {summary_path}")

        result["summary_file"] = str(summary_path)
        return result

    # ------------------------------------------------------------------
    # Layer 1 — DWARF
    # ------------------------------------------------------------------

    def _extract_dwarf(self, out: Path) -> Dict[str, Any]:
        """
        Extract DWARF debug information using ``readelf --debug-dump``.

        Recovers source file references, compilation units, and — when
        full DWARF is present — variable names and types.
        """
        name = self.elf_path.name

        # Check if any DWARF sections exist at all
        sections_out = self._run("readelf", "-S", str(self.elf_path))
        has_dwarf = ".debug_" in sections_out

        if not has_dwarf:
            return {
                "available": False,
                "source_files": [],
                "note": (
                    "No DWARF sections found.  To get debug info, install "
                    f"the companion debuginfo package (e.g. {name}-debuginfo) "
                    "or recompile with -g / RUSTFLAGS='-g'."
                ),
            }

        # Compilation units → source file paths
        cu_out = self._run("readelf", "--debug-dump=info", str(self.elf_path))
        source_files = self._parse_dwarf_source_files(cu_out)

        # Line number table → file:line mapping
        lines_out = self._run("readelf", "--debug-dump=lines", str(self.elf_path))

        dwarf_dir = out / "dwarf"
        dwarf_dir.mkdir(exist_ok=True)

        cu_file = dwarf_dir / f"{name}_debug_info.txt"
        cu_file.write_text(cu_out, encoding="utf-8")

        lines_file = dwarf_dir / f"{name}_debug_lines.txt"
        lines_file.write_text(lines_out, encoding="utf-8")

        return {
            "available": True,
            "source_files": source_files,
            "debug_info_file": str(cu_file),
            "debug_lines_file": str(lines_file),
            "note": (
                f"Found {len(source_files)} original source file references. "
                "These are the paths on the build machine — use them to locate "
                "matching sources in the .src.rpm or upstream repository."
            ),
        }

    @staticmethod
    def _parse_dwarf_source_files(debug_info: str) -> List[str]:
        """Parse DW_AT_name / DW_AT_comp_dir entries from readelf output."""
        files: List[str] = []
        for line in debug_info.splitlines():
            line = line.strip()
            if "DW_AT_name" in line or "DW_AT_comp_dir" in line:
                if ":" in line:
                    value = line.split(":", 1)[-1].strip()
                    # Filter out non-path entries (type names, etc.)
                    if "/" in value or value.endswith(
                        (".c", ".cpp", ".rs", ".go", ".h", ".hpp")
                    ):
                        if value not in files:
                            files.append(value)
        return files

    # ------------------------------------------------------------------
    # Layer 2 — Symbol demangling
    # ------------------------------------------------------------------

    def _demangle_symbols(self, out: Path) -> Dict[str, Any]:
        """
        Extract all symbols with ``nm`` and demangle them.

        C++ symbols are demangled with ``c++filt``.
        Rust symbols are demangled with ``rustfilt`` when available,
        otherwise with ``c++filt`` (partial).
        Go symbols are already human-readable.
        """
        name = self.elf_path.name

        # nm: all symbols, including dynamic
        nm_out = self._run("nm", "--demangle", "--dynamic", "-C", str(self.elf_path))
        if not nm_out:
            # Stripped binary — fall back to readelf dynamic symbols
            nm_out = self._run("readelf", "--syms", "--wide", str(self.elf_path))

        raw_symbols = self._parse_nm_output(nm_out)

        # Try rustfilt for Rust symbols
        if shutil.which("rustfilt"):
            demangled_out = self._run_pipe(
                ["rustfilt"],
                input_text="\n".join(s["raw"] for s in raw_symbols),
            )
            demangled_names = demangled_out.splitlines()
            for i, sym in enumerate(raw_symbols):
                if i < len(demangled_names):
                    sym["demangled"] = demangled_names[i]

        # Bucket into functions, objects, and undefined imports
        functions = [s for s in raw_symbols if s.get("type") in ("T", "t", "W", "w")]
        objects = [s for s in raw_symbols if s.get("type") in ("D", "d", "B", "b")]
        imports = [s for s in raw_symbols if s.get("type") == "U"]

        sym_dir = out / "symbols"
        sym_dir.mkdir(exist_ok=True)

        # Write human-readable function skeleton
        skeleton = self._build_function_skeleton(functions)
        skeleton_file = sym_dir / f"{name}_functions.txt"
        skeleton_file.write_text(skeleton, encoding="utf-8")

        all_syms_file = sym_dir / f"{name}_all_symbols.json"
        with open(all_syms_file, "w", encoding="utf-8") as fh:
            json.dump(raw_symbols, fh, indent=2, ensure_ascii=False)

        return {
            "total": len(raw_symbols),
            "functions": len(functions),
            "objects": len(objects),
            "imports": len(imports),
            "demangled": sum(
                1 for s in raw_symbols if s.get("demangled") != s.get("raw")
            ),
            "skeleton_file": str(skeleton_file),
            "all_symbols_file": str(all_syms_file),
        }

    @staticmethod
    def _parse_nm_output(nm_out: str) -> List[Dict[str, str]]:
        """Parse ``nm`` output into a list of symbol dicts."""
        symbols: List[Dict[str, str]] = []
        for line in nm_out.splitlines():
            parts = line.strip().split(None, 2)
            if len(parts) == 3:
                addr, sym_type, raw_name = parts
                symbols.append({"addr": addr, "type": sym_type, "raw": raw_name,
                                 "demangled": raw_name})
            elif len(parts) == 2:
                sym_type, raw_name = parts
                symbols.append({"addr": "", "type": sym_type, "raw": raw_name,
                                 "demangled": raw_name})
        return symbols

    @staticmethod
    def _build_function_skeleton(functions: List[Dict[str, str]]) -> str:
        """
        Produce a C-style function skeleton listing from demangled names.

        This is the cleanest fragment you can produce without a decompiler —
        every function boundary and its name, ordered by address.
        """
        lines = [
            "// ============================================================",
            "// RECOVERED FUNCTION SKELETON",
            "// Generated by THE FORGE RPM Ripper & ELF Analyzer",
            "//",
            "// Note: argument types and return types are inferred where",
            "// possible from DWARF / mangled names.  In stripped binaries",
            "// they default to 'void *'.  This is a SKELETON, not source.",
            "// ============================================================",
            "",
        ]
        for sym in functions:
            name = sym.get("demangled", sym.get("raw", "?"))
            addr = sym.get("addr", "")
            prefix = f"/* {addr} */ " if addr else ""
            lines.append(f"{prefix}void {name}(void);")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Layer 3 — String literals
    # ------------------------------------------------------------------

    def _extract_strings(self, out: Path) -> Dict[str, Any]:
        """
        Extract printable strings ≥ 8 characters from all ELF sections.

        Categorises strings into: paths, URLs, error messages, version
        strings, and generic literals — making it easy to understand the
        binary's internal structure even without any symbols.
        """
        name = self.elf_path.name
        raw = self._run("strings", "-n", "8", str(self.elf_path))
        all_strings = raw.splitlines()

        categorised: Dict[str, List[str]] = {
            "paths": [],
            "urls": [],
            "errors": [],
            "versions": [],
            "other": [],
        }
        error_keywords = ("error", "failed", "panic", "fatal", "cannot",
                           "invalid", "unexpected", "denied")
        version_patterns = ("version", "v0.", "v1.", "v2.", "v3.", "release")

        for s in all_strings:
            sl = s.lower()
            if s.startswith(("/", "./", "../")) or s.startswith("\\\\"):
                categorised["paths"].append(s)
            elif sl.startswith(("http://", "https://", "ftp://", "ssh://")):
                categorised["urls"].append(s)
            elif any(kw in sl for kw in error_keywords):
                categorised["errors"].append(s)
            elif any(p in sl for p in version_patterns):
                categorised["versions"].append(s)
            else:
                categorised["other"].append(s)

        str_dir = out / "strings"
        str_dir.mkdir(exist_ok=True)

        cat_file = str_dir / f"{name}_strings.json"
        with open(cat_file, "w", encoding="utf-8") as fh:
            json.dump(categorised, fh, indent=2, ensure_ascii=False)

        raw_file = str_dir / f"{name}_strings_raw.txt"
        raw_file.write_text(raw, encoding="utf-8")

        return {
            "count": len(all_strings),
            "paths": len(categorised["paths"]),
            "urls": len(categorised["urls"]),
            "errors": len(categorised["errors"]),
            "versions": len(categorised["versions"]),
            "categorised_file": str(cat_file),
        }

    # ------------------------------------------------------------------
    # Layer 4 — Disassembly
    # ------------------------------------------------------------------

    def _disassemble(self, out: Path) -> Dict[str, Any]:
        """
        Produce an annotated disassembly using ``objdump -d``.

        The result has demangled symbol names (--demangle) and source-line
        interleaving (--line-numbers) when DWARF is present.
        """
        name = self.elf_path.name
        disasm_dir = out / "disassembly"
        disasm_dir.mkdir(exist_ok=True)

        disasm_out = self._run(
            "objdump", "--demangle", "--line-numbers",
            "--disassemble", "--wide",
            str(self.elf_path),
        )
        disasm_file = disasm_dir / f"{name}_disasm.asm"
        disasm_file.write_text(disasm_out, encoding="utf-8")

        lines = len(disasm_out.splitlines())
        return {
            "lines": lines,
            "file": str(disasm_file),
            "note": (
                "Full annotated disassembly.  Function boundaries are marked "
                "with demangled names.  Use with symbols/functions.txt for "
                "context."
            ),
        }

    # ------------------------------------------------------------------
    # Layer 5 — Ghidra headless (optional)
    # ------------------------------------------------------------------

    def _run_ghidra(self, out: Path) -> Dict[str, Any]:
        """
        Run Ghidra headless analyzer and export decompiled C pseudocode.

        Requires ``analyzeHeadless`` (from Ghidra's support/ directory) to
        be on the PATH.  Install from https://ghidra-sre.org
        """
        if not shutil.which("analyzeHeadless"):
            return {
                "status": "not_installed",
                "note": (
                    "Ghidra not found.  Download from https://ghidra-sre.org "
                    "and ensure analyzeHeadless is on your PATH."
                ),
            }

        name = self.elf_path.name
        ghidra_dir = out / "ghidra"
        ghidra_dir.mkdir(exist_ok=True)
        project_dir = ghidra_dir / "project"
        project_dir.mkdir(exist_ok=True)

        try:
            proc = subprocess.run(
                [
                    "analyzeHeadless",
                    str(project_dir),
                    "forge_decompile",
                    "-import", str(self.elf_path),
                    "-postScript", "DecompileAllFunctions.java",
                    "-scriptPath", str(ghidra_dir),
                    "-deleteProject",
                ],
                capture_output=True,
                text=True,
                timeout=300,
            )
            status = "success" if proc.returncode == 0 else "error"
            log_file = ghidra_dir / f"{name}_ghidra.log"
            log_file.write_text(proc.stdout + proc.stderr, encoding="utf-8")
            return {"status": status, "log": str(log_file)}
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "note": "Ghidra timed out after 5 minutes."}

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    @staticmethod
    def _run(*args: str) -> str:
        """Run a subprocess, return stdout; empty string on any error."""
        try:
            proc = subprocess.run(
                list(args),
                capture_output=True,
                text=True,
                timeout=60,
            )
            return proc.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return ""

    @staticmethod
    def _run_pipe(cmd: List[str], input_text: str) -> str:
        """Run a command with stdin piped from *input_text*."""
        try:
            proc = subprocess.run(
                cmd,
                input=input_text,
                capture_output=True,
                text=True,
                timeout=30,
            )
            return proc.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return ""


# ---------------------------------------------------------------------------
# SrcRpmFinder
# ---------------------------------------------------------------------------

class SrcRpmFinder:
    """
    Helps locate the companion Source RPM (.src.rpm) for a binary RPM.

    The RPM ecosystem (Fedora, RHEL, CentOS, openSUSE) always publishes
    source RPMs.  Fetching the .src.rpm gives you the **actual source code**
    — the only way to get it without decompiling.

    Usage:
        finder = SrcRpmFinder("warp-terminal-0.1-1.fc39.x86_64.rpm")
        hints = finder.find_hints()
        print(hints["src_rpm_name"])    # warp-terminal-0.1-1.fc39.src.rpm
        print(hints["koji_url"])        # Koji build system URL
        print(hints["fedora_src_url"])  # src.fedoraproject.org URL
    """

    # Public Fedora/RHEL Koji instances
    _KOJI_BASES = [
        "https://kojipkgs.fedoraproject.org/packages",
        "https://koji.mbox.centos.org/pkgs",
    ]

    def __init__(self, rpm_path: str):
        self.rpm_path = Path(rpm_path)

    def find_hints(self) -> Dict[str, Any]:
        """
        Return a dict of URLs and names pointing to likely source RPMs.

        Does NOT download anything — only constructs the URLs so the user
        can fetch them with their package manager or browser.
        """
        rpm_info = self._query_rpm_metadata()
        name = rpm_info.get("name", self.rpm_path.stem)
        version = rpm_info.get("version", "")
        release = rpm_info.get("release", "")
        src_rpm = rpm_info.get("sourcerpm", f"{name}-{version}-{release}.src.rpm")

        # Parse epoch and dist from release (e.g. 1.fc39 → dist = fc39)
        dist = ""
        if "." in release:
            dist = release.rsplit(".", 1)[-1]

        results: Dict[str, Any] = {
            "package_name": name,
            "version": version,
            "release": release,
            "src_rpm_name": src_rpm,
            "dist": dist,
            "fetch_commands": [],
            "urls": [],
            "note": (
                "The .src.rpm contains the ACTUAL source code for this package. "
                "It is the safest and most complete way to recover source."
            ),
        }

        # dnf/yum command
        if shutil.which("dnf"):
            results["fetch_commands"].append(
                f"dnf download --source {name}"
            )
        if shutil.which("yum"):
            results["fetch_commands"].append(
                f"yumdownloader --source {name}"
            )

        # Koji URL pattern
        # https://kojipkgs.fedoraproject.org/packages/<name>/<version>/<release>/src/
        for base in self._KOJI_BASES:
            url = f"{base}/{name}/{version}/{release}/src/{src_rpm}"
            results["urls"].append(url)

        # Fedora src.fedoraproject.org
        results["urls"].append(
            f"https://src.fedoraproject.org/rpms/{name}"
        )
        # Red Hat / CentOS Stream
        results["urls"].append(
            f"https://gitlab.com/redhat/centos-stream/rpms/{name}"
        )

        return results

    def _query_rpm_metadata(self) -> Dict[str, str]:
        """Query RPM metadata from the package file."""
        fields = {
            "name": "%{NAME}",
            "version": "%{VERSION}",
            "release": "%{RELEASE}",
            "arch": "%{ARCH}",
            "sourcerpm": "%{SOURCERPM}",
        }
        query_fmt = "\n".join(f"{k}={v}" for k, v in fields.items())
        try:
            out = subprocess.check_output(
                ["rpm", "-qp", "--queryformat", query_fmt, str(self.rpm_path)],
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=15,
            )
            info: Dict[str, str] = {}
            for line in out.splitlines():
                if "=" in line:
                    k, _, v = line.partition("=")
                    info[k.strip()] = v.strip()
            return info
        except (subprocess.CalledProcessError, FileNotFoundError,
                subprocess.TimeoutExpired):
            return {}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

class RpmRipperCLI:
    """Command-line interface for the RPM Ripper, ELF Analyzer, and ELF Decompiler."""

    def run(self, argv: Optional[List[str]] = None) -> int:
        parser = argparse.ArgumentParser(
            prog="rpm_ripper",
            description=(
                "🔧 THE FORGE — RPM Ripper, ELF Analyzer & Decompiler.\n\n"
                "Extracts RPM packages, preserves ELF binaries, and recovers\n"
                "as much human-readable source information as possible through\n"
                "DWARF extraction, symbol demangling, and disassembly."
            ),
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=(
                "examples:\n"
                "  # Rip an RPM and analyse all ELF binaries inside it\n"
                "  %(prog)s warp-terminal-0.1.rpm -o out/\n\n"
                "  # Analyse a single ELF file you already have\n"
                "  %(prog)s --analyze-only /usr/bin/warp-terminal\n\n"
                "  # Full decompilation pipeline on a single ELF\n"
                "  %(prog)s --decompile /usr/bin/warp-terminal -o src_out/\n\n"
                "  # With Ghidra decompilation (requires Ghidra installed)\n"
                "  %(prog)s --decompile /usr/bin/warp-terminal --ghidra\n\n"
                "  # Find the .src.rpm to get the real source code\n"
                "  %(prog)s --find-source warp-terminal-0.1.fc39.x86_64.rpm\n"
            ),
        )

        # Mutually exclusive primary actions
        action = parser.add_mutually_exclusive_group()
        action.add_argument(
            "--analyze-only",
            metavar="ELF",
            help="Analyse a single ELF file directly (no RPM needed)",
        )
        action.add_argument(
            "--decompile",
            metavar="ELF",
            help=(
                "Run the full source-recovery pipeline on a single ELF: "
                "DWARF extraction → symbol demangling → string analysis → "
                "disassembly (→ Ghidra if --ghidra is set)"
            ),
        )
        action.add_argument(
            "--find-source",
            metavar="RPM",
            help=(
                "Print URLs and commands to fetch the companion .src.rpm "
                "(which contains the real source code) for a given binary RPM"
            ),
        )

        parser.add_argument(
            "rpm",
            nargs="?",
            help="Path to the .rpm file to rip (required unless an action flag is used)",
        )
        parser.add_argument(
            "-o", "--output-dir",
            default="rpm_ripped",
            help="Output directory (default: rpm_ripped/)",
        )
        parser.add_argument(
            "-r", "--report",
            default=None,
            help="Additional path to save the JSON analysis report",
        )
        parser.add_argument(
            "--ghidra",
            action="store_true",
            default=False,
            help=(
                "Enable Ghidra headless decompiler (Layer 5) when using "
                "--decompile.  Requires analyzeHeadless on PATH."
            ),
        )

        args = parser.parse_args(argv)

        if args.analyze_only:
            return self._run_elf_only(args.analyze_only)

        if args.decompile:
            return self._run_decompile(args.decompile, args.output_dir, args.ghidra)

        if args.find_source:
            return self._run_find_source(args.find_source)

        if not args.rpm:
            parser.print_help()
            return 1

        return self._run_rip(args.rpm, args.output_dir, args.report)

    # ------------------------------------------------------------------

    def _run_rip(self, rpm_path: str, output_dir: str, extra_report: Optional[str]) -> int:
        print("=" * 60)
        print("🔥 THE FORGE — RPM Ripper & ELF Analyzer")
        print("=" * 60)
        try:
            ripper = RpmRipper(rpm_path, output_dir)
            report = ripper.rip()
        except (FileNotFoundError, RuntimeError) as exc:
            print(f"\n❌ Error: {exc}", file=sys.stderr)
            return 1

        if extra_report:
            extra_path = Path(extra_report)
            extra_path.parent.mkdir(parents=True, exist_ok=True)
            with open(extra_path, "w", encoding="utf-8") as fh:
                json.dump(report, fh, indent=2, ensure_ascii=False)
            print(f"📄 Report also saved → {extra_path}")

        self._print_summary(report["summary"])
        return 0

    def _run_elf_only(self, elf_path: str) -> int:
        print("=" * 60)
        print("🔥 THE FORGE — ELF Analyzer")
        print("=" * 60)
        try:
            analysis = ElfAnalyzer(elf_path).analyze()
        except (FileNotFoundError, ValueError) as exc:
            print(f"\n❌ Error: {exc}", file=sys.stderr)
            return 1

        print(json.dumps(analysis, indent=2))
        return 0

    def _run_decompile(self, elf_path: str, output_dir: str, use_ghidra: bool) -> int:
        print("=" * 60)
        print("🔥 THE FORGE — ELF Source Recovery Pipeline")
        print("=" * 60)
        self._print_elf_explanation()
        try:
            result = ElfDecompiler(elf_path).decompile(
                output_dir=output_dir,
                use_ghidra=use_ghidra,
            )
        except (FileNotFoundError, ValueError) as exc:
            print(f"\n❌ Error: {exc}", file=sys.stderr)
            return 1

        print("\n📂 Recovered artefacts:")
        layers = result.get("layers", {})
        dwarf = layers.get("dwarf", {})
        if dwarf.get("available"):
            print(f"  DWARF source files  : {len(dwarf.get('source_files', []))}"
                  f" → {dwarf.get('debug_info_file', '')}")
        syms = layers.get("symbols", {})
        if syms.get("total", 0):
            print(f"  Symbols (demangled) : {syms.get('demangled', 0)}/{syms.get('total', 0)}"
                  f" → {syms.get('skeleton_file', '')}")
        strs = layers.get("strings", {})
        if strs.get("count", 0):
            print(f"  Strings extracted   : {strs.get('count', 0)}"
                  f" → {strs.get('categorised_file', '')}")
        disasm = layers.get("disassembly", {})
        if disasm.get("lines", 0):
            print(f"  Disassembly lines   : {disasm.get('lines', 0)}"
                  f" → {disasm.get('file', '')}")
        print(f"\n  Full summary        : {result.get('summary_file', '')}")
        print("=" * 60)
        return 0

    def _run_find_source(self, rpm_path: str) -> int:
        print("=" * 60)
        print("🔥 THE FORGE — Source RPM Finder")
        print("=" * 60)
        try:
            hints = SrcRpmFinder(rpm_path).find_hints()
        except Exception as exc:
            print(f"\n❌ Error: {exc}", file=sys.stderr)
            return 1

        print(f"\n  Package     : {hints['package_name']} {hints['version']}-{hints['release']}")
        print(f"  Source RPM  : {hints['src_rpm_name']}")
        print(f"\n  {hints['note']}")

        if hints["fetch_commands"]:
            print("\n  📥 Fetch with your package manager:")
            for cmd in hints["fetch_commands"]:
                print(f"    $ {cmd}")

        if hints["urls"]:
            print("\n  🌐 Direct download URLs:")
            for url in hints["urls"]:
                print(f"    {url}")

        print("=" * 60)
        return 0

    @staticmethod
    def _print_elf_explanation() -> None:
        print()
        print("ℹ️  ELF IS NOT SOURCE CODE")
        print("   ELF is a compiled binary. Compilation is lossy: variable names,")
        print("   comments, and high-level structure are mostly gone. Recovery is")
        print("   approximate. Layers used (best → least complete):")
        print("     1. DWARF debug info  — source file/line references")
        print("     2. Symbol demangling — function names and signatures")
        print("     3. String literals   — error messages, paths, version strings")
        print("     4. Disassembly       — annotated assembly code (objdump)")
        print("     5. Ghidra            — C-like pseudocode (pass --ghidra)")
        print("   ✅ Best approach: fetch the .src.rpm (use --find-source)")
        print()

    @staticmethod
    def _print_summary(summary: Dict[str, Any]) -> None:
        print("\n" + "=" * 60)
        print("📊 Analysis Summary")
        print("=" * 60)
        print(f"  Package          : {summary['package']} {summary['version']}")
        print(f"  Architecture     : {summary['arch']}")
        print(f"  ELF binaries     : {summary['elf_count']}")
        print(f"  Stripped         : {summary['stripped_binaries']}")
        print(f"  Dominant language: {summary['dominant_language']}")

        if summary["language_breakdown"]:
            print("  Language breakdown:")
            for lang, count in sorted(summary["language_breakdown"].items()):
                print(f"    {lang}: {count}")

        if summary["framework_breakdown"]:
            print("  Frameworks detected:")
            for fw, count in sorted(summary["framework_breakdown"].items()):
                print(f"    {fw}: {count} binaries")

        if summary["machine_breakdown"]:
            print("  Machine types:")
            for mach, count in sorted(summary["machine_breakdown"].items()):
                print(f"    {mach}: {count}")

        print("=" * 60)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    sys.exit(RpmRipperCLI().run())


if __name__ == "__main__":
    main()
