from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CommandParameter:
    name: str
    type: str = "string"
    required: bool = False
    description: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CommandParameter:
        return cls(
            name=data.get("name", ""),
            type=data.get("type", "string"),
            required=bool(data.get("required", False)),
            description=data.get("description", ""),
        )


@dataclass
class CollectorCommand:
    id: str
    name: str
    description: str
    shell: str  # cmd | powershell | bash
    platform: str  # windows | linux
    category: str
    lines: list[str]
    syntax: str = ""
    output_type: str = "text"  # text | csv | evtx | dat | binary | zip | json
    os_min: str = ""
    os_max: str = ""
    distros: list[str] = field(default_factory=list)
    dfir_tags: list[str] = field(default_factory=list)
    parameters: list[CommandParameter] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    required_step: bool = False
    favorite: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CollectorCommand:
        params = [CommandParameter.from_dict(p) for p in data.get("parameters", [])]
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            shell=(data.get("shell") or "cmd").lower(),
            platform=(data.get("platform") or "windows").lower(),
            category=data.get("category", "Other"),
            lines=list(data.get("lines") or data.get("Command") or []),
            syntax=data.get("syntax", ""),
            output_type=data.get("output_type", "text"),
            os_min=data.get("os_min", ""),
            os_max=data.get("os_max", ""),
            distros=list(data.get("distros") or []),
            dfir_tags=list(data.get("dfir_tags") or []),
            parameters=params,
            examples=list(data.get("examples") or []),
            required_step=bool(data.get("required_step", False)),
            favorite=bool(data.get("favorite", False)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "shell": self.shell,
            "platform": self.platform,
            "category": self.category,
            "lines": self.lines,
            "syntax": self.syntax,
            "output_type": self.output_type,
            "os_min": self.os_min,
            "os_max": self.os_max,
            "distros": self.distros,
            "dfir_tags": self.dfir_tags,
            "parameters": [
                {
                    "name": p.name,
                    "type": p.type,
                    "required": p.required,
                    "description": p.description,
                }
                for p in self.parameters
            ],
            "examples": self.examples,
            "required_step": self.required_step,
            "favorite": self.favorite,
        }
