"""Command-line interface for just-init."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from email_validator import EmailNotValidError, validate_email
from just_init.generators.python import generate_python_project


def resolve_value(value: str, label: str) -> str:
    """Resolve explicit metadata or request it interactively."""
    resolved = value.strip()
    if resolved:
        return resolved
    if sys.stdin.isatty():
        resolved = input(f"{label}: ").strip()
        if resolved:
            return resolved
    raise ValueError(f"{label} is required. Supply the matching command option.")


def resolve_email(value: str) -> str:
    """Resolve and validate the author's email."""
    while True:
        email = resolve_value(value, "Author email")

        try:
            validate_email(email, check_deliverability=False)
            return email
        except EmailNotValidError as error:
            if not sys.stdin.isatty():
                raise ValueError(f"Invalid email: {error}") from None

            print(f"Invalid email: {error}")
            value = ""


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Generate a project with just-init.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    init_parser = subparsers.add_parser("init", help="Generate a new project.")
    init_parser.add_argument("language", choices=["python"])
    init_parser.add_argument("project_name")
    init_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(".."),
        help="Project parent directory. Defaults to one level above the current directory.",
    )
    init_parser.add_argument("--author", default="")
    init_parser.add_argument("--email", default="")
    init_parser.add_argument("--github-username", default="")
    return parser.parse_args()


def main() -> int:
    """Generate the requested project."""
    args = parse_args()
    try:
        project_directory = generate_python_project(
            project_name=args.project_name,
            output_directory=args.output_dir.expanduser().resolve(),
            author=resolve_value(args.author, "Author name"),
            email=resolve_email(args.email),
            github_username=resolve_value(args.github_username, "GitHub username or organization"),
        )
    except (RuntimeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    print(f"Created {args.language} project at {project_directory}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
