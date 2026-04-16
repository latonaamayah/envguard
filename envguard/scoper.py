from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set

SCOPE_PATTERNS: Dict[str, List[str]] = {
    "test": ["TEST_", "_TEST", "MOCK_", "FAKE_", "STUB_"],
    "production": ["PROD_", "_PROD", "PRODUCTION_"],
    "development": ["DEV_", "_DEV", "DEVELOPMENT_", "LOCAL_"],
    "staging": ["STAGING_", "_STAGING", "STAGE_"],
}


@dataclass
class ScopeEntry:
    key: str
    scope: str


@dataclass
class ScopeResult:
    entries: List[ScopeEntry] = field(default_factory=list)
    unscoped: List[str] = field(default_factory=list)

    def has_scoped(self) -> bool:
        return len(self.entries) > 0

    def keys_for_scope(self, scope: str) -> List[str]:
        return [e.key for e in self.entries if e.scope == scope]

    def all_scopes(self) -> Set[str]:
        return {e.scope for e in self.entries}

    def summary(self) -> str:
        total = len(self.entries) + len(self.unscoped)
        scoped = len(self.entries)
        return (
            f"{scoped}/{total} keys matched a scope; "
            f"{len(self.unscoped)} unscoped"
        )


def _detect_scope(key: str) -> str | None:
    upper = key.upper()
    for scope, patterns in SCOPE_PATTERNS.items():
        for pat in patterns:
            if upper.startswith(pat) or upper.endswith(pat.rstrip("_")):
                return scope
    return None


def scope(env: Dict[str, str]) -> ScopeResult:
    result = ScopeResult()
    for key in env:
        detected = _detect_scope(key)
        if detected:
            result.entries.append(ScopeEntry(key=key, scope=detected))
        else:
            result.unscoped.append(key)
    return result
