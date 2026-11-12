# Prefer a shared vtk-wasm object wrapping helper over per-module plumbing

* Status: accepted
* Date: 2026-02-28
* Decision-makers: tkoyama010

## Context and Problem Statement

Every module that touches the vtk-wasm namespace (`mesh.py`, `plotter.py`, `rendering.py`, and `ts/renderer.ts`) hand-rolls the same object plumbing: awaited getter calls, object identity/lifetime management (`delete()` calls), and error propagation across the WASM boundary. Issue [#797](https://github.com/tkoyama010/pyvista-wasm/issues/797) asks for a shared pattern matching PyVista's object model, backed by the `VTK::CommonCore` object model that vtk-wasm provides underneath. How should the wrapping pattern be defined and applied?

## Decision Drivers

- **Consistency**: the same vtk-wasm interaction should look the same in every module.
- **Auditability**: object lifetime (wasm objects are never garbage-collected) must be reviewable in one place.
- **Low ceremony**: the pattern must not introduce an abstraction layer that hides the awaited-getter nature of the vtk-wasm API.

## Considered Options

- **Option A: Shared wrapping helper, applied module by module**
- **Option B: Continue per-module hand-rolled plumbing**
- **Option C: A full wrapper class hierarchy mirroring VTK's object tree**

## Decision

We go with **Option A: a shared wrapping helper, applied module by module**.

The shared pattern is codified as a single helper module (`ts/renderer.ts` functions for the WASM side, `rendering.py` for the scene-data side) with these rules:

1. **Every vtk-wasm getter is awaited.** Getter methods return Promises; calling without `await` is a bug the type layer (`ts/vtk.d.ts`) already rejects.
2. **Object lifetime is explicit.** Any `vtk.*` object created in a helper is either attached to the scene (actor/renderer/camera) or explicitly `delete()`-d before the helper returns. No leaked temporaries.
3. **Errors propagate as overlay messages.** A helper that cannot complete throws; `buildScene` catches and shows the loading-overlay error. No silent fallbacks inside helpers.
4. **One vocabulary.** Helpers are named `setup*` (build and attach), `apply*` (mutate existing objects), and `inject*` (copy Python-side data into wasm objects).

Modules migrate to the helper one at a time; a module keeps its own plumbing only while a migration PR touches it.

## Consequences

- New vtk-wasm interactions copy an auditable template instead of reinventing promise/lifetime handling.
- The full wrapper hierarchy of Option C is rejected: it would hide the async boundary and duplicate `ts/vtk.d.ts`.
- Migration is incremental; until it completes, some modules still hand-roll plumbing (tracked against issue #797).
