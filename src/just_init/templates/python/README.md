# My Project

A short description of the project.

## Overview

My Project is a typed Python package maintained with reproducible tooling,
automated quality gates, and Conventional Commit-based releases.

## Requirements and support

- Python 3.13
- [uv](https://docs.astral.sh/uv/)
- [just](https://just.systems/)

Only the latest released version receives security fixes. See
[SECURITY.md](SECURITY.md) for responsible disclosure guidance.

## Quick start

```bash
just install
just hooks
just check
```

## Development workflow

| Command | Purpose |
| --- | --- |
| `just test` | Run tests with coverage. |
| `just lint` | Run Ruff linting. |
| `just format` | Apply Ruff formatting. |
| `just typecheck` | Run Pyright. |
| `just check` | Run all quality checks. |
| `just build` | Build source and wheel distributions. |

Run `just check` before opening a pull request. The CI workflow repeats these
quality gates on pull requests and `main`.

## Contribution and releases

Read [CONTRIBUTING.md](CONTRIBUTING.md) before contributing. Use Conventional
Commits, for example `feat: add parser support`.

Release Please owns version changes, changelog updates, tags, and GitHub
Releases. Do not manually edit versions or run `cz bump`.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
