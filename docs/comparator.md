# envguard comparator

The `comparator` module provides side-by-side comparison of two `.env` files,
highlighting keys that were added, removed, or changed between environments.

## Usage

```python
from envguard.loader import load_env_file
from envguard.comparator import compare

left = load_env_file(".env.staging")
right = load_env_file(".env.production")

result = compare(left, right, left_file=".env.staging", right_file=".env.production")

if result.has_differences:
    print(result.summary())

    for entry in result.changed:
        print(f"CHANGED  {entry.key}: {entry.left_value!r} → {entry.right_value!r}")

    for entry in result.left_only:
        print(f"LEFT ONLY  {entry.key}={entry.left_value!r}")

    for entry in result.right_only:
        print(f"RIGHT ONLY {entry.key}={entry.right_value!r}")
else:
    print("No differences found.")
```

## API

### `compare(left, right, left_file, right_file) -> CompareResult`

Compares two dictionaries of environment variables.

| Parameter    | Type            | Description                        |
|--------------|-----------------|------------------------------------|
| `left`       | `Dict[str, str]`| Variables from the first env file  |
| `right`      | `Dict[str, str]`| Variables from the second env file |
| `left_file`  | `str`           | Label for the left file (display)  |
| `right_file` | `str`           | Label for the right file (display) |

### `CompareResult`

| Attribute / Property | Description                                      |
|----------------------|--------------------------------------------------|
| `entries`            | All `CompareEntry` objects for every key seen    |
| `has_differences`    | `True` if any entry is not `equal`               |
| `changed`            | Entries whose value differs between files        |
| `left_only`          | Keys present only in the left file               |
| `right_only`         | Keys present only in the right file              |
| `summary()`          | Human-readable counts of each difference type   |

### `CompareEntry`

| Field         | Type           | Description                              |
|---------------|----------------|------------------------------------------|
| `key`         | `str`          | The environment variable name            |
| `left_value`  | `str \| None`  | Value in the left file, or `None`        |
| `right_value` | `str \| None`  | Value in the right file, or `None`       |
| `status`      | `str`          | One of `equal`, `changed`, `left_only`, `right_only` |
