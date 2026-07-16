"""Interfaces shared by project generators."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectContext:
    """Project metadata supplied to a language generator."""

    project_name: str
    output_directory: Path
    author: str
    email: str
    github_username: str
