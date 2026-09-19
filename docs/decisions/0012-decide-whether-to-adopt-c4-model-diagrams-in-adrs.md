# Decide whether to adopt C4 model diagrams in ADRs

* Status: proposed
* Date: 2026-09-19
* Decision-makers: tkoyama010

## Context and Problem Statement

ADRs in `docs/decisions/` record *why* a decision was made ([ADR-0000](0000-use-markdown-architectural-decision-records.md)), but the structure they decide about is described almost entirely in prose. Where a diagram has helped, it was drawn ad hoc: [ADR-0009](0009-decide-how-to-sync-github-repository-settings-with-terraform.md) embeds a Mermaid `sequenceDiagram`, and `slides/slides.md` carries several more. Nothing says what a diagram in an ADR is supposed to show, at which level of abstraction, or with which vocabulary, so two records that both draw "the architecture" can disagree about what counts as a box.

The [C4 model](https://c4model.com/) is a candidate vocabulary: it fixes four zoom levels — System Context, Container, Component, Code — and a small element set (person, software system, container, component) that keeps every diagram's boxes comparable. pyvista-wasm has a genuinely layered architecture to describe — a Python-facing PyVista API (`src/pyvista_wasm/`), a TypeScript glue layer (`ts/renderer.ts`), the vtk-wasm module it drives, and the in-browser Python runtime that hosts them — which is exactly the shape C4's Context and Container levels exist to draw.

Should pyvista-wasm adopt C4 as the notation for architecture diagrams in ADRs, and if so, with which toolchain?

## Decision Drivers

- **Shared vocabulary across records**: Diagrams drawn by different contributors in different ADRs should use the same element types and the same levels, so a reader can compare them without re-learning the notation each time.
- **Plain text under version control**: Diagrams must be diffable Markdown that travels through the same PR review flow as the record itself ([ADR-0000](0000-use-markdown-architectural-decision-records.md)). Binary images or an external editor would break that.
- **No new toolchain in CI**: Documentation is built by Sphinx on Read the Docs for every PR. A notation that requires a JVM, Docker, or Graphviz in the docs build is a disproportionate cost for a small project.
- **Rendering in the published docs**: ADRs are published alongside the rest of `docs/`. A diagram that renders on GitHub but not on Read the Docs (or the reverse) is only half a diagram.
- **Low authoring overhead**: Records must stay cheap to write. If drawing the diagram costs more than writing the decision, contributors will skip it and the notation will not stick.
- **Right level of abstraction**: The useful levels here are Context (who uses pyvista-wasm and what it depends on) and Container (Python API, TypeScript glue, vtk-wasm, browser runtime). Diagrams of individual classes duplicate the code and rot.

## Considered Options

- **Option A: Status quo — ad-hoc Mermaid diagrams, no C4 notation**
- **Option B: Adopt C4 notation using the existing Mermaid toolchain**
- **Option C: Adopt C4 with Structurizr DSL as the model source, with ADRs linked into the model**
- **Option D: Adopt C4 with PlantUML and the C4-PlantUML standard library**

## Decision Outcome

Chosen option: "**Option B: Adopt C4 notation using the existing Mermaid toolchain**", because it is the only option that gives ADRs a shared architectural vocabulary without adding anything to the documentation build.

The toolchain is already in place and already proven for ADRs: `sphinxcontrib.mermaid` is enabled in `docs/conf.py`, pinned as a docs dependency in `pyproject.toml` (`sphinxcontrib-mermaid>=2.0.0,<3.0.0`, resolved to 2.1.1 in `uv.lock`), and [ADR-0009](0009-decide-how-to-sync-github-repository-settings-with-terraform.md) already renders a `{mermaid}` block through it. The extension defaults `mermaid_version` to 11.12.1 and `docs/conf.py` does not override it, so the Mermaid release loaded in the published docs is one that ships the `C4Context`/`C4Container`/`C4Component` diagram types. Slidev loads its own Mermaid (`mermaid` `^11.16.1` in `slides/package.json`), so the same C4 source can be pasted into the deck without a second notation.

Options C and D both add a runtime the project does not otherwise need — a JVM plus Structurizr Lite, or Java plus Graphviz plus `sphinxcontrib-plantuml` — to buy model-level features (a single model rendered into many views, Structurizr's `!adrs` integration) that a repository with a dozen ADRs does not yet need. Option A is what the project does today and is what prompted the question.

Adopting C4 means, concretely:

- When an ADR needs an architecture diagram, it is drawn in C4 notation at **System Context** or **Container** level. Component level is used only when the decision is genuinely about internal structure.
- **Code level is never drawn.** The type stub `src/pyvista_wasm/__init__.pyi` and the API reference built by `autosummary` already describe that level and stay correct automatically.
- Diagrams stay inside the ADR that needs them, in a `{mermaid}` block. There is no central model file to keep in sync.
- ADRs without an architectural component (tooling, process, documentation decisions) still need no diagram. C4 is a notation to use when drawing, not an obligation to draw.

### Consequences

- Good, because architecture diagrams across ADRs become comparable: the same element types at the same two levels, instead of whatever shape each record invented.
- Good, because nothing is added to the docs build — no new dependency, no JVM, no Graphviz — so Read the Docs previews keep working unchanged on every PR.
- Good, because the diagram source is Markdown inside the record, so it is reviewed in the same diff as the decision it illustrates and cannot drift into a separate artifact.
- Good, because the same C4 source can be reused in `slides/slides.md`, which already renders Mermaid.
- Bad, because Mermaid's C4 diagram support is flagged experimental upstream: its syntax may change between Mermaid releases, and `mermaid_version` is unpinned in `docs/conf.py`, so a future default bump could alter or break rendering. The mitigation is cheap — pin `mermaid_version` if that ever happens.
- Bad, because Mermaid offers little layout control for C4 diagrams compared with Structurizr or PlantUML, so large diagrams look worse. This pushes records toward few, small diagrams, which is the intended outcome anyway.
- Bad, because with no central model, an element that appears in two ADRs can be described inconsistently. Accepted: records are immutable decisions in time, not a live model, and Option C remains available if a live model is ever wanted.
- Neutral, because existing non-C4 diagrams (the `sequenceDiagram` in [ADR-0009](0009-decide-how-to-sync-github-repository-settings-with-terraform.md), the deck's diagrams) are not retrofitted. C4 governs *architecture* diagrams; sequence and flow diagrams remain the right tool for showing a workflow over time.

### Confirmation

This decision is confirmed by the documentation build, not by inspection: the diagram below is a C4 System Context diagram of pyvista-wasm, and the Read the Docs preview built for the pull request that introduces this record must render it. If it does not render, Mermaid's experimental C4 support is not usable here and this record should be rejected rather than merged with a broken diagram.

```{mermaid}
C4Context
    title System context — pyvista-wasm

    Person(author, "Python author", "Writes PyVista code and wants an interactive 3D view")

    System_Boundary(browser, "Web browser") {
        System(pvwasm, "pyvista-wasm", "PyVista-compatible Python API plus the TypeScript renderer that drives it")
        System_Ext(runtime, "JupyterLite / Pyodide", "Runs the Python code in the browser")
        System_Ext(vtkwasm, "vtk-wasm", "VTK compiled to WebAssembly; renders to a WebGL canvas")
    }

    System_Ext(pyvista, "PyVista", "The upstream API that pyvista-wasm mirrors")

    Rel(author, pvwasm, "Calls Plotter, meshes, filters")
    Rel(pvwasm, runtime, "Executes in")
    Rel(pvwasm, vtkwasm, "Builds the scene through the TypeScript glue layer")
    Rel(pvwasm, pyvista, "Mirrors the public API of")
```

Thereafter, compliance is a review concern: a PR that adds an architecture diagram to an ADR in notation other than C4, or that draws Code-level structure, contradicts this record.

## Pros and Cons of the Options

### Option A: Status quo — ad-hoc Mermaid diagrams, no C4 notation

What the project does today: a `sequenceDiagram` in [ADR-0009](0009-decide-how-to-sync-github-repository-settings-with-terraform.md), flow and sequence diagrams in `slides/slides.md`, no rule about architecture diagrams.

- Good, because it has zero cost: nothing to adopt, nothing to learn, nothing to configure.
- Good, because Mermaid's non-C4 diagram types are stable and render reliably in both Sphinx and Slidev.
- Neutral, because it is not *wrong* — a small project can carry architecture in prose for a long time.
- Bad, because the level of abstraction is decided per diagram, so records cannot be compared and readers must re-orient in each one.
- Bad, because nothing distinguishes "a system", "a deployable unit", and "a module" in a project whose whole story is the boundary between Python, TypeScript, and WebAssembly.

### Option B: Adopt C4 notation using the existing Mermaid toolchain

C4 vocabulary expressed in Mermaid `C4Context` / `C4Container` blocks, rendered by the already-enabled `sphinxcontrib.mermaid`.

- Good, because the toolchain already exists and is already used by an ADR, so adoption costs one paragraph in this record and nothing in CI.
- Good, because C4's four levels give an explicit answer to "how far should I zoom", which is the question the status quo leaves open.
- Good, because the notation is small: contributors need four element types, not a diagramming language.
- Neutral, because it provides notation only, not a model — there is no validation that two diagrams describe the same system consistently.
- Bad, because Mermaid's C4 support is experimental upstream and its layout engine is weak for anything beyond a modest diagram.

### Option C: Adopt C4 with Structurizr DSL as the model source, with ADRs linked into the model

[Structurizr](https://structurizr.com/) DSL describes the system once as a model; views are generated from it. Structurizr Lite can also ingest `docs/decisions/` via `!adrs` and render ADRs beside the diagrams, scoped to the software system or container they concern.

- Good, because one model generates every view, so Context and Container diagrams cannot contradict each other.
- Good, because `!adrs` is the direct answer to "integrate C4 and ADRs": decisions become navigable from the element they are about.
- Good, because Structurizr's layout and export options are far better than Mermaid's.
- Neutral, because the DSL is still plain text under version control, satisfying that driver.
- Bad, because it requires running Structurizr Lite (a JVM application, normally via Docker) to see or publish anything, which is a new toolchain for the docs build and for every contributor.
- Bad, because rendering into Read the Docs means exporting diagrams as images in CI or hosting a second site — either way the diagram stops being reviewable as a diff.
- Bad, because a central model is maintenance that only pays off at a scale this project has not reached.

### Option D: Adopt C4 with PlantUML and the C4-PlantUML standard library

[C4-PlantUML](https://github.com/plantuml-stdlib/C4-PlantUML) provides C4 macros for PlantUML, rendered in Sphinx through `sphinxcontrib-plantuml`.

- Good, because it is the most mature C4 implementation: stable syntax, full element set, good layout control.
- Good, because the source stays plain text in the record, like Option B.
- Neutral, because it would sit alongside Mermaid rather than replace it, since the deck and the existing sequence diagrams stay on Mermaid.
- Bad, because it adds `sphinxcontrib-plantuml` plus a Java runtime and Graphviz to the documentation build, which Read the Docs must then install on every PR.
- Bad, because the project would carry two diagram toolchains for one notation, and contributors would have to know which block type to use where.

## More Information

- C4 model: [https://c4model.com/](https://c4model.com/)
- Mermaid C4 diagram syntax (flagged experimental): [https://mermaid.js.org/syntax/c4.html](https://mermaid.js.org/syntax/c4.html)
- Structurizr DSL, including `!adrs`: [https://docs.structurizr.com/dsl](https://docs.structurizr.com/dsl)
- C4-PlantUML: [https://github.com/plantuml-stdlib/C4-PlantUML](https://github.com/plantuml-stdlib/C4-PlantUML)
- Sphinx configuration that makes Option B free: `extensions` in [`docs/conf.py`](../conf.py); `sphinxcontrib-mermaid` in the `docs` dependency group of [`pyproject.toml`](../../pyproject.toml)
- Prior art in this repository: the `{mermaid}` block in [ADR-0009](0009-decide-how-to-sync-github-repository-settings-with-terraform.md)
- Revisit triggers: Mermaid changing or dropping its C4 syntax; a need for a single model rendered into many synchronized views; or diagrams growing past what Mermaid's layout can present legibly — any of which argues for Option C.
