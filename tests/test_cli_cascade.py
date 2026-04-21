import argparse
import os
import pytest
from envguard.cli_cascade import build_cascade_parser, run_cascade


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path


def _write(path, content: str):
    path.write_text(content)
    return str(path)


def _args(files, strict=False, show_overrides=False):
    return argparse.Namespace(
        files=files,
        strict=strict,
        show_overrides=show_overrides,
    )


def test_run_cascade_exits_zero(tmp_env):
    f1 = _write(tmp_env / "base.env", "DB_HOST=localhost\nAPP_ENV=dev\n")
    f2 = _write(tmp_env / "prod.env", "APP_ENV=production\n")
    code = run_cascade(_args([f1, f2]))
    assert code == 0


def test_run_cascade_missing_file_exits_two(tmp_env):
    code = run_cascade(_args(["/nonexistent/.env"]))
    assert code == 2


def test_run_cascade_merged_output(tmp_env, capsys):
    f1 = _write(tmp_env / "a.env", "KEY_A=val_a\n")
    f2 = _write(tmp_env / "b.env", "KEY_B=val_b\n")
    run_cascade(_args([f1, f2]))
    out = capsys.readouterr().out
    assert "KEY_A=val_a" in out
    assert "KEY_B=val_b" in out


def test_run_cascade_override_detected_strict_exits_one(tmp_env):
    f1 = _write(tmp_env / "base.env", "DB_HOST=localhost\n")
    f2 = _write(tmp_env / "prod.env", "DB_HOST=prod.db.example.com\n")
    code = run_cascade(_args([f1, f2], strict=True))
    assert code == 1


def test_run_cascade_no_override_strict_exits_zero(tmp_env):
    f1 = _write(tmp_env / "base.env", "KEY_A=a\n")
    f2 = _write(tmp_env / "prod.env", "KEY_B=b\n")
    code = run_cascade(_args([f1, f2], strict=True))
    assert code == 0


def test_run_cascade_show_overrides_prints_message(tmp_env, capsys):
    f1 = _write(tmp_env / "base.env", "DB_HOST=localhost\n")
    f2 = _write(tmp_env / "prod.env", "DB_HOST=prod.db\n")
    run_cascade(_args([f1, f2], show_overrides=True))
    out = capsys.readouterr().out
    assert "overrides" in out.lower() or "overridden" in out.lower()


def test_build_cascade_parser_returns_parser():
    parser = build_cascade_parser()
    assert parser is not None
