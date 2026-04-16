# envguard splitter

The `splitter` module divides a flat `.env` dictionary into logical groups
based on key prefixes (e.g. `DB_`, `AWS_`, `APP_`).

## Usage

```python
from envguard.loader import load_env_file
from envguard.splitter import split

env = load_env_file(".env")
result = split(env)

for group, vars_ in result.groups.items():
    print(f"[{group}]")
    for k, v in vars_.items():
        print(f"  {k}={v}")

if result.ungrouped:
    print("[ungrouped]")
    for k, v in result.ungrouped.items():
        print(f"  {k}={v}")
```

## API

### `split(env, prefixes=None, separator="_") -> SplitResult`

| Parameter   | Type              | Description                                          |
|-------------|-------------------|------------------------------------------------------|
| `env`       | `Dict[str, str]`  | The environment variables to split.                  |
| `prefixes`  | `List[str] | None`| Restrict grouping to these prefixes only.            |
| `separator` | `str`             | Segment separator used to detect prefixes (default `_`). |

### `SplitResult`

| Attribute    | Type                        | Description                              |
|--------------|-----------------------------|------------------------------------------|
| `groups`     | `Dict[str, Dict[str, str]]` | Keyed by uppercase prefix.               |
| `ungrouped`  | `Dict[str, str]`            | Keys that did not match any prefix.      |

#### Methods

- `has_groups() -> bool` — `True` if at least one group was detected.
- `group_names() -> List[str]` — Sorted list of group names.
- `total_keys() -> int` — Total number of keys across all groups and ungrouped.
- `summary() -> str` — Human-readable summary of group sizes.

## Notes

- Prefix detection is case-insensitive; group names are always uppercased.
- Keys with no separator (or whose prefix is not in the explicit list) go to `ungrouped`.
- Use `prefixes=["DB", "AWS"]` to produce only those groups and place everything else in `ungrouped`.
