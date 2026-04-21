# Cascader

The `cascader` module merges multiple `.env` dictionaries in cascade order. Later layers override earlier ones, and all overrides are tracked for auditing.

## Usage

```python
from envguard.cascader import cascade

base = {"DB_HOST": "localhost", "APP_ENV": "development"}
production = {"DB_HOST": "prod.db.example.com", "APP_SECRET": "s3cr3t"}

result = cascade([base, production], layer_names=["base", "production"])

print(result.merged)
# {'DB_HOST': 'prod.db.example.com', 'APP_ENV': 'development', 'APP_SECRET': 's3cr3t'}

print(result.has_overrides)   # True
print(result.overridden_keys) # ['DB_HOST']
print(result.summary())
# 3 key(s) resolved across 2 layer(s); 1 override(s) applied.
```

## API

### `cascade(layers, layer_names=None) -> CascadeResult`

Merges a list of `Dict[str, str]` in order. The last layer wins on conflicts.

| Parameter     | Type                    | Description                                    |
|---------------|-------------------------|------------------------------------------------|
| `layers`      | `List[Dict[str, str]]`  | Ordered list of env dictionaries               |
| `layer_names` | `Optional[List[str]]`   | Human-readable names for each layer (optional) |

### `CascadeResult`

| Attribute         | Type                  | Description                              |
|-------------------|-----------------------|------------------------------------------|
| `entries`         | `List[CascadeEntry]`  | All resolution events across all layers  |
| `merged`          | `Dict[str, str]`      | Final merged environment                 |
| `has_overrides`   | `bool`                | True if any key was overridden           |
| `overridden_keys` | `List[str]`           | Keys that were overridden by later layers|
| `layer_count`     | `int`                 | Number of distinct layers processed      |

### `CascadeEntry`

| Attribute        | Type            | Description                                  |
|------------------|-----------------|----------------------------------------------|
| `key`            | `str`           | Environment variable name                    |
| `value`          | `str`           | Resolved value from this layer               |
| `source`         | `str`           | Layer name where this value came from        |
| `layer_index`    | `int`           | Zero-based index of the source layer         |
| `was_overridden` | `bool`          | True if a previous layer had this key        |
| `previous_value` | `Optional[str]` | The value before this override               |

## CLI

```bash
python -m envguard.cli_cascade base.env staging.env production.env
```

### Flags

| Flag              | Description                                          |
|-------------------|------------------------------------------------------|
| `--strict`        | Exit with code 1 if any overrides are detected       |
| `--show-overrides`| Print a detailed list of overridden keys and values  |
