# envguard pruner

The `pruner` module removes unwanted variables from an env dictionary based on configurable rules.

## Features

- Remove **empty** variables (blank values)
- Remove **placeholder** variables (e.g. `changeme`, `todo`, `placeholder`)
- Remove **explicitly selected** keys by name

## Usage

```python
from envguard.pruner import prune

env = {
    "APP_NAME": "myapp",
    "DB_PASSWORD": "",
    "API_KEY": "changeme",
    "PORT": "8080",
}

result = prune(env)
print(result.summary())
# Pruned 2 variable(s): DB_PASSWORD, API_KEY

print(result.kept)
# {'APP_NAME': 'myapp', 'PORT': '8080'}
```

## API

### `prune(env, empty=True, placeholders=True, keys=None)`

| Parameter      | Type            | Default | Description                              |
|----------------|-----------------|---------|------------------------------------------|
| `env`          | `Dict[str, str]`| —       | Input environment variables              |
| `empty`        | `bool`          | `True`  | Prune variables with empty values        |
| `placeholders` | `bool`          | `True`  | Prune variables with placeholder values  |
| `keys`         | `Set[str]`      | `None`  | Explicitly prune these keys              |

### `PruneResult`

| Attribute / Method | Description                          |
|--------------------|--------------------------------------|
| `pruned`           | List of `PruneEntry` items removed   |
| `kept`             | Dict of variables that were retained |
| `has_pruned()`     | Returns `True` if anything was pruned|
| `pruned_keys()`    | List of removed key names            |
| `summary()`        | Human-readable summary string        |

### Placeholder values detected

`changeme`, `todo`, `fixme`, `placeholder`, `xxx`, `<value>`, `your_value_here`
