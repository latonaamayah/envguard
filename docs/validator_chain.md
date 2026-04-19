# Validator Chain

The `validator_chain` module provides a composable pipeline for running sequential validation or transformation steps against an env dictionary.

## Overview

A **chain** is an ordered list of named steps. Each step receives the current env dict and returns `(passed: bool, message: str)`. If a step fails, the chain halts immediately — subsequent steps are not executed.

## Usage

```python
from envguard.validator_chain import run_chain

env = {"DB_HOST": "localhost", "PORT": "5432"}

def check_db_host(env):
    return "DB_HOST" in env, "DB_HOST must be present"

def check_port_numeric(env):
    port = env.get("PORT", "")
    return port.isdigit(), f"PORT must be numeric, got '{port}'"

result = run_chain(env, [
    ("db_host_present", check_db_host),
    ("port_numeric", check_port_numeric),
])

print(result.summary())
# All 2 chain steps passed.
```

## API

### `run_chain(env, steps) -> ChainResult`

| Parameter | Type | Description |
|-----------|------|-------------|
| `env` | `Dict[str, str]` | Environment variables to validate |
| `steps` | `List[Tuple[str, StepFn]]` | Ordered list of `(name, callable)` pairs |

### `ChainResult`

| Attribute / Method | Description |
|--------------------|-------------|
| `steps` | All executed `ChainStep` objects |
| `env` | The env dict passed into the chain |
| `has_failures` | `True` if any step failed |
| `failed_steps` | List of failing steps |
| `passed_steps` | List of passing steps |
| `summary()` | Human-readable pass/fail summary |

### `ChainStep`

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Step identifier |
| `passed` | `bool` | Whether the step passed |
| `message` | `str` | Diagnostic message from the step |

## Notes

- The chain is **fail-fast**: execution stops at the first failing step.
- Unhandled exceptions inside a step are caught and treated as failures; the exception message is stored in `ChainStep.message`.
