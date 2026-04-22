# AGENTS.md

## Dev environment tips

No local setup is required. CI verifies the dev environment on every PR.

## Testing instructions

CI runs the full test suite on every PR. Keep fixing and pushing until all CI checks pass.

## PR instructions

- Follow [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `docs:`, `chore:`, etc.
- Write commit messages and PR descriptions to explain **why**, not what. The diff shows what changed; the message should explain the motivation.
- Remove AI coding agent co-author lines (e.g. `Co-Authored-By: Claude`) from commit messages and PR descriptions.
- Ignore `src/pyvista_wasm/templates/renderer.js` — it is a generated build artifact.
