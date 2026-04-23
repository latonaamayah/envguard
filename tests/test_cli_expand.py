"""Tests for envguard.cli_expand."""
import argparse
import pytest
from envguard.cli_expand import build_expand_parser, run_expand, _parse_mapping


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path / ".env"


def _write(path, content: str):
    path.write_text(content)


def _args(env_file, maps=None, strict=False):
    ns = argparse.Namespace(
        env_file=str(env_file),
        map=maps or [],
        strict=strict,
    )
    return ns


def test_run_expand_exits_zero(tmp_env):
    _write(tmp_env, "DB_HOST=localhost\n")
    assert run_expand(_args(tmp_env)) == 0


def test_run_expand_missing_file_exits_two(tmp_path):
    missing = tmp_path / "missing.env"
    assert run_expand(_args(missing)) == 2


def test_run_expand_outputs_original_when_no_mapping(tmp_env, capsys):
    _write(tmp_env, "DB_HOST=localhost\n")
    run_expand(_args(tmp_env))
    out = capsys.readouterr().out
    assert "DB_HOST=localhost" in out


def test_run_expand_outputs_canonical_key(tmp_env, capsys):
    _write(tmp_env, "DB_PWD=secret\n")
    run_expand(_args(tmp_env, maps=["DB_PWD=DB_PASSWORD"]))
    out = capsys.readouterr().out
    assert "DB_PASSWORD=secret" in out
    assert "DB_PWD" not in out


def test_run_expand_strict_exits_one_when_expanded(tmp_env):
    _write(tmp_env, "DB_PWD=secret\n")
    assert run_expand(_args(tmp_env, maps=["DB_PWD=DB_PASSWORD"], strict=True)) == 1


def test_run_expand_strict_exits_zero_when_no_expansion(tmp_env):
    _write(tmp_env, "DB_HOST=localhost\n")
    assert run_expand(_args(tmp_env, maps=[], strict=True)) == 0


def test_parse_mapping_valid():
    m = _parse_mapping(["A=ALPHA", "B=BETA"])
    assert m == {"A": "ALPHA", "B": "BETA"}


def test_parse_mapping_invalid_raises():
    with pytest.raises(ValueError):
        _parse_mapping(["INVALID"])


def test_build_expand_parser_returns_parser():
    p = build_expand_parser()
    assert p is not None
