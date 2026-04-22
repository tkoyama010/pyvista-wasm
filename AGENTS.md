# AGENTS.md

## Dev environment

```bash
uv sync --group dev
uv run pre-commit install
uv run playwright install chromium
npm install  # only when editing TypeScript files
npm run build  # regenerate src/pyvista_wasm/templates/renderer.js after TS edits
```

## Testing

```bash
uv run pytest -m "not playwright"   # standard test run
uv run tox -e py312                 # test against a specific Python version
uv run pytest --cov=pyvista_wasm    # with coverage
```

## PR instructions

- Follow [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `docs:`, `chore:`, etc.
- Write commit messages and PR descriptions to explain **why**, not what. The diff shows what changed; the message should explain the motivation.
- Remove AI coding agent co-author lines (e.g. `Co-Authored-By: Claude`) from commit messages and PR descriptions.
- Run `uv run pre-commit run --all-files` before opening a PR.
- Ignore `src/pyvista_wasm/templates/renderer.js` — it is a generated build artifact.
