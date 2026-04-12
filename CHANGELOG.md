# Changelog

## [0.5.0](https://github.com/tkoyama010/pyvista-wasm/compare/pyvista-wasm-v0.4.0...pyvista-wasm-v0.5.0) (2026-04-12)


### Features

* add VTK.wasm configuration options (rendering backend and execution mode) ([#108](https://github.com/tkoyama010/pyvista-wasm/issues/108)) ([d5a3347](https://github.com/tkoyama010/pyvista-wasm/commit/d5a334773c462e95b3aaf3eaecd06087f090f2a8))
* mirror VTK.wasm binary to npm and serve via jsDelivr CDN ([#110](https://github.com/tkoyama010/pyvista-wasm/issues/110)) ([2c85e37](https://github.com/tkoyama010/pyvista-wasm/commit/2c85e379095f4017bb8333712fa49d7c2f6a74b4))

## [0.4.0](https://github.com/tkoyama010/pyvista-wasm/compare/pyvista-wasm-v0.3.0...pyvista-wasm-v0.4.0) (2026-04-12)

### Features

- add loading overlay components for 3D rendering UX ([#107](https://github.com/tkoyama010/pyvista-wasm/issues/107)) ([a312ffd](https://github.com/tkoyama010/pyvista-wasm/commit/a312ffd40828ebba1af6163effdbbfe817d4cae8))

### Bug Fixes

- update preview workflow to use ReadTheDocs JupyterLite URL ([#90](https://github.com/tkoyama010/pyvista-wasm/issues/90)) ([fc695bb](https://github.com/tkoyama010/pyvista-wasm/commit/fc695bb823fa9fdc0c5a489c46c7d1f419a96d4b))
- **workflow:** remove --system flag from uv run to fix nightly tests ([#88](https://github.com/tkoyama010/pyvista-wasm/issues/88)) ([42526e5](https://github.com/tkoyama010/pyvista-wasm/commit/42526e5da211afa68fc497935a0ef090fe717fb2))

## [0.3.0](https://github.com/tkoyama010/pyvista-wasm/compare/pyvista-wasm-v0.2.0...pyvista-wasm-v0.3.0) (2026-04-05)

### Features

- add __main__.py to enable python -m pyvista_wasm ([#80](https://github.com/tkoyama010/pyvista-wasm/issues/80)) ([d3f4346](https://github.com/tkoyama010/pyvista-wasm/commit/d3f4346cba0cdc32f20ec70fc255d5e09552ae82))
- add intro.ipynb notebook and update ReadTheDocs config for JupyterLite ([#83](https://github.com/tkoyama010/pyvista-wasm/issues/83)) ([291f90e](https://github.com/tkoyama010/pyvista-wasm/commit/291f90eba1dc81560615f12735d6d26b779168dd))
- Update Try Lite Now link to ReadTheDocs and remove JupyterLite deploy action ([#82](https://github.com/tkoyama010/pyvista-wasm/issues/82)) ([0baad4c](https://github.com/tkoyama010/pyvista-wasm/commit/0baad4cb91b420141149b1be159edab677903bf1))

### Bug Fixes

- **workflow:** add site verification step and increase timeout for preview capture ([#81](https://github.com/tkoyama010/pyvista-wasm/issues/81)) ([3d56501](https://github.com/tkoyama010/pyvista-wasm/commit/3d5650186de66ebc63d47529e5919d35895aa93d))

### Documentation

- add SECURITY.md ([#73](https://github.com/tkoyama010/pyvista-wasm/issues/73)) ([cce04b1](https://github.com/tkoyama010/pyvista-wasm/commit/cce04b18ccdc5677a932d3df5e7ea8f4abef4720))
- update stlite badge URL to new share.stlite.net domain ([#55](https://github.com/tkoyama010/pyvista-wasm/issues/55)) ([d55d33d](https://github.com/tkoyama010/pyvista-wasm/commit/d55d33d89f41fe69c8676682babb17136176c07a))

## [0.2.0](https://github.com/tkoyama010/pyvista-wasm/compare/pyvista-wasm-v0.1.1...pyvista-wasm-v0.2.0) (2026-03-31)

### Features

- add "Try it with JupyterLite!" button to Sphinx docs ([#40](https://github.com/tkoyama010/pyvista-wasm/issues/40)) ([39de62b](https://github.com/tkoyama010/pyvista-wasm/commit/39de62ba611133660f5c78fd3430deb63f30fef9))
- add preview table and JupyterLite deployment ([#41](https://github.com/tkoyama010/pyvista-wasm/issues/41)) ([ed5d76c](https://github.com/tkoyama010/pyvista-wasm/commit/ed5d76c206ee5283db54c76a1e289297a2b91877))

### Bug Fixes

- resolve mypy type errors in mesh.py ([#48](https://github.com/tkoyama010/pyvista-wasm/issues/48)) ([f01c4a8](https://github.com/tkoyama010/pyvista-wasm/commit/f01c4a84dca1ef1c935aa545b3f8b2370514fc4f))

### Documentation

- add stlite badge to README ([#34](https://github.com/tkoyama010/pyvista-wasm/issues/34)) ([f68169a](https://github.com/tkoyama010/pyvista-wasm/commit/f68169a3ceda6cebb00dfedab2bfeb6306acd90d))

## [0.1.1](https://github.com/tkoyama010/pyvista-wasm/compare/pyvista-wasm-v0.1.0...pyvista-wasm-v0.1.1) (2026-03-25)

### Bug Fixes

- render mesh PolyData correctly in VTK.wasm ([#25](https://github.com/tkoyama010/pyvista-wasm/issues/25)) ([14a0ca3](https://github.com/tkoyama010/pyvista-wasm/commit/14a0ca391001a7c34d4a8a8c61165e7319da1c5a))

### Documentation

- add docs folder to satisfy PY004 requirement ([#27](https://github.com/tkoyama010/pyvista-wasm/issues/27)) ([9906767](https://github.com/tkoyama010/pyvista-wasm/commit/99067674fb17fb60b812fb8607ef1bfad26050ef))
- add PyPI badge to Install section ([#24](https://github.com/tkoyama010/pyvista-wasm/issues/24)) ([8e28c82](https://github.com/tkoyama010/pyvista-wasm/commit/8e28c82226ac902a26782744d7b52d8519792fd6))

### Continuous Integration

- add concurrency group to auto-cancel redundant runs (GH102) ([#28](https://github.com/tkoyama010/pyvista-wasm/issues/28)) ([3e82392](https://github.com/tkoyama010/pyvista-wasm/commit/3e82392622e19eca6075a9f515258f1f8000bb59))
- add Renovate for automated VTK.wasm CDN version updates ([#21](https://github.com/tkoyama010/pyvista-wasm/issues/21)) ([a0cec82](https://github.com/tkoyama010/pyvista-wasm/commit/a0cec8244ad6d62cb48db760fd031d920b44f75f))
- add workflow to update uv.lock on release-please PRs ([#30](https://github.com/tkoyama010/pyvista-wasm/issues/30)) ([39af99b](https://github.com/tkoyama010/pyvista-wasm/commit/39af99bcf4fefd8f0b5ba76db303b2604f4da61f))

## 0.1.0 (2026-03-25)

### Documentation

- add contributing guide ([#14](https://github.com/tkoyama010/pyvista-wasm/issues/14)) ([37737f7](https://github.com/tkoyama010/pyvista-wasm/commit/37737f7764eb7e920d201db45b138ba358404dce)), closes [#8](https://github.com/tkoyama010/pyvista-wasm/issues/8)
- add GitHub Sponsors funding configuration ([#22](https://github.com/tkoyama010/pyvista-wasm/issues/22)) ([a4f2fbb](https://github.com/tkoyama010/pyvista-wasm/commit/a4f2fbbb5aaae7c29cc75f62e84508879de8136c))
- add issue templates for bug reports, features, and documentation ([#12](https://github.com/tkoyama010/pyvista-wasm/issues/12)) ([1eab65d](https://github.com/tkoyama010/pyvista-wasm/commit/1eab65d2c07babbf7de3e41bec42efce4a8a43cc)), closes [#6](https://github.com/tkoyama010/pyvista-wasm/issues/6)
- add pull request template and code of conduct ([#13](https://github.com/tkoyama010/pyvista-wasm/issues/13)) ([853757b](https://github.com/tkoyama010/pyvista-wasm/commit/853757b97f94caaefeb4731a1560c46152253ad4)), closes [#7](https://github.com/tkoyama010/pyvista-wasm/issues/7)

### Continuous Integration

- add Dependabot for GitHub Actions and npm dependency updates ([#20](https://github.com/tkoyama010/pyvista-wasm/issues/20)) ([63d43ea](https://github.com/tkoyama010/pyvista-wasm/commit/63d43ea6970290f427435fa9429db69186cdddba))
- add nightly tests workflow (SPEC-0004) ([#11](https://github.com/tkoyama010/pyvista-wasm/issues/11)) ([186ab1e](https://github.com/tkoyama010/pyvista-wasm/commit/186ab1e163e11eabdb3190996b7dccbf2479fe29)), closes [#5](https://github.com/tkoyama010/pyvista-wasm/issues/5)
- add release-please workflow for automated releases ([#10](https://github.com/tkoyama010/pyvista-wasm/issues/10)) ([9fb1600](https://github.com/tkoyama010/pyvista-wasm/commit/9fb160083b0ac21f2d4e53c08fcb25bda30b8718))
