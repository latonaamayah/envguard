# envguard

> Validate and audit `.env` files against a schema definition to prevent missing or misconfigured environment variables in production.

---

## Installation

```bash
pip install envguard
```

Or with [pipx](https://pypa.github.io/pipx/):

```bash
pipx install envguard
```

---

## Usage

Define a schema file (`.env.schema`) describing the expected variables:

```ini
DATABASE_URL=required,url
SECRET_KEY=required,min_length:32
DEBUG=optional,boolean
PORT=optional,integer,default:8000
```

Then validate your `.env` file against it:

```bash
envguard validate --env .env --schema .env.schema
```

**Example output:**

```
✔  DATABASE_URL   valid
✔  SECRET_KEY     valid
✘  DEBUG          invalid value: expected boolean, got "yes_please"
⚠  PORT           missing, using default: 8000

1 error found. Fix issues before deploying.
```

You can also audit all `.env` files in a project directory:

```bash
envguard audit --dir ./
```

---

## Options

| Flag | Description |
|------|-------------|
| `--env` | Path to the `.env` file (default: `.env`) |
| `--schema` | Path to the schema file (default: `.env.schema`) |
| `--strict` | Exit with error code on warnings |
| `--quiet` | Suppress output, return exit code only |

---

## License

[MIT](LICENSE) © envguard contributors