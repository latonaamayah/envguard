from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Any


@dataclass
class ChainStep:
    name: str
    passed: bool
    message: str = ""


@dataclass
class ChainResult:
    steps: List[ChainStep] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)

    @property
    def has_failures(self) -> bool:
        return any(not s.passed for s in self.steps)

    @property
    def failed_steps(self) -> List[ChainStep]:
        return [s for s in self.steps if not s.passed]

    @property
    def passed_steps(self) -> List[ChainStep]:
        return [s for s in self.steps if s.passed]

    def summary(self) -> str:
        total = len(self.steps)
        failed = len(self.failed_steps)
        if failed == 0:
            return f"All {total} chain steps passed."
        return f"{failed}/{total} chain steps failed."


StepFn = Callable[[Dict[str, str]], tuple[bool, str]]


def run_chain(env: Dict[str, str], steps: List[tuple[str, StepFn]]) -> ChainResult:
    """Run a sequence of validation/transform steps against an env dict.

    Each step is a (name, callable) pair. The callable receives the current
    env and returns (passed: bool, message: str).
    """
    result = ChainResult(env=dict(env))
    for name, fn in steps:
        try:
            passed, message = fn(result.env)
        except Exception as exc:  # noqa: BLE001
            passed, message = False, str(exc)
        result.steps.append(ChainStep(name=name, passed=passed, message=message))
        if not passed:
            break
    return result
