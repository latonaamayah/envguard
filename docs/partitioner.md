# Partitioner

The `partitioner` module splits `.env` variables into named **buckets** based on regex rules applied to key names.

## Usage

```python
from envguard.partitioner import partition

env = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "AWS_ACCESS_KEY": "AKIA123",
    "LOG_LEVEL": "info",
}

rules = {
    "database": r"^DB_",
    "cloud":    r"^AWS_",
}

result = partition(env, rules, default_bucket="misc")

print(result.summary())
# 4 variable(s) partitioned into 3 bucket(s)

print(result.bucket_names())
# ['cloud', 'database', 'misc']

print(result.get_bucket("database"))
# {'DB_HOST': 'localhost', 'DB_PORT': '5432'}
```

## API

### `partition(env, rules, default_bucket="default") -> PartitionResult`

| Parameter        | Type              | Description                                      |
|------------------|-------------------|--------------------------------------------------|
| `env`            | `Dict[str, str]`  | The environment variables to partition           |
| `rules`          | `Dict[str, str]`  | Mapping of bucket name to regex pattern          |
| `default_bucket` | `str`             | Bucket for keys that match no rule               |

Rules are evaluated in insertion order; the **first matching rule wins**.

### `PartitionResult`

| Method / Property       | Description                                      |
|-------------------------|--------------------------------------------------|
| `has_buckets()`         | `True` if at least one bucket was created        |
| `bucket_names()`        | Sorted list of bucket names                      |
| `keys_for_bucket(name)` | List of keys assigned to the given bucket        |
| `get_bucket(name)`      | `Dict[str, str]` of variables in the bucket      |
| `summary()`             | Human-readable summary string                    |
| `entries`               | Flat list of `PartitionEntry` objects            |

## CLI

```bash
envguard-partition .env --rule database=^DB_ --rule cloud=^AWS_ --format json
```

### Options

| Flag               | Description                                  |
|--------------------|----------------------------------------------|
| `--rule`           | `BUCKET=PATTERN` (repeatable)                |
| `--default-bucket` | Name for unmatched keys (default: `default`) |
| `--format`         | `text` (default) or `json`                   |
