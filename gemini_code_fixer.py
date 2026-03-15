#!/usr/bin/env python3
"""
THE FORGE — Gemini Program Fixer
==================================
Use the FREE Gemini CLI (google/generative-ai) to fix broken programs —
no paid subscription required.

This replaces paid tools (GitHub Copilot, ChatGPT Code Interpreter, etc.)
with Google Gemini's FREE tier for day-to-day code repair tasks.

Free tier limits (as of 2024/2025):
  • Gemini 1.5 Flash  — 15 req/min, 1 million tokens/day FREE
  • Gemini 1.5 Pro    — 2 req/min,  50 req/day FREE
  • Flash is more than enough for fixing programs.

Setup (one-time, free):
  1. Get a FREE API key at https://aistudio.google.com/apikey
  2. Export it:  export GEMINI_API_KEY="your-key-here"
      OR store it:  python3 gemini_code_fixer.py --save-key YOUR_KEY
  3. Run:  python3 gemini_code_fixer.py --fix broken_script.py
            python3 gemini_code_fixer.py --fix script.py --error "NameError: name 'foo'"

If the Gemini CLI / API is unavailable, falls back to built-in
pattern-based fixes for common Python, JavaScript, and shell errors.

Usage
─────
Library:
    from gemini_code_fixer import GeminiProgramFixer

    fixer = GeminiProgramFixer()
    result = fixer.fix_file("my_script.py", error_msg="SyntaxError: ...")
    print(result["fixed_code"])
    print(result["explanation"])

CLI:
    # Fix a file, print the diff + apply it
    python3 gemini_code_fixer.py --fix my_script.py

    # Pass the exact error message for more precise fixing
    python3 gemini_code_fixer.py --fix my_script.py \\
        --error "ImportError: No module named 'requests'"

    # Explain what a file does (free alternative to Copilot chat)
    python3 gemini_code_fixer.py --explain my_script.py

    # Review a file for bugs / security issues
    python3 gemini_code_fixer.py --review my_script.py

    # Save API key so you don't have to export it each time
    python3 gemini_code_fixer.py --save-key YOUR_GEMINI_API_KEY

    # Fix + auto-apply (writes fixed file as <name>.fixed.<ext>)
    python3 gemini_code_fixer.py --fix my_script.py --apply
"""

import argparse
import difflib
import json
import os
import re
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Key storage
# ---------------------------------------------------------------------------
_KEY_FILE = Path.home() / ".config" / "forge" / "gemini_api_key"


def _load_api_key() -> Optional[str]:
    """Return Gemini API key from env var or stored file."""
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if key:
        return key
    if _KEY_FILE.exists():
        key = _KEY_FILE.read_text().strip()
        if key:
            return key
    return None


def _save_api_key(key: str) -> None:
    _KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
    _KEY_FILE.write_text(key.strip())
    _KEY_FILE.chmod(0o600)
    print(f"✅ API key saved to {_KEY_FILE}")


# ---------------------------------------------------------------------------
# Gemini REST caller (no external SDK needed — just urllib)
# ---------------------------------------------------------------------------

def _call_gemini(
    prompt: str,
    api_key: str,
    model: str = "gemini-1.5-flash",
    max_tokens: int = 8192,
) -> str:
    """
    Call the Gemini REST API directly using only stdlib (no pip install needed).

    Falls back to the ``gemini`` CLI tool if the REST call fails.
    """
    import urllib.request
    import urllib.error

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": 0.2,
        },
    }).encode()

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
            return (
                data["candidates"][0]["content"]["parts"][0]["text"]
            )
    except (urllib.error.URLError, KeyError, IndexError, json.JSONDecodeError) as exc:
        # Try falling back to `gemini` CLI tool if installed
        return _call_gemini_cli(prompt) or f"[Gemini API error: {exc}]"


def _call_gemini_cli(prompt: str) -> str:
    """Try the `gemini` npm CLI tool as a fallback."""
    for cmd in ("gemini", "npx @google/generative-ai"):
        try:
            proc = subprocess.run(
                [cmd.split()[0]] + cmd.split()[1:] + [prompt[:2000]],
                capture_output=True, text=True, timeout=60,
            )
            if proc.returncode == 0 and proc.stdout.strip():
                return proc.stdout.strip()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    return ""


# ---------------------------------------------------------------------------
# Built-in pattern-based fallback fixer (no API needed)
# ---------------------------------------------------------------------------

_PATTERN_FIXES: List[Tuple[str, str, str]] = [
    # (error pattern, description, fix hint)
    (r"IndentationError",
     "Indentation error",
     "Check that all blocks use consistent spaces (4 spaces recommended). "
     "Never mix tabs and spaces."),
    (r"SyntaxError: invalid syntax",
     "Python syntax error",
     "Common causes: missing colon after if/for/def/class, unmatched brackets, "
     "or invalid use of Python 2 syntax in Python 3."),
    (r"ImportError|ModuleNotFoundError",
     "Missing module",
     "Run: pip3 install <module-name>  — or check for a typo in the import."),
    (r"NameError: name '(\w+)' is not defined",
     "Undefined variable",
     "The variable was used before assignment, or there is a typo in the name."),
    (r"AttributeError: '(\w+)' object has no attribute '(\w+)'",
     "Wrong attribute/method name",
     "Check the correct method name in the docs. "
     "Possible causes: typo, using wrong type, or calling deprecated API."),
    (r"TypeError: .+ argument",
     "Wrong argument type or count",
     "Check the function signature. You may be passing the wrong number of "
     "arguments, or passing a string where an int is expected (or vice versa)."),
    (r"FileNotFoundError|No such file",
     "File not found",
     "Check that the path exists and that the working directory is correct. "
     "Use Path(__file__).parent / 'data.txt' for paths relative to the script."),
    (r"ConnectionRefused|Connection refused",
     "Connection refused",
     "The server/service is not running. Start it first, or check the host/port."),
    (r"PermissionError|Permission denied",
     "Permission denied",
     "The file or directory is not readable/writable. "
     "Use chmod to fix permissions, or run with sudo if appropriate."),
    (r"KeyError: '?(\w+)'?",
     "Missing dictionary key",
     "Use dict.get(key, default) instead of dict[key] to avoid KeyError. "
     "Or check that the key exists: if key in d:"),
    (r"IndexError: list index out of range",
     "List index out of range",
     "Check that the list is not empty before indexing. "
     "Use 'if lst: val = lst[0]' or 'for x in lst:' instead of lst[0]."),
    (r"RecursionError",
     "Infinite recursion",
     "Add a base case to your recursive function. "
     "Or increase the limit with sys.setrecursionlimit() if intentional."),
    (r"UnicodeDecodeError",
     "Unicode decode error",
     "Open files with encoding='utf-8', errors='replace'. "
     "For binary files use 'rb' mode."),
    (r"JSONDecodeError|json.decoder",
     "Invalid JSON",
     "The input is not valid JSON. Validate it with: python3 -m json.tool file.json"),
    (r"requests.exceptions.ConnectionError",
     "Network connection error",
     "Check that the URL is correct and the service is reachable. "
     "Try: curl -I <url>  to test connectivity."),
    (r"ssl.SSLError|CERTIFICATE_VERIFY_FAILED",
     "SSL certificate error",
     "Add verify=False to requests.get() for testing (not production!), "
     "or install certificates: pip install certifi"),
    (r"cannot import name '(\w+)' from '(\w+)'",
     "Import name not found in module",
     "The symbol was removed or renamed in a newer version. "
     "Check the module's changelog or docs for the new name."),
    (r"address already in use|OSError: \[Errno 98\]",
     "Port already in use",
     "Another process is using that port. "
     "Find it: lsof -i :<port>  and kill it, or use a different port."),
    (r"GEMINI_API_KEY|gemini.*auth|sign.in.*gemini",
     "Gemini auth issue",
     "Set your free API key:  export GEMINI_API_KEY=your-key\n"
     "Get a free key at: https://aistudio.google.com/apikey\n"
     "Or run: python3 gemini_code_fixer.py --save-key YOUR_KEY"),
]


def _pattern_fix(error_msg: str) -> Optional[Tuple[str, str]]:
    """Return (description, hint) for a known error pattern, or None."""
    for pattern, desc, hint in _PATTERN_FIXES:
        if re.search(pattern, error_msg, re.IGNORECASE):
            return desc, hint
    return None


# ===========================================================================
# GeminiProgramFixer
# ===========================================================================

class GeminiProgramFixer:
    """
    Fix broken programs using the FREE Gemini AI — no paid subscription.

    Workflow:
    1. Read the broken source file
    2. Build a prompt: file content + error message + fix request
    3. Send to Gemini 1.5 Flash (free tier, 15 req/min)
    4. Parse the response: extract the fixed code and explanation
    5. Return a diff of the changes + the complete fixed file
    6. Optionally write the fixed file back to disk

    If no API key is available, falls back to built-in pattern-based fixes
    for 20+ common Python/JS/shell errors (no network needed).

    Getting a FREE Gemini API key
    ──────────────────────────────
    1. Go to https://aistudio.google.com/apikey
    2. Click "Create API key" — it's FREE, no credit card
    3. Run: python3 gemini_code_fixer.py --save-key YOUR_KEY
       OR:  export GEMINI_API_KEY=your-key
    """

    # Prompt templates
    _FIX_PROMPT = textwrap.dedent("""\
        You are an expert programmer helping to fix a broken program.
        Analyze the code and the error, then provide a complete fixed version.

        === SOURCE FILE: {filename} ===
        {code}

        === ERROR MESSAGE ===
        {error}

        === INSTRUCTIONS ===
        1. Identify the root cause of the error.
        2. Provide the COMPLETE fixed version of the file (not just a snippet).
        3. Use this exact format:

        EXPLANATION:
        <one paragraph explaining what was wrong and what you fixed>

        FIXED_CODE:
        ```{lang}
        <complete fixed file content here>
        ```

        Do not add any other text outside these two sections.
    """)

    _EXPLAIN_PROMPT = textwrap.dedent("""\
        Explain what this {lang} program does, in plain English.
        Be concise — 3-5 sentences max.
        Then list the main functions/classes with one-line descriptions.

        === FILE: {filename} ===
        {code}
    """)

    _REVIEW_PROMPT = textwrap.dedent("""\
        Review this {lang} program for bugs, security issues, and improvements.
        For each issue, show: [SEVERITY] location — description — how to fix.
        Use severity levels: CRITICAL, HIGH, MEDIUM, LOW, INFO.

        === FILE: {filename} ===
        {code}
    """)

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-1.5-flash",
    ):
        self.api_key = api_key or _load_api_key()
        self.model   = model

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def fix_file(
        self,
        file_path: str,
        error_msg: str = "",
        apply: bool = False,
    ) -> Dict[str, Any]:
        """
        Fix a broken source file.

        Parameters
        ──────────
        file_path   Path to the broken source file.
        error_msg   The error/traceback to fix (optional but improves results).
        apply       If True, write the fixed code to <name>.fixed.<ext>.

        Returns a dict with:
            fixed_code    The complete fixed file content.
            explanation   What was wrong and what was fixed.
            diff          Unified diff showing the changes.
            output_file   Path to the written fixed file (if apply=True).
            method        "gemini" | "pattern" | "none"
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        original = path.read_text(encoding="utf-8", errors="replace")
        lang     = self._detect_language(path)

        # 1. Try Gemini API
        if self.api_key:
            result = self._fix_with_gemini(original, path.name, lang, error_msg)
            method = "gemini"
        else:
            result = None

        # 2. Fallback: pattern-based fix
        if result is None:
            result = self._fix_with_patterns(original, error_msg, lang)
            method = "pattern" if result else "none"

        # Ensure we always return something
        if result is None:
            result = {
                "fixed_code":  original,
                "explanation": (
                    "Could not automatically fix this file.\n"
                    "No GEMINI_API_KEY found and no pattern match.\n"
                    "To get a free key: https://aistudio.google.com/apikey\n"
                    "Then run: python3 gemini_code_fixer.py --save-key YOUR_KEY"
                ),
            }
            method = "none"

        fixed = result["fixed_code"]
        diff  = self._make_diff(original, fixed, path.name)
        output_file: Optional[str] = None

        if apply and fixed != original:
            stem = path.stem
            suffix = path.suffix
            out = path.parent / f"{stem}.fixed{suffix}"
            out.write_text(fixed, encoding="utf-8")
            output_file = str(out)

        return {
            "file":        str(path),
            "language":    lang,
            "fixed_code":  fixed,
            "explanation": result["explanation"],
            "diff":        diff,
            "changed":     fixed != original,
            "output_file": output_file,
            "method":      method,
        }

    def explain_file(self, file_path: str) -> str:
        """Return a plain-English explanation of the file (free Gemini)."""
        path     = Path(file_path)
        code     = path.read_text(encoding="utf-8", errors="replace")
        lang     = self._detect_language(path)
        prompt   = self._EXPLAIN_PROMPT.format(
            filename=path.name, lang=lang, code=code[:8000]
        )
        if self.api_key:
            return _call_gemini(prompt, self.api_key, self.model)
        return (
            "No GEMINI_API_KEY set — cannot explain without the API.\n"
            "Get a free key: https://aistudio.google.com/apikey"
        )

    def review_file(self, file_path: str) -> str:
        """Return a security + bug review of the file (free Gemini)."""
        path   = Path(file_path)
        code   = path.read_text(encoding="utf-8", errors="replace")
        lang   = self._detect_language(path)
        prompt = self._REVIEW_PROMPT.format(
            filename=path.name, lang=lang, code=code[:8000]
        )
        if self.api_key:
            return _call_gemini(prompt, self.api_key, self.model)
        return (
            "No GEMINI_API_KEY set — cannot review without the API.\n"
            "Get a free key: https://aistudio.google.com/apikey"
        )

    def check_auth(self) -> Dict[str, Any]:
        """Diagnose Gemini API auth and return a status dict."""
        key = self.api_key
        if not key:
            return {
                "status":  "no_key",
                "message": (
                    "❌ No GEMINI_API_KEY found.\n\n"
                    "To fix (free, no credit card):\n"
                    "  1. Visit https://aistudio.google.com/apikey\n"
                    "  2. Click 'Create API key'\n"
                    "  3. Run: python3 gemini_code_fixer.py --save-key YOUR_KEY\n"
                    "     OR:  export GEMINI_API_KEY=your-key"
                ),
            }

        # Quick ping
        import urllib.request
        import urllib.error
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models?"
            f"key={key}&pageSize=1"
        )
        try:
            with urllib.request.urlopen(url, timeout=10):
                pass
            return {
                "status":  "ok",
                "message": "✅ Gemini API key is valid and working.",
                "model":   self.model,
                "key_preview": f"{key[:8]}…{key[-4:]}",
            }
        except urllib.error.HTTPError as exc:
            if exc.code == 400:
                return {
                    "status":  "invalid_key",
                    "message": "❌ API key is invalid (HTTP 400). Get a new one at https://aistudio.google.com/apikey",
                }
            if exc.code == 403:
                return {
                    "status":  "quota_exceeded",
                    "message": "❌ Quota exceeded or API not enabled. Check https://aistudio.google.com",
                }
            return {"status": "error", "message": f"HTTP {exc.code}: {exc}"}
        except urllib.error.URLError as exc:
            return {"status": "network_error", "message": f"Network error: {exc}"}

    # ------------------------------------------------------------------
    # Gemini-based fix
    # ------------------------------------------------------------------

    def _fix_with_gemini(
        self,
        code: str,
        filename: str,
        lang: str,
        error_msg: str,
    ) -> Optional[Dict[str, str]]:
        prompt = self._FIX_PROMPT.format(
            filename=filename,
            code=code[:12000],   # stay within free token budget
            error=error_msg or "(no error message provided — fix any obvious bugs)",
            lang=lang,
        )
        try:
            response = _call_gemini(prompt, self.api_key, self.model)
        except Exception:
            return None

        return self._parse_gemini_response(response, code)

    def _parse_gemini_response(
        self, response: str, original: str
    ) -> Dict[str, str]:
        """Extract EXPLANATION and FIXED_CODE sections from Gemini response."""
        explanation = ""
        fixed_code  = original   # default: unchanged

        # Extract EXPLANATION
        exp_m = re.search(r"EXPLANATION:\s*\n(.*?)(?=\nFIXED_CODE:|$)",
                          response, re.DOTALL | re.IGNORECASE)
        if exp_m:
            explanation = exp_m.group(1).strip()

        # Extract FIXED_CODE from fenced block
        code_m = re.search(
            r"FIXED_CODE:\s*\n```[a-z]*\n(.*?)```",
            response, re.DOTALL | re.IGNORECASE,
        )
        if code_m:
            fixed_code = code_m.group(1)
        else:
            # Looser: any fenced block in the response
            fence_m = re.search(r"```[a-z]*\n(.*?)```", response, re.DOTALL)
            if fence_m:
                fixed_code = fence_m.group(1)

        if not explanation:
            explanation = response[:500]

        return {"fixed_code": fixed_code, "explanation": explanation}

    # ------------------------------------------------------------------
    # Pattern-based fallback fix
    # ------------------------------------------------------------------

    @staticmethod
    def _fix_with_patterns(
        code: str, error_msg: str, lang: str
    ) -> Optional[Dict[str, str]]:
        """Apply deterministic pattern-based fixes for common errors."""
        if not error_msg:
            return None

        hit = _pattern_fix(error_msg)
        if not hit:
            return None

        desc, hint = hit
        explanation = f"{desc}\n\nSuggested fix:\n{hint}"

        # Apply simple automatic fixes where possible
        fixed = code
        if "IndentationError" in error_msg:
            # Replace all tabs with 4 spaces
            fixed = fixed.replace("\t", "    ")
        elif re.search(r"UnicodeDecodeError", error_msg):
            # Inject encoding='utf-8' into open() calls
            fixed = re.sub(
                r'\bopen\(([^,\)]+)\)',
                r"open(\1, encoding='utf-8', errors='replace')",
                fixed,
            )
        elif re.search(r"GEMINI_API_KEY|gemini.*auth", error_msg, re.I):
            # Inject env-var lookup at top of file
            if "GEMINI_API_KEY" not in code:
                fixed = (
                    "import os\n"
                    "GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')\n\n"
                    + code
                )

        return {"fixed_code": fixed, "explanation": explanation}

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    @staticmethod
    def _detect_language(path: Path) -> str:
        ext_map = {
            ".py": "python", ".js": "javascript", ".ts": "typescript",
            ".sh": "bash", ".rs": "rust", ".go": "go",
            ".c": "c", ".cpp": "cpp", ".java": "java",
            ".rb": "ruby", ".php": "php", ".cs": "csharp",
        }
        return ext_map.get(path.suffix.lower(), "text")

    @staticmethod
    def _make_diff(original: str, fixed: str, filename: str) -> str:
        diff_lines = list(difflib.unified_diff(
            original.splitlines(keepends=True),
            fixed.splitlines(keepends=True),
            fromfile=f"a/{filename}",
            tofile=f"b/{filename}",
            n=3,
        ))
        return "".join(diff_lines) if diff_lines else "(no changes)"


# ===========================================================================
# CLI
# ===========================================================================

class GeminiCodeFixerCLI:
    """Command-line interface for GeminiProgramFixer."""

    def run(self, argv: Optional[List[str]] = None) -> int:
        parser = argparse.ArgumentParser(
            prog="gemini_code_fixer",
            description=(
                "🔧 THE FORGE — Gemini Program Fixer\n\n"
                "Fix broken programs with the FREE Gemini AI.\n"
                "No paid subscription needed.\n"
                "Get a free key: https://aistudio.google.com/apikey"
            ),
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=(
                "examples:\n"
                "  # Fix a Python file\n"
                "  %(prog)s --fix my_script.py\n\n"
                "  # Fix with the exact error message for better results\n"
                "  %(prog)s --fix my_script.py --error 'NameError: name foo'\n\n"
                "  # Fix and auto-apply the changes\n"
                "  %(prog)s --fix my_script.py --apply\n\n"
                "  # Explain what a file does\n"
                "  %(prog)s --explain my_script.py\n\n"
                "  # Review for bugs/security issues\n"
                "  %(prog)s --review my_script.py\n\n"
                "  # Check if your Gemini API key works\n"
                "  %(prog)s --check-auth\n\n"
                "  # Save your free API key\n"
                "  %(prog)s --save-key AIzaSy...\n"
            ),
        )

        action = parser.add_mutually_exclusive_group()
        action.add_argument("--fix", metavar="FILE",
            help="Fix a broken source file with Gemini AI")
        action.add_argument("--explain", metavar="FILE",
            help="Explain what a source file does (plain English)")
        action.add_argument("--review", metavar="FILE",
            help="Review a file for bugs and security issues")
        action.add_argument("--check-auth", action="store_true",
            help="Test whether your Gemini API key works")
        action.add_argument("--save-key", metavar="KEY",
            help="Save your Gemini API key to ~/.config/forge/gemini_api_key")

        parser.add_argument("--error", metavar="MSG", default="",
            help="Error message / traceback to fix (improves Gemini results)")
        parser.add_argument("--apply", action="store_true", default=False,
            help="Write fixed file to <name>.fixed.<ext>")
        parser.add_argument("--model", default="gemini-1.5-flash",
            help="Gemini model to use (default: gemini-1.5-flash, free tier)")
        parser.add_argument("--json", action="store_true", default=False,
            help="Output results as JSON")

        args = parser.parse_args(argv)

        if args.save_key:
            _save_api_key(args.save_key)
            return 0

        fixer = GeminiProgramFixer(model=args.model)

        if args.check_auth:
            status = fixer.check_auth()
            if args.json:
                print(json.dumps(status, indent=2))
            else:
                print(status["message"])
            return 0 if status["status"] == "ok" else 1

        if args.fix:
            return self._do_fix(fixer, args.fix, args.error, args.apply, args.json)

        if args.explain:
            result = fixer.explain_file(args.explain)
            print(result)
            return 0

        if args.review:
            result = fixer.review_file(args.review)
            print(result)
            return 0

        parser.print_help()
        return 1

    # ------------------------------------------------------------------

    @staticmethod
    def _do_fix(
        fixer: GeminiProgramFixer,
        file_path: str,
        error_msg: str,
        apply: bool,
        as_json: bool,
    ) -> int:
        try:
            result = fixer.fix_file(file_path, error_msg=error_msg, apply=apply)
        except FileNotFoundError as exc:
            print(f"❌ {exc}", file=sys.stderr)
            return 1

        if as_json:
            # Don't dump full code to JSON unless small
            out = {k: v for k, v in result.items() if k != "fixed_code"}
            out["fixed_code_lines"] = len(result["fixed_code"].splitlines())
            print(json.dumps(out, indent=2))
            return 0

        print("=" * 64)
        print(f"🔧 THE FORGE — Gemini Program Fixer")
        print(f"   File    : {result['file']}")
        print(f"   Language: {result['language']}")
        print(f"   Method  : {result['method']}")
        print("=" * 64)

        print(f"\n📝 Explanation:\n{textwrap.indent(result['explanation'], '   ')}")

        if result["changed"]:
            print(f"\n📋 Diff:")
            diff = result["diff"]
            for line in diff.splitlines()[:60]:
                if line.startswith("+") and not line.startswith("+++"):
                    print(f"\033[32m{line}\033[0m")   # green
                elif line.startswith("-") and not line.startswith("---"):
                    print(f"\033[31m{line}\033[0m")   # red
                else:
                    print(line)
            if diff.count("\n") > 60:
                print(f"   … ({diff.count(chr(10)) - 60} more lines)")

            if apply and result["output_file"]:
                print(f"\n✅ Fixed file written to: {result['output_file']}")
            elif not apply:
                print(
                    f"\n💡 To apply the fix, re-run with --apply\n"
                    f"   Or copy the fixed code from above."
                )
        else:
            print("\n✅ No changes needed — the code looks correct already.")

        if result["method"] == "none":
            print(
                "\n💡 For better fixes, set a FREE Gemini API key:\n"
                "   https://aistudio.google.com/apikey\n"
                "   python3 gemini_code_fixer.py --save-key YOUR_KEY"
            )

        return 0


# ---------------------------------------------------------------------------
# Module-level type alias for import
# ---------------------------------------------------------------------------
from typing import List  # re-export for external callers


def main() -> None:
    sys.exit(GeminiCodeFixerCLI().run())


if __name__ == "__main__":
    main()
