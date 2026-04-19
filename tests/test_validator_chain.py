import pytest
from envguard.validator_chain import run_chain, ChainResult, ChainStep



def env():
    return {"DB_HOST": "localhost", "PORT": "5432", "SECRET": "abc123"}


def _always_pass(env):
    return True, "ok"


def _always_fail(env):
    return False, "step failed"


def _requires_key(key):
    def _check(env):
        if key in env:
            return True, f"{key} present"
        return False, f"{key} missing"
    return _check


def test_returns_chain_result(env):
    result = run_chain(env, [])
    assert isinstance(result, ChainResult)


def test_empty_steps_no_failures(env):
    result = run_chain(env, [])
    assert not result.has_failures


def test_single_passing_step(env):
    result = run_chain(env, [("check", _always_pass)])
    assert not result.has_failures
    assert len(result.steps) == 1
    assert result.steps[0].passed


def test_single_failing_step(env):
    result = run_chain(env, [("check", _always_fail)])
    assert result.has_failures
    assert result.failed_steps[0].name == "check"


def test_chain_stops_after_first_failure(env):
    steps = [
        ("pass1", _always_pass),
        ("fail1", _always_fail),
        ("pass2", _always_pass),
    ]
    result = run_chain(env, steps)
    assert len(result.steps) == 2
    assert result.steps[-1].name == "fail1"


def test_all_steps_run_when_passing(env):
    steps = [(f"step{i}", _always_pass) for i in range(5)]
    result = run_chain(env, steps)
    assert len(result.steps) == 5
    assert not result.has_failures


def test_requires_key_present(env):
    result = run_chain(env, [("db_host", _requires_key("DB_HOST"))])
    assert not result.has_failures
    assert "present" in result.steps[0].message


def test_requires_key_missing(env):
    result = run_chain(env, [("missing", _requires_key("MISSING_KEY"))])
    assert result.has_failures
    assert "missing" in result.steps[0].message


def test_summary_all_passed(env):
    result = run_chain(env, [("s", _always_pass), ("t", _always_pass)])
    assert "All 2" in result.summary()


def test_summary_with_failure(env):
    result = run_chain(env, [("s", _always_pass), ("t", _always_fail)])
    assert "1/2" in result.summary()


def test_exception_in_step_treated_as_failure(env):
    def _raises(e):
        raise ValueError("boom")
    result = run_chain(env, [("explode", _raises)])
    assert result.has_failures
    assert "boom" in result.steps[0].message


def test_passed_steps_helper(env):
    steps = [("p", _always_pass), ("f", _always_fail)]
    result = run_chain(env, steps)
    assert len(result.passed_steps) == 1
    assert result.passed_steps[0].name == "p"
