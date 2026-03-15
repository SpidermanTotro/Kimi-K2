"""
NullClaw Error Parser
=====================
Parses build / compiler error output for:
  • TypeScript / tsc    (file.ts:L:C - error TSXXXX: …)
  • esbuild             (file.ts:L:C: error: …)
  • Python              (File "f.py", line N / ErrorType: msg)
  • Rust / cargo        (error[EXXXX]: …  --> file.rs:L:C)
  • Go                  (./file.go:L:C: message)
  • C / C++ gcc/clang   (file.c:L:C: error: …)
  • npm / node          (npm ERR!  / Cannot find module)
  • Make                (make: *** [target] Error N)
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import List, Optional


# ---------------------------------------------------------------------------
# Data class
# ---------------------------------------------------------------------------

@dataclass
class BuildError:
    file_path: str
    line: int
    column: int
    code: Optional[str]
    message: str
    language: str = "unknown"
    raw_line: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    def __str__(self) -> str:
        loc = f"{self.file_path}:{self.line}:{self.column}"
        code = f" [{self.code}]" if self.code else ""
        return f"{loc}{code} — {self.message}"


# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------

# TypeScript tsc:  src/Foo.tsx:42:8 - error TS2304: Cannot find name 'x'.
_TS_RE = re.compile(
    r"^(?P<file>.+?\.(?:ts|tsx|js|jsx|mts|cts)):(?P<line>\d+):(?P<col>\d+)"
    r"\s+-\s+error\s+(?P<code>TS\d+)?:?\s*(?P<msg>.+)$"
)

# esbuild:  src/Foo.tsx:42:8: error: message
_ESBUILD_RE = re.compile(
    r"^(?P<file>.+?\.(?:ts|tsx|js|jsx|mts|cts)):(?P<line>\d+):(?P<col>\d+)"
    r":\s+error:\s+(?P<msg>.+)$"
)

# Rust:  error[E0425]: cannot find value `x` in this scope
#          --> src/main.rs:10:5
_RUST_HEADER_RE = re.compile(
    r"^error(?:\[(?P<code>E\d+)\])?:\s*(?P<msg>.+)$"
)
_RUST_LOC_RE = re.compile(
    r"^\s+-->\s+(?P<file>.+\.rs):(?P<line>\d+):(?P<col>\d+)"
)

# Python:  File "script.py", line 42, in <module>
#          NameError: name 'x' is not defined
_PY_FILE_RE = re.compile(
    r'^  File "(?P<file>[^"]+)", line (?P<line>\d+)'
)
_PY_ERR_RE = re.compile(
    r"^(?P<code>\w+Error|\w+Exception|SyntaxError|IndentationError"
    r"|ImportError|ModuleNotFoundError|AttributeError|TypeError"
    r"|ValueError|KeyError|NameError|RuntimeError|OSError|IOError"
    r"|FileNotFoundError|PermissionError|ZeroDivisionError"
    r"|StopIteration|AssertionError|NotImplementedError):\s*(?P<msg>.+)$"
)

# Go:  ./main.go:10:5: undefined: x
_GO_RE = re.compile(
    r"^(?P<file>.+?\.go):(?P<line>\d+):(?P<col>\d+):\s+(?P<msg>.+)$"
)

# C/C++ gcc/clang:  main.c:10:5: error: 'x' undeclared
_C_RE = re.compile(
    r"^(?P<file>.+?\.(?:c|cpp|cc|cxx|h|hpp)):(?P<line>\d+):(?P<col>\d+)"
    r":\s+error:\s+(?P<msg>.+)$"
)

# npm:  npm ERR!  code ENOENT
_NPM_ERR_RE = re.compile(r"^npm ERR!\s+(?P<msg>.+)$")

# Generic "Cannot find module"
_NODE_MODULE_RE = re.compile(
    r"(?P<msg>Cannot find module '(?P<mod>[^']+)')"
)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse_first_error(log_text: str) -> Optional[BuildError]:
    """Return the first parseable build error, or None."""
    errors = parse_all_errors(log_text, limit=1)
    return errors[0] if errors else None


def parse_all_errors(log_text: str, limit: int = 100) -> List[BuildError]:
    """Return up to *limit* build errors found in *log_text*."""
    errors: List[BuildError] = []
    lines = log_text.splitlines()
    i = 0
    pending_rust: Optional[dict] = None

    while i < len(lines) and len(errors) < limit:
        raw = lines[i]
        stripped = raw.strip()

        # ── Rust (two-line pattern) ────────────────────────────────
        m = _RUST_HEADER_RE.match(stripped)
        if m and not stripped.startswith("error: could not compile"):
            pending_rust = {"code": m.group("code"), "msg": m.group("msg")}
            i += 1
            continue

        if pending_rust is not None:
            m2 = _RUST_LOC_RE.match(raw)
            if m2:
                errors.append(BuildError(
                    file_path=m2.group("file"),
                    line=int(m2.group("line")),
                    column=int(m2.group("col")),
                    code=pending_rust["code"],
                    message=pending_rust["msg"],
                    language="rust",
                    raw_line=raw,
                ))
                pending_rust = None
                i += 1
                continue
            else:
                pending_rust = None   # next line wasn't a location

        # ── TypeScript ────────────────────────────────────────────
        m = _TS_RE.match(stripped)
        if m:
            errors.append(BuildError(
                file_path=m.group("file"),
                line=int(m.group("line")),
                column=int(m.group("col")),
                code=m.group("code"),
                message=m.group("msg").strip(),
                language="typescript",
                raw_line=raw,
            ))
            i += 1
            continue

        # ── esbuild ───────────────────────────────────────────────
        m = _ESBUILD_RE.match(stripped)
        if m:
            errors.append(BuildError(
                file_path=m.group("file"),
                line=int(m.group("line")),
                column=int(m.group("col")),
                code=None,
                message=m.group("msg").strip(),
                language="typescript",
                raw_line=raw,
            ))
            i += 1
            continue

        # ── Python (two-line pattern: File …  then ErrorType: …) ──
        m = _PY_FILE_RE.match(raw)
        if m:
            py_file = m.group("file")
            py_line = int(m.group("line"))
            # Look ahead for the error type
            for j in range(i + 1, min(i + 5, len(lines))):
                m2 = _PY_ERR_RE.match(lines[j].strip())
                if m2:
                    errors.append(BuildError(
                        file_path=py_file,
                        line=py_line,
                        column=1,
                        code=m2.group("code"),
                        message=m2.group("msg").strip(),
                        language="python",
                        raw_line=raw,
                    ))
                    i = j
                    break
            i += 1
            continue

        # ── Go ────────────────────────────────────────────────────
        m = _GO_RE.match(stripped)
        if m and not m.group("msg").startswith("note:"):
            errors.append(BuildError(
                file_path=m.group("file"),
                line=int(m.group("line")),
                column=int(m.group("col")),
                code=None,
                message=m.group("msg").strip(),
                language="go",
                raw_line=raw,
            ))
            i += 1
            continue

        # ── C / C++ ───────────────────────────────────────────────
        m = _C_RE.match(stripped)
        if m:
            errors.append(BuildError(
                file_path=m.group("file"),
                line=int(m.group("line")),
                column=int(m.group("col")),
                code=None,
                message=m.group("msg").strip(),
                language="c",
                raw_line=raw,
            ))
            i += 1
            continue

        # ── npm ───────────────────────────────────────────────────
        m = _NPM_ERR_RE.match(stripped)
        if m and not errors:   # only emit npm error if nothing else found yet
            errors.append(BuildError(
                file_path="package.json",
                line=1,
                column=1,
                code="npm",
                message=m.group("msg").strip(),
                language="javascript",
                raw_line=raw,
            ))
            i += 1
            continue

        i += 1

    return errors


def load_log_file(path) -> str:
    return Path(path).read_text(encoding="utf-8", errors="replace")
