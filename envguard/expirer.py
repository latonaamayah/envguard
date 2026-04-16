from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional


@dataclass
class ExpireEntry:
    key: str
    value: str
    expires_at: Optional[datetime]
    is_expired: bool
    days_remaining: Optional[int]

    @property
    def message(self) -> str:
        if self.is_expired:
            return f"{self.key}: expired"
        if self.days_remaining is not None:
            return f"{self.key}: expires in {self.days_remaining} day(s)"
        return f"{self.key}: no expiry set"


@dataclass
class ExpireResult:
    entries: List[ExpireEntry] = field(default_factory=list)

    @property
    def has_expired(self) -> bool:
        return any(e.is_expired for e in self.entries)

    @property
    def expired_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.is_expired]

    @property
    def expiring_soon(self) -> List[str]:
        return [
            e.key
            for e in self.entries
            if not e.is_expired and e.days_remaining is not None and e.days_remaining <= 7
        ]

    def summary(self) -> str:
        total = len(self.entries)
        expired = len(self.expired_keys)
        soon = len(self.expiring_soon)
        return f"{total} key(s) checked — {expired} expired, {soon} expiring soon"


def expire(
    env: Dict[str, str],
    expiry_map: Dict[str, str],
    reference_date: Optional[datetime] = None,
) -> ExpireResult:
    """Check expiry dates for env vars. expiry_map maps key -> ISO date string."""
    now = reference_date or datetime.utcnow()
    result = ExpireResult()

    for key, value in env.items():
        iso = expiry_map.get(key)
        if iso is None:
            result.entries.append(ExpireEntry(key=key, value=value, expires_at=None, is_expired=False, days_remaining=None))
            continue
        try:
            expires_at = datetime.fromisoformat(iso)
        except ValueError:
            result.entries.append(ExpireEntry(key=key, value=value, expires_at=None, is_expired=False, days_remaining=None))
            continue

        delta = (expires_at - now).days
        is_expired = expires_at < now
        days_remaining = None if is_expired else max(0, delta)
        result.entries.append(ExpireEntry(key=key, value=value, expires_at=expires_at, is_expired=is_expired, days_remaining=days_remaining))

    return result
