"""Python project generator."""

from __future__ import annotations

import importlib.resources
import keyword
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

def bootstrap_python_project(project_directory: Path, author: str, email: str) -> None:
    """Initialize a generated project with a minimal first commit."""
    commands = (
        ["git", "init", "--initial-branch=main"],
        ["git", "config", "user.name", author],
        ["git", "config", "user.email", email],
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


def _normalize_name(value: str) -> tuple[str, str, str]:
    distribution_name = re.sub(r"[^A-Za-z0-9]+", "-", value.strip()).strip("-").lower()
    if not distribution_name:
        raise ValueError("Project name must include at least one letter or number.")

    module_name = distribution_name.replace("-", "_")
    if not module_name.isidentifier() or keyword.iskeyword(module_name):
        raise ValueError(
            f"Project name {value!r} becomes invalid import name {module_name!r}."
        )

    title = " ".join(part.capitalize() for part in distribution_name.split("-"))
    return distribution_name, module_name, title


def generate_python_project(
    project_name: str,
    output_directory: Path,
    author: str,
    email: str,
    github_username: str,
) -> Path:
    distribution_name, module_name, title = _normalize_name(project_name)
    output_directory = output_directory.resolve()
    output_directory.mkdir(parents=True, exist_ok=True)
    target = output_directory / distribution_name
    if target.exists():
        raise ValueError(f"Refusing to overwrite existing directory {target}.")

    template = importlib.resources.files("just_init").joinpath("templates", "python")
    with tempfile.TemporaryDirectory(prefix=".just-init-", dir=output_directory) as td:
        staged_project = Path(td) / distribution_name
        with importlib.resources.as_file(template) as template_directory:
            shutil.copytree(
                template_directory,
                staged_project,
                ignore=shutil.ignore_patterns(
                    "*.md",
                    "*.json",
                    "*.yaml",
                    "*.yml",
                    ".*",
                    "LICENSE",
                    "__pycache__",
                    "*.pyc",
                ),
            )

        replacements = {
            "my-project": distribution_name,
            "my_project": module_name,
            "My Project": title,
            "Your Name": author,
            "your.email@example.com": email,
            "your-username": github_username,
        }
        for path in staged_project.rglob("*"):
            if path.is_dir():
                continue
            try:
                content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for placeholder, replacement in replacements.items():
                content = content.replace(placeholder, replacement)
            path.write_text(content, encoding="utf-8")

        (staged_project / "src" / "my_project").rename(staged_project / "src" / module_name)

        keep_top_level = {"justfile", "pyproject.toml", "src"}
        for child in staged_project.iterdir():
            if child.name not in keep_top_level:
                if child.is_dir():
                    shutil.rmtree(child)
                else:
                    child.unlink()

        for child in (staged_project / "src").iterdir():
            if child.name != module_name:
                if child.is_dir():
                    shutil.rmtree(child)
                else:
                    child.unlink()

        bootstrap_python_project(staged_project, author, email)
        staged_project.replace(target)

    return target
