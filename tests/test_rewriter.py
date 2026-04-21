"""Tests for envguard.rewriter."""
import pytest
from envguard.rewriter import rewrite, RewriteEntry, RewriteResult


@pytest.fixture()
def lines():
    return [
        "# Database config\n",
        "DB_HOST=localhost\n",
        "DB_PORT=5432\n",
        "\n",
        "APP_ENV=development\n",
        "SECRET_KEY=old-secret\n",
    ]


def test_returns_rewrite_result(lines):
    result = rewrite(lines, {})
    assert isinstance(result, RewriteResult)


def test_no_changes_when_updates_empty(lines):
    result = rewrite(lines, {})
    assert not result.has_changes
    assert result.changed_keys == []


def test_single_key_rewritten(lines):
    result = rewrite(lines, {"DB_HOST": "db.prod.example.com"})
    assert result.has_changes
    assert "DB_HOST" in result.changed_keys


def test_rewritten_value_in_output(lines):
    result = rewrite(lines, {"DB_HOST": "db.prod.example.com"})
    dotenv = result.as_dotenv()
    assert "DB_HOST=db.prod.example.com" in dotenv


def test_unchanged_keys_preserved(lines):
    result = rewrite(lines, {"DB_HOST": "newhost"})
    dotenv = result.as_dotenv()
    assert "DB_PORT=5432" in dotenv
    assert "APP_ENV=development" in dotenv


def test_multiple_keys_rewritten(lines):
    result = rewrite(lines, {"DB_PORT": "3306", "APP_ENV": "production"})
    assert set(result.changed_keys) == {"DB_PORT", "APP_ENV"}


def test_comments_preserved(lines):
    result = rewrite(lines, {"DB_HOST": "newhost"})
    assert "# Database config" in result.as_dotenv()


def test_blank_lines_preserved(lines):
    result = rewrite(lines, {})
    out = result.lines
    assert "" in out


def test_new_key_appended_when_not_in_file(lines):
    result = rewrite(lines, {"NEW_VAR": "hello"})
    dotenv = result.as_dotenv()
    assert "NEW_VAR=hello" in dotenv
    assert "NEW_VAR" in result.changed_keys


def test_entry_old_value_is_none_for_new_key(lines):
    result = rewrite(lines, {"BRAND_NEW": "value"})
    entry = next(e for e in result.entries if e.key == "BRAND_NEW")
    assert entry.old_value is None


def test_entry_changed_false_when_value_same(lines):
    result = rewrite(lines, {"DB_PORT": "5432"})
    entry = next(e for e in result.entries if e.key == "DB_PORT")
    assert not entry.changed
    assert "DB_PORT" not in result.changed_keys


def test_summary_no_changes(lines):
    result = rewrite(lines, {"APP_ENV": "development"})
    assert result.summary() == "No keys rewritten."


def test_summary_with_changes(lines):
    result = rewrite(lines, {"SECRET_KEY": "new-secret"})
    assert "SECRET_KEY" in result.summary()
    assert "1 key(s)" in result.summary()
