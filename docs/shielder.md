# Shielder

The `shielder` module replaces sensitive `.env` values with placeholder references, making it safe to commit or share configuration files without exposing secrets.

## Usage

```python
from envguard.shielder import shield

env = {
    "DB_HOST": "localhost",
    "DB_PASSWORD": "supersecret",
    "API_KEY": "abc123",
}

result = shield(env)
print(result.summary())      # "2/3 keys shielded"
print(result.shielded_keys)  # ["DB_PASSWORD", "API_KEY"]
print(result.as_dict)        # {"DB_HOST": "localhost", "DB_PASSWORD": "${DB_PASSWORD}", ...}
```

## Auto-detection

By default, `shield()` identifies sensitive keys by checking whether the key name (case-insensitive) contains any of the following patterns:

- `password`
- `secret`
- `token`
- `api_key` / `apikey`
- `private`
- `auth`

## Explicit Key List

Pass a list of keys to shield only those specific variables, bypassing auto-detection:

```python
result = shield(env, keys=["DB_HOST", "APP_NAME"])
```

## Custom Placeholders

The default placeholder format is `${KEY}`. You can customise the prefix and suffix:

```python
result = shield(env, prefix="%{", suffix="}")
# DB_PASSWORD -> %{DB_PASSWORD}
```

## API Reference

### `shield(env, keys=None, prefix="${", suffix="}")`

| Parameter | Type | Description |
|-----------|------|-------------|
| `env` | `dict` | Input environment mapping |
| `keys` | `list \| None` | Explicit keys to shield; `None` triggers auto-detection |
| `prefix` | `str` | Placeholder prefix (default `${`) |
| `suffix` | `str` | Placeholder suffix (default `}`) |

Returns a `ShieldResult` object.

### `ShieldResult`

| Attribute / Method | Description |
|--------------------|-------------|
| `entries` | List of `ShieldEntry` objects |
| `has_shielded` | `True` if any key was shielded |
| `shielded_keys` | List of keys that were shielded |
| `as_dict` | Final env dict with shielded values |
| `summary()` | Human-readable summary string |
