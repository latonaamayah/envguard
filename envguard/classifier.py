from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

# Category patterns: (category_name, list of substrings to match in key)
_CATEGORY_PATTERNS: List[tuple[str, List[str]]] = [
    ("database", ["DB_", "DATABASE_", "POSTGRES", "MYSQL", "MONGO", "REDIS", "SQLITE"]),
    ("auth", ["AUTH_", "JWT_", "OAUTH_", "TOKEN", "SECRET", "PASSWORD", "API_KEY"]),
    ("cloud", ["AWS_", "GCP_", "AZURE_", "S3_", "BUCKET", "REGION"]),
    ("network", ["HOST", "PORT", "URL", "ENDPOINT", "DOMAIN", "PROXY"]),
    ("logging", ["LOG_", "LOGGING_", "LOG_LEVEL", "SENTRY_", "DATADOG_"]),
    ("feature", ["FEATURE_", "FLAG_", "ENABLE_", "DISABLE_"]),
    ("email", ["SMTP_", "MAIL_", "EMAIL_", "SENDGRID_", "MAILGUN_"]),
]


@dataclass
class ClassifyEntry:
    key: str
    value: str
    category: str


@dataclass
class ClassifyResult:
    categories: Dict[str, List[ClassifyEntry]] = field(default_factory=dict)
    uncategorized: List[ClassifyEntry] = field(default_factory=list)

    def has_categories(self) -> bool:
        return bool(self.categories)

    def category_names(self) -> List[str]:
        return sorted(self.categories.keys())

    def summary(self) -> str:
        total = sum(len(v) for v in self.categories.values()) + len(self.uncategorized)
        cats = len(self.categories)
        return (
            f"{total} variable(s) classified into {cats} categorie(s); "
            f"{len(self.uncategorized)} uncategorized."
        )


def _detect_category(key: str) -> str | None:
    upper = key.upper()
    for category, patterns in _CATEGORY_PATTERNS:
        for pattern in patterns:
            if pattern in upper:
                return category
    return None


def classify(env: Dict[str, str]) -> ClassifyResult:
    """Classify environment variables into named categories based on key patterns."""
    result = ClassifyResult()
    for key, value in env.items():
        category = _detect_category(key)
        entry = ClassifyEntry(key=key, value=value, category=category or "uncategorized")
        if category:
            result.categories.setdefault(category, []).append(entry)
        else:
            result.uncategorized.append(entry)
    return result
