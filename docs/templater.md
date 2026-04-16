# envguard templater

The `templater` module renders template strings using values from a `.env` file.
Placeholders use `{{VAR_NAME}}` syntax and are replaced with matching env values.

## Usage

```python
from envguard.templater import render_templates

context = {"HOST": "localhost", "PORT": "5432"}
templates = {"DB_URL": "postgres://{{HOST}}:{{PORT}}/mydb"}

result = render_templates(templates, context)
print(result.as_dict())
# {'DB_URL': 'postgres://localhost:5432/mydb'}
```

## Strict Mode

Pass `strict=True` to collect errors for any placeholder that cannot be resolved:

```python
result = render_templates({"X": "{{MISSING}}"}, context, strict=True)
if result.has_errors:
    for e in result.errors:
        print(e)
```

## CLI

```bash
envguard-template .env \
  --template DB_URL=postgres://{{HOST}}:{{PORT}}/db \
  --template REDIS_URL=redis://{{HOST}}:6379 \
  --strict
```

Options:

| Flag | Description |
|------|-------------|
| `--template KEY=TMPL` | Template entry (repeatable) |
| `--strict` | Exit 1 if any placeholder is unresolved |
| `--format text\|json` | Output format (default: text) |

## TemplateEntry

| Field | Type | Description |
|-------|------|-------------|
| `key` | str | Output key name |
| `template` | str | Original template string |
| `rendered` | str | Rendered value |
| `missing_vars` | list[str] | Unresolved placeholder names |
