"""Python project generator."""

from __future__ import annotations

import importlib.resources
import keyword
import re
import os
import subprocess
import tempfile
from collections.abc import Callable
from importlib.resources.abc import Traversable
from pathlib import Path

from just_init.generators.base import ProjectContext

BootstrapRunner = Callable[[Path, ProjectContext], None]


def bootstrap_python_project(
    project_directory: Path,
    context: ProjectContext,
) -> None:
    """Initialize Git, install tooling, and verify a generated Python project."""
    commands = (
        ["git", "init", "--initial-branch=main"],
        ["git", "config", "user.name", context.author],
        ["git", "config", "user.email", context.email],
        ["uv", "lock"],
        ["uv", "sync", "--locked", "--all-groups"],
        ["uv", "run", "pre-commit", "install", "--install-hooks"],
        ["uv", "run", "pre-commit", "run", "--all-files"],
        ["uv", "run", "ruff", "format", "--check", "."],
        ["uv", "run", "ruff", "check", "."],
        ["uv", "run", "pyright"],
        ["uv", "run", "pytest", "--cov"],
        ["git", "add", "--all"],
        [
            "git",
            "commit",
            "--allow-empty",
            "--no-verify",
            "-m",
            f"chore: initialize {project_directory.name}",
        ],
    )
    env = os.environ.copy()
    env.pop("VIRTUAL_ENV", None)
    try:
        for command in commands:
            subprocess.run(command, cwd=project_directory, check=True, env=env)
    except FileNotFoundError as error:
        raise RuntimeError(
            f"{error.filename or 'Required command'} is required to generate a Python project."
        ) from error
    except subprocess.CalledProcessError as error:
        command = " ".join(error.cmd) if isinstance(error.cmd, list) else str(error.cmd)
        raise RuntimeError(
            f"Command failed while bootstrapping project: {command}"
        ) from error


class PythonProjectGenerator:
    """Generate a complete modern Python project from packaged boilerplate."""

    language = "python"

    def __init__(
        self, bootstrap_runner: BootstrapRunner = bootstrap_python_project
    ) -> None:
        self._bootstrap_runner = bootstrap_runner

    def generate(self, context: ProjectContext) -> Path:
        """Create a project directory and generate its lockfile."""
        distribution_name, module_name, title = self._normalize_name(
            context.project_name
        )
        output_directory = context.output_directory.resolve()
        output_directory.mkdir(parents=True, exist_ok=True)
        target = output_directory / distribution_name
        if target.exists():
            raise ValueError(f"Refusing to overwrite existing directory {target}.")

        with tempfile.TemporaryDirectory(
            prefix=".just-init-",
            dir=output_directory,
        ) as temporary_directory:
            staged_project = Path(temporary_directory) / distribution_name
            self._copy_template(staged_project)
            self._replace_placeholders(
                staged_project,
                {
                    "my-project": distribution_name,
                    "my_project": module_name,
                    "My Project": title,
                    "Your Name": context.author,
                    "your.email@example.com": context.email,
                    "your-username": context.github_username,
                },
            )
            (staged_project / "src" / "my_project").rename(
                staged_project / "src" / module_name
            )
            self._bootstrap_runner(staged_project, context)
            staged_project.replace(target)

        return target

    @staticmethod
    def _normalize_name(value: str) -> tuple[str, str, str]:
        distribution_name = (
            re.sub(r"[^A-Za-z0-9]+", "-", value.strip()).strip("-").lower()
        )
        if not distribution_name:
            raise ValueError("Project name must include at least one letter or number.")

        module_name = distribution_name.replace("-", "_")
        if not module_name.isidentifier() or keyword.iskeyword(module_name):
            raise ValueError(
                f"Project name {value!r} becomes invalid import name {module_name!r}."
            )

        title = " ".join(part.capitalize() for part in distribution_name.split("-"))
        return distribution_name, module_name, title

    @staticmethod
    def _copy_template(destination: Path) -> None:
        template = importlib.resources.files("just_init").joinpath(
            "templates", "python"
        )

        def copy_tree(source: Traversable, target: Path) -> None:
            target.mkdir(parents=True, exist_ok=True)
            for child in source.iterdir():
                child_target = target / child.name
                if child.is_dir():
                    copy_tree(child, child_target)
                else:
                    child_target.write_bytes(child.read_bytes())

        copy_tree(template, destination)

    @staticmethod
    def _replace_placeholders(
        project_directory: Path, replacements: dict[str, str]
    ) -> None:
        for path in project_directory.rglob("*"):
            if path.is_dir():
                continue
            try:
                content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue

            for placeholder, replacement in replacements.items():
                content = content.replace(placeholder, replacement)
            path.write_text(content, encoding="utf-8")
