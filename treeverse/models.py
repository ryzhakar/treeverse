from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any
from typing import Self

import yaml
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class TreeverseBaseModel(BaseModel):
    """Base model for Treeverse with YAML serialization capabilities."""

    model_config = ConfigDict(
        json_encoders={
            Path: str,
        },
    )

    @classmethod
    def from_yaml(cls, yaml_str: str) -> Self:
        """Deserialize from YAML string."""
        raw_objects = yaml.safe_load(yaml_str)
        return cls.model_validate(raw_objects)

    def to_yaml(self) -> str:
        """Serialize to YAML string using JSON as a proxy."""
        json_data = json.loads(self.model_dump_json(exclude_none=True))
        return yaml.dump(json_data, sort_keys=False)


class FileInfo(TreeverseBaseModel):
    """Represents metadata of a file."""

    full_path: Path = Field(..., description='Complete path of the file')
    file_size_bytes: int = Field(..., description='Size of the file in bytes')
    last_modified: datetime = Field(
        ...,
        description='Last modification timestamp',
    )
    is_text_file: bool = Field(
        ...,
        description='Whether the file is a text file',
    )
    text_encoding: str | None = Field(
        None,
        description='Detected text encoding (for text files)',
    )
    line_count: int | None = Field(
        None,
        description='Number of lines in the file (for text files)',
    )
    word_count: int | None = Field(
        None,
        description='Number of words in the file (for text files)',
    )
    character_count: int | None = Field(
        None,
        description='Number of characters in the file (for text files)',
    )


class FileNode(TreeverseBaseModel):
    """Represents a node in the file tree."""

    file_name: str = Field(..., description='Name of the file')
    file_info: FileInfo = Field(..., description='Metadata of the file')
    custom_data: dict[str, Any] = Field(
        description='Custom data associated with the file',
        default_factory=dict,
    )
    child_nodes: list[FileNode] = Field(
        default_factory=list,
        description='List of child nodes (for directories)',
    )

    def add_child(self, child: FileNode) -> FileNode:
        """Adds a child node and returns a new FileNode instance."""
        return self.model_copy(
            update={'child_nodes': [*self.child_nodes, child]},
        )
