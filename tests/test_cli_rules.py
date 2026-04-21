"""Tests for envguard.cli_rules."""
import argparse
import os
import tempfile

import pytest

from envguard.cli_rules import build_rules_parser, run_rules, _parse_rule_pairs


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path


def _write(path, content: str):
    path.write_text(content)
    return str(path)


def _args(env_file, rule_pairs=None, severity="error", strict=False, list_rules=False):
    return argparse.Namespace(
        env_file=env_file,
        rule_pairs=rule_pairs or [],
        severity=severity,
        strict=strict,
        list_rules=list_rules,
    )


def test_run_rules_exits_zero_no_rules(tmp_env):
    f = _write(tmp_env / ".env", "DB_HOST=localhost\n")
    assert run_rules(_args(f)) == 0


def test_run_rules_passes_valid_value(tmp_env):
    f = _write(tmp_env / ".env", "DB_HOST=localhost\n")
    assert run_rules(_args(f, rule_pairs=["not_empty:DB_HOST"])) == 0


def test_run_rules_fails_empty_value(tmp_env):
    f = _write(tmp_env / ".env", "DB_HOST=\n")
    assert run_rules(_args(f, rule_pairs=["not_empty:DB_HOST"])) == 1


def test_run_rules_warning_severity_exits_zero_without_strict(tmp_env):
    f = _write(tmp_env / ".env", "DB_HOST=\n")
    assert run_rules(_args(f, rule_pairs=["not_empty:DB_HOST"], severity="warning")) == 0


def test_run_rules_warning_severity_exits_one_with_strict(tmp_env):
    f = _write(tmp_env / ".env", "DB_HOST=\n")
    assert run_rules(_args(f, rule_pairs=["not_empty:DB_HOST"], severity="warning", strict=True)) == 1


def test_run_rules_missing_file_exits_two(tmp_env):
    assert run_rules(_args(str(tmp_env / "missing.env"))) == 2


def test_run_rules_list_rules_exits_zero(tmp_env, capsys):
    f = _write(tmp_env / ".env", "K=V\n")
    code = run_rules(_args(f, list_rules=True))
    assert code == 0
    out = capsys.readouterr().out
    assert "not_empty" in out


def test_parse_rule_pairs_single():
    result = _parse_rule_pairs(["not_empty:DB_HOST"])
    assert result == {"not_empty": ["DB_HOST"]}


def test_parse_rule_pairs_multiple_keys_same_rule():
    result = _parse_rule_pairs(["not_empty:A", "not_empty:B"])
    assert result["not_empty"] == ["A", "B"]


def test_parse_rule_pairs_skips_invalid_format():
    result = _parse_rule_pairs(["invalid_no_colon"])
    assert result == {}


def test_build_rules_parser_returns_parser():
    parser = build_rules_parser()
    assert isinstance(parser, argparse.ArgumentParser)
