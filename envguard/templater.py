from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re


@dataclass
class TemplateEntry:
    key: str
    template: str
    rendered: str
    missing_vars: List[str] = field(default_factory=list)

    @property
    def has_missing(self) -> bool:
        return bool(self.missing_vars)


@dataclass
class TemplateResult:
    entries: List[TemplateEntry] = field(default_factory=list)
    _errors: List[str] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return bool(self._errors)

    @property
    def errors(self) -> List[str]:
        return list(self._errors)

    def as_dict(self) -> Dict[str, str]:
        return {e.key: e.rendered for e in self.entries}

    def summary(self) -> str:
        total = len(self.entries)
        failed = sum(1 for e in self.entries if e.has_missing)
        return f"{total} template(s) rendered, {failed} with missing variable(s)."


_PLACEHOLDER_RE = re.compile(r"\{\{\s*(\w+)\s*\}\}")


def render_templates(
    templates: Dict[str, str],
    context: Dict[str, str],
    strict: bool = False,
) -> TemplateResult:
    """Render each template string using values from context.

    Args:
        templates: mapping of key -> template string with {{VAR}} placeholders.
        context: env vars available for substitution.
        strict: if True, add an error for any unresolved placeholder.
    """
    result = TemplateResult()

    for key, template in templates.items():
        missing: List[str] = []

        def replacer(m: re.Match) -> str:
            var = m.group(1)
            if var in context:
                return context[var]
            missing.append(var)
            return m.group(0)

        rendered = _PLACEHOLDER_RE.sub(replacer, template)
        entry = TemplateEntry(key=key, template=template, rendered=rendered, missing_vars=missing)
        result.entries.append(entry)

        if strict and missing:
            result._errors.append(
                f"Key '{key}': unresolved placeholder(s): {', '.join(missing)}"
            )

    return result
