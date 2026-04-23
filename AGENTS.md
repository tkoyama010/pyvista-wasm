# AGENTS.md

This repository aims to fully realize PyVista's API using vtk-wasm, enabling PyVista to run entirely in the browser via WebAssembly.

The architecture calls vtk-wasm from TypeScript: TypeScript acts as the glue layer that loads the vtk-wasm module and bridges its C++ VTK bindings to the Python-facing PyVista API.

## Dev environment tips

No local setup is required. CI verifies the dev environment on every PR.

## Testing instructions

- CI runs the full test suite on every PR.
- [pre-commit.ci](https://pre-commit.ci) automatically runs linting and formatting checks.
- [Read the Docs](https://readthedocs.org) builds a documentation preview for every PR.
- After creating a PR, monitor CI continuously, keep fixing and pushing until all checks pass.

## Test conventions

- Group related tests into a class named after the function or command under test (e.g. `TestCreateGif`, `TestCaptureMarimoPreview`).
- Do not use comment banners (e.g. `# ---`) to separate test sections; use classes instead.

## Issue instructions

- When creating an issue, follow the templates in `.github/ISSUE_TEMPLATE/` (`bug_report.yml`, `feature_request.yml`, `documentation.yml`).

## PR instructions

- Follow [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `docs:`, `chore:`, etc.
- Write commit messages and PR descriptions to explain **why**; the message and descriptions should explain the motivation.
- Remove commit messages and PR descriptions to explain **what**; the diff shows what changed.
- Remove commit messages and PR descriptions to explain **test information**; the diff shows test code, and CI shows test results.
- Remove AI coding agent co-author lines (e.g. `Co-Authored-By: Claude`) from commit messages and PR descriptions.
