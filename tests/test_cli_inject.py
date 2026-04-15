"""Tests for envguard.cli_inject."""
import argparse
from pathlib import Path

import pytest

from envguard.cli_inject import run_inject


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


def _args(source, target, overwrite=False, dry_run=False):
    ns = argparse.Namespace()
    ns.source = str(source)
    ns.target = str(target)
    ns.overwrite = overwrite
    ns.dry_run = dry_run
    return ns


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_run_inject_exits_zero(tmp_env):
    src = _write(tmp_env / "source.env", "NEW_KEY=hello\n")
    tgt = _write(tmp_env / "target.env", "EXISTING=world\n")
    assert run_inject(_args(src, tgt)) == 0


def test_run_inject_missing_source_exits_two(tmp_env):
    tgt = _write(tmp_env / "target.env", "EXISTING=world\n")
    assert run_inject(_args(tmp_env / "no.env", tgt)) == 2


def test_run_inject_writes_merged_file(tmp_env):
    src = _write(tmp_env / "source.env", "NEW_KEY=hello\n")
    tgt = _write(tmp_env / "target.env", "EXISTING=world\n")
    run_inject(_args(src, tgt))
    content = (tmp_env / "target.env").read_text()
    assert "NEW_KEY=hello" in content
    assert "EXISTING=world" in content


def test_run_inject_does_not_overwrite_by_default(tmp_env):
    src = _write(tmp_env / "source.env", "PORT=9999\n")
    tgt = _write(tmp_env / "target.env", "PORT=8080\n")
    run_inject(_args(src, tgt, overwrite=False))
    content = (tmp_env / "target.env").read_text()
    assert "PORT=8n
def test_run_inject_overwrites_when_flag_set(tmp_env):
    src = _write(tmp_env / "source.env", "PORT=9999\n")
    tgt = _write(tmp_env / "target.env", "PORT=8080\n")
    run_inject(_args(src, tgt, overwrite=True))
    content = (tmp_env / "target.env").read_text()
    assert "PORT=9999" in content


def test_run_inject_dry_run_does_not_write(tmp_env):
    src = _write(tmp_env / "source.env", "NEW_KEY=hello\n")
    tgt = _write(tmp_env / "target.env", "EXISTING=world\n")
    run_inject(_args(src, tgt, dry_run=True))
    content = (tmp_env / "target.env").read_text()
    assert "NEW_KEY" not in content


def test_run_inject_creates_target_if_missing(tmp_env):
    src = _write(tmp_env / "source.env", "KEY=value\n")
    tgt = tmp_env / "new_target.env"
    assert run_inject(_args(src, tgt)) == 0
    assert tgt.exists()
