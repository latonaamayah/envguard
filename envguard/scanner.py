"""Scanner module — detects potentially insecure or suspicious patterns in .env values."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import re

_PATTERNS: List[Tuple[str, str]] = [
    (r"(?i)password\s*=\s*.{0,3}$", "weak or empty password value"),
    (r"(?i)(secret|token|key)\s*=\s*(test|example|changeme|placeholder|dummy|fake|todo)", "placeholder secret value"),
    (r"https?://[^@]+:[^@]+@", "credentials embedded in URL"),
    (r"(?i)^(true|false|1|0|yes|no)$", None),  # benign — skip
    (r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "non-printable control characters in value"),
    (r"(?i)(aws_secret|aws_key).*=.+", "potential AWS credential"),
    (r"(?i)private[_-]?key\s*=\s*-+BEGIN", "raw private key material"),
]

_PLACEHOLDER_RE = re.compile(
    r"(?i)^(changeme|todo|fixme|placeholder|example|test|dummy|fake|replace_me|your_.*_here|<.*>|\[.*\])$"
)


@dataclass
class ScanIssue:
    key: str
    value: str
    reason: str
    severity: str  # "error" | "warning"


@dataclass
class ScanResult:
    issues: List[ScanIssue] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return bool(self.issues)

    @property
    def errors(self) -> List[ScanIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> List[ScanIssue]:
        return [i for i in self.issues if i.severity == "warning"]

    def summary(self) -> str:
        if not self.has_issues:
            return "No security issues detected."
        return (
            f"{len(self.errors)} error(s), {len(self.warnings)} warning(s) found "
            f"across {len(self.issues)} issue(s)."
        )


def scan(env: Dict[str, str]) -> ScanResult:
    """Scan *env* dict for suspicious or insecure patterns."""
    result = ScanResult()

    for key, value in env.items():
        stripped = value.strip()

        # Placeholder detection (warning)
        if _PLACEHOLDER_RE.match(stripped):
            result.issues.append(
                ScanIssue(key=key, value=value, reason="placeholder value detected", severity="warning")
            )
            continue

        for pattern, reason in _PATTERNS:
            if reason is None:
                continue  # benign pattern — skip
            combined = f"{key}={value}"
            if re.search(pattern, combined):
                severity = "error" if "credential" in reason or "private key" in reason or "AWS" in reason else "warning"
                result.issues.append(ScanIssue(key=key, value=value, reason=reason, severity=severity))
                break

    return result
