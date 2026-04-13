"""Tests for envguard.loader module."""

import pytest
from pathlib import Path

from envguard.loader import (
    load_env_file,
    load_env_file_safe,
    EnvFileNotFoundError,
    EnvParseError,
)


@pytest.fixture
def tmp_env(tmp_path):
    """Helper that writes content to a temp .env file and returns its path."""
    def _write(content: str) -> str:
        env_file = tmp_path / ".env"
        env_file.write_text(content, encoding="utf-8")
        return str(env_file)
    return _write


def test_load_simple_key_value(tmp_env):
    path = tmp_env("KEY=value\n")
    result = load_env_file(path)
    assert result == {"KEY": "value"}


def test_load_multiple_vars(tmp_env):
    path = tmp_env("HOST=localhost\nPORT=5432\nDEBUG=true\n")
    result = load_env_file(path)
    assert result == {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}


def test_skip_blank_lines_and_comments(tmp_env):
    content = "# This is a comment\n\nKEY=value\n\n# Another comment\n"
    path = tmp_env(content)
    result = load_env_file(path)
    assert result == {"KEY": "value"}


def test_strip_double_quotes(tmp_env):
    path = tmp_env('KEY="hello world"\n')
    result = load_env_file(path)
    assert result["KEY"] == "hello world"


def test_strip_single_quotes(tmp_env):
    path = tmp_env("KEY='hello world'\n")
    result = load_env_file(path)
    assert result["KEY"] == "hello world"


def test_inline_comment_stripped(tmp_env):
    path = tmp_env("KEY=value # this is ignored\n")
    result = load_env_file(path)
    assert result["KEY"] == "value"


def test_value_with_equals_sign(tmp_env):
    path = tmp_env("KEY=a=b=c\n")
    result = load_env_file(path)
    assert result["KEY"] == "a=b=c"


def test_file_not_found_raises():
    with pytest.raises(EnvFileNotFoundError):
        load_env_file("/nonexistent/path/.env")


def test_malformed_line_raises(tmp_env):
    path = tmp_env("BADLINE\n")
    with pytest.raises(EnvParseError, match="missing '='")
        load_env_file(path)


def test_empty_key_raises(tmp_env):
    path = tmp_env("=value\n")
    with pytest.raises(EnvParseError, match="empty key"):
        load_env_file(path)


def test_load_env_file_safe_returns_none_on_missing():
    result = load_env_file_safe("/nonexistent/.env")
    assert result is None


def test_load_env_file_safe_returns_dict_on_success(tmp_env):
    path = tmp_env("KEY=val\n")
    result = load_env_file_safe(path)
    assert result == {"KEY": "val"}
