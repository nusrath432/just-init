"""Tests for the packaged Python project generator."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from just_init.generators import python
from just_init.generators.base import ProjectContext
from just_init.generators.python import PythonProjectGenerator


def bootstrap_project(project_directory: Path, context: ProjectContext) -> None:
    """Provide a deterministic bootstrap step for unit tests."""
    (project_directory / "uv.lock").write_text("version = 1\n", encoding="utf-8")


def project_context(output_directory: Path) -> ProjectContext:
    """Create explicit project metadata for generator tests."""
    return ProjectContext(
        project_name="prism-proxy",
        output_directory=output_directory,
        author="Example Author",
        email="author@example.com",
        github_username="example-org",
    )


def test_generates_complete_python_project() -> None:
    with tempfile.TemporaryDirectory() as temporary_directory:
        project = PythonProjectGenerator(bootstrap_runner=bootstrap_project).generate(
            project_context(Path(temporary_directory))
        )

        assert project.name == "prism-proxy"
        assert (project / "uv.lock").is_file()
        assert (project / "src" / "prism_proxy" / "py.typed").is_file()
        assert not (project / "src" / "my_project").exists()
        assert (project / ".github" / "workflows" / "ci.yaml").is_file()
        assert (project / ".vscode" / "settings.json").is_file()
        assert (project / ".github" / "ISSUE_TEMPLATE" / "bug_report.yml").is_file()
        assert (project / ".github" / "dependabot.yml").is_file()
        assert (project / "CODE_OF_CONDUCT.md").is_file()
        assert (project / ".editorconfig").is_file()

        pyproject = (project / "pyproject.toml").read_text(encoding="utf-8")
        assert 'name = "prism-proxy"' in pyproject
        assert 'prism_proxy = ["py.typed"]' in pyproject
        assert "Example Author" in pyproject
        assert "https://github.com/example-org/prism-proxy" in pyproject

        assert "# Prism Proxy" in (project / "README.md").read_text(encoding="utf-8")
        assert "author@example.com" in (project / "SECURITY.md").read_text(
            encoding="utf-8"
        )
        assert "@example-org" in (project / ".github" / "CODEOWNERS").read_text(
            encoding="utf-8"
        )


def test_rejects_existing_target_directory() -> None:
    with tempfile.TemporaryDirectory() as temporary_directory:
        output_directory = Path(temporary_directory)
        (output_directory / "prism-proxy").mkdir()

        with pytest.raises(ValueError, match="Refusing to overwrite"):
            PythonProjectGenerator(bootstrap_runner=bootstrap_project).generate(
                project_context(output_directory)
            )


@pytest.mark.parametrize("name", ["", "123-project", "class"])
def test_rejects_invalid_project_names(name: str) -> None:
    with pytest.raises(ValueError, match="Project name"):
        PythonProjectGenerator._normalize_name(name)


def test_reports_missing_bootstrap_command(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    def raise_file_not_found(*args: object, **kwargs: object) -> None:
        raise FileNotFoundError

    monkeypatch.setattr(python.subprocess, "run", raise_file_not_found)

    with pytest.raises(RuntimeError, match="Required command is required"):
        python.bootstrap_python_project(tmp_path, project_context(tmp_path))


def test_bootstrap_initializes_main_branch_and_runs_checks(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    commands: list[list[str]] = []

    def record_command(
        command: list[str],
        **kwargs: object,
    ) -> None:
        commands.append(command)

    monkeypatch.setattr(python.subprocess, "run", record_command)
    context = project_context(tmp_path)
    project_directory = tmp_path / "prism-proxy"
    project_directory.mkdir()
    python.bootstrap_python_project(project_directory, context)

    assert commands == [
        ["git", "init", "--initial-branch=main"],
        ["git", "config", "user.name", "Example Author"],
        ["git", "config", "user.email", "author@example.com"],
        ["uv", "lock"],
        ["uv", "sync", "--locked", "--all-groups"],
        ["uv", "run", "pre-commit", "install", "--install-hooks"],
        ["uv", "run", "pre-commit", "run", "--all-files"],
        ["uv", "run", "ruff", "format", "--check", "."],
        ["uv", "run", "ruff", "check", "."],
        ["uv", "run", "pyright"],
        ["uv", "run", "pytest", "--cov"],
        ["git", "add", "--all"],
        ["git", "commit", "-m", "chore: initialize prism-proxy"],
    ]
