# Caster

The `caster` module casts raw string values from a `.env` file into typed Python objects based on a caller-supplied type map.

## Supported Types

| Type     | Example input | Result        |
|----------|--------------|---------------|
| `int`    | `"8080"`     | `8080`        |
| `float`  | `"3.14"`     | `3.14`        |
| `bool`   | `"true"`     | `True`        |
| `str`    | `"myapp"`    | `"myapp"`     |

Boolean truthy values: `true`, `1`, `yes`, `on`.  
Boolean falsy values: `false`, `0`, `no`, `off`.

## Usage

```python
from envguard.caster import cast

env = {"PORT": "8080", "DEBUG": "true", "NAME": "myapp"}
type_map = {"PORT": "int", "DEBUG": "bool"}

result = cast(env, type_map)
print(result.as_dict)  # {"PORT": 8080, "DEBUG": True, "NAME": "myapp"}
```

## API

### `cast(env, type_map) -> CastResult`

Casts each key in `env` using the type declared in `type_map`. Keys not present in `type_map` default to `str`.

### `CastResult`

| Attribute / Method | Description |
|--------------------|-------------|
| `entries`          | List of `CastEntry` objects |
| `has_errors`       | `True` if any cast failed |
| `failed_keys`      | List of keys that could not be cast |
| `as_dict`          | Dict of successfully cast key→value pairs |
| `summary()`        | Human-readable summary string |

### `CastEntry`

| Field         | Description |
|---------------|-------------|
| `key`         | Variable name |
| `raw`         | Original string value |
| `cast`        | Converted value (or original on error) |
| `target_type` | Requested type string |
| `error`       | Error message if cast failed, else `None` |
