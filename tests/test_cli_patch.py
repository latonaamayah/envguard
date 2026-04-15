"""Tests for envguard.cli_patch."""
import argparse
import os
import pytest
from envguard.cli_patch import run_patch, build_patch_parser


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path / ".env"


def _write(path, content):
    path.write_text(content)


def _args(env_file, overrides, in_place=False):
    ns = argparse.Namespace(env_file=str(env_file), overrides=overrides, in_place=in_place)
    return ns


def test_run_patch_exits_zero(tmp_env):
    _write(tmp_env, "HOST=localhost\nPORT=5432\n")
    code = run_patch(_args(tmp_env, ["PORT=9999"]))
    assert code == 0


def test_run_patch_outputs_updated_value(tmp_env, capsys):
    _write(tmp_env, "HOST=localhost\nPORT=5432\n")
    run_patch(_args(tmp_env, ["PORT=9999"]))
    out = capsys.readouterr().out
    assert "PORT=9999" in out


def test_run_patch_outputs_unchanged_key(tmp_env, capsys):
    _write(tmp_env, "HOST=localhost\nPORT=5432\n")
    run_patch(_args(tmp_env, ["PORT=9999"]))
    out = capsys.readouterr().out
    assert "HOST=localhost" in out


def test_run_patch_adds_new_key(tmp_env, capsys):
    _write(tmp_env, "HOST=localhost\n")
    run_patch(_args(tmp_env, ["NEW_KEY=hello"]))
    out = capsys.readouterr().out
    assert "NEW_KEY=hello" in out


def test_run_patch_in_place_writes_file(tmp_env):
    _write(tmp_env, "HOST=localhost\nPORT=5432\n")
    run_patch(_args(tmp_env, ["PORT=8080"], in_place=True))
    content = tmp_env.read_text()
    assert "PORT=8080" in content


def test_run_patch_missing_file_exits_two(tmp_env):
    code = run_patch(_args(tmp_env, ["KEY=val"]))
    assert code == 2


def test_build_patch_parser_returns_parser():
    parser = build_patch_parser()
    assert parser is not None
