# envguard Linter

The **linter** module inspects `.env` file values against your schema and
reports style and best-practice issues *before* they reach production.

## What it checks

| Check | Severity | Description |
|---|---|---|
| Empty required variable | error | A variable marked `required: true` is present in the file but has an empty value. |
| Sensitive key without description | warning | Variables whose names contain `SECRET`, `PASSWORD`, `TOKEN`, `KEY`, or `PASS` should have a `description` in the schema. |
| Value exceeds 512 characters | warning | Unusually long values may indicate a pasted blob or misconfiguration. |
| Leading / trailing whitespace | warning | Whitespace around values is almost always unintentional and can cause subtle bugs. |

## Usage

```python
from envguard.loader import load_env_file
from envguard.schema import Schema
from envguard.linter import lint

env = load_env_file(".env")
schema = Schema.from_file("envguard.schema.yml")

result = lint(env, schema)

if result.has_issues:
    for issue in result.issues:
        print(f"[{issue.severity.upper()}] {issue.key}: {issue.message}")
    print(result.summary())
```

## LintResult API

### Properties

- **`has_issues`** – `True` if any issues were found.
- **`errors`** – List of issues with `severity == "error"`.
- **`warnings`** – List of issues with `severity == "warning"`.

### Methods

- **`summary()`** – Returns a human-readable summary string.

## LintIssue fields

| Field | Type | Description |
|---|---|---|
| `key` | `str` | The environment variable name. |
| `message` | `str` | Human-readable explanation of the issue. |
| `severity` | `str` | Either `"error"` or `"warning"`. |

## Exit codes (CLI integration — coming soon)

| Code | Meaning |
|---|---|
| `0` | No lint issues. |
| `1` | One or more **errors** found. |
| `2` | Only **warnings** found (configurable). |
