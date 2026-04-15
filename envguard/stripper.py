"""Strip comments and blank lines from a .env file, returning a clean version."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class StripResult:
    """Result of stripping a .env mapping."""

    stripped: Dict[str, str] = field(default_factory=dict)
    removed_comments: List[str] = field(default_factory=list)
    removed_blanks: int = 0
    removed_inline_comments: List[str] = field(default_factory=list)

    def has_changes(self) -> bool:
        """Return True if any content was stripped."""
        return (
            bool(self.removed_comments)
            or self.removed_blanks > 0
            or bool(self.removed_inline_comments)
        )

    def summary(self) -> str:
        comments = len(self.removed_comments)
        inline = len(self.removed_inline_comments)
        blanks = self.removed_blanks
        if not self.has_changes():
            return "Nothing stripped; env is already clean."
        parts = []
        if comments:
            parts.append(f"{comments} comment line(s)")
        if blanks:
            parts.append(f"{blanks} blank line(s)")
        if inline:
            parts.append(f"{inline} inline comment(s)")
        return "Stripped: " + ", ".join(parts) + "."


def strip(raw_lines: List[str]) -> StripResult:
    """Parse *raw_lines* from a .env file and return a StripResult.

    - Full-line comments (``# …``) are recorded and excluded.
    - Blank / whitespace-only lines are counted and excluded.
    - Inline comments (``KEY=value  # comment``) are trimmed from values.
    - Valid ``KEY=value`` pairs are kept in *stripped*.
    """
    result = StripResult()

    for raw in raw_lines:
        line = raw.rstrip("\n")

        # Blank line
        if not line.strip():
            result.removed_blanks += 1
            continue

        # Full-line comment
        if line.lstrip().startswith("#"):
            result.removed_comments.append(line)
            continue

        # Key=value (possibly with inline comment)
        if "=" not in line:
            # Not a valid assignment — skip silently
            continue

        key, _, rest = line.partition("=")
        key = key.strip()

        # Strip inline comment: split on ` #` but not inside quotes
        value = rest
        if not (value.startswith('"') or value.startswith("'")):
            # Simple unquoted value — strip trailing inline comment
            if " #" in value:
                value, _, comment_text = value.partition(" #")
                result.removed_inline_comments.append(f"{key}: # {comment_text.strip()}")
            value = value.strip()
        else:
            # Quoted value — remove enclosing quotes then check inline
            quote_char = value[0]
            close = value.find(quote_char, 1)
            if close != -1:
                inner = value[1:close]
                tail = value[close + 1:]
                if " #" in tail:
                    _, _, comment_text = tail.partition(" #")
                    result.removed_inline_comments.append(
                        f"{key}: # {comment_text.strip()}"
                    )
                value = inner
            else:
                value = value.strip(quote_char)

        result.stripped[key] = value

    return result
