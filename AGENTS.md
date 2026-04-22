# AGENTS.md

## Dev environment tips

No local setup is required. CI verifies the dev environment on every PR.

## Testing instructions

CI runs the full test suite on every PR. [pre-commit.ci](https://pre-commit.ci) automatically runs linting and formatting checks. [Read the Docs](https://readthedocs.org) builds a documentation preview for every PR. Keep fixing and pushing until all CI checks pass.

## PR instructions

- Follow [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `docs:`, `chore:`, etc.
- Write commit messages and PR descriptions to explain **why**; the message and descriptions should explain the motivation.
- Remove descriptions of **what** changed from commit messages and PR descriptions. The diff shows what changed.
- Remove test information from commit messages and PR descriptions. The diff shows test code, and CI shows test results.
- Remove AI coding agent co-author lines (e.g. `Co-Authored-By: Claude`) from commit messages and PR descriptions.
