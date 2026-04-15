"""Evaluator: score an env file against a schema and produce a quality grade."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envguard.schema import Schema
from envguard.validator import validate


GRADE_THRESHOLDS = [
    (90, "A"),
    (75, "B"),
    (60, "C"),
    (40, "D"),
    (0, "F"),
]


@dataclass
class EvaluationResult:
    score: int
    grade: str
    total_vars: int
    passed: int
    failed: int
    warnings: int
    breakdown: Dict[str, int] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)

    @property
    def has_failures(self) -> bool:
        return self.failed > 0

    def summary(self) -> str:
        return (
            f"Score: {self.score}/100 (Grade: {self.grade}) "
            f"| Passed: {self.passed} | Failed: {self.failed} | Warnings: {self.warnings}"
        )


def _compute_grade(score: int) -> str:
    for threshold, letter in GRADE_THRESHOLDS:
        if score >= threshold:
            return letter
    return "F"


def evaluate(env: Dict[str, str], schema: Schema) -> EvaluationResult:
    result = validate(env, schema)

    total = len(schema.variables)
    failed = len(result.errors)
    warnings = len(result.warnings)
    passed = max(0, total - failed)

    error_penalty = (failed / total * 60) if total else 0
    warning_penalty = (warnings / max(total, 1) * 20)
    score = max(0, round(100 - error_penalty - warning_penalty))

    grade = _compute_grade(score)

    breakdown = {
        "error_penalty": round(error_penalty),
        "warning_penalty": round(warning_penalty),
    }

    notes: list[str] = []
    if failed == 0:
        notes.append("All required variables are present and valid.")
    else:
        notes.append(f"{failed} variable(s) failed validation.")
    if warnings:
        notes.append(f"{warnings} warning(s) detected.")

    return EvaluationResult(
        score=score,
        grade=grade,
        total_vars=total,
        passed=passed,
        failed=failed,
        warnings=warnings,
        breakdown=breakdown,
        notes=notes,
    )
