"""Tests for the reporter module."""

import json

import pytest

from envguard.reporter import OutputFormat, render
from envguard.validator import ValidationResult


@pytest.fixture
def valid_result() -> ValidationResult:
    result = ValidationResult()
    return result


@pytest.fixture
def failed_result() -> ValidationResult:
    result = ValidationResult()
    result.add_error("DATABASE_URL is required but missing")
    result.add_warning("DEBUG is set but not defined in schema")
    return result


def test_render_text_valid(valid_result: ValidationResult) -> None:
    output = render(valid_result, fmt=OutputFormat.TEXT, use_color=False)
    assert "valid" in output.lower()
    assert "ERROR" not in output
    assert "WARN" not in output


def test_render_text_with_errors(failed_result: ValidationResult) -> None:
    output = render(failed_result, fmt=OutputFormat.TEXT, use_color=False)
    assert "[ERROR]" in output
    assert "DATABASE_URL is required but missing" in output


def test_render_text_with_warnings(failed_result: ValidationResult) -> None:
    output = render(failed_result, fmt=OutputFormat.TEXT, use_color=False)
    assert "[WARN]" in output
    assert "DEBUG is set but not defined in schema" in output


def test_render_json_valid(valid_result: ValidationResult) -> None:
    output = render(valid_result, fmt=OutputFormat.JSON)
    data = json.loads(output)
    assert data["valid"] is True
    assert data["errors"] == []
    assert data["warnings"] == []


def test_render_json_failed(failed_result: ValidationResult) -> None:
    output = render(failed_result, fmt=OutputFormat.JSON)
    data = json.loads(output)
    assert data["valid"] is False
    assert len(data["errors"]) == 1
    assert len(data["warnings"]) == 1


def test_render_text_color_codes_present(failed_result: ValidationResult) -> None:
    output = render(failed_result, fmt=OutputFormat.TEXT, use_color=True)
    # ANSI escape codes should be present when color is enabled
    assert "\033[" in output


def test_render_text_no_color_codes(failed_result: ValidationResult) -> None:
    output = render(failed_result, fmt=OutputFormat.TEXT, use_color=False)
    assert "\033[" not in output
