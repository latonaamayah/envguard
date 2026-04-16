# Archiver

The `archiver` module lets you save labeled snapshots of `.env` files over time, enabling historical comparison and rollback reference.

## Core Concepts

- **ArchiveEntry** — a labeled snapshot with a timestamp and variable map.
- **ArchiveResult** — a collection of archive entries loaded from or saved to a JSON file.

## Usage

```python
from envguard.archiver import archive, save_archive, load_archive, ArchiveResult
from pathlib import Path

env = {"DB_HOST": "localhost", "APP_ENV": "production"}
entry = archive(env, label="v1.0.0")

result = load_archive(Path(".envarchive.json"))
result.entries.append(entry)
save_archive(result, Path(".envarchive.json"))
```

## CLI

### Save an archive

```bash
envguard-archive save .env --label v1.0.0
```

### List archives

```bash
envguard-archive list
```

### Show a specific archive

```bash
envguard-archive show v1.0.0
```

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--label` | required | Label for the archive entry |
| `--archive` | `.envarchive.json` | Path to the archive storage file |

## ArchiveResult API

| Method | Description |
|--------|-------------|
| `has_entries()` | Returns `True` if any entries exist |
| `labels()` | Returns list of all labels |
| `get(label)` | Returns the entry for a label or `None` |
| `summary()` | Human-readable count string |
