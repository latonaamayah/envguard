# Masker

The `envguard.masker` module provides utilities for **redacting sensitive environment variable values** before printing, logging, or exporting them.

## Why masking matters

When debugging or auditing `.env` files it is often necessary to display variable names and values. However, secrets such as passwords, API tokens, and private keys must never appear in plain text in logs or CLI output.

The masker detects sensitive keys automatically based on common naming conventions and replaces their values with a configurable mask string.

## Usage

```python
from envguard.masker import mask

env = {
    "APP_ENV": "production",
    "DB_HOST": "localhost",
    "DB_PASSWORD": "s3cr3t!",
    "STRIPE_API_KEY": "sk_live_abc123",
}

result = mask(env)
print(result.masked)
# {
#   'APP_ENV': 'production',
#   'DB_HOST': 'localhost',
#   'DB_PASSWORD': '***',
#   'STRIPE_API_KEY': '***',
# }

print(result.summary())
# Masked 2 sensitive key(s): DB_PASSWORD, STRIPE_API_KEY
```

## Options

| Parameter | Type | Default | Description |
|---|---|---|---|
| `env` | `dict` | — | The environment variable mapping to process |
| `extra_sensitive` | `list[str]` | `None` | Additional key names to treat as sensitive |
| `mask_char` | `str` | `"***"` | Replacement string for masked values |
| `reveal_prefix` | `int` | `0` | Number of leading characters to keep visible |

### Partial reveal

Sometimes it is useful to show the first few characters of a secret for identification without exposing the full value:

```python
result = mask(env, reveal_prefix=4)
# DB_PASSWORD → 's3cr***'
```

## Sensitive keyword detection

A key is considered sensitive when its lowercased name contains any of the following substrings:

`password`, `passwd`, `secret`, `token`, `api_key`, `apikey`, `auth`, `credential`, `private`, `key`, `cert`, `pwd`

Additional keys can always be passed via `extra_sensitive`.

## MaskResult

| Attribute | Type | Description |
|---|---|---|
| `original` | `dict` | Unmodified copy of the input env |
| `masked` | `dict` | Env with sensitive values replaced |
| `masked_keys` | `list[str]` | Sorted list of keys that were masked |
| `has_masked` | `bool` | `True` if at least one key was masked |
| `summary()` | `str` | Human-readable summary of masking activity |
