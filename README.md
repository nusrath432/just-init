# just-init

`just-init` is an extensible project generator. It currently creates modern
Python projects and is structured to add Go and TypeScript generators later.

## Generate a Python project

Requirements: [uv](https://docs.astral.sh/uv/), [just](https://just.systems/),
and Git.

```bash
git clone https://github.com/your-username/just-init.git
cd just-init
just init python prism-proxy
```

This creates `../prism-proxy/` (one level above your current directory) with the `prism_proxy` import package, generated
`uv.lock`, project-specific metadata, documentation, workflows, release
configuration, and tests. It prompts for your name, email, and GitHub username
one at a time; initializes Git with a `main` branch; installs dependencies and
hooks; runs the generated project's checks; and creates the verified initial
commit, for example `chore: initialize prism-proxy`.

For non-interactive generation:

```bash
just init python prism-proxy . "Example Author" "author@example.com" "example-org"
```

## Develop just-init

```bash
just install
just hooks
just check
```

| Command | Purpose |
| --- | --- |
| `just init python <name>` | Create a Python project one level above the current directory by default. |
| `just test` | Run generator tests with coverage. |
| `just lint` | Run Ruff linting. |
| `just format` | Apply Ruff formatting. |
| `just typecheck` | Run Pyright. |
| `just check` | Run linting, formatting verification, type checks, and tests. |
| `just commit` | Create a Conventional Commit with Commitizen. |
| `just build` | Build source and wheel distributions. |
| `just clean` | Remove local caches and build artifacts. |

## Contribution and releases

Use Conventional Commits, for example `feat: add typescript generator`.
Pre-commit validates files, Ruff checks, and commit messages. Pull requests to
`main` run the CI workflow.

Do not manually bump versions or run `cz bump`. Release Please creates release
pull requests, updates `CHANGELOG.md`, creates tags and GitHub Releases, and
attaches built distributions when a release pull request is merged.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
