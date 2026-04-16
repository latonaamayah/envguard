from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import secrets
import string


@dataclass
class RotateEntry:
    key: str
    old_value: str
    new_value: str

    @property
    def changed(self) -> bool:
        return self.old_value != self.new_value


@dataclass
class RotateResult:
    entries: List[RotateEntry] = field(default_factory=list)

    @property
    def has_rotated(self) -> bool:
        return any(e.changed for e in self.entries)

    @property
    def rotated_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.changed]

    def summary(self) -> str:
        n = len(self.rotated_keys)
        return f"{n} key(s) rotated."

    def as_dict(self) -> Dict[str, str]:
        return {e.key: e.new_value for e in self.entries}


def _generate_secret(length: int = 32) -> str:
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return "".join(secrets.choice(alphabet) for _ in range(length))


def rotate(
    env: Dict[str, str],
    keys: Optional[List[str]] = None,
    length: int = 32,
    generator=None,
) -> RotateResult:
    """Rotate values for specified keys (or all keys) with newly generated secrets."""
    gen = generator or (lambda: _generate_secret(length))
    target_keys = keys if keys is not None else list(env.keys())
    entries: List[RotateEntry] = []
    for k, v in env.items():
        if k in target_keys:
            new_val = gen()
            entries.append(RotateEntry(key=k, old_value=v, new_value=new_val))
        else:
            entries.append(RotateEntry(key=k, old_value=v, new_value=v))
    return RotateResult(entries=entries)
