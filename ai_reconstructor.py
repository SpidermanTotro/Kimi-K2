#!/usr/bin/env python3
"""
THE FORGE — AI Binary Reconstructor
=====================================
"Like the Herculaneum scrolls, we can X-ray a binary and reassemble it."

Background — The Herculaneum Scroll Analogy
─────────────────────────────────────────────
In 79 AD, the eruption of Vesuvius carbonised a villa library of papyrus
scrolls.  In 2023/2024 the "Vesuvius Challenge" showed that a combination
of:
  1. High-resolution CT scanning         — multi-pass non-destructive imaging
  2. Virtual unwrapping                  — computational unrolling of the layers
  3. AI "crackle" / ink detection        — pattern recognition on the scan slices
  4. ML text recognition (SegmentAnything + large LMs)  — reading the text
  5. Scholar assembly                    — stitching fragments into coherent text

…could read 2000-year-old charred scrolls without physically opening them.

We apply the SAME pipeline to compiled ELF binaries:

  Scroll pipeline          →  Binary pipeline
  ─────────────────────────────────────────────────────────────────────
  CT scan slices           →  Multi-layer ELF scan (BinaryXRay)
  Virtual unwrapping       →  Module/namespace reconstruction (VirtualUnwrapper)
  Crackle / ink detection  →  Symbol & string pattern detection (AIPatternMatcher)
  ML text recognition      →  Source code fragment generation (AIPatternMatcher)
  Scholar assembly         →  Annotated source output (ScrollAssembler)
  Confidence per column    →  confidence_score per ScrollFragment

─────────────────────────────────────────────────────────────────────────────
Pipeline overview
─────────────────────────────────────────────────────────────────────────────

  ┌─────────────────────────────────────────────────────────────────────┐
  │                       ELF / binary input                            │
  └──────────────────────────────┬──────────────────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │       BinaryXRay         │  Layer 1-6 structural scan
                    │  (CT scan of the binary) │  (header, sections, symbols,
                    └────────────┬────────────┘   DWARF, strings, call-graph)
                                 │
                    ┌────────────▼────────────┐
                    │     VirtualUnwrapper     │  Groups layers into modules,
                    │  (unroll the scroll)     │  infers namespaces, function
                    └────────────┬────────────┘  groups, and data structures
                                 │
                    ┌────────────▼────────────┐
                    │    AIPatternMatcher      │  Matches patterns → generates
                    │  (read the ink)          │  source fragments + confidence
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │     ScrollAssembler      │  Writes annotated source files,
                    │  (assemble the scroll)   │  scroll map, and summary report
                    └─────────────────────────┘

─────────────────────────────────────────────────────────────────────────────
Usage
─────────────────────────────────────────────────────────────────────────────
Library:
    from ai_reconstructor import BinaryXRay, VirtualUnwrapper
    from ai_reconstructor import AIPatternMatcher, ScrollAssembler

    # Full pipeline in one call
    from ai_reconstructor import ScrollAssembler
    report = ScrollAssembler("/usr/bin/warp-terminal").reconstruct("recon/")

    # Or step by step
    xray    = BinaryXRay("/usr/bin/warp-terminal").scan()
    modules = VirtualUnwrapper(xray).unwrap()
    frags   = AIPatternMatcher(modules).match()
    report  = ScrollAssembler.from_fragments(frags).write("recon/")

CLI:
    # Fast X-ray scan only (safe read-only)
    python3 ai_reconstructor.py --xray /usr/bin/warp-terminal

    # Unwrap + show module map
    python3 ai_reconstructor.py --unwrap /usr/bin/warp-terminal

    # Full reconstruction pipeline
    python3 ai_reconstructor.py --reconstruct /usr/bin/warp-terminal -o recon/

    # Full pipeline from an already-ripped package dir or report JSON
    python3 ai_reconstructor.py --full rpm_ripped/ -o recon/
    python3 ai_reconstructor.py --full analysis_report.json -o recon/
"""

import argparse
import dataclasses
import hashlib
import json
import os
import re
import struct
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Import THE FORGE tools we build on
# ---------------------------------------------------------------------------

def _import_safe(module: str, symbol: str) -> Optional[Any]:
    """Import *symbol* from *module* without crashing if unavailable."""
    try:
        mod = __import__(module, fromlist=[symbol])
        return getattr(mod, symbol, None)
    except ImportError:
        return None

SafeElfReader  = _import_safe("binary_tools", "SafeElfReader")
ElfAnalyzer    = _import_safe("rpm_ripper",    "ElfAnalyzer")
ElfDecompiler  = _import_safe("rpm_ripper",    "ElfDecompiler")

ELF_MAGIC = b"\x7fELF"


# ===========================================================================
# ScrollFragment — the atom of reconstruction
# ===========================================================================

@dataclasses.dataclass
class ScrollFragment:
    """
    A single reconstructed fragment of source code.

    Analogous to one "column" of text recovered from a Herculaneum scroll:
    it may be complete, partial, or heavily interpolated, and always carries
    a *confidence_score* so downstream tools know how trustworthy it is.
    """

    # Identification
    fragment_id: str          # unique id: "<module>/<function>"
    module:      str          # inferred module / compilation unit
    name:        str          # symbol / function / data name

    # The reconstructed content
    source_type:    str       # "function" | "struct" | "const" | "module" | "unknown"
    language:       str       # "rust" | "c" | "c++" | "go" | "python" | "unknown"
    reconstructed:  str       # the reconstructed source text
    raw_evidence:   List[str] # evidence items that led to this reconstruction

    # Quality metadata
    confidence_score: float   # 0.0 (guess) … 1.0 (certain from DWARF)
    evidence_layers:  List[str]  # which scan layers contributed

    # Location in the binary
    address:     Optional[str] = None   # hex virtual address
    size_bytes:  Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)

    @property
    def confidence_label(self) -> str:
        if self.confidence_score >= 0.85:
            return "high"
        if self.confidence_score >= 0.50:
            return "medium"
        if self.confidence_score >= 0.20:
            return "low"
        return "very-low"


# ===========================================================================
# BinaryXRay  — multi-layer structural scan
# ===========================================================================

class BinaryXRay:
    """
    Performs a multi-pass non-destructive scan of an ELF binary — like
    a CT scanner imaging a Herculaneum scroll from multiple angles.

    Six scan layers (analogous to the six CT-scan orientations):

    Layer 1  — Structural skeleton   : ELF header, section layout, PT_LOAD segments
    Layer 2  — Bone detail           : symbol table (demangled), DWARF source paths
    Layer 3  — Ink / text            : string literals ≥ 8 chars
    Layer 4  — Neural pathways       : call-graph edges from objdump
    Layer 5  — Tissue analysis       : data structure hints from .data / .rodata
    Layer 6  — Build fingerprint     : build-id, compiler flags, version strings
    """

    # Minimum string length for extraction
    _MIN_STR_LEN = 8

    def __init__(self, elf_path: str):
        self.elf_path = Path(elf_path).resolve()
        if not self.elf_path.exists():
            raise FileNotFoundError(f"Binary not found: {self.elf_path}")
        with open(self.elf_path, "rb") as fh:
            if fh.read(4) != ELF_MAGIC:
                raise ValueError(f"Not a valid ELF file: {self.elf_path}")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def scan(self) -> Dict[str, Any]:
        """
        Run all six scan layers and return a structured scan report.

        All sub-scans are non-destructive — the binary is opened read-only
        via SafeElfReader or via external tools that only read the file.
        """
        print(f"🔬 X-raying: {self.elf_path.name}")

        result: Dict[str, Any] = {
            "binary": str(self.elf_path),
            "sha256": self._sha256(),
            "size_bytes": self.elf_path.stat().st_size,
            "layers": {},
        }

        print("  [1/6] Structural skeleton …")
        result["layers"]["skeleton"]  = self._scan_skeleton()

        print("  [2/6] Bone detail (symbols + DWARF) …")
        result["layers"]["symbols"]   = self._scan_symbols()

        print("  [3/6] Ink extraction (string literals) …")
        result["layers"]["strings"]   = self._scan_strings()

        print("  [4/6] Neural pathways (call graph) …")
        result["layers"]["callgraph"] = self._scan_callgraph()

        print("  [5/6] Tissue analysis (data patterns) …")
        result["layers"]["data"]      = self._scan_data_patterns()

        print("  [6/6] Build fingerprint …")
        result["layers"]["build"]     = self._scan_build_fingerprint()

        # Quick summary
        sym_count = len(result["layers"]["symbols"].get("demangled", []))
        str_count = result["layers"]["strings"].get("count", 0)
        src_files = len(result["layers"]["symbols"].get("all_source_files", [])
                        or result["layers"]["symbols"].get("dwarf_source_files", []))
        print(f"\n  📊 Scan complete: {sym_count} symbols, {str_count} strings, "
              f"{src_files} source file refs")

        return result

    # ------------------------------------------------------------------
    # Layer 1 — Structural skeleton
    # ------------------------------------------------------------------

    def _scan_skeleton(self) -> Dict[str, Any]:
        """ELF header + section table + program headers."""
        sections: List[Dict] = []
        segments: List[Dict] = []

        if SafeElfReader is not None:
            try:
                with SafeElfReader(str(self.elf_path)) as elf:
                    hdr  = elf.read_header()
                    secs = elf.list_sections()
                    sections = secs
            except Exception:
                hdr = {}
        else:
            hdr = self._readelf_header()

        # Program headers via readelf
        phdr_out = self._run("readelf", "-l", str(self.elf_path))
        for line in phdr_out.splitlines():
            if line.strip().startswith(("LOAD", "PT_LOAD")):
                parts = line.split()
                if len(parts) >= 5:
                    segments.append({
                        "type":    parts[0],
                        "vaddr":   parts[1] if len(parts) > 1 else "?",
                        "filesz":  parts[4] if len(parts) > 4 else "?",
                    })

        return {
            "header":   hdr,
            "sections": [s.get("name", "") for s in sections if s.get("name")],
            "section_count": len(sections),
            "segments": segments,
            "has_debug": any(
                s.get("name") in (".debug_info", ".debug_abbrev",
                                   ".debug_line", ".debug_str")
                for s in sections
            ),
            "has_symtab": any(
                s.get("name") == ".symtab"
                for s in sections
            ),
        }

    def _readelf_header(self) -> Dict[str, Any]:
        out = self._run("readelf", "-h", str(self.elf_path))
        info: Dict[str, str] = {}
        for line in out.splitlines():
            if ":" in line:
                k, _, v = line.partition(":")
                info[k.strip().lower().replace(" ", "_")] = v.strip()
        return info

    # ------------------------------------------------------------------
    # Layer 2 — Symbols + DWARF
    # ------------------------------------------------------------------

    def _scan_symbols(self) -> Dict[str, Any]:
        """Demangle all symbols and extract source file paths from DWARF and strings."""
        raw_syms  = self._get_raw_symbols()
        demangled = self._demangle(raw_syms)

        # Primary: DWARF compilation-unit source paths
        dwarf_files = self._get_dwarf_source_files()

        # Secondary: source paths embedded as panic / assert location strings
        # (very common in stripped Rust binaries — every panic! macro embeds
        # the source path as a static string, e.g.
        # ".../grep-searcher-0.1.13/src/searcher/mod.rs")
        string_files = self._extract_source_paths_from_strings()
        all_source_files = sorted(set(dwarf_files + string_files))

        # Infer language using symbols AND all discovered source paths
        language = self._infer_language(demangled, all_source_files)

        return {
            "raw":                raw_syms[:500],
            "demangled":          demangled[:500],
            "total":              len(raw_syms),
            "demangled_count":    len(demangled),
            "dwarf_source_files": dwarf_files,
            "string_source_files": string_files,
            "all_source_files":   all_source_files,
            "language":           language,
        }

    def _get_raw_symbols(self) -> List[str]:
        out = self._run("readelf", "--syms", "--wide", str(self.elf_path))
        # Strip GLIBC version-index suffix: "(2)" etc.
        _ver = re.compile(r'\s*\(\d+\)$')
        names: List[str] = []
        for line in out.splitlines():
            parts = line.split()
            if len(parts) >= 8:
                name = _ver.sub("", parts[7]).strip()
                if name and name != "Name":
                    names.append(name)
        return names

    def _demangle(self, names: List[str]) -> List[str]:
        """Demangle C++/Rust/Go mangled names where possible."""
        if not names:
            return []
        # c++filt handles C++ and Rust (with rustfilt fallback)
        try:
            proc = subprocess.run(
                ["c++filt"],
                input="\n".join(names),
                capture_output=True, text=True, timeout=30,
            )
            return [l for l in proc.stdout.splitlines() if l]
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return names

    def _get_dwarf_source_files(self) -> List[str]:
        out = self._run("readelf", "--debug-dump=info", str(self.elf_path))
        files: List[str] = []
        for line in out.splitlines():
            # DW_AT_name or DW_AT_comp_dir give source paths
            if "DW_AT_name" in line or "DW_AT_comp_dir" in line:
                m = re.search(r':\s*(.+)$', line)
                if m:
                    val = m.group(1).strip().strip('"')
                    if "/" in val or "." in val:
                        files.append(val)
        return sorted(set(files))

    def _extract_source_paths_from_strings(self) -> List[str]:
        """
        Extract source file paths embedded in string literals.

        Rust binaries embed every panic/assert location as a static string,
        even when fully stripped.  These look like:
            /usr/share/cargo/registry/grep-searcher-0.1.13/src/searcher/mod.rs
            library/core/src/slice/memchr.rs
            /build/rustc-xxx/library/std/src/thread/mod.rs
        This gives us the full crate + module structure for free.

        We use targeted regex patterns (not a generic path finder) because
        Rust panic strings often directly concatenate path + message text
        with no separator (e.g. "mod.rsslice reader: …").
        """
        strings_data = self._scan_strings()
        strings = strings_data.get("strings", [])

        # Cargo registry crates: match /usr/share/cargo/registry/<crate>-<ver>/src/<path>.rs
        _cargo_re = re.compile(
            r'/usr/share/cargo/registry/'
            r'[a-zA-Z0-9_-]+-\d[.\d]*/src/'
            r'[a-zA-Z0-9_/-]+\.(?:rs|go|c|cpp|h|hpp|py)'
        )
        # Rust stdlib / build machine paths:
        #   /build/<dir>/<pkg>/library/<crate>/src/<path>.rs
        #   library/<crate>/src/<path>.rs
        _stdlib_re = re.compile(
            r'(?:/build/[^\s/]+/[^\s/]+|library)'
            r'/[a-zA-Z0-9_/-]+\.(?:rs|go)'
        )

        found: List[str] = []
        for s in strings:
            for pat in (_cargo_re, _stdlib_re):
                for m in pat.finditer(s):
                    path = m.group(0).strip(".,;:!?")
                    found.append(path)
        return sorted(set(found))

    def _infer_language(
        self, symbols: List[str], source_files: List[str]
    ) -> str:
        all_text = " ".join(symbols) + " ".join(source_files)

        # Rust: .rs source paths, or Rust-specific stdlib symbols
        if (any(".rs" in f for f in source_files)
                or any(s in all_text for s in
                       ("::{{closure}}", "std::panicking", "rust_panic",
                        "core::fmt", "_Unwind_Backtrace"))):
            return "rust"

        # Go: .go source paths or Go runtime symbols
        if (any(".go" in f for f in source_files)
                or any(s in all_text for s in
                       ("runtime.main", "goroutine", "go.buildinfo"))):
            return "go"

        # C++: mangled names or vtable markers
        if any(s in all_text for s in ("_ZN", "vtable", "typeinfo",
                                        "_ZTI", "_ZTV")):
            return "c++"

        # Python extension modules
        if (any(".py" in f for f in source_files)
                or "PyObject" in all_text or "Py_InitModule" in all_text):
            return "python"

        return "c"

    # ------------------------------------------------------------------
    # Layer 3 — String literals
    # ------------------------------------------------------------------

    def _scan_strings(self) -> Dict[str, Any]:
        """Extract printable strings ≥ min_len from the binary."""
        if SafeElfReader is not None:
            try:
                with SafeElfReader(str(self.elf_path)) as elf:
                    strings = elf.extract_strings(min_len=self._MIN_STR_LEN)
                return {"strings": strings, "count": len(strings), "source": "mmap"}
            except Exception:
                pass

        # Fallback: `strings` command
        out = self._run("strings", "-n", str(self._MIN_STR_LEN), str(self.elf_path))
        strings = [l for l in out.splitlines() if l]
        return {"strings": strings, "count": len(strings), "source": "strings_cmd"}

    # ------------------------------------------------------------------
    # Layer 4 — Call graph
    # ------------------------------------------------------------------

    def _scan_callgraph(self) -> Dict[str, Any]:
        """
        Extract a call graph (caller → callee edges) from objdump output.
        Looks for CALL / BL / BLX instructions and resolves targets via
        symbol names from the PLT / symbol table.
        """
        out = self._run("objdump", "-d", "--no-show-raw-insn",
                        str(self.elf_path))
        edges: List[Tuple[str, str]] = []
        current_func = "<unknown>"
        # Match function labels: "000000000042ab10 <_ZN3foo3bar17h...>:"
        # Must have a non-zero address and an angle-bracket name.
        # Reject bare section headers like "Disassembly of section .text:"
        sym_re  = re.compile(r'^[0-9a-f]+ <([^>]+)>:\s*$')
        call_re = re.compile(r'call[q]?\s+[0-9a-f]+\s+<([^>+]+)')

        for line in out.splitlines()[:50000]:   # limit for large binaries
            m = sym_re.match(line)
            if m:
                label = m.group(1)
                # Skip ELF section header lines inserted by objdump
                # ("Disassembly of section .text:" is not a symbol label)
                if not label.startswith("."):
                    current_func = label
                continue
            m = call_re.search(line)
            if m:
                callee = m.group(1).split("@")[0].strip()
                if callee and callee != current_func and not callee.startswith("."):
                    edges.append((current_func, callee))

        # Build adjacency dict (callee_count per function)
        callee_counts: Dict[str, int] = {}
        caller_counts: Dict[str, int] = {}
        for caller, callee in edges:
            callee_counts[callee] = callee_counts.get(callee, 0) + 1
            caller_counts[caller] = caller_counts.get(caller, 0) + 1

        most_called = sorted(callee_counts, key=callee_counts.get, reverse=True)[:20]  # type: ignore[arg-type]
        most_callers = sorted(caller_counts, key=caller_counts.get, reverse=True)[:20]  # type: ignore[arg-type]

        return {
            "edge_count":    len(edges),
            "unique_callers": len(caller_counts),
            "unique_callees": len(callee_counts),
            "most_called":   most_called,
            "hub_functions": most_callers,
        }

    # ------------------------------------------------------------------
    # Layer 5 — Data patterns
    # ------------------------------------------------------------------

    def _scan_data_patterns(self) -> Dict[str, Any]:
        """
        Infer data structure hints from .rodata / .data / .bss sections.
        Looks for:
          • Jump / vtable patterns (arrays of 8-byte aligned pointers)
          • Format string patterns ("%d", "%s", …)
          • Error / log message clusters
          • URL / path literals
          • Magic numbers / version strings
        """
        strings_data = self._scan_strings()
        strings = strings_data.get("strings", [])

        vtable_hints: List[str] = []
        format_strings: List[str] = []
        error_messages: List[str] = []
        urls: List[str] = []
        paths: List[str] = []
        version_strings: List[str] = []

        _fmt_re  = re.compile(r'%[-+0-9*.]*[diouxXeEfgGcsSpnq]')
        _url_re  = re.compile(r'https?://\S+')
        _path_re = re.compile(r'^/[a-zA-Z0-9_./-]{4,}$')
        _ver_re  = re.compile(r'\b\d+\.\d+[\d.]*\b')

        for s in strings:
            if _fmt_re.search(s):
                format_strings.append(s)
            if _url_re.search(s):
                urls.append(s)
            if _path_re.match(s):
                paths.append(s)
            if any(w in s.lower() for w in ("error", "failed", "panic",
                                             "assert", "fatal", "abort",
                                             "cannot", "invalid", "unexpected")):
                error_messages.append(s)
            if _ver_re.search(s) and len(s) < 40:
                version_strings.append(s)

        return {
            "format_strings":   format_strings[:50],
            "error_messages":   error_messages[:50],
            "urls":             urls[:30],
            "paths":            paths[:50],
            "version_strings":  version_strings[:20],
            "format_count":     len(format_strings),
            "error_count":      len(error_messages),
            "url_count":        len(urls),
            "path_count":       len(paths),
        }

    # ------------------------------------------------------------------
    # Layer 6 — Build fingerprint
    # ------------------------------------------------------------------

    def _scan_build_fingerprint(self) -> Dict[str, Any]:
        """Extract build-id, compiler identification, and version strings."""
        out = self._run("readelf", "-n", str(self.elf_path))
        build_id = None
        for line in out.splitlines():
            if "Build ID:" in line:
                parts = line.split("Build ID:")
                if len(parts) == 2:
                    build_id = parts[1].strip()
                    break

        # Compiler identification from .comment or strings
        comment_out = self._run("readelf", "-p", ".comment", str(self.elf_path))
        compiler = "unknown"
        for line in comment_out.splitlines():
            lower = line.lower()
            if "gcc" in lower:
                compiler = "GCC"
                break
            if "clang" in lower or "llvm" in lower:
                compiler = "Clang/LLVM"
                break
            if "rustc" in lower:
                compiler = "rustc"
                break
            if "go" in lower and "version" in lower:
                compiler = "Go compiler"
                break

        # Version from strings
        version = None
        strings = self._scan_strings().get("strings", [])
        for s in strings:
            if re.match(r'v?\d+\.\d+\.\d+', s) and len(s) < 30:
                version = s
                break

        return {
            "build_id":   build_id,
            "compiler":   compiler,
            "version":    version,
        }

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def _run(self, *args: str) -> str:
        try:
            proc = subprocess.run(
                list(args), capture_output=True, text=True, timeout=60,
            )
            return proc.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return ""

    def _sha256(self) -> str:
        h = hashlib.sha256()
        with open(self.elf_path, "rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()


# ===========================================================================
# DeepElfParser  — pure-Python ELF binary parser (no external tools)
# ===========================================================================

# ELF section-header types
_SHT = {0:"NULL",1:"PROGBITS",2:"SYMTAB",3:"STRTAB",4:"RELA",5:"HASH",
        6:"DYNAMIC",7:"NOTE",8:"NOBITS",9:"REL",10:"SHLIB",11:"DYNSYM",
        14:"INIT_ARRAY",15:"FINI_ARRAY",16:"PREINIT_ARRAY",17:"GROUP",
        18:"SYMTAB_SHNDX",0x6fffffff:"GNU_VERSYM",0x6ffffffe:"GNU_VERNEED",
        0x6ffffffd:"GNU_VERDEF",0x6ffffff6:"GNU_HASH",0x6ffffff5:"GNU_PRELINK_MAP"}
# ELF section-header flags
_SHF = {1:"WRITE",2:"ALLOC",4:"EXECINSTR",16:"MERGE",32:"STRINGS",
        64:"INFO_LINK",128:"LINK_ORDER",256:"OS_NONCONFORMING",512:"GROUP",
        1024:"TLS",0x0ff00000:"MASKOS",0xf0000000:"MASKPROC"}
# ELF program-header segment types
_PT  = {0:"NULL",1:"LOAD",2:"DYNAMIC",3:"INTERP",4:"NOTE",5:"SHLIB",
        6:"PHDR",7:"TLS",0x6474e550:"GNU_EH_FRAME",0x6474e551:"GNU_STACK",
        0x6474e552:"GNU_RELRO",0x6474e553:"GNU_PROPERTY"}
# ELF dynamic-section tag meanings
_DT_NAMES = {
    0:"NULL",1:"NEEDED",2:"PLTRELSZ",3:"PLTGOT",4:"HASH",5:"STRTAB",
    6:"SYMTAB",7:"RELA",8:"RELASZ",9:"RELAENT",10:"STRSZ",11:"SYMENT",
    12:"INIT",13:"FINI",14:"SONAME",15:"RPATH",16:"SYMBOLIC",17:"REL",
    18:"RELSZ",19:"RELENT",20:"PLTREL",21:"DEBUG",22:"TEXTREL",23:"JMPREL",
    24:"BIND_NOW",25:"INIT_ARRAY",26:"FINI_ARRAY",28:"INIT_ARRAYSZ",
    29:"FINI_ARRAYSZ",30:"RUNPATH",31:"FLAGS",32:"PREINIT_ARRAY",
    33:"PREINIT_ARRAYSZ",34:"SYMTAB_SHNDX",35:"RELRSZ",36:"RELR",37:"RELRENT",
    0x6ffffef5:"GNU_HASH",0x6ffffff0:"VERSYM",0x6ffffffe:"VERNEED",
    0x6fffffff:"VERNEEDNUM",0x6ffffffd:"VERDEF",0x6ffffffc:"VERDEFNUM",
}
# Symbol type and binding decoding
_STT = {0:"NOTYPE",1:"OBJECT",2:"FUNC",3:"SECTION",4:"FILE",5:"COMMON",6:"TLS"}
_STB = {0:"LOCAL",1:"GLOBAL",2:"WEAK",10:"GNU_UNIQUE"}
_STV = {0:"DEFAULT",1:"INTERNAL",2:"HIDDEN",3:"PROTECTED"}


class DeepElfParser:
    """
    Pure-Python ELF binary parser — reads every structure directly from
    an ``mmap.ACCESS_READ`` mapping using ``struct.unpack``.

    No external tools are called.  The binary is never executed.

    Analogous to the CT scanner itself in the Herculaneum pipeline: it
    doesn't "interpret" the data yet — it just faithfully records every
    byte in structured form so the higher layers (ElfUnderstanding,
    VirtualUnwrapper, AIPatternMatcher) can reason about it.

    Parsed structures
    ─────────────────
    • ELF header            (e_ident through e_shstrndx)
    • Program headers       (PT_LOAD, PT_DYNAMIC, PT_INTERP, …)
    • Section headers       (name, type, flags, offset, size, …)
    • Section contents
        – .dynamic          DT_NEEDED, DT_SONAME, DT_INIT, DT_FINI, …
        – .dynsym / .symtab  all symbol entries (name, type, bind, addr, size)
        – .strtab / .dynstr string tables
        – .rela.plt / .rela.dyn   relocations → (offset, type, sym, addend)
        – .note.*           build-id, ABI, property
        – .gnu.hash         GNU hash table (fast symbol lookup)
    • Derived data
        – PLT stub addresses
        – GOT slot map
        – Imported symbols (undefined, GLOBAL/WEAK)
        – Exported symbols (defined, GLOBAL, non-LOCAL)
        – Shared library dependencies (DT_NEEDED)
    """

    # Struct format strings
    _ELF64_HDR  = "<4sBBBBBxxxxxxx HHIQQQIHHHHHH"  # 64-byte header after ident
    _ELF64_SHDR = "<IIQQQQIIQQ"   # 64-byte section header
    _ELF64_PHDR = "<IIQQQQQQ"     # 56-byte program header
    _ELF64_SYM  = "<IBBHQQ"       # 24-byte symbol
    _ELF64_DYN  = "<qQ"           # 16-byte dynamic entry
    _ELF64_RELA = "<QIiQ"         # Wait: Elf64_Rela = off(8) info(8) addend(8) - but struct fields differ
    # Elf64_Rela: r_offset(u64) r_info(u64) r_addend(i64)
    _ELF64_RELA_REAL = "<QQq"     # 24 bytes
    _ELF32_HDR  = "<4sBBBBBxxxxxxx HHIIIIIHHHHHH"
    _ELF32_SHDR = "<IIIIIIIIII"   # 40-byte section header
    _ELF32_PHDR = "<IIIIIIII"     # 32-byte program header
    _ELF32_SYM  = "<IIIBBH"       # 16-byte symbol
    _ELF32_DYN  = "<iI"           # 8-byte dynamic entry
    _ELF32_RELA_REAL = "<IIi"     # 12 bytes

    def __init__(self, elf_path: str):
        self.path = Path(elf_path).resolve()
        if not self.path.exists():
            raise FileNotFoundError(f"Not found: {self.path}")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def parse(self) -> Dict[str, Any]:
        """
        Parse the full ELF structure and return a comprehensive dict.

        The result contains every field extracted directly from the binary
        format — no readelf, no objdump, no external tools.
        """
        import mmap as _mmap
        with open(self.path, "rb") as fh:
            mm = _mmap.mmap(fh.fileno(), 0, access=_mmap.ACCESS_READ)
            try:
                return self._parse_mmap(mm)
            finally:
                mm.close()

    # ------------------------------------------------------------------
    # Internal parse implementation
    # ------------------------------------------------------------------

    def _parse_mmap(self, mm: Any) -> Dict[str, Any]:
        size = len(mm)

        # ── e_ident ────────────────────────────────────────────────────
        if size < 16 or mm[:4] != ELF_MAGIC:
            raise ValueError(f"Not a valid ELF: {self.path}")

        ei_class = mm[4]   # 1=32-bit, 2=64-bit
        ei_data  = mm[5]   # 1=little-endian, 2=big-endian
        is_64    = (ei_class == 2)
        is_le    = (ei_data  == 1)

        endian = "<" if is_le else ">"

        # ── ELF header ─────────────────────────────────────────────────
        hdr = self._parse_header(mm, is_64, endian)

        # ── Section headers + string table ─────────────────────────────
        sections = self._parse_section_headers(mm, hdr, is_64, endian)
        shstrtab = self._read_strtab(
            mm, sections[hdr["e_shstrndx"]] if hdr["e_shstrndx"] < len(sections) else {}
        )
        # Resolve section names
        for sh in sections:
            sh["name"] = self._strtab_lookup(shstrtab, sh.get("sh_name", 0))

        # ── Program headers ────────────────────────────────────────────
        phdrs = self._parse_program_headers(mm, hdr, is_64, endian)

        # ── Section contents ───────────────────────────────────────────
        dynstr  = self._find_strtab(mm, sections, ".dynstr")
        strtab  = self._find_strtab(mm, sections, ".strtab")

        dynsyms  = self._parse_symtab(mm, sections, ".dynsym",  dynstr,  is_64, endian)
        symtab   = self._parse_symtab(mm, sections, ".symtab",  strtab,  is_64, endian)
        dynamic  = self._parse_dynamic(mm, sections, dynstr, endian, is_64)
        notes    = self._parse_notes(mm, sections, endian)
        relas    = self._parse_relocations(mm, sections, dynsyms, is_64, endian)
        gnu_hash = self._parse_gnu_hash(mm, sections, endian, is_64)

        # ── Derived: imports / exports / deps ─────────────────────────
        imports  = [s for s in dynsyms  if s.get("shndx") == 0   and s["bind"] in ("GLOBAL","WEAK") and s["name"]]
        exports  = [s for s in dynsyms  if s.get("shndx") != 0   and s["bind"] in ("GLOBAL","WEAK") and s["name"]]
        dso_deps = [e["val_str"] for e in dynamic if e["tag_name"] == "NEEDED" and e.get("val_str")]

        # ── All symbols merged ─────────────────────────────────────────
        all_syms = dynsyms + [s for s in symtab
                               if not any(d["name"] == s["name"] for d in dynsyms)]

        # ── GOT / PLT analysis ─────────────────────────────────────────
        plt_stubs = self._find_plt_stubs(sections, relas)

        return {
            "path":       str(self.path),
            "size_bytes": size,
            "class":      "64-bit" if is_64 else "32-bit",
            "endian":     "little" if is_le else "big",
            "header":     hdr,
            "sections":   sections,
            "phdrs":      phdrs,
            "dynsyms":    dynsyms,
            "symtab":     symtab,
            "all_symbols": all_syms,
            "imports":    imports,
            "exports":    exports,
            "dynamic":    dynamic,
            "dso_deps":   dso_deps,
            "notes":      notes,
            "relocations": relas,
            "plt_stubs":  plt_stubs,
            "gnu_hash":   gnu_hash,
            "section_count":  len(sections),
            "symbol_count":   len(all_syms),
            "import_count":   len(imports),
            "export_count":   len(exports),
        }

    # ------------------------------------------------------------------
    # ELF header
    # ------------------------------------------------------------------

    def _parse_header(self, mm: Any, is_64: bool, endian: str) -> Dict[str, Any]:
        if is_64:
            # After the 16-byte e_ident
            fmt = endian + "HHIQQQIHHHHHH"   # 48 bytes
            needed = 16 + struct.calcsize(fmt)
            if len(mm) < needed:
                raise ValueError("ELF file too short to contain full header")
            (e_type, e_machine, e_version, e_entry, e_phoff, e_shoff,
             e_flags, e_ehsize, e_phentsize, e_phnum, e_shentsize,
             e_shnum, e_shstrndx) = struct.unpack_from(fmt, mm, 16)
        else:
            fmt = endian + "HHIIIIIHHHHHH"
            needed = 16 + struct.calcsize(fmt)
            if len(mm) < needed:
                raise ValueError("ELF file too short to contain full header")
            (e_type, e_machine, e_version, e_entry, e_phoff, e_shoff,
             e_flags, e_ehsize, e_phentsize, e_phnum, e_shentsize,
             e_shnum, e_shstrndx) = struct.unpack_from(fmt, mm, 16)

        _ETYPES   = {0:"ET_NONE",1:"ET_REL",2:"ET_EXEC",3:"ET_DYN",4:"ET_CORE"}
        _MACHINES = {0x3E:"x86-64",0x28:"ARM",0xB7:"AArch64",0x08:"MIPS",
                     0x14:"PowerPC",0x15:"PPC64",0x02:"SPARC",0x3:"x86",
                     0xF3:"RISC-V"}

        return {
            "e_type":     _ETYPES.get(e_type,    f"0x{e_type:04x}"),
            "e_machine":  _MACHINES.get(e_machine, f"0x{e_machine:04x}"),
            "e_version":  e_version,
            "e_entry":    f"0x{e_entry:016x}" if is_64 else f"0x{e_entry:08x}",
            "e_phoff":    e_phoff,
            "e_shoff":    e_shoff,
            "e_flags":    f"0x{e_flags:08x}",
            "e_ehsize":   e_ehsize,
            "e_phentsize": e_phentsize,
            "e_phnum":    e_phnum,
            "e_shentsize": e_shentsize,
            "e_shnum":    e_shnum,
            "e_shstrndx": e_shstrndx,
            "is_64bit":   is_64,
            "is_pie":     e_type == 3,   # ET_DYN = position-independent executable
        }

    # ------------------------------------------------------------------
    # Section headers
    # ------------------------------------------------------------------

    def _parse_section_headers(
        self, mm: Any, hdr: Dict, is_64: bool, endian: str
    ) -> List[Dict[str, Any]]:
        e_shoff    = hdr["e_shoff"]
        e_shnum    = hdr["e_shnum"]
        e_shentsize = hdr["e_shentsize"]

        if e_shoff == 0 or e_shnum == 0:
            return []

        fmt = endian + ("IIQQQQIIQQ" if is_64 else "IIIIIIIIII")
        entry_size = struct.calcsize(fmt)

        sections: List[Dict] = []
        for i in range(e_shnum):
            off = e_shoff + i * e_shentsize
            if off + entry_size > len(mm):
                break
            fields = struct.unpack_from(fmt, mm, off)
            if is_64:
                sh_name, sh_type, sh_flags, sh_addr, sh_offset, sh_size, \
                    sh_link, sh_info, sh_addralign, sh_entsize = fields
            else:
                sh_name, sh_type, sh_flags, sh_addr, sh_offset, sh_size, \
                    sh_link, sh_info, sh_addralign, sh_entsize = fields

            sections.append({
                "index":       i,
                "sh_name":     sh_name,
                "name":        "",          # filled in later from .shstrtab
                "type":        _SHT.get(sh_type, f"0x{sh_type:x}"),
                "sh_type":     sh_type,
                "flags":       self._decode_flags(sh_flags, _SHF),
                "sh_flags":    sh_flags,
                "addr":        f"0x{sh_addr:x}",
                "sh_addr":     sh_addr,
                "offset":      sh_offset,
                "size":        sh_size,
                "sh_link":     sh_link,
                "sh_info":     sh_info,
                "alignment":   sh_addralign,
                "entry_size":  sh_entsize,
                "executable":  bool(sh_flags & 4),
                "writable":    bool(sh_flags & 1),
                "loadable":    bool(sh_flags & 2),
            })
        return sections

    # ------------------------------------------------------------------
    # Program headers
    # ------------------------------------------------------------------

    def _parse_program_headers(
        self, mm: Any, hdr: Dict, is_64: bool, endian: str
    ) -> List[Dict[str, Any]]:
        e_phoff    = hdr["e_phoff"]
        e_phnum    = hdr["e_phnum"]
        e_phentsize = hdr["e_phentsize"]

        if e_phoff == 0 or e_phnum == 0:
            return []

        fmt = endian + ("IIQQQQQQ" if is_64 else "IIIIIIII")
        entry_size = struct.calcsize(fmt)

        phdrs: List[Dict] = []
        for i in range(e_phnum):
            off = e_phoff + i * e_phentsize
            if off + entry_size > len(mm):
                break
            fields = struct.unpack_from(fmt, mm, off)

            if is_64:
                p_type, p_flags, p_offset, p_vaddr, p_paddr, \
                    p_filesz, p_memsz, p_align = fields
            else:
                p_type, p_offset, p_vaddr, p_paddr, \
                    p_filesz, p_memsz, p_flags, p_align = fields

            perm = ("r" if p_flags & 4 else "-"
                  + "w" if p_flags & 2 else "-"
                  + "x" if p_flags & 1 else "-")

            phdrs.append({
                "index":    i,
                "type":     _PT.get(p_type, f"PT_0x{p_type:x}"),
                "p_type":   p_type,
                "offset":   p_offset,
                "vaddr":    f"0x{p_vaddr:x}",
                "filesz":   p_filesz,
                "memsz":    p_memsz,
                "flags":    perm,
                "p_flags":  p_flags,
                "align":    p_align,
                "executable": bool(p_flags & 1),
                "writable":   bool(p_flags & 2),
                "readable":   bool(p_flags & 4),
            })
        return phdrs

    # ------------------------------------------------------------------
    # Symbol tables
    # ------------------------------------------------------------------

    def _parse_symtab(
        self, mm: Any, sections: List[Dict],
        sec_name: str, strtab: bytes,
        is_64: bool, endian: str,
    ) -> List[Dict[str, Any]]:
        sec = next((s for s in sections if s["name"] == sec_name), None)
        if sec is None or sec["size"] == 0:
            return []

        if is_64:
            fmt = endian + "IBBHQQ"    # st_name(4) st_info(1) st_other(1) st_shndx(2) st_value(8) st_size(8)
            entry_size = 24
        else:
            fmt = endian + "IIIBBH"    # st_name(4) st_value(4) st_size(4) st_info(1) st_other(1) st_shndx(2)
            entry_size = 16

        syms: List[Dict] = []
        offset = sec["offset"]
        count  = sec["size"] // entry_size

        for i in range(count):
            off = offset + i * entry_size
            if off + entry_size > len(mm):
                break
            fields = struct.unpack_from(fmt, mm, off)

            if is_64:
                st_name, st_info, st_other, st_shndx, st_value, st_size = fields
            else:
                st_name, st_value, st_size, st_info, st_other, st_shndx = fields

            sym_type = _STT.get(st_info & 0xF,  f"0x{st_info & 0xF:x}")
            sym_bind = _STB.get(st_info >> 4,   f"0x{st_info >> 4:x}")
            sym_vis  = _STV.get(st_other & 0x3, "DEFAULT")
            sym_name = self._strtab_lookup(strtab, st_name)

            syms.append({
                "index":   i,
                "name":    sym_name,
                "type":    sym_type,
                "bind":    sym_bind,
                "vis":     sym_vis,
                "shndx":   st_shndx,
                "value":   f"0x{st_value:x}",
                "st_value": st_value,
                "size":    st_size,
                "is_func":     sym_type == "FUNC",
                "is_object":   sym_type == "OBJECT",
                "is_imported": st_shndx == 0 and sym_bind in ("GLOBAL", "WEAK"),
                "is_exported": st_shndx != 0 and sym_bind in ("GLOBAL", "WEAK"),
            })
        return syms

    # ------------------------------------------------------------------
    # Dynamic section
    # ------------------------------------------------------------------

    def _parse_dynamic(
        self, mm: Any, sections: List[Dict],
        dynstr: bytes, endian: str, is_64: bool,
    ) -> List[Dict[str, Any]]:
        sec = next((s for s in sections if s["name"] == ".dynamic"), None)
        if sec is None:
            # Try finding it via PT_DYNAMIC program header
            return []

        fmt        = endian + ("qQ" if is_64 else "iI")
        entry_size = 16 if is_64 else 8
        entries: List[Dict] = []

        offset = sec["offset"]
        count  = sec["size"] // entry_size

        for i in range(count):
            off = offset + i * entry_size
            if off + entry_size > len(mm):
                break
            d_tag, d_val = struct.unpack_from(fmt, mm, off)
            tag_name = _DT_NAMES.get(d_tag & 0xFFFFFFFF, f"DT_0x{d_tag:x}")

            # Resolve string values for string-table tags
            val_str: Optional[str] = None
            if tag_name in ("NEEDED", "SONAME", "RPATH", "RUNPATH"):
                val_str = self._strtab_lookup(dynstr, d_val)

            entries.append({
                "tag":      d_tag,
                "tag_name": tag_name,
                "val":      d_val,
                "val_str":  val_str,
            })

            if d_tag == 0:   # DT_NULL = end of .dynamic
                break

        return entries

    # ------------------------------------------------------------------
    # Relocations
    # ------------------------------------------------------------------

    def _parse_relocations(
        self, mm: Any, sections: List[Dict],
        dynsyms: List[Dict], is_64: bool, endian: str,
    ) -> List[Dict[str, Any]]:
        relas: List[Dict] = []

        for sec in sections:
            if sec["type"] not in ("RELA", "REL"):
                continue
            if is_64:
                fmt        = endian + "QQq" if sec["type"] == "RELA" else endian + "QQ"
                entry_size = 24 if sec["type"] == "RELA" else 16
            else:
                fmt        = endian + "IIi" if sec["type"] == "RELA" else endian + "II"
                entry_size = 12 if sec["type"] == "RELA" else 8

            offset = sec["offset"]
            count  = sec["size"] // entry_size

            for i in range(count):
                off = offset + i * entry_size
                if off + entry_size > len(mm):
                    break
                fields = struct.unpack_from(fmt, mm, off)

                if is_64:
                    r_offset = fields[0]
                    r_info   = fields[1]
                    r_addend = fields[2] if sec["type"] == "RELA" else 0
                    sym_idx  = r_info >> 32
                    r_type   = r_info & 0xFFFFFFFF
                else:
                    r_offset = fields[0]
                    r_info   = fields[1]
                    r_addend = fields[2] if sec["type"] == "RELA" else 0
                    sym_idx  = r_info >> 8
                    r_type   = r_info & 0xFF

                sym_name = ""
                if 0 < sym_idx < len(dynsyms):
                    sym_name = dynsyms[sym_idx]["name"]

                relas.append({
                    "section":  sec["name"],
                    "offset":   f"0x{r_offset:x}",
                    "type":     r_type,
                    "sym_idx":  sym_idx,
                    "sym_name": sym_name,
                    "addend":   r_addend,
                })

        return relas

    # ------------------------------------------------------------------
    # NOTE sections
    # ------------------------------------------------------------------

    def _parse_notes(
        self, mm: Any, sections: List[Dict], endian: str
    ) -> List[Dict[str, Any]]:
        notes: List[Dict] = []
        for sec in sections:
            if sec["type"] != "NOTE":
                continue
            offset = sec["offset"]
            end    = offset + sec["size"]
            pos    = offset
            while pos + 12 <= end:
                namesz, descsz, n_type = struct.unpack_from(
                    endian + "III", mm, pos
                )
                pos += 12
                name = b""
                if namesz > 0 and pos + namesz <= end:
                    name = bytes(mm[pos: pos + namesz]).rstrip(b"\x00")
                    pos += (namesz + 3) & ~3   # align to 4 bytes
                desc = b""
                if descsz > 0 and pos + descsz <= end:
                    desc = bytes(mm[pos: pos + descsz])
                    pos += (descsz + 3) & ~3

                note: Dict[str, Any] = {
                    "section":  sec["name"],
                    "name":     name.decode("ascii", errors="replace"),
                    "type":     n_type,
                    "desc_len": descsz,
                }
                # Build-ID note
                if name == b"GNU" and n_type == 3:
                    note["build_id"] = desc.hex()
                # ABI version note
                if name == b"GNU" and n_type == 1 and len(desc) >= 16:
                    abi = struct.unpack_from("<IIII", desc)
                    os_map = {0: "Linux", 1: "Hurd", 2: "Solaris", 3: "FreeBSD"}
                    note["abi_os"]      = os_map.get(abi[0], str(abi[0]))
                    note["abi_version"] = f"{abi[1]}.{abi[2]}.{abi[3]}"
                notes.append(note)
        return notes

    # ------------------------------------------------------------------
    # GNU hash table
    # ------------------------------------------------------------------

    def _parse_gnu_hash(
        self, mm: Any, sections: List[Dict], endian: str, is_64: bool
    ) -> Dict[str, Any]:
        sec = next((s for s in sections if s["name"] == ".gnu.hash"), None)
        if sec is None or sec["size"] < 16:
            return {"present": False}

        offset = sec["offset"]
        nbuckets, symoffset, bloom_size, bloom_shift = struct.unpack_from(
            endian + "IIII", mm, offset
        )
        return {
            "present":     True,
            "nbuckets":    nbuckets,
            "symoffset":   symoffset,
            "bloom_size":  bloom_size,
            "bloom_shift": bloom_shift,
        }

    # ------------------------------------------------------------------
    # PLT stub detection
    # ------------------------------------------------------------------

    @staticmethod
    def _find_plt_stubs(
        sections: List[Dict], relas: List[Dict]
    ) -> List[Dict[str, Any]]:
        """
        Map PLT stub addresses to the imported symbol names they call.
        Each .rela.plt entry gives (GOT slot address, symbol index).
        The PLT stub at base + i * 16 calls GOT[sym].
        """
        plt = next((s for s in sections if s["name"] == ".plt"), None)
        if plt is None:
            return []

        plt_relas = [r for r in relas if r["section"] == ".rela.plt"]
        stubs: List[Dict] = []
        plt_base = plt["sh_addr"]

        for i, rela in enumerate(plt_relas):
            stub_addr = plt_base + (i + 1) * 16    # first stub is PLT[0] (resolver)
            stubs.append({
                "index":     i,
                "addr":      f"0x{stub_addr:x}",
                "sym_name":  rela["sym_name"],
                "got_slot":  rela["offset"],
            })
        return stubs

    # ------------------------------------------------------------------
    # String table helpers
    # ------------------------------------------------------------------

    def _find_strtab(
        self, mm: Any, sections: List[Dict], name: str
    ) -> bytes:
        sec = next((s for s in sections if s["name"] == name), None)
        if sec is None:
            return b""
        return self._read_strtab(mm, sec)

    @staticmethod
    def _read_strtab(mm: Any, sec: Dict) -> bytes:
        if not sec:
            return b""
        offset = sec.get("offset", 0)
        size   = sec.get("size", 0)
        if offset == 0 or size == 0 or offset + size > len(mm):
            return b""
        return bytes(mm[offset: offset + size])

    @staticmethod
    def _strtab_lookup(strtab: bytes, index: int) -> str:
        if not strtab or index >= len(strtab):
            return ""
        end = strtab.find(b"\x00", index)
        if end == -1:
            end = len(strtab)
        return strtab[index:end].decode("utf-8", errors="replace")

    @staticmethod
    def _decode_flags(flags: int, flag_map: Dict[int, str]) -> List[str]:
        return [name for bit, name in flag_map.items()
                if isinstance(bit, int) and flags & bit]


# ===========================================================================
# ElfUnderstanding  — semantic layer on top of DeepElfParser
# ===========================================================================

class ElfUnderstanding:
    """
    Takes the raw structural data from DeepElfParser and builds
    **semantic understanding** — like the "ink detection" pass in the
    Herculaneum pipeline that goes from "here are the CT voxels" to
    "here is what the ink says".

    Answers questions like:
    • What does this binary *do*?  (purpose from strings + imports)
    • Which external functions does it call and from which libraries?
    • What is its initialization sequence?
    • What configuration / environment variables does it read?
    • What algorithms are likely embedded?  (crypto, compression, regex, …)
    • How is it structured?  (single binary vs. plugin host, daemon vs. CLI, …)
    """

    # Known algorithm fingerprints: (import_or_string_patterns, label)
    _ALGORITHM_FINGERPRINTS: List[Tuple[List[str], str]] = [
        (["pcre2_match", "pcre2_compile"],      "PCRE2 regex engine"),
        (["regexec", "regcomp"],                "POSIX regex"),
        (["SSL_connect", "SSL_read"],           "OpenSSL TLS"),
        (["mbedtls_", "mbedtls_pk_"],           "mbedTLS"),
        (["pthread_create", "pthread_join"],    "POSIX threads"),
        (["tokio", "async_runtime"],            "Tokio async runtime (Rust)"),
        (["rayon::", "ThreadPool"],             "Rayon parallel iterators (Rust)"),
        (["zstd_decompress", "ZSTD_compress"],  "Zstandard compression"),
        (["lz4_compress", "LZ4_decompress"],    "LZ4 compression"),
        (["inflate", "deflate", "zlib"],        "zlib/gzip compression"),
        (["brotli_compress", "BrotliDecompress"],"Brotli compression"),
        (["blake3_", "BLAKE3"],                 "BLAKE3 hashing"),
        (["SHA256_Init", "SHA256_Update"],      "SHA-256 hashing"),
        (["md5_init", "MD5Final"],              "MD5 hashing"),
        (["sqlite3_open", "sqlite3_exec"],      "SQLite database"),
        (["jemalloc", "je_malloc"],             "jemalloc allocator"),
        (["mimalloc", "mi_malloc"],             "mimalloc allocator"),
        (["mmap", "munmap"],                    "Memory-mapped I/O"),
        (["fork", "execve"],                    "Process spawning"),
        (["inotify_init", "inotify_add_watch"], "Linux inotify file watching"),
    ]

    def __init__(self, parse_result: Dict[str, Any]):
        self._p = parse_result

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def understand(self) -> Dict[str, Any]:
        """
        Run all semantic analyses and return a structured understanding dict.
        """
        imports_set = {s["name"] for s in self._p.get("imports", [])}
        exports_set = {s["name"] for s in self._p.get("exports", [])}
        all_names   = {s["name"] for s in self._p.get("all_symbols", [])}
        dso_deps    = self._p.get("dso_deps", [])

        purpose       = self._infer_purpose(imports_set, dso_deps)
        binary_type   = self._classify_binary_type()
        algorithms    = self._detect_algorithms(imports_set | all_names)
        init_sequence = self._trace_init_sequence()
        env_vars      = self._find_env_vars_and_config(imports_set)
        security      = self._security_analysis(imports_set)
        lib_usage     = self._library_usage_map(dso_deps, imports_set)
        exec_flow     = self._execution_flow_summary()

        return {
            "purpose":        purpose,
            "binary_type":    binary_type,
            "algorithms":     algorithms,
            "init_sequence":  init_sequence,
            "env_config":     env_vars,
            "security":       security,
            "library_usage":  lib_usage,
            "execution_flow": exec_flow,
            "import_count":   self._p.get("import_count", 0),
            "export_count":   self._p.get("export_count", 0),
            "imports":        sorted(imports_set),
            "dso_deps":       dso_deps,
        }

    # ------------------------------------------------------------------
    # Purpose inference
    # ------------------------------------------------------------------

    def _infer_purpose(
        self, imports: set, deps: List[str]
    ) -> str:
        dep_str = " ".join(deps).lower()
        imp_str = " ".join(imports).lower()

        hints: List[str] = []
        if "pcre2" in dep_str or "pcre2_match" in imp_str:
            hints.append("regex/pattern search")
        if any(x in dep_str for x in ("gtk", "qt", "xcb", "wayland", "webkit")):
            hints.append("GUI application")
        if any(x in dep_str for x in ("openssl", "gnutls", "mbedtls", "nss")):
            hints.append("TLS/SSL network communication")
        if any(x in imp_str for x in ("sqlite3", "leveldb", "rocksdb")):
            hints.append("database")
        if any(x in imp_str for x in ("pthread_create", "fork", "clone")):
            hints.append("multi-process/threaded")
        if any(x in imp_str for x in ("mmap", "munmap", "mremap")):
            hints.append("memory-mapped I/O")
        if any(x in imp_str for x in ("inotify", "epoll", "kqueue", "select")):
            hints.append("event-driven I/O")
        if "libz" in dep_str or "zstd" in dep_str:
            hints.append("compressed data processing")
        if not hints:
            hints.append("general purpose utility")
        return "; ".join(hints)

    # ------------------------------------------------------------------
    # Binary type
    # ------------------------------------------------------------------

    def _classify_binary_type(self) -> Dict[str, Any]:
        hdr     = self._p.get("header", {})
        phdrs   = self._p.get("phdrs", [])
        dynamic = self._p.get("dynamic", [])
        exports = self._p.get("exports", [])

        e_type  = hdr.get("e_type", "")
        is_pie  = hdr.get("is_pie", False)
        is_dyn  = any(p["type"] == "DYNAMIC" for p in phdrs)
        is_interp = any(p["type"] == "INTERP" for p in phdrs)

        has_main   = any(s["name"] == "main" for s in exports)
        has_init   = any(p["tag_name"] in ("INIT","INIT_ARRAY") for p in dynamic)
        has_soname = any(p["tag_name"] == "SONAME" for p in dynamic)

        kind = "unknown"
        if e_type == "ET_DYN":
            if has_soname:
                kind = "shared library (.so)"
            elif is_pie:
                kind = "PIE executable (position-independent)"
            else:
                kind = "shared object"
        elif e_type == "ET_EXEC":
            kind = "static executable"
        elif e_type == "ET_REL":
            kind = "relocatable object (.o)"
        elif e_type == "ET_CORE":
            kind = "core dump"

        return {
            "kind":       kind,
            "is_pie":     is_pie,
            "is_dynamic": is_dyn,
            "needs_interp": is_interp,
            "has_main":   has_main,
            "has_soname": has_soname,
            "has_init":   has_init,
        }

    # ------------------------------------------------------------------
    # Algorithm detection
    # ------------------------------------------------------------------

    def _detect_algorithms(self, symbol_set: set) -> List[str]:
        found: List[str] = []
        sym_str = " ".join(symbol_set).lower()
        for patterns, label in self._ALGORITHM_FINGERPRINTS:
            if any(p.lower() in sym_str for p in patterns):
                found.append(label)
        return found

    # ------------------------------------------------------------------
    # Initialization sequence
    # ------------------------------------------------------------------

    def _trace_init_sequence(self) -> Dict[str, Any]:
        dynamic = self._p.get("dynamic", [])
        phdrs   = self._p.get("phdrs",   [])
        secs    = self._p.get("sections", [])

        # Build a fast lookup so we can cross-reference INIT_ARRAY / INIT_ARRAYSZ
        dyn_val = {e["tag_name"]: e["val"] for e in dynamic}

        steps: List[str] = []
        step = 1

        interp = next((p for p in phdrs if p["type"] == "INTERP"), None)
        if interp:
            steps.append(f"{step}. Dynamic linker (ld-linux) loads and relocates the binary")
            step += 1

        gnu_relro = next((p for p in phdrs if p["type"] == "GNU_RELRO"), None)
        if gnu_relro:
            steps.append(f"{step}. GNU_RELRO: relocations committed, GOT made read-only (security)")
            step += 1

        if "INIT" in dyn_val:
            steps.append(
                f"{step}. DT_INIT: call single constructor at {dyn_val['INIT']:#x}"
            )
            step += 1

        if "INIT_ARRAY" in dyn_val:
            # INIT_ARRAYSZ is byte-size; divide by pointer width (8 for 64-bit, 4 for 32-bit)
            ptr_sz   = 8 if self._p.get("class") == "64-bit" else 4
            arraysz  = dyn_val.get("INIT_ARRAYSZ", 0)
            count    = arraysz // ptr_sz if ptr_sz else 0
            steps.append(
                f"{step}. DT_INIT_ARRAY: call {count} constructor(s) "
                f"at {dyn_val['INIT_ARRAY']:#x} ({arraysz} bytes)"
            )
            step += 1

        if "FINI_ARRAY" in dyn_val:
            ptr_sz   = 8 if self._p.get("class") == "64-bit" else 4
            arraysz  = dyn_val.get("FINI_ARRAYSZ", 0)
            count    = arraysz // ptr_sz if ptr_sz else 0
            steps.append(
                f"{step}. DT_FINI_ARRAY: {count} destructor(s) at {dyn_val['FINI_ARRAY']:#x}"
            )
            step += 1

        if "FINI" in dyn_val:
            steps.append(
                f"{step}. DT_FINI: call single destructor at {dyn_val['FINI']:#x}"
            )
            step += 1

        # .ctors section (older GCC style)
        if any(s["name"] in (".ctors", ".init") for s in secs):
            steps.append(f"{step}. .ctors / .init section present (legacy constructor chain)")
            step += 1

        gnu_stack = next((p for p in phdrs if p["type"] == "GNU_STACK"), None)
        if gnu_stack:
            nx = not gnu_stack.get("executable", False)
            steps.append(
                f"{step}. GNU_STACK: "
                + ("non-executable stack (NX enabled ✅)" if nx
                   else "EXECUTABLE stack — NX disabled ⚠️")
            )

        return {"steps": steps, "interp": interp}

    # ------------------------------------------------------------------
    # Environment / config reading
    # ------------------------------------------------------------------

    def _find_env_vars_and_config(
        self, imports: set
    ) -> Dict[str, Any]:
        reads_env  = "getenv" in imports
        reads_conf = any(x in imports for x in ("fopen", "open", "stat", "access"))
        reads_proc = any(x in imports for x in ("readdir", "opendir"))

        return {
            "reads_environment_variables": reads_env,
            "reads_config_files":          reads_conf,
            "reads_proc_or_sys":           reads_proc,
        }

    # ------------------------------------------------------------------
    # Security analysis
    # ------------------------------------------------------------------

    def _security_analysis(self, imports: set) -> Dict[str, Any]:
        # ── Detect language so we can apply language-specific rules ───
        all_syms = {s["name"] for s in self._p.get("all_symbols", [])}
        all_names = imports | all_syms
        is_rust = any(n in all_names for n in (
            "_Unwind_Resume", "_Unwind_Backtrace", "__rust_alloc",
            "rust_begin_unwind", "__rg_", "__rust_",
        ))
        is_go = any(n.startswith("runtime.") for n in all_names)

        # Stack canary: __stack_chk_fail imported → compiled with -fstack-protector
        # Rust/Go don't use this (they have language-level memory safety instead)
        stack_prot = "__stack_chk_fail" in imports
        lang_safe  = is_rust or is_go   # memory-safe language — canary not needed

        # FORTIFY_SOURCE: presence of __*_chk variants
        fortify = any("_chk" in s for s in imports)

        # Dangerous functions
        dangerous = [s for s in imports if s in (
            "gets", "strcpy", "strcat", "sprintf", "vsprintf",
            "scanf", "sscanf", "fscanf", "strtok",
        )]

        # PIE
        is_pie = self._p.get("header", {}).get("is_pie", False)

        # RELRO
        phdrs = self._p.get("phdrs", [])
        relro = any(p["type"] == "GNU_RELRO" for p in phdrs)

        # NX stack
        gnu_stack = next((p for p in phdrs if p["type"] == "GNU_STACK"), None)
        nx_stack  = gnu_stack is not None and not gnu_stack.get("executable", False)

        # For memory-safe languages, award full credit for canary + fortify
        # because the language itself provides equivalent (or stronger) guarantees.
        effective_canary  = stack_prot or lang_safe
        effective_fortify = fortify    or lang_safe

        score = sum([effective_canary, effective_fortify, is_pie, relro, nx_stack])
        grade = ["F", "D", "C", "B", "A", "A+"][min(score, 5)]

        return {
            "stack_canary":        stack_prot,
            "fortify_source":      fortify,
            "language_memory_safe": lang_safe,
            "pie":                 is_pie,
            "relro":               relro,
            "nx_stack":            nx_stack,
            "dangerous_funcs":     dangerous,
            "hardening_score":     score,
            "hardening_grade":     grade,
            "is_rust":             is_rust,
            "is_go":               is_go,
        }

    # ------------------------------------------------------------------
    # Library usage map
    # ------------------------------------------------------------------

    @staticmethod
    def _library_usage_map(
        deps: List[str], imports: set
    ) -> Dict[str, List[str]]:
        """Map each library to the symbols imported from it."""
        lib_map: Dict[str, List[str]] = {}
        # Use heuristic: libc symbols start with predictable prefixes
        _lib_prefixes: List[Tuple[str, str]] = [
            ("libc.so",   ["malloc","free","printf","open","read","write",
                           "close","mmap","fork","execve","getenv","fopen"]),
            ("libpthread",["pthread_create","pthread_join","pthread_mutex",
                           "pthread_cond","pthread_rwlock","sem_"]),
            ("libdl",     ["dlopen","dlsym","dlclose","dlerror"]),
            ("libm",      ["sin","cos","sqrt","pow","log","exp","floor","ceil"]),
        ]
        for lib in deps:
            matched: List[str] = []
            for prefix, syms in _lib_prefixes:
                if prefix in lib:
                    matched = [s for s in imports if any(s.startswith(p) for p in syms)]
            lib_map[lib] = matched
        return lib_map

    # ------------------------------------------------------------------
    # Execution flow summary
    # ------------------------------------------------------------------

    def _execution_flow_summary(self) -> Dict[str, Any]:
        """High-level execution flow based on binary structure."""
        phdrs   = self._p.get("phdrs",   [])
        dynamic = self._p.get("dynamic", [])
        imports = {s["name"] for s in self._p.get("imports", [])}

        load_segments = [p for p in phdrs if p["type"] == "LOAD"]
        exec_segs     = [p for p in load_segments if p.get("executable")]
        data_segs     = [p for p in load_segments if p.get("writable")]

        return {
            "load_segment_count":  len(load_segments),
            "exec_segment_count":  len(exec_segs),
            "data_segment_count":  len(data_segs),
            "has_thread_local":    any(p["type"] == "TLS"  for p in phdrs),
            "has_eh_frame":        any(p["type"] == "GNU_EH_FRAME" for p in phdrs),
            "uses_dlopen":         "dlopen" in imports,
            "uses_fork_exec":      "fork" in imports and "execve" in imports,
            "uses_mmap":           "mmap" in imports,
        }


# ===========================================================================
# ProgressiveScan  — CT-scanner style multi-depth scan with progress
# ===========================================================================

class ProgressiveScan:
    """
    Multi-depth progressive scanner — like adjusting the CT scanner settings
    from a quick scout image to a full high-resolution scan.

    Six depth levels:

    Depth 1 — Header only     (< 0.01 s)  Identity check: magic, arch, type, PIE
    Depth 2 — Skeleton        (< 0.1 s)   Section/segment layout
    Depth 3 — Symbols         (< 0.5 s)   Full symbol table + language detection
    Depth 4 — Deep structure  (< 2 s)     Dynamic section, relocations, GOT/PLT,
                                          imports/exports, notes (build-id, ABI)
    Depth 5 — Understanding   (< 5 s)     Semantic analysis: purpose, algorithms,
                                          security hardening, init sequence,
                                          config/env reading patterns
    Depth 6 — Reconstruction  (open)      Full BinaryXRay + VirtualUnwrapper +
                                          AIPatternMatcher + ScrollAssembler

    Usage::

        # Print a progress report at each depth
        for update in ProgressiveScan(elf_path).scan(max_depth=5):
            print(f"[{update['depth']}/5] {update['label']}: "
                  f"{update['summary']}")

        # Run to a specific depth and get the full result
        result = ProgressiveScan(elf_path).run(depth=4)
    """

    _DEPTH_LABELS = {
        1: "Header identity",
        2: "Section/segment skeleton",
        3: "Symbol table + language",
        4: "Deep structure (dynamic, relos, PLT)",
        5: "Semantic understanding",
        6: "Full AI reconstruction",
    }

    def __init__(self, elf_path: str):
        self.elf_path = Path(elf_path).resolve()
        if not self.elf_path.exists():
            raise FileNotFoundError(f"Not found: {self.elf_path}")
        with open(self.elf_path, "rb") as fh:
            if fh.read(4) != ELF_MAGIC:
                raise ValueError(f"Not a valid ELF: {self.elf_path}")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self, depth: int = 4) -> Dict[str, Any]:
        """
        Run all scan passes up to *depth* and return the combined result.

        Unlike ``scan()`` (a generator), this blocks until *depth* is reached
        and returns the aggregated result dict.
        """
        result: Dict[str, Any] = {"binary": str(self.elf_path), "depth": depth}
        for update in self.scan(max_depth=depth):
            result.update(update.get("data", {}))
        return result

    def scan(
        self, max_depth: int = 6
    ):   # → Iterator[Dict[str, Any]]
        """
        Generator: yields one progress-update dict per depth level.

        Each dict has::

            {
                "depth":    int,          # 1–6
                "label":    str,          # human-readable label
                "progress": float,        # 0.0–1.0
                "summary":  str,          # one-line summary
                "data":     Dict,         # depth-specific result data
            }
        """
        max_depth = max(1, min(6, max_depth))

        # ── Depth 1: Header identity ───────────────────────────────────
        if max_depth >= 1:
            data = self._depth1_header()
            yield {
                "depth":    1,
                "label":    self._DEPTH_LABELS[1],
                "progress": 1 / max_depth,
                "summary":  (
                    f"{data['class']} {data['machine']} {data['type']}"
                    + (" [PIE]" if data.get("is_pie") else "")
                    + f" — {data['size_bytes']:,} bytes"
                ),
                "data": data,
            }
            if max_depth == 1:
                return

        # ── Depth 2: Skeleton ──────────────────────────────────────────
        if max_depth >= 2:
            data = self._depth2_skeleton()
            yield {
                "depth":    2,
                "label":    self._DEPTH_LABELS[2],
                "progress": 2 / max_depth,
                "summary":  (
                    f"{data['section_count']} sections, "
                    f"{data['phdr_count']} segments"
                    + (" [HAS_DWARF]" if data.get("has_debug") else "")
                    + (" [STRIPPED]" if not data.get("has_symtab") else "")
                ),
                "data": data,
            }
            if max_depth == 2:
                return

        # ── Depth 3: Symbols + language ───────────────────────────────
        if max_depth >= 3:
            data = self._depth3_symbols()
            yield {
                "depth":    3,
                "label":    self._DEPTH_LABELS[3],
                "progress": 3 / max_depth,
                "summary":  (
                    f"language={data['language']}, "
                    f"{data['dynsym_count']} dynsyms, "
                    f"{data['source_file_count']} src paths"
                ),
                "data": data,
            }
            if max_depth == 3:
                return

        # ── Depth 4: Deep structure ────────────────────────────────────
        if max_depth >= 4:
            data = self._depth4_deep()
            sec  = data.get("security", {})
            yield {
                "depth":    4,
                "label":    self._DEPTH_LABELS[4],
                "progress": 4 / max_depth,
                "summary":  (
                    f"{data['import_count']} imports, "
                    f"{data['export_count']} exports, "
                    f"{len(data.get('dso_deps', []))} libs, "
                    f"hardening={sec.get('hardening_grade','?')}"
                ),
                "data": data,
            }
            if max_depth == 4:
                return

        # ── Depth 5: Semantic understanding ───────────────────────────
        if max_depth >= 5:
            data = self._depth5_understanding()
            algs = data.get("algorithms", [])
            yield {
                "depth":    5,
                "label":    self._DEPTH_LABELS[5],
                "progress": 5 / max_depth,
                "summary":  (
                    f"purpose={data.get('purpose','?')!r:.60}, "
                    f"algorithms=[{', '.join(algs[:3])}]"
                ),
                "data": data,
            }
            if max_depth == 5:
                return

        # ── Depth 6: Full AI reconstruction ───────────────────────────
        if max_depth >= 6:
            data = self._depth6_reconstruct()
            yield {
                "depth":    6,
                "label":    self._DEPTH_LABELS[6],
                "progress": 1.0,
                "summary":  (
                    f"{data.get('module_count', 0)} modules, "
                    f"{data.get('fragment_count', 0)} fragments"
                ),
                "data": data,
            }

    # ------------------------------------------------------------------
    # Depth implementations
    # ------------------------------------------------------------------

    def _depth1_header(self) -> Dict[str, Any]:
        """Read only the 64-byte ELF header."""
        parser = DeepElfParser(str(self.elf_path))
        import mmap as _mmap
        with open(self.elf_path, "rb") as fh:
            mm = _mmap.mmap(fh.fileno(), 0, access=_mmap.ACCESS_READ)
            try:
                ei_class = mm[4]
                ei_data  = mm[5]
                is_64    = (ei_class == 2)
                endian   = "<" if ei_data == 1 else ">"
                hdr = parser._parse_header(mm, is_64, endian)
            finally:
                mm.close()

        return {
            "class":      hdr["class"] if False else ("64-bit" if is_64 else "32-bit"),
            "machine":    hdr["e_machine"],
            "type":       hdr["e_type"],
            "entry":      hdr["e_entry"],
            "is_pie":     hdr["is_pie"],
            "is_64bit":   is_64,
            "size_bytes": self.elf_path.stat().st_size,
            "sha256":     self._sha256_fast(),
        }

    def _depth2_skeleton(self) -> Dict[str, Any]:
        """Parse section and program headers only."""
        import mmap as _mmap
        parser = DeepElfParser(str(self.elf_path))
        with open(self.elf_path, "rb") as fh:
            mm = _mmap.mmap(fh.fileno(), 0, access=_mmap.ACCESS_READ)
            try:
                is_64   = mm[4] == 2
                endian  = "<" if mm[5] == 1 else ">"
                hdr     = parser._parse_header(mm, is_64, endian)
                secs    = parser._parse_section_headers(mm, hdr, is_64, endian)
                phdrs   = parser._parse_program_headers(mm, hdr, is_64, endian)
                shstr   = parser._read_strtab(
                    mm,
                    secs[hdr["e_shstrndx"]] if hdr["e_shstrndx"] < len(secs) else {}
                )
                for s in secs:
                    s["name"] = parser._strtab_lookup(shstr, s["sh_name"])
            finally:
                mm.close()

        has_debug = any(s["name"] in (".debug_info", ".debug_abbrev",
                                       ".debug_line") for s in secs)
        has_sym   = any(s["name"] == ".symtab" for s in secs)
        exec_secs = [s["name"] for s in secs if s.get("executable") and s["name"]]

        return {
            "section_count": len(secs),
            "phdr_count":    len(phdrs),
            "sections":      [s["name"] for s in secs if s["name"]],
            "exec_sections": exec_secs,
            "has_debug":     has_debug,
            "has_symtab":    has_sym,
            "segment_types": [p["type"] for p in phdrs],
        }

    def _depth3_symbols(self) -> Dict[str, Any]:
        """Parse symbol tables + detect language."""
        import mmap as _mmap
        parser = DeepElfParser(str(self.elf_path))
        with open(self.elf_path, "rb") as fh:
            mm = _mmap.mmap(fh.fileno(), 0, access=_mmap.ACCESS_READ)
            try:
                is_64   = mm[4] == 2
                endian  = "<" if mm[5] == 1 else ">"
                hdr     = parser._parse_header(mm, is_64, endian)
                secs    = parser._parse_section_headers(mm, hdr, is_64, endian)
                shstr   = parser._read_strtab(
                    mm,
                    secs[hdr["e_shstrndx"]] if hdr["e_shstrndx"] < len(secs) else {}
                )
                for s in secs:
                    s["name"] = parser._strtab_lookup(shstr, s["sh_name"])
                dynstr  = parser._find_strtab(mm, secs, ".dynstr")
                strtab  = parser._find_strtab(mm, secs, ".strtab")
                dynsyms = parser._parse_symtab(mm, secs, ".dynsym", dynstr, is_64, endian)
                symtab  = parser._parse_symtab(mm, secs, ".symtab", strtab, is_64, endian)
            finally:
                mm.close()

        # Language inference via BinaryXRay helper
        xray = BinaryXRay.__new__(BinaryXRay)
        xray.elf_path = self.elf_path
        string_files = xray._extract_source_paths_from_strings()
        sym_names    = [s["name"] for s in dynsyms + symtab if s["name"]]
        language     = xray._infer_language(sym_names, string_files)

        return {
            "dynsym_count":    len(dynsyms),
            "symtab_count":    len(symtab),
            "dynsyms":         [s["name"] for s in dynsyms if s["name"]][:100],
            "language":        language,
            "source_files":    string_files,
            "source_file_count": len(string_files),
        }

    def _depth4_deep(self) -> Dict[str, Any]:
        """Full DeepElfParser parse."""
        parse = DeepElfParser(str(self.elf_path)).parse()
        security = ElfUnderstanding(parse)._security_analysis(
            {s["name"] for s in parse.get("imports", [])}
        )
        return {
            "import_count":  parse["import_count"],
            "export_count":  parse["export_count"],
            "dso_deps":      parse["dso_deps"],
            "imports":       [s["name"] for s in parse["imports"] if s["name"]][:100],
            "exports":       [s["name"] for s in parse["exports"] if s["name"]][:50],
            "notes":         parse["notes"],
            "plt_stubs":     parse["plt_stubs"][:50],
            "reloc_count":   len(parse["relocations"]),
            "section_count": parse["section_count"],
            "symbol_count":  parse["symbol_count"],
            "gnu_hash":      parse["gnu_hash"],
            "security":      security,
            "dynamic_tags":  [e["tag_name"] for e in parse["dynamic"] if e["tag_name"] != "NULL"],
        }

    def _depth5_understanding(self) -> Dict[str, Any]:
        """Semantic understanding layer."""
        parse       = DeepElfParser(str(self.elf_path)).parse()
        understands = ElfUnderstanding(parse).understand()
        return understands

    def _depth6_reconstruct(self) -> Dict[str, Any]:
        """Full reconstruction pipeline."""
        return ScrollAssembler(
            elf_path=str(self.elf_path)
        ).reconstruct(
            output_dir=str(Path(str(self.elf_path) + "_reconstructed"))
        )

    def _sha256_fast(self) -> str:
        h = hashlib.sha256()
        with open(self.elf_path, "rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()


# ===========================================================================
# VirtualUnwrapper  — reassemble layers into modules
# ===========================================================================

class VirtualUnwrapper:
    """
    Takes the raw scan result from BinaryXRay and "virtually unrolls" it —
    grouping symbols and strings into logical module/namespace units, just
    as the Herculaneum scroll virtual-unwrapping algorithm computationally
    unrolls the charred papyrus layers into a flat, readable sheet.

    Output: a list of ``UnwrappedModule`` dicts, each representing one
    inferred compilation unit / source file with all its associated symbols,
    strings, call relationships, and data patterns.
    """

    def __init__(self, scan: Dict[str, Any]):
        self._scan = scan

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def unwrap(self) -> List[Dict[str, Any]]:
        """
        Reassemble scan layers into a list of inferred module dicts.

        Each module dict has:
          name        Inferred module / file name
          language    Detected language
          symbols     Symbols assigned to this module
          strings     Strings likely from this module
          callers     Functions in this module that call outward
          callees     Functions this module calls
          source_path Original source path (if DWARF available), else None
          confidence  Overall module confidence (0-1)
        """
        layers   = self._scan.get("layers", {})
        skeleton = layers.get("skeleton", {})
        sym_data = layers.get("symbols", {})
        str_data = layers.get("strings", {})
        cg_data  = layers.get("callgraph", {})
        data_pat = layers.get("data", {})
        language = sym_data.get("language", "unknown")

        # ── Step 1: seed modules from ALL source file paths ──────────
        # Use both DWARF-derived and string-embedded source paths.
        # String-embedded paths (Rust panic locations) look like:
        #   /usr/share/cargo/registry/grep-searcher-0.1.13/src/searcher/mod.rs
        # We group by crate name + module path to keep the module count
        # manageable (avoid one module per panic site).
        modules: Dict[str, Dict[str, Any]] = {}

        all_source_files = sym_data.get("all_source_files", []) or (
            sym_data.get("dwarf_source_files", [])
            + sym_data.get("string_source_files", [])
        )

        for path in all_source_files:
            # Normalise: strip everything before /src/ to get the crate-relative path
            if "/src/" in path:
                # e.g. ".../grep-searcher-0.1.13/src/searcher/mod.rs"
                # crate name = the directory just before /src/
                before_src, _, rel = path.partition("/src/")
                crate_dir = before_src.rsplit("/", 1)[-1]
                # Strip version suffix from crate name: "grep-searcher-0.1.13" → "grep_searcher"
                crate_name = re.sub(r'-\d[\d.]*$', '', crate_dir).replace("-", "_")
                # Module path = rel path without extension: "searcher/mod.rs" → "searcher::mod"
                mod_rel = re.sub(r'\.rs$', '', rel).replace("/", "::").rstrip("::")
                key = f"{crate_name}::{mod_rel}" if mod_rel else crate_name
            elif "/" in path:
                name_part = path.rsplit("/", 1)[-1]
                key = re.sub(r'\.[a-z]+$', '', name_part)
            else:
                key = re.sub(r'\.[a-z]+$', '', path)

            key = key or "misc"
            # If the key is just "mod" or "lib" prefix with parent
            if key in ("mod", "lib", "main", "test"):
                if "/src/" in path:
                    before_src = path.partition("/src/")[0]
                    parent = re.sub(r'-\d[\d.]*$', '',
                                    before_src.rsplit("/", 1)[-1]).replace("-", "_")
                    key = f"{parent}::{key}"

            confidence = 0.9 if path in sym_data.get("dwarf_source_files", []) else 0.6
            if key not in modules:
                modules[key] = self._empty_module(
                    name=key,
                    source_path=path,
                    language=language,
                    confidence=confidence,
                )
            elif confidence > modules[key]["confidence"]:
                modules[key]["source_path"] = path
                modules[key]["confidence"]  = confidence

        # ── Step 2: assign demangled symbols to modules ───────────────
        for sym in sym_data.get("demangled", []):
            mod_key = self._infer_module_for_symbol(sym, language)
            if mod_key not in modules:
                modules[mod_key] = self._empty_module(
                    name=mod_key, language=language, confidence=0.5
                )
            modules[mod_key]["symbols"].append(sym)

        # ── Step 3: cluster strings into modules ──────────────────────
        for s in str_data.get("strings", []):
            mod_key = self._infer_module_for_string(s, modules)
            if mod_key not in modules:
                modules[mod_key] = self._empty_module(
                    name=mod_key, language=language, confidence=0.3
                )
            modules[mod_key]["strings"].append(s)

        # ── Step 4: assign call-graph hub functions to modules ────────
        for func in cg_data.get("hub_functions", []):
            mod_key = self._infer_module_for_symbol(func, language)
            if mod_key not in modules:
                modules[mod_key] = self._empty_module(
                    name=mod_key, language=language, confidence=0.4
                )
            modules[mod_key].setdefault("hub_functions", []).append(func)

        # ── Step 5: add data patterns to the most relevant module ─────
        error_msgs = data_pat.get("error_messages", [])
        urls        = data_pat.get("urls", [])
        paths       = data_pat.get("paths", [])
        if modules:
            main_mod = max(modules.values(),
                           key=lambda m: len(m.get("symbols", [])))
            main_mod.setdefault("data_patterns", {}).update({
                "error_messages": error_msgs[:10],
                "urls": urls[:10],
                "paths": paths[:10],
            })

        # ── Step 6: ensure there's always a root / main module ────────
        if not modules:
            binary_name = Path(self._scan.get("binary", "unknown")).stem
            modules[binary_name] = self._empty_module(
                name=binary_name, language=language, confidence=0.2
            )

        result = sorted(modules.values(),
                        key=lambda m: -len(m.get("symbols", [])))
        print(f"  🗺  Unwrapped {len(result)} logical modules "
              f"from {len(sym_data.get('demangled', []))} symbols")
        return result

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _empty_module(
        name: str,
        language: str = "unknown",
        source_path: Optional[str] = None,
        confidence: float = 0.5,
    ) -> Dict[str, Any]:
        return {
            "name":        name,
            "language":    language,
            "source_path": source_path,
            "confidence":  confidence,
            "symbols":     [],
            "strings":     [],
            "hub_functions": [],
            "data_patterns": {},
        }

    @staticmethod
    def _infer_module_for_symbol(sym: str, language: str) -> str:
        """
        Guess which module a symbol belongs to by parsing its prefix.
        Handles Rust (<crate>::<mod>), C++ (Foo::bar), Go (pkg.Func), C (prefix_).
        """
        # Rust: core::fmt::write → "core::fmt"
        if "::" in sym:
            parts = sym.split("::")
            # Take up to the first two segments as module key
            return "::".join(parts[:2]).split("<")[0].strip("_").lower() or "misc"

        # C++ class method: std::vector<int>::push_back → "std"
        if "." in sym and not sym.startswith("."):
            return sym.split(".")[0].lower() or "misc"

        # C / assembly: prefix_ → "prefix"
        if "_" in sym:
            return sym.split("_")[0].lower() or "misc"

        return sym[:12].lower() or "misc"

    @staticmethod
    def _infer_module_for_string(s: str, modules: Dict) -> str:
        """Try to assign a string to an existing module by keyword matching."""
        lower = s.lower()
        for key in modules:
            if key.lower() in lower:
                return key
        # Generic categorisation
        if any(w in lower for w in ("error", "failed", "panic", "fatal")):
            return "error_handling"
        if any(w in lower for w in ("http", "https", "url", "request", "response")):
            return "network"
        if any(w in lower for w in ("file", "path", "read", "write", "open")):
            return "io"
        if any(w in lower for w in ("config", "setting", "option", "default")):
            return "config"
        return "misc"


# ===========================================================================
# AIPatternMatcher  — read the ink (generate source fragments)
# ===========================================================================

class AIPatternMatcher:
    """
    Matches binary patterns to known language idioms and generates
    plausible source code fragments with confidence scores.

    Analogy: the ML "ink detection" and text-recognition step in the
    Herculaneum scroll pipeline — reading the barely-visible ink traces
    on the CT scan slices.

    The matcher uses two strategies:
    1. **Deterministic patterns** — rules derived from known binary patterns
       (e.g. a function named ``tokio::runtime::Builder::new`` is
       unambiguously a Rust async runtime builder).  High confidence.
    2. **Heuristic synthesis** — for unknown symbols, uses the symbol name,
       surrounding strings, and call relationships to synthesise a plausible
       function stub.  Medium/low confidence, clearly annotated.

    Optionally uses THE FORGE Kimi K2 model (if available) for step 2.
    """

    # Rust standard library patterns → stub templates
    _RUST_STUBS: Dict[str, str] = {
        "tokio::runtime":
            "pub mod runtime {\n    pub fn run() { /* async runtime */ }\n}",
        "std::collections::HashMap":
            "use std::collections::HashMap;\ntype Map<K, V> = HashMap<K, V>;",
        "serde::":
            "#[derive(Serialize, Deserialize)]\npub struct Placeholder {}",
        "log::":
            "use log::{debug, info, warn, error};\n// logging facade",
        "clap::":
            "use clap::Parser;\n#[derive(Parser)]\npub struct Args {}",
    }

    # C standard library patterns
    _C_STUBS: Dict[str, str] = {
        "malloc":  "void *malloc(size_t size);",
        "free":    "void free(void *ptr);",
        "printf":  "int printf(const char *fmt, ...);",
        "pthread": "// POSIX threads\n#include <pthread.h>",
    }

    # Go standard library patterns
    _GO_STUBS: Dict[str, str] = {
        "fmt.":     'import "fmt"\n// fmt package functions',
        "net/http": 'import "net/http"\n// HTTP client/server',
        "os.":      'import "os"\n// OS operations',
    }

    def __init__(self, modules: List[Dict[str, Any]]):
        self._modules = modules

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def match(self) -> List[ScrollFragment]:
        """
        Generate ScrollFragment objects for every inferred module.

        Returns fragments sorted by confidence (highest first).
        """
        fragments: List[ScrollFragment] = []
        for mod in self._modules:
            # One fragment per module (the module-level stub)
            mod_frag = self._synthesise_module(mod)
            fragments.append(mod_frag)

            # Individual function fragments for the top symbols
            for sym in mod.get("symbols", [])[:20]:
                frag = self._synthesise_symbol(sym, mod)
                if frag:
                    fragments.append(frag)

        # Sort: high confidence first, then by module name
        fragments.sort(key=lambda f: (-f.confidence_score, f.module))

        total = len(fragments)
        high  = sum(1 for f in fragments if f.confidence_score >= 0.85)
        med   = sum(1 for f in fragments if 0.50 <= f.confidence_score < 0.85)
        print(f"  🧩 Pattern matching: {total} fragments "
              f"({high} high, {med} medium confidence)")

        return fragments

    # ------------------------------------------------------------------
    # Synthesis helpers
    # ------------------------------------------------------------------

    def _synthesise_module(self, mod: Dict) -> ScrollFragment:
        """Generate a module-level fragment."""
        name     = mod["name"]
        lang     = mod.get("language", "unknown")
        src_path = mod.get("source_path")
        conf     = mod.get("confidence", 0.4)
        evidence = []
        layers   = []

        # Pick reconstruction based on language
        if src_path:
            evidence.append(f"DWARF source path: {src_path}")
            layers.append("dwarf")
            reconstructed = self._module_stub(name, lang, src_path)
            conf = max(conf, 0.85)
        else:
            reconstructed = self._module_stub(name, lang, None)
            layers.append("symbols")

        # Check for known library patterns
        for pattern, stub in {**self._RUST_STUBS,
                               **self._C_STUBS,
                               **self._GO_STUBS}.items():
            if name.lower().startswith(pattern.lower().rstrip(":")):
                reconstructed = stub
                conf = 0.92
                evidence.append(f"Matched library pattern: {pattern}")
                layers.append("pattern_db")
                break

        syms = mod.get("symbols", [])
        if syms:
            evidence.append(f"Contains {len(syms)} symbols: "
                            + ", ".join(syms[:5]))

        strs = mod.get("strings", [])
        if strs:
            evidence.append(f"{len(strs)} associated string literals")
            layers.append("strings")

        return ScrollFragment(
            fragment_id    = f"{name}/__module__",
            module         = name,
            name           = name,
            source_type    = "module",
            language       = lang,
            reconstructed  = reconstructed,
            raw_evidence   = evidence,
            confidence_score = min(conf, 1.0),
            evidence_layers  = layers,
        )

    def _synthesise_symbol(
        self, sym: str, mod: Dict
    ) -> Optional[ScrollFragment]:
        """Generate a function/struct fragment for a single symbol."""
        lang = mod.get("language", "unknown")
        name = mod["name"]
        conf = 0.35   # default: heuristic only

        # Clean up version suffixes and template params
        clean_sym = re.sub(r'@\w+', '', sym).split("<")[0].strip()
        if not clean_sym or len(clean_sym) < 2:
            return None

        # Determine source type
        src_type = "function"
        lower    = clean_sym.lower()
        if any(w in lower for w in ("struct", "class", "Trait", "Interface",
                                     "Type", "Builder")):
            src_type = "struct"
        elif any(w in lower for w in ("const", "CONST", "static", "STATIC")):
            src_type = "const"

        # Build the reconstruction
        reconstructed, conf = self._reconstruct_symbol(clean_sym, lang, src_type)
        evidence = [f"Symbol: {sym}"]
        layers   = ["symbols"]

        return ScrollFragment(
            fragment_id    = f"{name}/{clean_sym[:64]}",
            module         = name,
            name           = clean_sym,
            source_type    = src_type,
            language       = lang,
            reconstructed  = reconstructed,
            raw_evidence   = evidence,
            confidence_score = conf,
            evidence_layers  = layers,
        )

    def _reconstruct_symbol(
        self, sym: str, lang: str, src_type: str
    ) -> Tuple[str, float]:
        """Generate source text for a symbol. Returns (text, confidence)."""
        # Check pattern database first
        for pattern, stub in {**self._RUST_STUBS,
                               **self._C_STUBS,
                               **self._GO_STUBS}.items():
            if sym.startswith(pattern.rstrip(":")):
                return stub, 0.90

        # Language-specific heuristic stubs
        if lang in ("rust", "c++"):
            return self._rust_cpp_stub(sym, src_type), 0.35
        if lang == "go":
            return self._go_stub(sym, src_type), 0.35
        # C / unknown
        return self._c_stub(sym, src_type), 0.30

    @staticmethod
    def _module_stub(name: str, lang: str,
                     src_path: Optional[str]) -> str:
        comment = (
            f"// Reconstructed from: {src_path}"
            if src_path
            else f"// Module: {name}  (inferred from binary analysis)"
        )
        if lang == "rust":
            return (f"//! {comment}\n\n"
                    f"pub mod {re.sub(r'[^a-z0-9_]', '_', name.lower())} {{\n"
                    f"    // TODO: reconstructed module\n}}")
        if lang == "go":
            pkg = re.sub(r'[^a-z0-9]', '', name.lower()) or "main"
            return f"// {comment}\npackage {pkg}\n"
        if lang in ("c", "c++"):
            guard = name.upper().replace("::", "_").replace("/", "_")
            return (f"/* {comment} */\n"
                    f"#ifndef {guard}_H\n"
                    f"#define {guard}_H\n\n"
                    f"/* TODO: reconstructed header */\n\n"
                    f"#endif /* {guard}_H */\n")
        return f"# {comment}\n# Module: {name}\n"

    @staticmethod
    def _rust_cpp_stub(sym: str, src_type: str) -> str:
        # Extract last segment as the function/struct name
        parts = sym.split("::")
        short = parts[-1] if parts else sym
        if src_type == "struct":
            return f"pub struct {short} {{\n    // TODO\n}}"
        if src_type == "const":
            return f"pub const {short.upper()}: () = ();"
        # function
        args = ""
        ret  = ""
        if "new" in short.lower():
            ret = " -> Self"
        return f"pub fn {short}({args}){ret} {{\n    // TODO\n}}"

    @staticmethod
    def _go_stub(sym: str, src_type: str) -> str:
        parts = sym.split(".")
        short = parts[-1] if parts else sym
        if src_type == "struct":
            return f"type {short} struct {{\n\t// TODO\n}}"
        return f"func {short}() {{\n\t// TODO\n}}"

    @staticmethod
    def _c_stub(sym: str, src_type: str) -> str:
        short = sym.split("_")[-1] if "_" in sym else sym
        if src_type == "const":
            return f"#define {sym.upper()} 0  /* TODO */"
        return f"/* {sym} */\nvoid {short}(void) {{\n    /* TODO */\n}}"


# ===========================================================================
# ScrollAssembler  — write the final reconstruction
# ===========================================================================

class ScrollAssembler:
    """
    Assembles the reconstructed ScrollFragments into a directory of
    annotated source files with a scroll-map index.

    Analogous to how scroll reconstruction scholars assemble the
    confirmed column readings into a final edition, with confidence
    annotations and scholarly notes.

    Output structure:
      <output_dir>/
        scroll_map.json          — fragment index with confidence scores
        RECONSTRUCTION_NOTES.md  — human-readable reconstruction guide
        high_confidence/         — fragments with confidence ≥ 0.85
          <module>.<ext>
        medium_confidence/       — 0.50 – 0.85
          <module>.<ext>
        low_confidence/          — < 0.50
          <module>.<ext>
    """

    def __init__(
        self,
        elf_path: Optional[str] = None,
        fragments: Optional[List[ScrollFragment]] = None,
        scan: Optional[Dict[str, Any]] = None,
        modules: Optional[List[Dict[str, Any]]] = None,
    ):
        self._elf_path  = Path(elf_path).resolve() if elf_path else None
        self._fragments = fragments or []
        self._scan      = scan or {}
        self._modules   = modules or []

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def from_fragments(
        cls,
        fragments: List[ScrollFragment],
        scan: Optional[Dict] = None,
        modules: Optional[List[Dict]] = None,
    ) -> "ScrollAssembler":
        return cls(fragments=fragments, scan=scan or {}, modules=modules or [])

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def reconstruct(self, output_dir: str = "reconstructed") -> Dict[str, Any]:
        """
        Full pipeline: scan → unwrap → match → write.

        If *elf_path* was provided, runs the full BinaryXRay → VirtualUnwrapper
        → AIPatternMatcher pipeline first.
        """
        if self._elf_path and not self._fragments:
            print(f"🔬 Running full reconstruction pipeline on: "
                  f"{self._elf_path.name}")
            self._scan    = BinaryXRay(str(self._elf_path)).scan()
            self._modules = VirtualUnwrapper(self._scan).unwrap()
            self._fragments = AIPatternMatcher(self._modules).match()

        return self.write(output_dir)

    def write(self, output_dir: str = "reconstructed") -> Dict[str, Any]:
        """Write all fragments to *output_dir*."""
        if not self._fragments:
            raise ValueError("No fragments to write — call reconstruct() first "
                             "or provide fragments via from_fragments().")

        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)

        high_dir = out / "high_confidence"
        med_dir  = out / "medium_confidence"
        low_dir  = out / "low_confidence"
        for d in (high_dir, med_dir, low_dir):
            d.mkdir(exist_ok=True)

        created: List[str] = []
        scroll_map: List[Dict] = []

        # Group fragments by module and confidence tier
        by_module: Dict[str, List[ScrollFragment]] = {}
        for frag in self._fragments:
            by_module.setdefault(frag.module, []).append(frag)

        for module_name, frags in sorted(by_module.items()):
            # Use the highest-confidence fragment to determine the tier
            best = max(frags, key=lambda f: f.confidence_score)
            tier_dir = (
                high_dir if best.confidence_score >= 0.85
                else med_dir if best.confidence_score >= 0.50
                else low_dir
            )
            ext   = self._ext_for_language(best.language)
            fname = self._safe_filename(module_name, ext)
            fpath = tier_dir / fname

            content = self._render_module_file(module_name, frags)
            fpath.write_text(content, encoding="utf-8")
            created.append(str(fpath))

            # Scroll map entry
            scroll_map.append({
                "module":    module_name,
                "file":      str(fpath.relative_to(out)),
                "tier":      best.confidence_label,
                "confidence": round(best.confidence_score, 3),
                "fragments": len(frags),
                "language":  best.language,
                "evidence_layers": sorted(set(
                    layer
                    for f in frags
                    for layer in f.evidence_layers
                )),
            })

        # Write scroll map
        map_path = out / "scroll_map.json"
        with open(map_path, "w", encoding="utf-8") as fh:
            json.dump(scroll_map, fh, indent=2, ensure_ascii=False)
        created.append(str(map_path))

        # Write reconstruction notes
        notes_path = self._write_notes(out, scroll_map)
        created.append(notes_path)

        # Summary
        high_count = sum(1 for e in scroll_map if e["tier"] == "high")
        med_count  = sum(1 for e in scroll_map if e["tier"] == "medium")
        low_count  = sum(1 for e in scroll_map
                         if e["tier"] in ("low", "very-low"))

        print(f"\n📜 Reconstruction complete:")
        print(f"   {len(scroll_map)} modules → {len(created)} files")
        print(f"   Confidence: {high_count} high / {med_count} medium / "
              f"{low_count} low")
        print(f"   Scroll map: {map_path}")
        print(f"   Notes:      {notes_path}")

        return {
            "output_dir":    str(out),
            "module_count":  len(scroll_map),
            "fragment_count": len(self._fragments),
            "files_written": created,
            "scroll_map":    scroll_map,
            "confidence_summary": {
                "high":   high_count,
                "medium": med_count,
                "low":    low_count,
            },
        }

    # ------------------------------------------------------------------
    # Rendering helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _ext_for_language(lang: str) -> str:
        return {
            "rust": ".rs", "go": ".go", "c": ".c",
            "c++": ".cpp", "python": ".py",
        }.get(lang, ".txt")

    @staticmethod
    def _safe_filename(module_name: str, ext: str, max_stem: int = 60) -> str:
        """
        Convert *module_name* into a safe filename ≤ 255 bytes.

        Replaces non-alphanumeric characters with underscores, truncates the
        stem to *max_stem* characters, then appends a short hash so that two
        different modules that share the same truncated prefix get unique names.
        """
        safe = re.sub(r'[^a-zA-Z0-9._-]', '_', module_name)
        safe = re.sub(r'_+', '_', safe).strip('_')
        if len(safe) > max_stem:
            h = hashlib.md5(module_name.encode()).hexdigest()[:8]
            safe = safe[:max_stem] + "_" + h
        return (safe or "module") + ext

    @staticmethod
    def _render_module_file(
        module_name: str, frags: List[ScrollFragment]
    ) -> str:
        """Render all fragments for a module into a single source file."""
        best = max(frags, key=lambda f: f.confidence_score)
        lang = best.language
        conf = best.confidence_score

        # File header
        header = _FORGE_HEADER.format(
            module=module_name,
            confidence=f"{conf:.0%}",
            confidence_label=best.confidence_label,
            language=lang,
            fragment_count=len(frags),
            evidence=", ".join(sorted(set(
                layer for f in frags for layer in f.evidence_layers
            ))),
        )

        sections: List[str] = [header]
        for frag in sorted(frags, key=lambda f: -f.confidence_score):
            if frag.source_type == "module":
                sections.insert(1, frag.reconstructed)
                continue
            comment_char = "//" if lang in ("rust", "go", "c", "c++") else "#"
            block = (
                f"\n{comment_char} ── {frag.source_type}: {frag.name} "
                f"[confidence: {frag.confidence_score:.0%}]\n"
            )
            for ev in frag.raw_evidence:
                block += f"{comment_char}   evidence: {ev}\n"
            block += frag.reconstructed + "\n"
            sections.append(block)

        return "\n".join(sections)

    def _write_notes(
        self, out: Path, scroll_map: List[Dict]
    ) -> str:
        binary_name = (
            self._elf_path.name if self._elf_path else "unknown binary"
        )
        high  = [e for e in scroll_map if e["tier"] == "high"]
        med   = [e for e in scroll_map if e["tier"] == "medium"]
        low   = [e for e in scroll_map
                 if e["tier"] in ("low", "very-low")]

        lang_counts: Dict[str, int] = {}
        for e in scroll_map:
            lang_counts[e["language"]] = lang_counts.get(e["language"], 0) + 1
        dominant_lang = max(lang_counts, key=lang_counts.get) if lang_counts else "unknown"  # type: ignore[arg-type]

        lines = [
            "# Binary Reconstruction Notes",
            "",
            "Generated by **THE FORGE AI Reconstructor**",
            "Inspired by the Herculaneum Scroll reconstruction technique.",
            "",
            "## The Scroll Analogy",
            "",
            "Just as the Vesuvius Challenge reconstructed ancient carbonised papyrus",
            "scrolls using CT scanning → virtual unwrapping → AI ink detection,",
            "this tool reconstructs source code from compiled ELF binaries using:",
            "",
            "| Scroll step         | Binary equivalent                           |",
            "|---------------------|---------------------------------------------|",
            "| CT scan             | BinaryXRay (6-layer structural scan)        |",
            "| Virtual unwrapping  | VirtualUnwrapper (module grouping)          |",
            "| Ink detection       | AIPatternMatcher (symbol/string patterns)   |",
            "| Text recognition    | Source stub synthesis                       |",
            "| Scholar assembly    | ScrollAssembler (confidence-annotated output)|",
            "",
            "## Binary Analysed",
            "",
            f"- **File**: `{binary_name}`",
            f"- **Dominant language**: {dominant_lang}",
            f"- **Modules inferred**: {len(scroll_map)}",
            "",
            "## Confidence Tiers",
            "",
            "### High confidence (≥ 85%)",
            "Derived from DWARF debug information or known library pattern matching.",
            "These reconstructions are likely structurally correct.",
            "",
        ]
        for e in high[:10]:
            lines.append(f"- `{e['file']}` — {e['module']} "
                         f"({e['confidence']:.0%}, {e['fragments']} fragments)")

        lines += [
            "",
            "### Medium confidence (50–85%)",
            "Derived from symbol demangling and string analysis.",
            "Structure is plausible but may have incorrect signatures or types.",
            "",
        ]
        for e in med[:10]:
            lines.append(f"- `{e['file']}` — {e['module']} "
                         f"({e['confidence']:.0%})")

        lines += [
            "",
            "### Low confidence (< 50%)",
            "Heuristic stubs only.  Treat as scaffolding, not as real source.",
            "",
        ]
        for e in low[:5]:
            lines.append(f"- `{e['file']}` — {e['module']}")

        lines += [
            "",
            "## How to improve the reconstruction",
            "",
            "1. **Install debuginfo** — `dnf install <package>-debuginfo` adds",
            "   DWARF sections which raise all confidence scores dramatically.",
            "",
            "2. **Find the source RPM** — the companion `.src.rpm` contains the",
            "   original source.  Use `rpm_ripper.py --find-source` to locate it.",
            "",
            "3. **Check GitHub** — search for the binary name on GitHub.  Many",
            "   projects publish the full source matching the installed binary.",
            "",
            "4. **Ghidra decompilation** — run `rpm_ripper.py --decompile --ghidra`",
            "   for higher-fidelity function body reconstruction.",
            "",
            "5. **Warp terminal** — Warp's source is not public, but the Rust",
            "   symbol names and DWARF paths reveal the crate structure.",
            "",
            "## Legal note",
            "",
            "Reconstructed source is for study and interoperability only.",
            "Do not redistribute without verifying licensing of the original.",
            "",
            "---",
            "*Generated by THE FORGE ai_reconstructor.py*",
        ]

        path = out / "RECONSTRUCTION_NOTES.md"
        path.write_text("\n".join(lines), encoding="utf-8")
        return str(path)


# ---------------------------------------------------------------------------
# Module-level templates
# ---------------------------------------------------------------------------

_FORGE_HEADER = textwrap.dedent("""\
    {comment_open}
    THE FORGE — AI Binary Reconstructor
    Module:     {module}
    Confidence: {confidence} ({confidence_label})
    Language:   {language}
    Fragments:  {fragment_count}
    Evidence:   {evidence}
    {comment_close}
""").format_map(
    {
        "comment_open":  "/*",
        "comment_close": "*/",
        "module":        "{module}",
        "confidence":    "{confidence}",
        "confidence_label": "{confidence_label}",
        "language":      "{language}",
        "fragment_count": "{fragment_count}",
        "evidence":      "{evidence}",
    }
)


# ===========================================================================
# Convenience entry point: reconstruct from a rip report or directory
# ===========================================================================

def reconstruct_from_report(
    report_path: str,
    output_dir: str = "reconstructed",
) -> Dict[str, Any]:
    """
    Run the full reconstruction pipeline starting from an
    ``analysis_report.json`` produced by RpmRipper or DebRipper.

    Processes every ELF found in the report.
    """
    report_file = Path(report_path)
    if report_file.is_dir():
        # Try to find analysis_report.json inside the directory
        candidate = report_file / "analysis_report.json"
        if candidate.exists():
            report_file = candidate
        else:
            raise FileNotFoundError(
                f"No analysis_report.json found in {report_path}"
            )

    with open(report_file, encoding="utf-8") as fh:
        report = json.load(fh)

    elf_files = report.get("elf_files", [])
    if not elf_files:
        raise ValueError(f"No ELF files listed in report: {report_file}")

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    results = []
    for ef in elf_files:
        if "error" in ef:
            continue
        elf_path = ef.get("path") or ef.get("safe_header", {}).get("path", "")
        if not elf_path or not Path(elf_path).exists():
            continue

        print(f"\n{'=' * 60}")
        print(f"📜 Reconstructing: {Path(elf_path).name}")
        print(f"{'=' * 60}")

        elf_out = out / Path(elf_path).name
        try:
            result = ScrollAssembler(elf_path=elf_path).reconstruct(
                output_dir=str(elf_out)
            )
            results.append(result)
        except Exception as exc:
            print(f"  ⚠️  Failed: {exc}")
            results.append({"elf": elf_path, "error": str(exc)})

    summary = {
        "source_report": str(report_file),
        "output_dir":    str(out),
        "elf_count":     len(results),
        "results":       results,
    }
    summary_path = out / "reconstruction_summary.json"
    with open(summary_path, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, ensure_ascii=False)
    print(f"\n📊 Full summary → {summary_path}")
    return summary


# ===========================================================================
# CLI
# ===========================================================================

class AIReconstructorCLI:
    """
    Command-line interface for THE FORGE AI Reconstructor.

    Ties together BinaryXRay, VirtualUnwrapper, AIPatternMatcher,
    and ScrollAssembler into a single coherent pipeline.
    """

    def run(self, argv: Optional[List[str]] = None) -> int:
        parser = argparse.ArgumentParser(
            prog="ai_reconstructor",
            description=(
                "🔬 THE FORGE — AI Binary Reconstructor\n\n"
                "Like the Herculaneum scroll reconstruction: X-ray a binary,\n"
                "virtually unwrap it, and use AI to reconstruct the source."
            ),
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=(
                "examples:\n"
                "  # Fast X-ray scan (safe, read-only)\n"
                "  %(prog)s --xray /usr/bin/warp-terminal\n\n"
                "  # Show the unwrapped module map\n"
                "  %(prog)s --unwrap /usr/bin/warp-terminal\n\n"
                "  # Full reconstruction pipeline for a single ELF\n"
                "  %(prog)s --reconstruct /usr/bin/warp-terminal -o recon/\n\n"
                "  # Full pipeline from a package rip report or directory\n"
                "  %(prog)s --full analysis_report.json -o recon/\n"
                "  %(prog)s --full warp_ripped/ -o recon/\n"
            ),
        )

        action = parser.add_mutually_exclusive_group()
        action.add_argument(
            "--xray", metavar="ELF",
            help="Run a 6-layer X-ray scan on an ELF binary (read-only)",
        )
        action.add_argument(
            "--unwrap", metavar="ELF",
            help="X-ray + virtual unwrap: show the inferred module map",
        )
        action.add_argument(
            "--reconstruct", metavar="ELF",
            help="Full pipeline: X-ray → unwrap → pattern match → write source",
        )
        action.add_argument(
            "--full", metavar="REPORT_OR_DIR",
            help=(
                "Full pipeline from an analysis_report.json or ripped package "
                "directory (processes every ELF in the report)"
            ),
        )
        action.add_argument(
            "--deep", metavar="ELF",
            help=(
                "Progressive deep scan: runs all 6 CT-scanner depth levels "
                "with live progress (like adjusting the scroll scanner settings)"
            ),
        )
        action.add_argument(
            "--understand", metavar="ELF",
            help="Run DeepElfParser + ElfUnderstanding: purpose, algorithms, security",
        )

        parser.add_argument(
            "--scan-depth", metavar="N", type=int, default=5,
            choices=range(1, 7),
            help=(
                "Depth for --deep scan (1–6, default 5). "
                "1=header, 2=skeleton, 3=symbols, 4=deep-structure, "
                "5=understanding, 6=full-reconstruction"
            ),
        )
        parser.add_argument(
            "-o", "--output-dir", default="ai_reconstructor_out",
            help="Output directory (default: ai_reconstructor_out/)",
        )
        parser.add_argument(
            "--json", action="store_true", default=False,
            help="Output results as JSON to stdout",
        )

        args = parser.parse_args(argv)

        if args.xray:
            return self._run_xray(args.xray, args.json)
        if args.unwrap:
            return self._run_unwrap(args.unwrap, args.json)
        if args.reconstruct:
            return self._run_reconstruct(args.reconstruct,
                                          args.output_dir, args.json)
        if args.full:
            return self._run_full(args.full, args.output_dir, args.json)
        if args.deep:
            return self._run_deep(args.deep, args.scan_depth, args.json)
        if args.understand:
            return self._run_understand(args.understand, args.json)

        parser.print_help()
        return 1

    # ------------------------------------------------------------------

    def _run_xray(self, elf_path: str, as_json: bool) -> int:
        if not as_json:
            print("=" * 64)
            print("🔥 THE FORGE — Binary X-Ray Scanner")
            print("=" * 64)
        try:
            scan = BinaryXRay(elf_path).scan()
        except (FileNotFoundError, ValueError) as exc:
            print(f"❌ {exc}", file=sys.stderr)
            return 1
        if as_json:
            print(json.dumps(scan, indent=2))
        else:
            self._print_xray(scan)
        return 0

    def _run_unwrap(self, elf_path: str, as_json: bool) -> int:
        if not as_json:
            print("=" * 64)
            print("🔥 THE FORGE — Virtual Unwrapper")
            print("=" * 64)
        try:
            scan    = BinaryXRay(elf_path).scan()
            modules = VirtualUnwrapper(scan).unwrap()
        except (FileNotFoundError, ValueError) as exc:
            print(f"❌ {exc}", file=sys.stderr)
            return 1
        if as_json:
            print(json.dumps(modules, indent=2))
        else:
            self._print_modules(modules)
        return 0

    def _run_reconstruct(
        self, elf_path: str, output_dir: str, as_json: bool
    ) -> int:
        if not as_json:
            print("=" * 64)
            print("🔥 THE FORGE — AI Source Reconstructor")
            print("=" * 64)
        try:
            result = ScrollAssembler(elf_path=elf_path).reconstruct(output_dir)
        except (FileNotFoundError, ValueError) as exc:
            print(f"❌ {exc}", file=sys.stderr)
            return 1
        if as_json:
            print(json.dumps(result, indent=2))
        else:
            self._print_reconstruction(result)
        return 0

    def _run_deep(
        self, elf_path: str, depth: int, as_json: bool
    ) -> int:
        """Progressive CT-scanner style deep scan."""
        if not as_json:
            print("=" * 64)
            print(f"🔥 THE FORGE — Progressive Deep Scan (depth {depth}/6)")
            print("=" * 64)
        try:
            scanner = ProgressiveScan(elf_path)
        except (FileNotFoundError, ValueError) as exc:
            print(f"❌ {exc}", file=sys.stderr)
            return 1

        combined: Dict[str, Any] = {"binary": elf_path}
        for update in scanner.scan(max_depth=depth):
            if as_json:
                combined.update(update.get("data", {}))
            else:
                d = update["depth"]
                label = update["label"]
                prog  = update["progress"]
                summ  = update["summary"]
                bar   = "█" * int(prog * 20) + "░" * (20 - int(prog * 20))
                print(f"\n  [{bar}] Depth {d}/6 — {label}")
                print(f"  └─ {summ}")

        if as_json:
            print(json.dumps(combined, indent=2, default=str))
        else:
            print(f"\n  ✅ Deep scan complete (depth {depth}/6)")
        return 0

    def _run_understand(self, elf_path: str, as_json: bool) -> int:
        """Semantic understanding layer."""
        if not as_json:
            print("=" * 64)
            print("🔥 THE FORGE — ELF Understanding")
            print("=" * 64)
        try:
            parse = DeepElfParser(elf_path).parse()
            understanding = ElfUnderstanding(parse).understand()
        except (FileNotFoundError, ValueError) as exc:
            print(f"❌ {exc}", file=sys.stderr)
            return 1
        if as_json:
            print(json.dumps(understanding, indent=2, default=str))
        else:
            self._print_understanding(understanding)
        return 0

    def _run_full(
        self, report_or_dir: str, output_dir: str, as_json: bool
    ) -> int:
        if not as_json:
            print("=" * 64)
            print("🔥 THE FORGE — Full Report Reconstruction")
            print("=" * 64)

        # If it's a single ELF, delegate to --reconstruct
        p = Path(report_or_dir)
        if p.is_file() and p.suffix != ".json":
            try:
                with open(str(p), "rb") as fh:
                    is_elf = fh.read(4) == ELF_MAGIC
            except OSError:
                is_elf = False
            if is_elf:
                return self._run_reconstruct(report_or_dir, output_dir, as_json)

        try:
            result = reconstruct_from_report(report_or_dir, output_dir)
        except (FileNotFoundError, ValueError) as exc:
            print(f"❌ {exc}", file=sys.stderr)
            return 1
        if as_json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\n✅ Reconstructed {result['elf_count']} ELF(s) → {output_dir}/")
        return 0

    # ------------------------------------------------------------------
    # Printers
    # ------------------------------------------------------------------

    @staticmethod
    def _print_xray(scan: Dict) -> None:
        layers = scan.get("layers", {})
        skel   = layers.get("skeleton", {})
        syms   = layers.get("symbols", {})
        strs   = layers.get("strings", {})
        cg     = layers.get("callgraph", {})
        build  = layers.get("build", {})

        print(f"\n  Binary    : {scan.get('binary')}")
        print(f"  Size      : {scan.get('size_bytes', 0):,} bytes")
        print(f"  SHA-256   : {scan.get('sha256', '')[:16]}…")
        print(f"\n  ── Layer 1: Structural skeleton")
        print(f"     Sections  : {skel.get('section_count', 0)}")
        print(f"     Has DWARF : {skel.get('has_debug', False)}")
        print(f"     Has symtab: {skel.get('has_symtab', False)}")
        print(f"\n  ── Layer 2: Symbols + DWARF")
        print(f"     Total syms  : {syms.get('total', 0)}")
        print(f"     Demangled   : {syms.get('demangled_count', 0)}")
        print(f"     Language    : {syms.get('language', 'unknown')}")
        all_src = (syms.get("all_source_files") or
                   syms.get("dwarf_source_files", []) +
                   syms.get("string_source_files", []))
        print(f"     DWARF files : {len(syms.get('dwarf_source_files', []))}")
        print(f"     String paths: {len(syms.get('string_source_files', []))}")
        print(f"     Total paths : {len(all_src)}")
        print(f"\n  ── Layer 3: Strings")
        print(f"     Count  : {strs.get('count', 0)}")
        print(f"\n  ── Layer 4: Call graph")
        print(f"     Edges  : {cg.get('edge_count', 0)}")
        print(f"     Hubs   : {', '.join(cg.get('hub_functions', [])[:3])}")
        print(f"\n  ── Layer 6: Build fingerprint")
        print(f"     Compiler : {build.get('compiler', 'unknown')}")
        print(f"     Build ID : {build.get('build_id', 'none')}")
        print(f"     Version  : {build.get('version', 'unknown')}")

    @staticmethod
    def _print_modules(modules: List[Dict]) -> None:
        print(f"\n  {len(modules)} modules inferred:\n")
        for i, mod in enumerate(modules[:30], 1):
            conf  = mod.get("confidence", 0)
            syms  = len(mod.get("symbols", []))
            strs  = len(mod.get("strings", []))
            src   = mod.get("source_path", "")
            label = "✅" if conf >= 0.85 else "⚠️ " if conf >= 0.5 else "❓"
            print(f"  {label} {i:2d}. {mod['name'][:40]:<40} "
                  f"conf={conf:.0%}  syms={syms}  strs={strs}")
            if src:
                print(f"        source: {src}")

    @staticmethod
    def _print_understanding(u: Dict) -> None:
        sec = u.get("security", {})
        bt  = u.get("binary_type", {})
        ef  = u.get("execution_flow", {})
        print(f"\n  🧠 ELF Understanding:")
        print(f"\n  ── Purpose")
        print(f"     {u.get('purpose','?')}")
        print(f"\n  ── Binary type")
        print(f"     {bt.get('kind','?')}"
              + (" [PIE]"    if bt.get("is_pie")      else "")
              + (" [dynamic]" if bt.get("is_dynamic") else "")
              + (" [has main]" if bt.get("has_main")  else ""))
        print(f"\n  ── Algorithms detected")
        for a in u.get("algorithms", []) or ["(none detected)"]:
            print(f"     • {a}")
        print(f"\n  ── Libraries ({len(u.get('dso_deps', []))})")
        for d in u.get("dso_deps", []):
            print(f"     {d}")

        # Imported symbols — the most useful thing for understanding behaviour
        imports = u.get("imports", [])
        if imports:
            print(f"\n  ── Imported symbols ({u.get('import_count', len(imports))} total)")
            # Group by category for readability
            categories = {
                "🔒 crypto/auth":   [s for s in imports if any(x in s.lower() for x in
                    ("ssl", "tls", "crypto", "sha", "md5", "aes", "rsa", "hmac", "getrandom"))],
                "🔤 regex":        [s for s in imports if "pcre" in s.lower() or "regex" in s.lower()],
                "🧵 threads":      [s for s in imports if "pthread" in s.lower() or "thread" in s.lower()],
                "📁 file/IO":      [s for s in imports if any(x in s.lower() for x in
                    ("open", "read", "write", "fstat", "mmap", "getcwd", "realpath"))],
                "🌐 network":      [s for s in imports if any(x in s.lower() for x in
                    ("recv", "send", "socket", "connect", "bind", "accept"))],
                "⚙️  process":     [s for s in imports if any(x in s.lower() for x in
                    ("fork", "exec", "spawn", "wait", "kill", "signal"))],
                "🧠 memory":       [s for s in imports if any(x in s.lower() for x in
                    ("malloc", "free", "realloc", "alloc", "mmap", "mremap", "brk"))],
                "🛠 unwind/debug": [s for s in imports if "_Unwind_" in s or "backtrace" in s.lower()],
            }
            shown = set()
            for label, syms in categories.items():
                if syms:
                    unique = [s for s in syms if s not in shown][:6]
                    if unique:
                        print(f"     {label:<20} {', '.join(unique)}")
                        shown.update(unique)
            # Remaining uncategorised
            rest = [s for s in imports[:60] if s not in shown]
            if rest:
                print(f"     📦 other           "
                      + ", ".join(rest[:8])
                      + (f" … (+{len(rest)-8})" if len(rest) > 8 else ""))

        print(f"\n  ── Security hardening  grade={sec.get('hardening_grade','?')}")
        if sec.get("language_memory_safe"):
            lang = "Rust" if sec.get("is_rust") else "Go" if sec.get("is_go") else "safe language"
            print(f"     ℹ️  {lang} binary — memory safety guaranteed by the language")
        print(f"     Stack canary : "
              + ("✅" if sec.get("stack_canary")
                 else ("✅ (via language)" if sec.get("language_memory_safe") else "❌")))
        print(f"     FORTIFY_SRC  : "
              + ("✅" if sec.get("fortify_source")
                 else ("✅ (via language)" if sec.get("language_memory_safe") else "❌")))
        print(f"     PIE          : {'✅' if sec.get('pie')      else '❌'}")
        print(f"     RELRO        : {'✅' if sec.get('relro')    else '❌'}")
        print(f"     NX stack     : {'✅' if sec.get('nx_stack') else '❌'}")
        if sec.get("dangerous_funcs"):
            print(f"     ⚠️  Dangerous : {', '.join(sec['dangerous_funcs'])}")
        print(f"\n  ── Execution flow")
        print(f"     Load segments  : {ef.get('load_segment_count', 0)}")
        print(f"     Exec segments  : {ef.get('exec_segment_count', 0)}")
        print(f"     Thread-local   : {ef.get('has_thread_local', False)}")
        print(f"     Exception frs  : {ef.get('has_eh_frame', False)}")
        print(f"     dlopen         : {ef.get('uses_dlopen', False)}")
        print(f"     fork+exec      : {ef.get('uses_fork_exec', False)}")
        init = u.get("init_sequence", {})
        if init.get("steps"):
            print(f"\n  ── Init sequence")
            for step in init["steps"]:
                print(f"     {step}")

    @staticmethod
    def _print_reconstruction(result: Dict) -> None:
        print(f"\n  📜 Reconstruction summary:")
        print(f"     Output dir   : {result['output_dir']}")
        print(f"     Modules      : {result['module_count']}")
        print(f"     Fragments    : {result['fragment_count']}")
        cs = result.get("confidence_summary", {})
        print(f"     Confidence   : {cs.get('high', 0)} high / "
              f"{cs.get('medium', 0)} medium / {cs.get('low', 0)} low")
        print(f"\n  Files written:")
        for f in result.get("files_written", [])[:10]:
            print(f"     {f}")
        if len(result.get("files_written", [])) > 10:
            extra = len(result["files_written"]) - 10
            print(f"     … and {extra} more")


# ===========================================================================
# Entry point
# ===========================================================================

def main() -> None:
    sys.exit(AIReconstructorCLI().run())


if __name__ == "__main__":
    main()
