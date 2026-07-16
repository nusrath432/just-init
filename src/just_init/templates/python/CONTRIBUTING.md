# Contributing to My Project

## Before you start

- Discuss substantial changes in an issue before implementation.
- Follow the [Code of Conduct](CODE_OF_CONDUCT.md).
- Never include credentials, production data, or generated artifacts in a pull
  request.

## Development setup

```bash
just install
just hooks
```

## Pull requests

1. Create a focused branch from `main`.
2. Add or update tests with behavior changes.
3. Run `just check`.
4. Use a Conventional Commit, such as `feat: add parser support`.
5. Complete the pull-request template and address review feedback.

The commit-message hook validates messages, and `just commit` provides an
interactive helper.

Do not manually change versions, create release tags, or run `cz bump`. Release
Please manages versions, `CHANGELOG.md`, release pull requests, and releases.
