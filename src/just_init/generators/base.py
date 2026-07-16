"""Interfaces shared by project generators."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class ProjectContext:
    """Project metadata supplied to a language generator."""

    project_name: str
    output_directory: Path
    author: str
    email: str
    github_username: str


class ProjectGenerator(Protocol):
    """A generator that creates one language-specific project."""

    language: str

    def generate(self, context: ProjectContext) -> Path:
        """Generate a project and return its directory."""
