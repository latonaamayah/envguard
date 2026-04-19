import pytest
import json
from pathlib import Path
from envguard.cli_vault import build_vault_parser, run_vault


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path


def _write(p: Path, content: str) -> Path:
    f = p / ".env"
    f.write_text(content)
    return f


def _args(env_file, keys=None, as_json=False):
    parser = build_vault_parser()
    argv = [str(env_file)]
    if keys:
        argv += ["--keys"] + keys
    if as_json:
        argv.append("--json")
    return parser.parse_args(argv)


def test_run_vault_exits_zero(tmp_env):
    f = _write(tmp_env, "DB_PASSWORD=secret\nAPI_KEY=abc123\n")
    assert run_vault(_args(f)) == 0


def test_run_vault_missing_file_exits_two(tmp_env):
    args = _args(tmp_env / "missing.env")
    assert run_vault(args) == 2


def test_run_vault_json_output(tmp_env, capsys):
    f = _write(tmp_env, "DB_PASSWORD=secret\n")
    run_vault(_args(f, as_json=True))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "DB_PASSWORD" in data


def test_run_vault_selected_keys_only(tmp_env, capsys):
    f = _write(tmp_env, "DB_PASSWORD=secret\nAPI_KEY=abc123\n")
    run_vault(_args(f, keys=["DB_PASSWORD"]))
    out = capsys.readouterr().out
    assert "DB_PASSWORD" in out
    assert "API_KEY" not in out


def test_run_vault_text_output_contains_stars(tmp_env, capsys):
    f = _write(tmp_env, "DB_PASSWORD=supersecret\n")
    run_vault(_args(f))
    out = capsys.readouterr().out
    assert "*" in out
