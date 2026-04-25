"""envguard.grapher — Build a dependency graph of .env variable references."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Set

_REF_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


@dataclass
class GraphNode:
    key: str
    references: List[str] = field(default_factory=list)
    referenced_by: List[str] = field(default_factory=list)

    def has_references(self) -> bool:
        return bool(self.references)

    def __str__(self) -> str:  # pragma: no cover
        refs = ", ".join(self.references) if self.references else "none"
        return f"{self.key} -> [{refs}]"


@dataclass
class GraphResult:
    nodes: Dict[str, GraphNode] = field(default_factory=dict)

    def has_cycles(self) -> bool:
        """Return True if the reference graph contains at least one cycle."""
        visited: Set[str] = set()
        stack: Set[str] = set()

        def _dfs(node: str) -> bool:
            visited.add(node)
            stack.add(node)
            for neighbour in self.nodes.get(node, GraphNode(node)).references:
                if neighbour not in visited:
                    if _dfs(neighbour):
                        return True
                elif neighbour in stack:
                    return True
            stack.discard(node)
            return False

        for key in self.nodes:
            if key not in visited:
                if _dfs(key):
                    return True
        return False

    def roots(self) -> List[str]:
        """Keys that are not referenced by any other key."""
        return [k for k, n in self.nodes.items() if not n.referenced_by]

    def leaves(self) -> List[str]:
        """Keys that reference no other key."""
        return [k for k, n in self.nodes.items() if not n.references]

    def summary(self) -> str:
        total = len(self.nodes)
        edges = sum(len(n.references) for n in self.nodes.values())
        cycle = "yes" if self.has_cycles() else "no"
        return f"nodes={total} edges={edges} cycles={cycle}"


def graph(env: Dict[str, str]) -> GraphResult:
    """Build a GraphResult from an env mapping."""
    nodes: Dict[str, GraphNode] = {k: GraphNode(key=k) for k in env}

    for key, value in env.items():
        for m in _REF_RE.finditer(value):
            ref = m.group(1) or m.group(2)
            if ref and ref != key:
                nodes[key].references.append(ref)
                if ref not in nodes:
                    nodes[ref] = GraphNode(key=ref)
                nodes[ref].referenced_by.append(key)

    return GraphResult(nodes=nodes)
