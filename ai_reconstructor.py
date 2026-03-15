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
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

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
