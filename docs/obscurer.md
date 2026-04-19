# Obscurer

The `obscurer` module masks sensitive environment variable values using configurable styles.

## Usage

```python
from envguard.obscurer import obscure

env = {
    "DB_PASSWORD": "supersecret",
    "API_TOKEN": "tok_abc123",
    "APP_HOST": "localhost",
}

result = obscure(env, style="partial")
print(result.summary())       # e.g. "2/3 keys obscured"
print(result.as_dict())       # {"DB_PASSWORD": "su*******et", ...}
print(result.obscured_keys()) # ["DB_PASSWORD", "API_TOKEN"]
```

## Styles

| Style     | Description                                      |
|-----------|--------------------------------------------------|
| `stars`   | Replaces entire value with `*` characters        |
| `partial` | Shows first 2 and last 2 characters, masks rest  |
| `hash`    | Replaces value with an 8-char SHA-256 prefix     |

## Sensitive Key Detection

Keys are considered sensitive if their name contains any of:
`password`, `secret`, `token`, `api_key`, `apikey`, `private`, `auth`

## Custom Keys

Pass an explicit list of keys to override automatic detection:

```python
result = obscure(env, keys=["MY_CUSTOM_KEY"])
```

## API

### `obscure(env, style="stars", keys=None) -> ObscureResult`

- `env`: dict of environment variables
- `style`: one of `stars`, `partial`, `hash`
- `keys`: optional list of keys to obscure (overrides auto-detection)

### `ObscureResult`

- `.has_obscured()` — True if any keys were obscured
- `.obscured_keys()` — list of obscured key names
- `.as_dict()` — full env dict with obscured values applied
- `.summary()` — human-readable summary string
