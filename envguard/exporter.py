"""Export validated env schemas to various formats (dotenv template, JSON, Markdown)."""

from __future__ import annotations

import json
from enum import Enum
from typing import IO

from envguard.schema import Schema


class ExportFormat(str, Enum):
    DOTENV = "dotenv"
    JSON = "json"
    MARKDOWN = "markdown"


def export_dotenv(schema: Schema) -> str:
    """Generate a .env.example template from the schema."""
    lines: list[str] = []
    for name, var in schema.variables.items():
        if var.description:
            lines.append(f"# {var.description}")
        parts = []
        if var.required:
            parts.append("required")
        if var.type:
            parts.append(f"type={var.type}")
        if var.allowed_values:
            parts.append(f"allowed={','.join(str(v) for v in var.allowed_values)}")
        if parts:
            lines.append(f"# [{', '.join(parts)}]")
        default = var.default if var.default is not None else ""
        lines.append(f"{name}={default}")
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


def export_json(schema: Schema) -> str:
    """Serialize the schema to a JSON string."""
    data: dict = {}
    for name, var in schema.variables.items():
        entry: dict = {"required": var.required}
        if var.type:
            entry["type"] = var.type
        if var.default is not None:
            entry["default"] = var.default
        if var.allowed_values:
            entry["allowed_values"] = list(var.allowed_values)
        if var.description:
            entry["description"] = var.description
        data[name] = entry
    return json.dumps({"variables": data}, indent=2) + "\n"


def export_markdown(schema: Schema) -> str:
    """Generate a Markdown reference table from the schema."""
    lines = [
        "# Environment Variables",
        "",
        "| Variable | Required | Type | Default | Allowed Values | Description |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for name, var in schema.variables.items():
        required = "Yes" if var.required else "No"
        type_ = var.type or "-"
        default = str(var.default) if var.default is not None else "-"
        allowed = ", ".join(str(v) for v in var.allowed_values) if var.allowed_values else "-"
        description = var.description or "-"
        lines.append(f"| `{name}` | {required} | {type_} | {default} | {allowed} | {description} |")
    lines.append("")
    return "\n".join(lines)


_EXPORTERS = {
    ExportFormat.DOTENV: export_dotenv,
    ExportFormat.JSON: export_json,
    ExportFormat.MARKDOWN: export_markdown,
}


def render(schema: Schema, fmt: ExportFormat, out: IO[str]) -> None:
    """Write the exported schema to *out* in the requested format.

    Raises
    ------
    ValueError
        If *fmt* is not a recognised :class:`ExportFormat` value.
    """
    exporter = _EXPORTERS.get(fmt)
    if exporter is None:
        raise ValueError(f"Unsupported export format: {fmt}")
    out.write(exporter(schema))
