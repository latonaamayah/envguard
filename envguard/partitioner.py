"""Partition .env variables into named buckets based on rules."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re


@dataclass
class PartitionEntry:
    key: str
    value: str
    bucket: str

    def __str__(self) -> str:
        return f"{self.key}={self.value} -> [{self.bucket}]"


@dataclass
class PartitionResult:
    entries: List[PartitionEntry] = field(default_factory=list)
    _buckets: Dict[str, List[PartitionEntry]] = field(default_factory=dict, repr=False)

    def has_buckets(self) -> bool:
        return bool(self._buckets)

    def bucket_names(self) -> List[str]:
        return sorted(self._buckets.keys())

    def keys_for_bucket(self, bucket: str) -> List[str]:
        return [e.key for e in self._buckets.get(bucket, [])]

    def get_bucket(self, bucket: str) -> Dict[str, str]:
        return {e.key: e.value for e in self._buckets.get(bucket, [])}

    def summary(self) -> str:
        total = len(self.entries)
        buckets = len(self._buckets)
        return f"{total} variable(s) partitioned into {buckets} bucket(s)"


def partition(
    env: Dict[str, str],
    rules: Dict[str, str],
    default_bucket: str = "default",
) -> PartitionResult:
    """Partition env variables into buckets.

    Args:
        env: Mapping of key -> value.
        rules: Mapping of bucket_name -> regex pattern matched against keys.
        default_bucket: Bucket name for keys that match no rule.

    Returns:
        PartitionResult with entries grouped by bucket.
    """
    result = PartitionResult()
    compiled = {bucket: re.compile(pattern) for bucket, pattern in rules.items()}

    for key, value in env.items():
        assigned: Optional[str] = None
        for bucket, regex in compiled.items():
            if regex.search(key):
                assigned = bucket
                break
        bucket_name = assigned if assigned is not None else default_bucket
        entry = PartitionEntry(key=key, value=value, bucket=bucket_name)
        result.entries.append(entry)
        result._buckets.setdefault(bucket_name, []).append(entry)

    return result
