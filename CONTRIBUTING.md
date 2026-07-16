# Contributing

## Development setup

```bash
just install
just hooks
```

## Quality checks

Run the checks before opening a pull request:

```bash
just check
```

Create feature branches and use Conventional Commits, such as
`feat: add go generator`. The commit-message hook validates the convention;
`just commit` provides an interactive helper.

Do not manually change project versions, create release tags, or run `cz bump`.
Release Please owns version updates, `CHANGELOG.md`, release pull requests, and
GitHub Releases after changes merge to `main`.