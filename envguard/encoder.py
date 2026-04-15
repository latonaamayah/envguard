"""Encode .env variables into different output formats (base64, url, hex)."""
from __future__ import annotations

import base64
import urllib.parse
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict


class EncodeFormat(str, Enum):
    BASE64 = "base64"
    URL = "url"
    HEX = "hex"


@dataclass
class EncodeEntry:
    key: str
    original: str
    encoded: str
    format: EncodeFormat


@dataclass
class EncodeResult:
    entries: list[EncodeEntry] = field(default_factory=list)
    format: EncodeFormat = EncodeFormat.BASE64

    @property
    def has_entries(self) -> bool:
        return len(self.entries) > 0

    @property
    def as_dict(self) -> Dict[str, str]:
        return {e.key: e.encoded for e in self.entries}

    def summary(self) -> str:
        return f"{len(self.entries)} variable(s) encoded as {self.format.value}."


def _encode_value(value: str, fmt: EncodeFormat) -> str:
    if fmt == EncodeFormat.BASE64:
        return base64.b64encode(value.encode()).decode()
    if fmt == EncodeFormat.URL:
        return urllib.parse.quote(value, safe="")
    if fmt == EncodeFormat.HEX:
        return value.encode().hex()
    raise ValueError(f"Unsupported format: {fmt}")


def encode(
    env: Dict[str, str],
    fmt: EncodeFormat = EncodeFormat.BASE64,
    keys: list[str] | None = None,
) -> EncodeResult:
    """Encode values in *env*.

    Args:
        env:  Mapping of variable names to their raw values.
        fmt:  Target encoding format.
        keys: If provided, only encode these keys; otherwise encode all.

    Returns:
        An :class:`EncodeResult` containing one entry per encoded variable.
    """
    result = EncodeResult(format=fmt)
    targets = keys if keys is not None else list(env.keys())
    for key in targets:
        if key not in env:
            continue
        original = env[key]
        encoded = _encode_value(original, fmt)
        result.entries.append(
            EncodeEntry(key=key, original=original, encoded=encoded, format=fmt)
        )
    return result
