# Env File Merger

The `merger` module allows you to combine multiple `.env` files into a single
resolved set of variables, with configurable conflict resolution.

## Usage (Python API)

```python
from envguard.merger import merge

result = merge(["base.env", "local.env", "production.env"])

print(result.merged)        # final dict of all variables
print(result.has_conflicts) # True if any key appeared in more than one file
print(result.summary())     # human-readable summary

for conflict in result.conflicts:
    print(conflict.key, conflict.values, conflict.winning_value)
```

## Precedence

By default **last file wins** (`override=True`). Pass `override=False` to
make the first occurrence win instead.

```python
result = merge(["base.env", "overrides.env"], override=False)  # first wins
```

## CLI

The `merge` subcommand is registered in `cli_merge.py` and can be wired into
the main `envguard` CLI.

```bash
# Print merged vars to stdout
envguard merge base.env local.env

# Write to file and show conflict details
envguard merge base.env local.env -o merged.env --show-conflicts

# First-wins mode
envguard merge base.env local.env --no-override
```

## Conflict Report

When `--show-conflicts` is passed, each key that appeared in more than one
file is printed to **stderr**:

```
[conflict] DATABASE_URL:
  /path/base.env = postgres://localhost/dev
  /path/local.env = postgres://localhost/test
  => using: postgres://localhost/test
```

Exit codes follow the same convention as the rest of `envguard`:

| Code | Meaning |
|------|---------|
| `0`  | Success |
| `1`  | Conflicts detected (only when `--strict` flag is used) |
| `2`  | File not found or parse error |

> **Tip:** Use `--strict` in CI pipelines to treat any conflict as a fatal
> error, ensuring no accidental variable shadowing goes unnoticed.
