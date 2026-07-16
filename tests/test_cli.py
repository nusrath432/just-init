"""Tests for the just-init command-line interface."""

from __future__ import annotations

import io
import sys
from pathlib import Path

import pytest

from just_init import cli
from just_init.generators.base import ProjectContext


class RecordingGenerator:
    """Test double that captures received project context."""

    def __init__(self) -> None:
        self.context: ProjectContext | None = None

    def generate(self, context: ProjectContext) -> Path:
        self.context = context
        return context.output_directory / context.project_name


class FailingGenerator:
    """Test double that models generation failure."""

    def generate(self, context: ProjectContext) -> Path:
        raise ValueError("generation failed")


class InteractiveInput(io.StringIO):
    """String input treated as an interactive terminal."""

    def isatty(self) -> bool:
        return True


def test_init_command_passes_explicit_metadata_to_generator(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    generator = RecordingGenerator()
    monkeypatch.setitem(cli.GENERATORS, "python", generator)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "just-init",
            "init",
            "python",
            "prism-proxy",
            "--output-dir",
            str(tmp_path),
            "--author",
            "Example Author",
            "--email",
            "author@example.com",
            "--github-username",
            "example-org",
        ],
    )

    assert cli.main() == 0
    assert generator.context == ProjectContext(
        project_name="prism-proxy",
        output_directory=tmp_path,
        author="Example Author",
        email="author@example.com",
        github_username="example-org",
    )
    assert "Created python project" in capsys.readouterr().out


def test_init_command_reports_generation_failure(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setitem(cli.GENERATORS, "python", FailingGenerator())
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "just-init",
            "init",
            "python",
            "prism-proxy",
            "--author",
            "Example Author",
            "--email",
            "author@example.com",
            "--github-username",
            "example-org",
        ],
    )

    assert cli.main() == 2
    assert "generation failed" in capsys.readouterr().err


def test_init_command_prompts_for_required_metadata(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    generator = RecordingGenerator()
    monkeypatch.setitem(cli.GENERATORS, "python", generator)
    monkeypatch.setattr(
        sys,
        "argv",
        ["just-init", "init", "python", "prism-proxy", "--output-dir", str(tmp_path)],
    )
    monkeypatch.setattr(
        cli.sys,
        "stdin",
        InteractiveInput("Example Author\nauthor@example.com\nexample-org\n"),
    )

    assert cli.main() == 0
    assert generator.context is not None
    assert generator.context.author == "Example Author"
    assert generator.context.email == "author@example.com"
    assert generator.context.github_username == "example-org"


def test_resolve_value_prompts_or_fails_when_not_supplied(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(cli.sys, "stdin", InteractiveInput("entered value\n"))
    assert cli.resolve_value("", "Author name") == "entered value"

    monkeypatch.setattr(cli.sys, "stdin", io.StringIO())
    with pytest.raises(ValueError, match="Author name is required"):
        cli.resolve_value("", "Author name")
