# Redactor

The `envguard.redactor` module replaces sensitive environment variable values
with a placeholder token so that `.env` contents can be safely logged, printed,
or exported without leaking secrets.

## Usage

```python
from envguard.redactor import redact

env = {
    "APP_ENV": "production",
    "DB_HOST": "localhost",
    "DB_PASSWORD": "s3cr3t",
    "GITHUB_TOKEN": "ghp_abc123",
}

result = redact(env)
print(result.redacted)
# {
#   "APP_ENV": "production",
#   "DB_HOST": "localhost",
#   "DB_PASSWORD": "[REDACTED]",
#   "GITHUB_TOKEN": "[REDACTED]",
# }
```

## API

### `redact(env, placeholder="[REDACTED]", extra_keys=None) -> RedactResult`

| Parameter | Type | Description |
|---|---|---|
| `env` | `dict[str, str]` | Environment variables to process |
| `placeholder` | `str` | Replacement string for sensitive values |
| `extra_keys` | `list[str] \| None` | Additional keys to treat as sensitive |

### `RedactResult`

| Attribute | Type | Description |
|---|---|---|
| `original` | `dict[str, str]` | Unmodified copy of the input |
| `redacted` | `dict[str, str]` | Output with sensitive values replaced |
| `redacted_keys` | `list[str]` | Names of keys that were redacted |

#### Methods

- **`has_redacted() -> bool`** — `True` when at least one value was redacted.
- **`summary() -> str`** — Human-readable count, e.g. `"2/5 variable(s) redacted."`

## Sensitive key detection

A key is considered sensitive when its lowercase name contains any of:
`password`, `passwd`, `secret`, `token`, `api_key`, `apikey`, `auth`,
`credential`, `private`, `access_key`, `signing`.

Additional keys can be passed via the `extra_keys` parameter (case-insensitive).
