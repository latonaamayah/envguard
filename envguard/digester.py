from __future__ import annotations
from dataclasses import dataclass, field
from hashlib import md5, sha1, sha256
from typing import Dict, Literal

HashAlgorithm = Literal["md5", "sha1", "sha256"]


@dataclass
class DigestEntry:
    key: str
    value: str
    algorithm: str
    digest: str

    def __str__(self) -> str:
        return f"{self.key}={self.digest} ({self.algorithm})"


@dataclass
class DigestResult:
    entries: list[DigestEntry] = field(default_factory=list)
    algorithm: str = "sha256"

    def has_entries(self) -> bool:
        return len(self.entries) > 0

    def as_dict(self) -> Dict[str, str]:
        return {e.key: e.digest for e in self.entries}

    def summary(self) -> str:
        return f"{len(self.entries)} key(s) digested using {self.algorithm}"


def _hash(value: str, algorithm: HashAlgorithm) -> str:
    encoded = value.encode("utf-8")
    if algorithm == "md5":
        return md5(encoded).hexdigest()
    if algorithm == "sha1":
        return sha1(encoded).hexdigest()
    return sha256(encoded).hexdigest()


def digest(
    env: Dict[str, str],
    algorithm: HashAlgorithm = "sha256",
    keys: list[str] | None = None,
) -> DigestResult:
    result = DigestResult(algorithm=algorithm)
    targets = keys if keys is not None else list(env.keys())
    for key in targets:
        if key not in env:
            continue
        value = env[key]
        h = _hash(value, algorithm)
        result.entries.append(DigestEntry(key=key, value=value, algorithm=algorithm, digest=h))
    return result
