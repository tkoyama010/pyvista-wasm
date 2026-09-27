# AGENTS.md

This repository aims to fully realize PyVista's API using vtk-wasm, enabling PyVista to run entirely in the browser via WebAssembly.

The architecture calls vtk-wasm from TypeScript: TypeScript acts as the glue layer that loads the vtk-wasm module and bridges its C++ VTK bindings to the Python-facing PyVista API.

## Project structure

- `src/pyvista_wasm/` — Python package (the PyVista-like API). Modules mirror the PyVista API surface (`plotter.py`, `mesh.py`, `camera.py`, ...). Uses lazy loading per [SPEC 1](https://scientific-python.org/specs/spec-0001/).
- `src/pyvista_wasm/templates/` — generated JavaScript bundles. Do not edit by hand; edit `ts/renderer.ts` and rebuild.
- `ts/renderer.ts` — TypeScript rendering bridge to vtk-wasm.
- `packages/vtk-wasm-binary/` — vtk-wasm binary artifacts. Never commit generated binaries from here.
- `tests/` — pytest suite (browser rendering tests use Playwright).
- `.github/ISSUE_TEMPLATE/`, `.github/pull_request_template.md` — contribution templates.

## Stack

- Python ≥ 3.12 (per [SPEC 0](https://scientific-python.org/specs/spec-0000/), minimums drop on a schedule)
- NumPy ≥ 2.0
- vtk-wasm (bundled in `packages/vtk-wasm-binary/`)
- Node.js with esbuild for the TypeScript bundle; Biome for JS/TS lint and format; TypeScript 7 for type checks
- pytest + Playwright (Chromium) for tests
- Ruff + mypy for Python lint and typing

## Commands

No local setup is required for review; CI verifies the dev environment on every PR. For local work:

```bash
# Run the test suite (Playwright tests excluded until VTK.wasm API work lands, see issue #2)
tox -e py312

# Lint and type-check Python
tox -e lint

# Lint / format / type-check / bundle TypeScript (requires `npm install`)
npm run lint
npm run format
npm run typecheck
npm run build

# Run pre-commit hooks locally
pre-commit run --all-files
```

## Testing

```bash
pytest tests/ src/ -m "not playwright" --cov=pyvista_wasm
```

Conventions:

- Group related tests into a class named after the function or command under test (e.g. `TestCameraAzimuth`, `TestTextureRendering`).
- Do not use comment banners (e.g. `# ---`) to separate test sections; use classes instead.

CI runs the full test suite on every PR, [pre-commit.ci](https://pre-commit.ci) runs linting and formatting checks, and [Read the Docs](https://readthedocs.org) builds a documentation preview for every PR. After creating a PR, monitor CI continuously, keep fixing and pushing until all checks pass.

## Code style

- Python: format with `ruff format`, lint with `ruff check`, type-annotate for `mypy src/`.
- TypeScript/JavaScript: format and lint with Biome (`npm run lint`, `npm run format`).
- YAML: formatted by `yamlfmt`, linted by `yamllint` (via pre-commit).

## Git workflow

- Follow [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `docs:`, `chore:`, etc.
- When creating a PR, follow the template in `.github/pull_request_template.md`.
- Write commit messages and PR descriptions to explain **why**; the diff shows what changed and CI shows test results.

## Boundaries

Never do the following:

- Never commit or modify anything under `.github/` workflows, CI configuration, or `.pre-commit-config.yaml` — generated/maintained infrastructure is out of scope for agent edits.
- Never commit secrets, API keys, or credentials. Never modify files that hold them.
- Never commit generated artifacts: `src/pyvista_wasm/templates/renderer.js` is built via `npm run build`, and vtk-wasm binaries live in `packages/vtk-wasm-binary/`.
- Never edit generated files by hand.

## Contributing

When creating an issue, follow the templates in `.github/ISSUE_TEMPLATE/`. Details that change often (dependency pins, hook lists) live in `pyproject.toml`, `package.json`, and `.pre-commit-config.yaml` — check those files instead of trusting this document.
