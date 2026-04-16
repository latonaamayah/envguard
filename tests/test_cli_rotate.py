import argparse
import pytest
from pathlib import Path
from envguard.cli_rotate import run_rotate


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path


def _write(p: Path, content: str) -> Path:
    p.write_text(content)
    return p


def _args(**kwargs) -> argparse.Namespace:
    defaults = dict(env_file=None, keys=None, length=32, output=None)
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_run_rotate_exits_zero(tmp_env):
    f = _write(tmp_env / ".env", "SECRET=old\nTOKEN=abc\n")
    assert run_rotate(_args(env_file=str(f))) == 0


def test_run_rotate_missing_file_exits_two(tmp_env):
    assert run_rotate(_args(env_file=str(tmp_env / "missing.env"))) == 2


def test_run_rotate_outputs_all_keys(tmp_env, capsys):
    f = _write(tmp_env / ".env", "SECRET=old\nTOKEN=abc\n")
    run_rotate(_args(env_file=str(f)))
    out = capsys.readouterr().out
    assert "SECRET=" in out
    assert "TOKEN=" in out


def test_run_rotate_selected_key_only(tmp_env, capsys):
    f = _write(tmp_env / ".env", "SECRET=old\nAPP_NAME=myapp\n")
    run_rotate(_args(env_file=str(f), keys=["SECRET"]))
    out = capsys.readouterr().out
    assert "APP_NAME=myapp" in out


def test_run_rotate_writes_output_file(tmp_env):
    f = _write(tmp_env / ".env", "SECRET=old\n")
    out_file = tmp_env / "rotated.env"
    run_rotate(_args(env_file=str(f), output=str(out_file)))
    assert out_file.exists()
    content = out_file.read_text()
    assert "SECRET=" in content


def test_run_rotate_output_value_differs(tmp_env):
    f = _write(tmp_env / ".env", "SECRET=old_value\n")
    out_file = tmp_env / "rotated.env"
    run_rotate(_args(env_file=str(f), output=str(out_file)))
    content = out_file.read_text()
    assert "old_value" not in content
