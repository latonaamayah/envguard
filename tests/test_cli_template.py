import pytest
from pathlib import Path
from envguard.cli_template import build_template_parser, run_template


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path


def _write(p: Path, content: str) -> Path:
    p.write_text(content)
    return p


def _args(tmp_env, env_content, templates, strict=False, fmt="text"):
    env_file = _write(tmp_env / ".env", env_content)
    parser = build_template_parser()
    argv = [str(env_file)]
    for t in templates:
        argv += ["--template", t]
    if strict:
        argv.append("--strict")
    argv += ["--format", fmt]
    return parser.parse_args(argv)


def test_run_template_exits_zero(tmp_env):
    args = _args(tmp_env, "HOST=localhost\nPORT=5432\n", ["URL=postgres://{{HOST}}:{{PORT}}"])
    assert run_template(args) == 0


def test_run_template_missing_file_exits_two(tmp_env):
    parser = build_template_parser()
    args = parser.parse_args(["/no/such/.env", "--template", "X={{Y}}"])
    assert run_template(args) == 2


def test_run_template_no_templates_exits_two(tmp_env):
    env_file = _write(tmp_env / ".env", "HOST=localhost\n")
    parser = build_template_parser()
    args = parser.parse_args([str(env_file)])
    assert run_template(args) == 2


def test_run_template_strict_missing_exits_one(tmp_env):
    args = _args(tmp_env, "HOST=localhost\n", ["X={{MISSING}}"], strict=True)
    assert run_template(args) == 1


def test_run_template_strict_resolved_exits_zero(tmp_env):
    args = _args(tmp_env, "HOST=localhost\n", ["X={{HOST}}"], strict=True)
    assert run_template(args) == 0


def test_run_template_json_format(tmp_env, capsys):
    args = _args(tmp_env, "HOST=db\n", ["CONN={{HOST}}"], fmt="json")
    run_template(args)
    out = capsys.readouterr().out
    import json
    data = json.loads(out)
    assert data["CONN"] == "db"


def test_run_template_text_ok_marker(tmp_env, capsys):
    args = _args(tmp_env, "HOST=db\n", ["CONN={{HOST}}"])
    run_template(args)
    out = capsys.readouterr().out
    assert "[OK]" in out


def test_run_template_text_missing_marker(tmp_env, capsys):
    args = _args(tmp_env, "HOST=db\n", ["CONN={{GONE}}"])
    run_template(args)
    out = capsys.readouterr().out
    assert "[MISSING]" in out
