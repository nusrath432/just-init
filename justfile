# List available commands
default:
    @just --list


# Generate a project in a new child directory.
init language project_name output_dir="." author="" email="" github_username="":
    uv run just-init init {{quote(language)}} {{quote(project_name)}} --output-dir {{quote(output_dir)}} --author {{quote(author)}} --email {{quote(email)}} --github-username {{quote(github_username)}}


# Install dependencies
install:
    uv sync


# Install git hooks
hooks:
    uv run pre-commit install --install-hooks


# Run tests
test:
    uv run pytest --cov


# Lint
lint:
    uv run ruff check .


# Format
format:
    uv run ruff format .


# Check formatting
format-check:
    uv run ruff format --check .


# Type check
typecheck:
    uv run pyright


# Run all checks
check:
    just lint
    just format-check
    just typecheck
    just test


# Run pre-commit manually
precommit:
    uv run pre-commit run --all-files


# Create conventional commit
commit:
    uv run cz commit


# Validate commit message
commit-check:
    uv run cz check --commit-msg-file .git/COMMIT_EDITMSG


# Update dependencies
update:
    uv lock --upgrade


# Build package
build:
    uv build


# Clean caches and build artifacts
clean:
    find . -type d -name "__pycache__" -prune -exec rm -rf {} +
    find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +
    find . -type d -name ".ruff_cache" -prune -exec rm -rf {} +
    find . -type d -name ".pyright" -prune -exec rm -rf {} +
    rm -rf .coverage
    rm -rf htmlcov
    rm -rf build
    rm -rf dist
    find . -type d -name "*.egg-info" -prune -exec rm -rf {} +


# Full reset
clean-all:
    just clean
    rm -rf .venv
