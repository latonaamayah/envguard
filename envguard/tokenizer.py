from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List
import re


@dataclass
class TokenEntry:
    key: str
    value: str
    tokens: List[str]

    @property
    def token_count(self) -> int:
        return len(self.tokens)


@dataclass
class TokenResult:
    entries: List[TokenEntry] = field(default_factory=list)

    def has_entries(self) -> bool:
        return len(self.entries) > 0

    def keys_with_multiple_tokens(self) -> List[str]:
        return [e.key for e in self.entries if e.token_count > 1]

    def as_dict(self) -> Dict[str, List[str]]:
        return {e.key: e.tokens for e in self.entries}

    def summary(self) -> str:
        total = sum(e.token_count for e in self.entries)
        return f"{len(self.entries)} keys tokenized, {total} total tokens"


def _tokenize_value(value: str) -> List[str]:
    """Split value into tokens by common delimiters: space, comma, pipe, semicolon."""
    if not value:
        return []
    tokens = re.split(r"[,|;\s]+", value.strip())
    return [t for t in tokens if t]


def tokenize(env: Dict[str, str]) -> TokenResult:
    entries = []
    for key, value in env.items():
        tokens = _tokenize_value(value)
        entries.append(TokenEntry(key=key, value=value, tokens=tokens))
    return TokenResult(entries=entries)
