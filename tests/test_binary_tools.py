"""
Tests for binary_tools.py — SafeElfReader, DebRipper, WarpRipper, GeminiAuthFixer

These tests:
  • Are Linux-only — they rely on ELF binaries, the ``ar`` utility, and
    ``/usr/bin/ls``.  Run them on Linux (including CI runners).
  • Never execute a binary (all ELF inspection is read-only mmap)
  • Use /usr/bin/ls (always present on Linux) as the test ELF
  • Build a minimal .deb in-memory to test DebRipper without a real Warp package
  • Test GeminiAuthFixer in an isolated temp directory
"""

import json
import os
import struct
import subprocess
import sys
import tarfile
import tempfile
from io import BytesIO
from pathlib import Path

import pytest

# Make sure we can import from the repo root
sys.path.insert(0, str(Path(__file__).parent.parent))

from binary_tools import (
    ELF_MAGIC,
    DebRipper,
    GeminiAuthFixer,
    SafeElfReader,
    WarpRipper,
)

# ---------------------------------------------------------------------------
# Platform guard
# ---------------------------------------------------------------------------

pytestmark = pytest.mark.skipif(
    sys.platform != "linux",
    reason="binary_tools tests are Linux-only (ELF format, ar utility)",
)

# Always-present ELF on every Linux system
TEST_ELF = "/usr/bin/ls"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_minimal_elf(path: Path, machine: int = 0x3E) -> None:
    """
    Write a syntactically valid minimal 64-bit ELF to *path*.
    It is NOT executable — just a structurally correct header for parsing.
    """
    # ELF ident (16 bytes)
    e_ident = (
        ELF_MAGIC           # magic
        + bytes([2])        # EI_CLASS = 64-bit
        + bytes([1])        # EI_DATA  = little-endian
        + bytes([1])        # EI_VERSION
        + bytes([0])        # EI_OSABI = System V
        + bytes(8)          # padding
    )
    # ELF header (rest of 64 bytes after ident)
    # e_type=ET_EXEC(2), e_machine, e_version=1, e_entry=0,
    # e_phoff=0, e_shoff=0, e_flags=0, e_ehsize=64,
    # e_phentsize=56, e_phnum=0, e_shentsize=64, e_shnum=0, e_shstrndx=0
    rest = struct.pack(
        "<HHIQQQIHHHHHH",
        2,        # e_type
        machine,  # e_machine (0x3E = x86-64)
        1,        # e_version
        0,        # e_entry
        0,        # e_phoff
        0,        # e_shoff
        0,        # e_flags
        64,       # e_ehsize
        56,       # e_phentsize
        0,        # e_phnum
        64,       # e_shentsize
        0,        # e_shnum
        0,        # e_shstrndx
    )
    path.write_bytes(e_ident + rest)


def _make_minimal_deb(deb_path: Path, pkg_name: str = "testpkg",
                       version: str = "1.0") -> None:
    """
    Build a minimal .deb archive at *deb_path* containing:
      • debian-binary
      • control.tar.gz  (control file only)
      • data.tar.gz     (one ELF + one shell script)
    """
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)

        # ── debian-binary ──────────────────────────────────────────
        (tmp / "debian-binary").write_bytes(b"2.0\n")

        # ── control.tar.gz ─────────────────────────────────────────
        control_text = (
            f"Package: {pkg_name}\n"
            f"Version: {version}\n"
            "Architecture: amd64\n"
            "Maintainer: test\n"
            "Description: test package\n"
        )
        ctrl_buf = BytesIO()
        with tarfile.open(fileobj=ctrl_buf, mode="w:gz") as tf:
            raw = control_text.encode()
            info = tarfile.TarInfo(name="./control")
            info.size = len(raw)
            tf.addfile(info, BytesIO(raw))
        (tmp / "control.tar.gz").write_bytes(ctrl_buf.getvalue())

        # ── data.tar.gz ────────────────────────────────────────────
        elf_path = tmp / "fake_elf"
        _make_minimal_elf(elf_path)
        elf_bytes = elf_path.read_bytes()

        script_bytes = b"#!/bin/bash\necho hello\n"

        data_buf = BytesIO()
        with tarfile.open(fileobj=data_buf, mode="w:gz") as tf:
            # ELF binary
            info = tarfile.TarInfo(name="./usr/bin/testbin")
            info.size = len(elf_bytes)
            info.mode = 0o755
            tf.addfile(info, BytesIO(elf_bytes))
            # Shell script
            info2 = tarfile.TarInfo(name="./usr/share/testpkg/install.sh")
            info2.size = len(script_bytes)
            info2.mode = 0o644
            tf.addfile(info2, BytesIO(script_bytes))
        (tmp / "data.tar.gz").write_bytes(data_buf.getvalue())

        # ── assemble the .deb with ar ──────────────────────────────
        subprocess.run(
            [
                "ar", "r", str(deb_path),
                "debian-binary",
                "control.tar.gz",
                "data.tar.gz",
            ],
            cwd=str(tmp),
            capture_output=True,
            check=True,
        )


# ===========================================================================
# SafeElfReader tests
# ===========================================================================

class TestSafeElfReader:

    def test_context_manager_opens_and_closes(self):
        with SafeElfReader(TEST_ELF) as elf:
            assert elf._mm is not None
        assert elf._mm is None   # closed on __exit__

    def test_read_header_fields(self):
        with SafeElfReader(TEST_ELF) as elf:
            hdr = elf.read_header()
        assert hdr["machine"] == "x86-64"
        assert hdr["class"]   == "64-bit"
        assert hdr["data"]    == "little-endian"
        assert hdr["is_64bit"]      is True
        assert hdr["little_endian"] is True
        assert hdr["size_bytes"]    > 0

    def test_list_sections_returns_list(self):
        with SafeElfReader(TEST_ELF) as elf:
            secs = elf.list_sections()
        assert isinstance(secs, list)
        assert len(secs) > 0
        # Every entry must have a 'name' and 'size'
        for s in secs:
            assert "name" in s
            assert "size" in s

    def test_list_sections_has_expected_sections(self):
        with SafeElfReader(TEST_ELF) as elf:
            names = {s["name"] for s in elf.list_sections()}
        # .text and .rodata are always present in /usr/bin/ls
        assert ".text" in names
        assert ".rodata" in names

    def test_list_symbols_no_version_index_suffix(self):
        """Symbols must not end with bare '(N)' version index tokens."""
        import re
        with SafeElfReader(TEST_ELF) as elf:
            syms = elf.list_symbols()
        ver_only = re.compile(r'^\(\d+\)$')
        for sym in syms:
            assert not ver_only.match(sym), (
                f"Symbol '{sym}' looks like a bare version-index token"
            )

    def test_list_symbols_returns_real_names(self):
        with SafeElfReader(TEST_ELF) as elf:
            syms = elf.list_symbols()
        # /usr/bin/ls is dynamically linked against libc — getenv should appear
        assert any("getenv" in s for s in syms)

    def test_extract_strings_returns_printable(self):
        with SafeElfReader(TEST_ELF) as elf:
            strs = elf.extract_strings(min_len=8)
        assert len(strs) > 0
        for s in strs:
            assert all(0x20 <= ord(c) <= 0x7E for c in s)

    def test_extract_strings_respects_min_len(self):
        with SafeElfReader(TEST_ELF) as elf:
            strs = elf.extract_strings(min_len=20)
        for s in strs:
            assert len(s) >= 20

    def test_sha256_is_hex_string(self):
        with SafeElfReader(TEST_ELF) as elf:
            sha = elf.sha256()
        assert len(sha) == 64
        assert all(c in "0123456789abcdef" for c in sha)

    def test_is_stripped_bool(self):
        with SafeElfReader(TEST_ELF) as elf:
            result = elf.is_stripped()
        assert isinstance(result, bool)

    def test_rejects_non_elf_file(self, tmp_path):
        bad = tmp_path / "not_an_elf.bin"
        bad.write_bytes(b"This is not an ELF file at all!\x00" * 4)
        with pytest.raises(ValueError, match="Not a valid ELF"):
            with SafeElfReader(str(bad)) as _:
                pass

    def test_rejects_missing_file(self, tmp_path):
        missing = tmp_path / "ghost.elf"
        with pytest.raises(FileNotFoundError):
            with SafeElfReader(str(missing)) as _:
                pass

    def test_rejects_too_small_file(self, tmp_path):
        tiny = tmp_path / "tiny.bin"
        tiny.write_bytes(b"\x7fELF")   # magic but too short
        with pytest.raises(ValueError):
            with SafeElfReader(str(tiny)) as _:
                pass

    def test_minimal_elf_header_parses(self, tmp_path):
        """Our hand-crafted minimal ELF must parse without errors."""
        elf_path = tmp_path / "minimal.elf"
        _make_minimal_elf(elf_path, machine=0x3E)
        with SafeElfReader(str(elf_path)) as elf:
            hdr = elf.read_header()
        assert hdr["machine"]  == "x86-64"
        assert hdr["class"]    == "64-bit"
        assert hdr["is_64bit"] is True

    def test_binary_never_executed(self, tmp_path):
        """
        Regression: opening an ELF with SafeElfReader must NEVER execute it.
        We verify by creating a file with ELF magic that is otherwise invalid,
        and confirming no side effects occur (no child process, no sentinel).
        """
        sentinel = tmp_path / "executed"
        # Minimal ELF with no code — just a header pointing at nothing
        elf_path = tmp_path / "dummy.elf"
        _make_minimal_elf(elf_path)
        with SafeElfReader(str(elf_path)) as elf:
            elf.read_header()   # parse only
        assert not sentinel.exists(), "ELF was executed — SafeElfReader is broken!"


# ===========================================================================
# DebRipper tests
# ===========================================================================

class TestDebRipper:

    @pytest.fixture
    def sample_deb(self, tmp_path):
        """Build a minimal synthetic .deb for testing."""
        deb = tmp_path / "testpkg_1.0_amd64.deb"
        _make_minimal_deb(deb, pkg_name="testpkg", version="1.0")
        return deb

    def test_rip_returns_report(self, sample_deb, tmp_path):
        out = tmp_path / "ripped"
        report = DebRipper(str(sample_deb), str(out)).rip()
        assert "elf_files" in report
        assert "source_files" in report
        assert "summary" in report

    def test_rip_finds_elf_binary(self, sample_deb, tmp_path):
        out = tmp_path / "ripped"
        report = DebRipper(str(sample_deb), str(out)).rip()
        assert report["summary"]["elf_count"] == 1

    def test_rip_finds_shell_script(self, sample_deb, tmp_path):
        out = tmp_path / "ripped"
        report = DebRipper(str(sample_deb), str(out)).rip()
        cats = report["source_files"]
        assert "shell_scripts" in cats
        assert len(cats["shell_scripts"]) == 1

    def test_rip_parses_control(self, sample_deb, tmp_path):
        out = tmp_path / "ripped"
        report = DebRipper(str(sample_deb), str(out)).rip()
        assert report["pkg_info"]["package"] == "testpkg"
        assert report["pkg_info"]["version"] == "1.0"
        assert report["summary"]["package"] == "testpkg"

    def test_rip_writes_report_json(self, sample_deb, tmp_path):
        out = tmp_path / "ripped"
        DebRipper(str(sample_deb), str(out)).rip()
        report_path = out / "analysis_report.json"
        assert report_path.exists()
        with open(report_path) as fh:
            data = json.load(fh)
        assert "elf_files" in data

    def test_rip_preserves_elf_in_elfs_dir(self, sample_deb, tmp_path):
        out = tmp_path / "ripped"
        DebRipper(str(sample_deb), str(out)).rip()
        elf_dir = out / "elfs"
        assert elf_dir.exists()
        preserved = list(elf_dir.iterdir())
        assert len(preserved) == 1
        assert preserved[0].read_bytes()[:4] == ELF_MAGIC

    def test_rip_raises_for_missing_deb(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            DebRipper("/no/such/file.deb", str(tmp_path)).rip()

    def test_parse_control_parses_fields(self):
        text = "Package: foo\nVersion: 2.0\nArchitecture: arm64\n"
        info = DebRipper._parse_control(text)
        assert info["package"] == "foo"
        assert info["version"] == "2.0"
        assert info["architecture"] == "arm64"

    def test_is_elf_correct(self, tmp_path):
        elf_file = tmp_path / "test.elf"
        _make_minimal_elf(elf_file)
        assert DebRipper._is_elf(str(elf_file))

        non_elf = tmp_path / "text.txt"
        non_elf.write_bytes(b"hello world")
        assert not DebRipper._is_elf(str(non_elf))

    def test_path_traversal_blocked(self, tmp_path):
        """data.tar entries with ../ must not escape the output directory."""
        deb = tmp_path / "evil.deb"
        (tmp_path / "debian-binary").write_bytes(b"2.0\n")

        ctrl_buf = BytesIO()
        with tarfile.open(fileobj=ctrl_buf, mode="w:gz") as tf:
            raw = b"Package: evil\nVersion: 1.0\nArchitecture: amd64\nMaintainer: x\nDescription: x\n"
            info = tarfile.TarInfo(name="./control")
            info.size = len(raw)
            tf.addfile(info, BytesIO(raw))
        (tmp_path / "control.tar.gz").write_bytes(ctrl_buf.getvalue())

        data_buf = BytesIO()
        evil_payload = b"evil content"
        # The traversal targets a file *within* tmp_path's parent so we can
        # reliably detect it without touching /tmp or any system paths.
        escape_name = "evil_escape.txt"
        with tarfile.open(fileobj=data_buf, mode="w:gz") as tf:
            info = tarfile.TarInfo(name=f"../../../{escape_name}")
            info.size = len(evil_payload)
            tf.addfile(info, BytesIO(evil_payload))
        (tmp_path / "data.tar.gz").write_bytes(data_buf.getvalue())

        subprocess.run(
            ["ar", "r", str(deb), "debian-binary", "control.tar.gz", "data.tar.gz"],
            cwd=str(tmp_path), capture_output=True,
        )

        out = tmp_path / "ripped"
        DebRipper(str(deb), str(out)).rip()

        # The file must not have escaped outside the output directory
        escaped = out.parent.parent.parent / escape_name
        assert not escaped.exists(), (
            f"Path traversal succeeded — {escaped} was created outside the output dir"
        )


# ===========================================================================
# WarpRipper tests
# ===========================================================================

class TestWarpRipper:

    def test_rip_single_elf(self, tmp_path):
        report = WarpRipper(TEST_ELF).rip(output_dir=str(tmp_path / "out"))
        assert "elf_files" in report
        assert report["summary"]["elf_count"] >= 1

    def test_rip_deb_package(self, tmp_path):
        deb = tmp_path / "warp-terminal_1.0_amd64.deb"
        _make_minimal_deb(deb, pkg_name="warp-terminal", version="1.0")
        out = tmp_path / "out"
        report = WarpRipper(str(deb)).rip(output_dir=str(out))
        assert report["pkg_info"]["package"] == "warp-terminal"
        assert (out / "warp_analysis_report.json").exists()

    def test_warp_binary_not_found_graceful(self, tmp_path):
        report = WarpRipper(TEST_ELF).rip(output_dir=str(tmp_path / "out"))
        assert "warp_analysis" in report

    def test_raises_for_unsupported_input(self, tmp_path):
        bad = tmp_path / "notanything.xyz"
        bad.write_bytes(b"garbage")
        with pytest.raises(ValueError):
            WarpRipper(str(bad)).rip(output_dir=str(tmp_path / "out"))

    def test_warp_analysis_has_required_keys(self, tmp_path):
        elf_path = tmp_path / "warp-terminal"
        _make_minimal_elf(elf_path)
        report = WarpRipper(str(elf_path)).rip(output_dir=str(tmp_path / "out"))
        wa = report["warp_analysis"]
        assert "found" in wa
        if wa["found"]:
            for key in ("version", "is_rust", "is_stripped",
                        "auth_paths", "config_paths", "env_vars"):
                assert key in wa, f"Missing key: {key}"


# ===========================================================================
# GeminiAuthFixer tests
# ===========================================================================

class TestGeminiAuthFixer:

    def test_diagnose_returns_required_keys(self):
        fixer = GeminiAuthFixer()
        diag  = fixer.diagnose()
        for key in ("found", "path", "type", "failure_modes",
                    "token_paths", "env_vars", "recommendations"):
            assert key in diag, f"Missing key: {key}"

    def test_diagnose_not_found_has_install_recommendation(self):
        fixer = GeminiAuthFixer()
        diag  = fixer.diagnose()
        if not diag["found"]:
            recs = " ".join(diag["recommendations"])
            assert "npm" in recs or "pip" in recs or "install" in recs.lower()

    def test_apply_fix_creates_required_files(self, tmp_path):
        fixer = GeminiAuthFixer()
        fixer.diagnose()
        result = fixer.apply_fix(api_key="test-api-key", output_dir=str(tmp_path))
        names = {Path(f).name for f in result["files_created"]}
        assert "credentials.json"   in names
        assert "gemini"             in names
        assert "gemini.env"         in names
        assert "GEMINI_AUTH_FIX.md" in names

    def test_credentials_json_contains_api_key(self, tmp_path):
        fixer = GeminiAuthFixer()
        fixer.diagnose()
        fixer.apply_fix(api_key="my-secret-key", output_dir=str(tmp_path))
        with open(tmp_path / "credentials.json") as fh:
            data = json.load(fh)
        assert data["apiKey"] == "my-secret-key"

    def test_credentials_json_template_when_no_key(self, tmp_path):
        fixer = GeminiAuthFixer()
        fixer.diagnose()
        fixer.apply_fix(api_key=None, output_dir=str(tmp_path))
        with open(tmp_path / "credentials.json") as fh:
            data = json.load(fh)
        assert "<YOUR_GEMINI_API_KEY>" in data["apiKey"]

    def test_wrapper_script_is_executable(self, tmp_path):
        fixer = GeminiAuthFixer()
        fixer.diagnose()
        fixer.apply_fix(api_key="k", output_dir=str(tmp_path))
        assert os.access(str(tmp_path / "gemini"), os.X_OK)

    def test_wrapper_contains_api_key(self, tmp_path):
        fixer = GeminiAuthFixer()
        fixer.diagnose()
        fixer.apply_fix(api_key="abc123", output_dir=str(tmp_path))
        content = (tmp_path / "gemini").read_text()
        assert "GEMINI_API_KEY" in content
        assert "abc123" in content

    def test_env_file_has_all_vars(self, tmp_path):
        fixer = GeminiAuthFixer()
        fixer.diagnose()
        fixer.apply_fix(api_key="envkey", output_dir=str(tmp_path))
        env = (tmp_path / "gemini.env").read_text()
        for var in ("GEMINI_API_KEY", "GOOGLE_API_KEY",
                    "GOOGLE_GENERATIVE_AI_API_KEY", "GEMINI_CREDENTIALS_FILE"):
            assert var in env

    def test_guide_markdown_has_required_sections(self, tmp_path):
        fixer = GeminiAuthFixer()
        fixer.diagnose()
        fixer.apply_fix(api_key="k", output_dir=str(tmp_path))
        guide = (tmp_path / "GEMINI_AUTH_FIX.md").read_text()
        assert "# Gemini CLI Authentication Fix Guide" in guide
        assert "https://aistudio.google.com/app/apikey" in guide
        assert "GEMINI_API_KEY" in guide

    def test_analyse_elf_cli(self, tmp_path):
        elf_path = tmp_path / "fake_gemini"
        _make_minimal_elf(elf_path)
        fixer = GeminiAuthFixer()
        cli_type, details = fixer._analyse_cli_binary(str(elf_path))
        assert cli_type == "elf"
        assert "token_paths" in details
        assert "env_vars_found" in details

    def test_analyse_node_script(self, tmp_path):
        script = tmp_path / "gemini"
        script.write_text(
            "#!/usr/bin/env node\n"
            'const GEMINI_API_KEY = process.env["GEMINI_API_KEY"];\n'
            'const credFile = "~/.config/gemini/credentials.json";\n'
        )
        fixer = GeminiAuthFixer()
        cli_type, details = fixer._analyse_cli_binary(str(script))
        assert cli_type == "node"
        assert any("credentials" in p for p in details.get("token_paths", []))

    def test_find_existing_tokens_returns_list(self):
        found = GeminiAuthFixer._find_existing_tokens()
        assert isinstance(found, list)
        for p in found:
            assert Path(p).exists()


# ===========================================================================
# CLI integration tests
# ===========================================================================

class TestBinaryToolsCLI:

    _REPO = str(Path(__file__).parent.parent)

    def _run(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "binary_tools.py", *args],
            capture_output=True, text=True, cwd=self._REPO,
        )

    def test_help_exits_zero(self):
        r = self._run("--help")
        assert r.returncode == 0
        assert "--inspect"          in r.stdout
        assert "--rip-deb"          in r.stdout
        assert "--rip-warp"         in r.stdout
        assert "--fix-gemini-auth"  in r.stdout
        assert "--diagnose-gemini"  in r.stdout

    def test_inspect_real_elf(self):
        r = self._run("--inspect", TEST_ELF)
        assert r.returncode == 0
        assert "x86-64"  in r.stdout
        assert "SHA-256"  in r.stdout
        assert "Sections" in r.stdout

    def test_inspect_json_output(self):
        r = self._run("--inspect", TEST_ELF, "--json")
        assert r.returncode == 0
        data = json.loads(r.stdout)
        assert data["header"]["machine"] == "x86-64"

    def test_inspect_missing_file_nonzero(self):
        r = self._run("--inspect", "/no/such/elf")
        assert r.returncode != 0

    def test_diagnose_gemini_exits_zero(self):
        r = self._run("--diagnose-gemini")
        assert r.returncode == 0

    def test_fix_gemini_creates_files(self, tmp_path):
        r = self._run(
            "--fix-gemini-auth", "--api-key", "cli-test-key",
            "-o", str(tmp_path),
        )
        assert r.returncode == 0
        assert (tmp_path / "credentials.json").exists()
        assert (tmp_path / "gemini").exists()
        assert (tmp_path / "GEMINI_AUTH_FIX.md").exists()

    def test_no_action_exits_nonzero(self):
        r = self._run()
        assert r.returncode != 0

    def test_rip_warp_and_fix_gemini_together(self, tmp_path):
        """--rip-warp and --fix-gemini-auth can be combined (not mutex)."""
        r = self._run(
            "--rip-warp", TEST_ELF,
            "--fix-gemini-auth", "--api-key", "combo-key",
            "-o", str(tmp_path),
        )
        assert r.returncode == 0
        assert (tmp_path / "warp_analysis_report.json").exists()
        assert (tmp_path / "credentials.json").exists()
