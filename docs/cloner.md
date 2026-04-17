# Cloner

The `cloner` module allows you to duplicate environment variables under new key names, optionally transforming their values.

## Usage

```python
from envguard.cloner import clone

env = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
}

result = clone(env, mapping={"DB_HOST": "DATABASE_HOST", "DB_PORT": "DATABASE_PORT"})

print(result.summary())
# Cloned 2 key(s):
#   DB_HOST -> DATABASE_HOST
#   DB_PORT -> DATABASE_PORT
```

## Value Transforms

You can optionally transform cloned values:

```python
result = clone(env, mapping={"DB_HOST": "DB_HOST_UPPER"}, transform="upper")
# DB_HOST_UPPER = "LOCALHOST"
```

Supported transforms:
- `upper` — converts value to uppercase
- `lower` — converts value to lowercase
- `None` — no transformation (default)

## API

### `clone(env, mapping, transform=None) -> CloneResult`

| Parameter   | Type              | Description                              |
|-------------|-------------------|------------------------------------------|
| `env`       | `Dict[str, str]`  | Source environment variables             |
| `mapping`   | `Dict[str, str]`  | `{source_key: new_key}` pairs            |
| `transform` | `str` or `None`   | Optional value transform                 |

### `CloneResult`

| Attribute      | Type               | Description                          |
|----------------|--------------------|--------------------------------------|
| `entries`      | `List[CloneEntry]` | Successfully cloned entries          |
| `skipped`      | `List[str]`        | Keys not found in source env         |
| `has_clones`   | `bool`             | Whether any clones were made         |
| `cloned_keys`  | `List[str]`        | New key names created                |
| `as_dict()`    | `Dict[str, str]`   | Cloned vars as a plain dictionary    |
| `summary()`    | `str`              | Human-readable summary               |
