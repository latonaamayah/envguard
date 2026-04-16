import pytest
from envguard.scorer import score, ScoreResult, ScoreEntry


@pytest.fixture
def env():
    return {
        "DATABASE_URL": "postgres://localhost/db",
        "API_KEY": "secret123",
        "debug": "",
        "PORT": "8080",
    }


def test_returns_score_result(env):
    result = score(env)
    assert isinstance(result, ScoreResult)


def test_entry_count_matches_env(env):
    result = score(env)
    assert len(result.entries) == len(env)


def test_has_entries_true(env):
    result = score(env)
    assert result.has_entries


def test_has_entries_false_empty():
    result = score({})
    assert not result.has_entries


def test_max_total_is_ten_per_key(env):
    result = score(env)
    assert result.max_total == len(env) * 10


def test_uppercase_key_scores_higher():
    result = score({"PORT": "8080"})
    entry = result.entries[0]
    assert entry.points == 10


def test_empty_value_loses_points():
    result = score({"PORT": ""})
    entry = result.entries[0]
    assert entry.points < 10


def test_lowercase_key_loses_points():
    result = score({"debug": "true"})
    entry = result.entries[0]
    assert entry.points < 10


def test_percent_between_0_and_100(env):
    result = score(env)
    assert 0.0 <= result.percent <= 100.0


def test_grade_a_for_perfect():
    result = score({"HOST": "localhost", "PORT": "8080"})
    assert result.grade == "A"


def test_grade_f_for_empty_values():
    result = score({"a": "", "b": ""})
    assert result.grade == "F"


def test_summary_contains_grade(env):
    result = score(env)
    assert result.grade in result.summary()


def test_empty_env_percent_zero():
    result = score({})
    assert result.percent == 0.0
