# Decide how pyvista-wasm executes PyVista filters on top of the vtk-wasm pipeline

* Status: accepted
* Date: 2026-02-14
* Decision-makers: tkoyama010

## Context and Problem Statement

PyVista's filter API (`clip`, `decimate`, `smooth`, `contour`, ...) is a thin Python wrapper over VTK's pipeline: each filter is a `vtkAlgorithm` whose output ports feed the renderer. pyvista-wasm drives the same VTK code compiled to WebAssembly (VTK.wasm), where `VTK::CommonExecutionModel` — the module defining algorithms, ports, and the pipeline — is available with serialization coverage ([vtk-wasm roadmap](https://kitware.github.io/vtk-wasm/roadmap/)). However, the pyvista-wasm renderer bridge (`ts/renderer.ts`) builds scenes as a flat list of actors with a `source` per actor, and some algorithm classes are not registered with the VTK.wasm `vtkDeserializer` in the rendering-mode binary — `vtkShrinkPolyData` is a known example, worked around with a hand-written JavaScript implementation. Issue [#778](https://github.com/tkoyama010/pyvista-wasm/issues/778) asks how pyvista-wasm should execute PyVista filters on top of the available `VTK::CommonExecutionModel` classes. Which execution strategy should pyvista-wasm adopt?

## Decision Drivers

- **PyVista parity**: filter methods should behave like their PyVista counterparts without Python-side reimplementation drift.
- **Upstream availability varies**: some `vtkAlgorithm` classes are not deserializable in the current VTK.wasm binary, so a strategy that requires every filter to be a wasm pipeline object fails for those filters.
- **Renderer simplicity**: the bridge must stay auditable; a scene format that grows an unbounded set of bespoke cases is a maintenance liability.
- **Testability**: the strategy must be verifiable in pytest (mock renderer) and Playwright (browser) without flaky visual assertions.

## Considered Options

- **Option A: Prefer wasm pipeline objects, fall back to documented manual implementations (hybrid)**
- **Option B: Always serialize real `vtkAlgorithm` chains and require upstream to register every filter**
- **Option C: Reimplement all filters in pure Python/NumPy and never use the wasm pipeline**

## Decision Outcome

Chosen option: **Option A — hybrid, prefer the wasm pipeline, fall back to manual implementations**.

1. When a filter class is registered with the VTK.wasm deserializer, pyvista-wasm serializes it as a `source` filter chain in the scene data and lets VTK.wasm execute it (this is how `clip`, `tube`, and `contour` work today).
2. When a filter class is unavailable upstream, pyvista-wasm implements it manually in the renderer bridge (as `shrink` already does), and the filter's docstring documents the manual implementation so the workaround can be removed when upstream registers the class.
3. Each new filter lands one at a time with a mock-renderer test asserting the serialized scene data and, where practical, a Playwright browser test.

This keeps PyVista parity for the most filters at the lowest maintenance cost, degrades gracefully where the wasm binary is incomplete, and gives every filter a documented upgrade path to a real pipeline object.

### Positive consequences

- Filters ship incrementally without blocking on upstream VTK.wasm registrations.
- The scene format stays flat and auditable; no bespoke pipeline graph format is introduced.
- Missing upstream deserializer registrations are easy to inventory (search for the documented manual implementations).

### Negative consequences

- Manual fallbacks can drift from VTK semantics until upstream classes become available; each carries a documented ceiling.
- Two execution paths mean two test surfaces per filter.

## Validation

The strategy is already validated by the shipped filters: `clip`, `tube`, and `contour` exercise the wasm pipeline path, and `shrink` exercises the manual fallback path. Both paths are covered by `tests/test_mesh.py`.

## More information

- Issue [#778](https://github.com/tkoyama010/pyvista-wasm/issues/778)
- [vtk-wasm roadmap — module coverage](https://kitware.github.io/vtk-wasm/roadmap/)
