# conda recipe

This directory holds the conda recipe for `pyvista-wasm`, used to submit the
package to [conda-forge](https://conda-forge.org) via
[staged-recipes](https://github.com/conda-forge/staged-recipes).

- `pyvista-wasm/recipe.yaml` — the recipe in the v1 (`recipe.yaml`) format
  required by staged-recipes. Keep the `version`, `sha256`, and runtime
  dependencies in sync with `pyproject.toml`.
- Once the package is on conda-forge, version bumps on new PyPI releases are
  handled automatically by the conda-forge
  [auto-tick bot](https://github.com/regro/cf-scripts) — this copy does not
  need to be updated for every release, only when the recipe itself changes.
- After the feedstock is created, all maintenance happens in
  [conda-forge/pyvista-wasm-feedstock](https://github.com/conda-forge/pyvista-wasm-feedstock);
  this directory then serves as the upstream reference.

Notes:

- The sdist already ships a prebuilt `renderer.js`, so the recipe strips the
  `hatch-build-scripts` hook (which would require `npm ci` network access)
  before installing.
- `vtk-wasm` is **not** a Python dependency: the JavaScript/WASM assets are
  loaded from CDN at render time inside the browser, so nothing extra is
  needed on the conda side.
