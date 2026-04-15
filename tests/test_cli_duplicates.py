"""Tests for envguard.cli_duplicates."""
import argparse
import pytest

from envguard.cli_duplicates import build_duplicates_parser, run_duplicates


@pytest.fixture()
def tmp_env(tmp_path):
    return tmp_path


def _write(path, content: str) -> str:
    path.write_text(content, encoding="utf-8")
    return str(path)


def _args(env_files, strict=False) -> argparse.Namespace:
    return argparse.Namespace(env_files=env_files, strict=strict)


# ── exit-code tests ────────────────────────────────────────────────────────

def test_run_duplicates_exits_zero_no_duplicates(tmp_env):
    f = _write(tmp_env / ".env", "FOO=1\nBAR=2\n")
    assert run_duplicates(_args([f])) == 0


def test_run_duplicates_exits_zero_with_duplicates_no_strict(tmp_env):
    f = _write(tmp_env / ".env", "FOO=1\nFOO=2\n")
    assert run_duplicates(_args([f], strict=False)) == 0


def test_run_duplicates_exits_one_strict_with_duplicates(tmp_env):
    f = _write(tmp_env / ".env", "KEY=a\nKEY=b\n")
    assert run_duplicates(_args([f], strict=True)) == 1


def test_run_duplicates_exits_zero_strict_no_duplicates(tmp_env):
    f = _write(tmp_env / ".env", "ALPHA=1\nBETA=2\n")
    assert run_duplicates(_args([f], strict=True)) == 0


def test_run_duplicates_missing_file_exits_two(tmp_env):
    assert run_duplicates(_args(["/nonexistent/.env"])) == 2


# ── output tests ───────────────────────────────────────────────────────────

def test_run_duplicates_prints_summary_no_dups(tmp_env, capsys):
    f = _write(tmp_env / ".env", "A=1\n")
    run_duplicates(_args([f]))
    out = capsys.readouterr().out
    assert "No duplicate keys found" in out


def test_run_duplicates_prints_duplicate_key(tmp_env, capsys):
    f = _write(tmp_env / ".env", "DB=x\nDB=y\n")
    run_duplicates(_args([f]))
    out = capsys.readouterr().out
    assert "DB" in out


# ── parser tests ───────────────────────────────────────────────────────────

def test_build_duplicates_parser_returns_parser():
    parser = build_duplicates_parser()
    assert isinstance(parser, argparse.ArgumentParser)


def test_parser_strict_flag_default_false():
    parser = build_duplicates_parser()
    args = parser.parse_args(["/some/.env"])
    assert args.strict is False


def test_parser_strict_flag_set():
    parser = build_duplicates_parser()
    args = parser.parse_args(["/some/.env", "--strict"])
    assert args.strict is True
