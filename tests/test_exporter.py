"""Tests for envguard.exporter."""

from __future__ import annotations

import io
import json

import pytest

from envguard.exporter import ExportFormat, export_dotenv, export_json, export_markdown, render
from envguard.schema import EnvVarSchema, Schema


@pytest.fixture()
def schema() -> Schema:
    return Schema(
        variables={
            "DATABASE_URL": EnvVarSchema(
                required=True,
                type="string",
                description="Postgres connection string",
            ),
            "LOG_LEVEL": EnvVarSchema(
                required=False,
                type="string",
                default="INFO",
                allowed_values=["DEBUG", "INFO", "WARNING", "ERROR"],
                description="Logging verbosity",
            ),
            "MAX_RETRIES": EnvVarSchema(
                required=False,
                type="integer",
                default=3,
            ),
        }
    )


# --- dotenv export ---

def test_dotenv_contains_variable_names(schema: Schema) -> None:
    output = export_dotenv(schema)
    assert "DATABASE_URL=" in output
    assert "LOG_LEVEL=INFO" in output
    assert "MAX_RETRIES=3" in output


def test_dotenv_includes_description_comment(schema: Schema) -> None:
    output = export_dotenv(schema)
    assert "# Postgres connection string" in output
    assert "# Logging verbosity" in output


def test_dotenv_marks_required(schema: Schema) -> None:
    output = export_dotenv(schema)
    assert "required" in output


def test_dotenv_includes_allowed_values(schema: Schema) -> None:
    output = export_dotenv(schema)
    assert "DEBUG,INFO,WARNING,ERROR" in output


# --- JSON export ---

def test_json_is_valid_json(schema: Schema) -> None:
    output = export_json(schema)
    parsed = json.loads(output)
    assert "variables" in parsed


def test_json_contains_all_variables(schema: Schema) -> None:
    parsed = json.loads(export_json(schema))
    assert set(parsed["variables"].keys()) == {"DATABASE_URL", "LOG_LEVEL", "MAX_RETRIES"}


def test_json_required_flag(schema: Schema) -> None:
    parsed = json.loads(export_json(schema))
    assert parsed["variables"]["DATABASE_URL"]["required"] is True
    assert parsed["variables"]["LOG_LEVEL"]["required"] is False


# --- Markdown export ---

def test_markdown_has_header(schema: Schema) -> None:
    output = export_markdown(schema)
    assert "# Environment Variables" in output


def test_markdown_contains_variable_rows(schema: Schema) -> None:
    output = export_markdown(schema)
    assert "`DATABASE_URL`" in output
    assert "`LOG_LEVEL`" in output


# --- render helper ---

def test_render_writes_to_stream(schema: Schema) -> None:
    buf = io.StringIO()
    render(schema, ExportFormat.DOTENV, buf)
    assert "DATABASE_URL" in buf.getvalue()


def test_render_unsupported_format_raises(schema: Schema) -> None:
    buf = io.StringIO()
    with pytest.raises(ValueError, match="Unsupported export format"):
        render(schema, "xml", buf)  # type: ignore[arg-type]
