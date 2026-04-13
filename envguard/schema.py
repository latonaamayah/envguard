"""Schema definition and parsing for envguard."""

from dataclasses import dataclass, field
from typing import Optional
import json
import os


VALID_TYPES = {"string", "integer", "boolean", "url", "email"}


@dataclass
class EnvVarSchema:
    name: str
    required: bool = True
    type: str = "string"
    default: Optional[str] = None
    description: Optional[str] = None
    allowed_values: list = field(default_factory=list)

    def __post_init__(self):
        if self.type not in VALID_TYPES:
            raise ValueError(
                f"Invalid type '{self.type}' for '{self.name}'. "
                f"Must be one of: {', '.join(VALID_TYPES)}"
            )


@dataclass
class Schema:
    variables: list[EnvVarSchema] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "Schema":
        variables = []
        for name, config in data.get("variables", {}).items():
            variables.append(
                EnvVarSchema(
                    name=name,
                    required=config.get("required", True),
                    type=config.get("type", "string"),
                    default=config.get("default"),
                    description=config.get("description"),
                    allowed_values=config.get("allowed_values", []),
                )
            )
        return cls(variables=variables)

    @classmethod
    def from_file(cls, path: str) -> "Schema":
        if not os.path.exists(path):
            raise FileNotFoundError(f"Schema file not found: {path}")
        with open(path, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)
