"""Tests for envguard.evaluator."""
import pytest

from envguard.schema import Schema, EnvVarSchema
from envguard.evaluator import evaluate, EvaluationResult


@pytest.fixture()
def schema() -> Schema:
    return Schema(
        variables=[
            EnvVarSchema(name="APP_ENV", required=True, type="string"),
            EnvVarSchema(name="PORT", required=True, type="integer"),
            EnvVarSchema(name="DEBUG", required=False, type="boolean"),
        ]
    )


def test_returns_evaluation_result(schema):
    env = {"APP_ENV": "production", "PORT": "8080", "DEBUG": "false"}
    result = evaluate(env, schema)
    assert isinstance(result, EvaluationResult)


def test_perfect_score_all_valid(schema):
    env = {"APP_ENV": "production", "PORT": "8080", "DEBUG": "false"}
    result = evaluate(env, schema)
    assert result.score == 100
    assert result.grade == "A"


def test_grade_f_all_missing(schema):
    result = evaluate({}, schema)
    assert result.grade == "F"
    assert result.score < 40


def test_failed_count_reflects_errors(schema):
    env = {"APP_ENV": "production"}  # PORT missing, DEBUG missing (optional)
    result = evaluate(env, schema)
    assert result.failed >= 1


def test_passed_count_correct(schema):
    env = {"APP_ENV": "production", "PORT": "8080", "DEBUG": "true"}
    result = evaluate(env, schema)
    assert result.passed == 3


def test_has_failures_true_when_errors(schema):
    result = evaluate({}, schema)
    assert result.has_failures is True


def test_has_failures_false_when_clean(schema):
    env = {"APP_ENV": "production", "PORT": "8080", "DEBUG": "false"}
    result = evaluate(env, schema)
    assert result.has_failures is False


def test_summary_contains_score(schema):
    env = {"APP_ENV": "production", "PORT": "8080", "DEBUG": "false"}
    result = evaluate(env, schema)
    assert "Score:" in result.summary()
    assert "Grade:" in result.summary()


def test_notes_present(schema):
    env = {"APP_ENV": "production", "PORT": "8080", "DEBUG": "false"}
    result = evaluate(env, schema)
    assert len(result.notes) >= 1


def test_breakdown_keys_present(schema):
    env = {"APP_ENV": "production", "PORT": "8080"}
    result = evaluate(env, schema)
    assert "error_penalty" in result.breakdown
    assert "warning_penalty" in result.breakdown
