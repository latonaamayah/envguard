# Tokenizer

The `tokenizer` module splits `.env` values into discrete tokens using common delimiters such as commas, pipes, semicolons, and whitespace.

## Use Case

Many environment variables store lists of values in a single string (e.g., `ALLOWED_HOSTS=localhost,127.0.0.1`). The tokenizer makes these values inspectable and auditable.

## API

### `tokenize(env: Dict[str, str]) -> TokenResult`

Tokenizes all values in the provided environment dictionary.

```python
from envguard.tokenizer import tokenize

env = {"HOSTS": "localhost,127.0.0.1", "NAME": "myapp"}
result = tokenize(env)
print(result.summary())
# 2 keys tokenized, 3 total tokens
```

### `TokenResult`

| Method | Description |
|---|---|
| `has_entries()` | Returns True if any entries exist |
| `keys_with_multiple_tokens()` | Keys whose value splits into more than one token |
| `as_dict()` | Returns `{key: [tokens]}` mapping |
| `summary()` | Human-readable summary string |

### `TokenEntry`

| Field | Type | Description |
|---|---|---|
| `key` | `str` | The environment variable name |
| `value` | `str` | The original value |
| `tokens` | `List[str]` | The split tokens |
| `token_count` | `int` | Number of tokens |

## CLI

```bash
envguard-tokenize .env
envguard-tokenize .env --key ALLOWED_HOSTS
envguard-tokenize .env --multi-only
```

## Supported Delimiters

- Comma `,`
- Pipe `|`
- Semicolon `;`
- Whitespace (space, tab)
