---
status: proposed
date: 2026-08-21
decision-makers: [tkoyama010]
consulted: []
informed: []
---

# Track PyVista API coverage matrix for pyvista-wasm

## Context and Problem Statement

pyvista-wasm exposes a growing subset of the PyVista public API in the browser via vtk-wasm, but there is no single place where a contributor or user can see which PyVista classes, functions, and filters are available, which are partial, and which are still missing. Parent issue [#515](https://github.com/tkoyama010/pyvista-wasm/issues/515) captures the need to track PyVista-to-pyvista-wasm API parity and ships a baseline snapshot of current coverage (v0.11.0) grouped by category — Plotting, Camera, Lighting, Mesh/Data, Filters, Readers, Text, Texture, Examples. The public API surface pyvista-wasm actually implements is declared in the type stub `src/pyvista_wasm/__init__.pyi`, and the documented surface is rendered by `docs/api/index.md` via Sphinx `autosummary`. Today these two surfaces are consistent by convention but nothing records *why* a coverage matrix is the parity-tracking mechanism, what its source of truth is, where it is published, how partial coverage is represented, or how often it is synced — and the parity gaps listed in [#515](https://github.com/tkoyama010/pyvista-wasm/issues/515) (datasets, filters, readers, plotting, theme, utilities) live only in an issue body that will scroll away and drift from the code. Which parity-tracking mechanism should pyvista-wasm adopt?

## Decision Drivers

- **Single-glance visibility of parity gaps**: A user or contributor must be able to see the entire PyVista public API surface and its pyvista-wasm coverage status in one place, without hopping between issues, project boards, or source files. This is a knock-out criterion.
- **Published where users already look**: The coverage status must live in the documentation site (where users go to learn the API), not only in a GitHub tracking issue (where users do not look). Co-locating coverage with the API reference is a knock-out criterion.
- **Single source of truth tied to the code**: The matrix must be derivable from the actual implemented surface — the type stub `src/pyvista_wasm/__init__.pyi` — so it cannot silently drift from what the package exports. A tracking issue body that is hand-edited and unrelated to the code is a drift risk.
- **Low maintenance burden**: The project has a single maintainer; the parity-tracking mechanism must not require per-item GitHub issues, a project board to groom, or a bespoke dashboard to host.
- **Representation of partial coverage**: Some surfaces are partially implemented (e.g., `PolyData` exists but many `PolyDataFilters` methods do not; `PointData` exists but not all data-array helpers do). The mechanism must represent *Partial* coverage and list what is missing, not just a binary implemented/not-implemented.
- **Sync cadence aligned to releases**: The matrix must be refreshed at a predictable cadence (per release) so it reflects the shipped package, not an arbitrary snapshot.

## Considered Options

- **Coverage matrix published in the docs, sourced from the `.pyi` stub, synced per release** — a single matrix table in `docs/api/` grouped by category, marking each PyVista public class/function as *Implemented*, *Partial*, or *Not implemented*; for *Partial* entries the missing methods/attributes are listed; the implemented column is generated/verified against `src/pyvista_wasm/__init__.pyi`; the matrix is refreshed per release and linked from `docs/api/index.md`.
- **Checklist of separate GitHub issues (one issue per PyVista item)** — one issue per missing class/function/filter, tracked on the Scrum board; the project board is the parity view.
- **Coverage matrix kept in a tracking issue body** — the matrix from [#515](https://github.com/tkoyama010/pyvista-wasm/issues/515) is maintained by editing the issue body over time; no docs surface.
- **Automated parity report generated in CI** — a script diffs the PyVista public API against `src/pyvista_wasm/__init__.pyi` and posts a parity report as a CI artifact / PR comment on every release tag.

## Decision Outcome

Chosen option: "Coverage matrix published in the docs, sourced from the `.pyi` stub, synced per release", because it is the only option that satisfies every decision driver simultaneously — it gives single-glance visibility of the whole surface in one table, it publishes the matrix on the documentation site where users already look (rather than burying it in a GitHub issue), it anchors the implemented column to the type stub `src/pyvista_wasm/__init__.pyi` (the same file Sphinx `autosummary` renders in `docs/api/index.md`), it represents partial coverage with an explicit *Partial* status plus a list of missing methods/attributes, it places a per-release sync burden on a single maintainer rather than grooming a per-item issue backlog, and it makes the matrix part of the reviewed docs PR flow so the *why* is preserved (see [ADR-0000](0000-use-markdown-architectural-decision-records.md)).

- **Source of truth**: `src/pyvista_wasm/__init__.pyi` — the type stub that declares every name the package exports; this is the same file `docs/api/index.md` renders via `autosummary`, so the matrix and the API reference can never disagree about what is implemented.
- **Published location**: `docs/api/index.md` (the existing API reference page), with the coverage matrix linked from it; the matrix itself lives in the docs tree so it is built by Sphinx and served on Read the Docs.
- **Sync cadence**: per release — the matrix is refreshed as part of the release PR so it reflects the shipped package version, with the baseline snapshot captured in [#515](https://github.com/tkoyama010/pyvista-wasm/issues/515) as the v0.11.0 starting point.

### Consequences

- Good, because a user reading the API reference sees coverage status inline — no second trip to a GitHub issue or project board to learn what is and is not available in the browser.
- Good, because the implemented column is anchored to `src/pyvista_wasm/__init__.pyi`, the same source Sphinx `autosummary` renders, so the matrix and the API reference stay consistent by construction.
- Good, because partial coverage is first-class: a *Partial* row names the missing methods/attributes (e.g., the `PolyDataFilters` methods not yet implemented), so a contributor knows exactly where to help without reading the source.
- Good, because it avoids issue sprawl — the PyVista public API is large (datasets, filters, readers, plotting, theme, utilities; see the parity gaps in [#515](https://github.com/tkoyama010/pyvista-wasm/issues/515)), and one issue per item would produce hundreds of issues that a single maintainer cannot groom.
- Good, because the matrix travels through the same PR review flow as the docs, preserving the rationale alongside the artifact.
- Bad, because the matrix is human-maintained at sync time: the implemented column is *verified* against the `.pyi` stub, but the *Not implemented* and *Partial* columns (which list PyVista API surface pyvista-wasm does not yet export) are authored by hand and can drift from upstream PyVista if the matrix is not refreshed per release.
- Bad, because a pure docs matrix has no automatic alarm when a new PyVista release adds API surface that pyvista-wasm has not tracked — the sync is a release-time discipline, not a CI gate (the automated CI report option would provide that gate, at the cost of building and maintaining the diff script).
- Neutral, because the matrix duplicates a slice of the information already in [#515](https://github.com/tkoyama010/pyvista-wasm/issues/515)'s baseline snapshot; the issue snapshot is the point-in-time baseline and the docs matrix is the living view, so the overlap is intentional.

### Confirmation

Compliance with this decision will be confirmed by:

1. A coverage matrix is published under `docs/api/` and linked from `docs/api/index.md`.
1. The matrix lists PyVista public classes/functions grouped by category (Plotting, Camera, Lighting, Mesh/Data, Filters, Readers, Text, Texture, Examples, Utilities).
1. Every row carries a status of *Implemented*, *Partial*, or *Not implemented*.
1. For *Partial* rows, the missing methods/attributes are listed.
1. Every entry marked *Implemented* corresponds to a name present in `src/pyvista_wasm/__init__.pyi` (i.e., the implemented column is consistent with the type stub).
1. The matrix is consistent with the `autosummary` entries rendered in `docs/api/index.md` (no name is documented that the matrix marks *Not implemented*, and vice versa).
1. The matrix references parent issue [#515](https://github.com/tkoyama010/pyvista-wasm/issues/515) and its v0.11.0 baseline snapshot.
1. The matrix is refreshed as part of the release PR for each release.

## Pros and Cons of the Options

### Coverage matrix published in the docs, sourced from the `.pyi` stub, synced per release

See the [PyVista API reference](https://docs.pyvista.org/api/core/_autosummary/pyvista.polydata) and [PolyDataFilters](https://docs.pyvista.org/api/core/_autosummary/pyvista.PolyDataFilters.html) for the upstream surface the matrix tracks.

- Good, because single-glance visibility is met: the whole surface and its status live in one table on the docs site.
- Good, because it is published where users already look — the API reference — so a user never has to visit a GitHub issue to learn what is available.
- Good, because the implemented column is anchored to `src/pyvista_wasm/__init__.pyi`, the same file `docs/api/index.md` renders, so the matrix and the API reference cannot disagree about what is implemented.
- Good, because partial coverage is represented explicitly with a *Partial* status and a list of missing methods/attributes.
- Good, because it avoids per-item issue sprawl — one maintained table replaces a backlog of hundreds of issues.
- Good, because it rides the existing docs PR/review flow and is built by Sphinx on Read the Docs with no new infrastructure.
- Good, because the per-release sync cadence keeps the matrix aligned to the shipped package.
- Bad, because the *Not implemented* / *Partial* columns are hand-authored against upstream PyVista and can drift if a PyVista release adds surface between pyvista-wasm releases.
- Bad, because there is no CI alarm for new upstream API surface; staying current is a release-time discipline.

### Checklist of separate GitHub issues (one issue per PyVista item)

- Good, because each gap is individually trackable, assignable, and closeable on the Scrum board.
- Good, because each issue carries its own discussion and acceptance criteria.
- Neutral, because a project board can be filtered by status, giving a rough parity view.
- Bad, because it fails single-glance visibility — the parity view is a board to navigate, not one table to read.
- Bad, because it is not published in the docs — a user reading the API reference sees no coverage status.
- Bad, because the PyVista public API is large (datasets, filters, readers, plotting, theme, utilities); one issue per item produces hundreds of issues that a single maintainer cannot groom, failing the low-maintenance driver.
- Bad, because the issues are not tied to `src/pyvista_wasm/__init__.pyi`, so an issue can stay open after its item is implemented (or be closed before), drifting from the code.

### Coverage matrix kept in a tracking issue body

- Good, because it reuses the baseline snapshot already captured in [#515](https://github.com/tkoyama010/pyvista-wasm/issues/515) — no new artifact to create.
- Good, because it is low-effort: editing an issue body is cheaper than maintaining a docs page.
- Neutral, because GitHub renders Markdown tables in issue bodies, so the matrix is readable in the issue.
- Bad, because it fails the published-where-users-look knock-out criterion — users read the docs site, not issue bodies, so coverage status is invisible to them.
- Bad, because the issue body is hand-edited and unrelated to `src/pyvista_wasm/__init__.pyi`, so it drifts from the code with no anchor.
- Bad, because the issue scrolls away as new issues arrive, and the matrix is not versioned with the docs or the code.

### Automated parity report generated in CI

See [PyVista `pyvista/__init__.py`](https://github.com/pyvista/pyvista) for the upstream surface a diff script would parse.

- Good, because it provides a CI alarm: every release tag (or PR) generates a fresh parity report, so new upstream API surface is detected automatically.
- Good, because the report is generated from the code (parsing PyVista's public API and `src/pyvista_wasm/__init__.pyi`), eliminating hand-authoring drift.
- Good, because it can be posted as a PR comment or CI artifact, giving maintainers an always-current view.
- Neutral, because the report could also be published into the docs, blending this option with the chosen one.
- Bad, because it requires building and maintaining a diff script that parses the PyVista public API surface — a non-trivial parser that must track upstream PyVista's module layout as it evolves.
- Bad, because a CI artifact or PR comment is not published on the docs site, failing the published-where-users-look knock-out criterion unless extra work publishes the report into the docs.
- Bad, because an automated report that lists *Not implemented* items cannot easily represent *Partial* coverage with a list of missing methods/attributes without a much richer (and more brittle) introspection of both APIs.

## More Information

### How partial coverage is represented

A row is marked *Partial* when the class/function exists in `src/pyvista_wasm/__init__.pyi` (so it is exported and documented) but does not implement the full upstream method/attribute set. The row then lists the missing methods/attributes. For example, `PolyData` is *Partial* because it is exported but many `PolyDataFilters` methods (`subdivide`, `triangulate`, `smooth`, `fill_holes`, `ray_trace`, `reconstruct_surface`, `merge`, `intersection`, `boolean_union`, `boolean_difference`, `project_points_to_plane`, `geodesic`, `decimate`, `connectivity`, `clean`, `compute_normals`, and more — see the parity gaps in [#515](https://github.com/tkoyama010/pyvista-wasm/issues/515)) are not yet implemented; `PointData` is *Partial* because it is exported but not all data-array helpers are available. A row is *Implemented* only when the exported surface matches the upstream surface it intends to cover; it is *Not implemented* when the name does not appear in the stub at all (e.g., `UnstructuredGrid`, `StructuredGrid`, `ImageData`, `RectilinearGrid`, `MultiBlock`, `ExplicitStructuredGrid`, `UniformGrid`).

### Why a coverage matrix over a checklist of separate issues

A checklist of one issue per PyVista item optimizes for individual trackability but fails single-glance visibility and the low-maintenance driver: the PyVista public API is large, and one issue per item yields hundreds of issues a single maintainer cannot groom, none of which is visible to a user reading the docs. A single matrix gives the whole parity picture in one place, anchors the implemented column to the code, represents partial coverage, and rides the docs PR flow — at the cost of hand-authoring the *Not implemented* / *Partial* columns per release.

### Why publish in the docs rather than keep in a tracking issue

A tracking issue body is invisible to users reading the docs site, is not versioned with the code, and drifts from `src/pyvista_wasm/__init__.pyi` with no anchor. Publishing the matrix in `docs/api/` co-locates coverage status with the API reference that Sphinx already renders from the same stub, so a user sees both *what is available* and *how complete it is* in one place, and the matrix travels through the same reviewed docs PR flow as the rest of the documentation.

### Sync cadence

The matrix is refreshed as part of the release PR for each release, so it reflects the shipped package version. The implemented column is verified against `src/pyvista_wasm/__init__.pyi` at sync time; the *Not implemented* / *Partial* columns are reconciled against the current PyVista release. The baseline snapshot in [#515](https://github.com/tkoyama010/pyvista-wasm/issues/515) is the v0.11.0 starting point and is not re-edited — the living view lives in the docs.

### Upgrade path

If drift between the matrix and upstream PyVista becomes a problem, the automated CI parity-report option can be layered on top of the chosen option: a release-time (or PR-time) script diffs the PyVista public API against `src/pyvista_wasm/__init__.pyi` and posts a report that the maintainer uses to update the matrix. The chosen option does not preclude this — the docs matrix remains the user-facing view, and the CI report becomes the maintainer-facing alarm that feeds it.

### Links

- PyVista PolyData: [https://docs.pyvista.org/api/core/\_autosummary/pyvista.polydata](https://docs.pyvista.org/api/core/_autosummary/pyvista.polydata)
- PyVista PolyDataFilters: [https://docs.pyvista.org/api/core/\_autosummary/pyvista.PolyDataFilters.html](https://docs.pyvista.org/api/core/_autosummary/pyvista.PolyDataFilters.html)
- PyVista filters: [https://docs.pyvista.org/api/core/filters.html](https://docs.pyvista.org/api/core/filters.html)
- PyVista plotting index: [https://docs.pyvista.org/api/plotting/index.html](https://docs.pyvista.org/api/plotting/index.html)
- Parent issue: [#515](https://github.com/tkoyama010/pyvista-wasm/issues/515) (Track PyVista API coverage matrix for pyvista-wasm, with the v0.11.0 baseline snapshot)
- This decision: [#516](https://github.com/tkoyama010/pyvista-wasm/issues/516)
- Related: [ADR-0000](0000-use-markdown-architectural-decision-records.md) (records travel through the same review/PR flow as code — the matrix is a reviewed docs artifact)
