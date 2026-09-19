# Decide whether to adopt C4 model diagrams in ADRs

* Status: proposed
* Date: 2026-09-19
* Decision-makers: tkoyama010

## Context and Problem Statement

ADRs record *why* a decision was made ([ADR-0000](0000-use-markdown-architectural-decision-records.md)), but describe structure almost entirely in prose. Diagrams appear ad hoc: a Mermaid `sequenceDiagram` in [ADR-0009](0009-decide-how-to-sync-github-repository-settings-with-terraform.md), more in `slides/slides.md`. Nothing says what a diagram should show, at which level, or with which vocabulary, so two records can both draw "the architecture" and disagree about what counts as a box.

The [C4 model](https://c4model.com/) supplies that vocabulary: four zoom levels — System Context, Container, Component, Code — and a small element set that keeps boxes comparable. pyvista-wasm has the layered shape C4's Context and Container levels exist to draw: a Python-facing PyVista API (`src/pyvista_wasm/`), a TypeScript glue layer (`ts/renderer.ts`), the vtk-wasm module it drives, and the in-browser Python runtime hosting them.

Should pyvista-wasm adopt C4 for architecture diagrams in ADRs, and with which toolchain?

## Decision Drivers

- **Shared vocabulary across records**: the same element types and levels everywhere, so readers need not re-learn the notation per record.
- **Plain text under version control**: diagrams must be diffable Markdown reviewed in the same PR flow as the record ([ADR-0000](0000-use-markdown-architectural-decision-records.md)); binary images and external editors break that.
- **No new toolchain in CI**: Sphinx builds the docs on Read the Docs for every PR, so requiring a JVM, Docker, or Graphviz is disproportionate here.
- **Rendering in the published docs**: a diagram that renders on GitHub but not on Read the Docs, or the reverse, is half a diagram.
- **Low authoring overhead**: if drawing costs more than writing the decision, contributors skip it and the notation never sticks.
- **Right level of abstraction**: Context and Container are the useful levels; class diagrams duplicate the code and rot.

## Considered Options

- **Option A: Status quo — ad-hoc Mermaid diagrams, no C4 notation**
- **Option B: Adopt C4 notation using the existing Mermaid toolchain**
- **Option C: Adopt C4 with Structurizr DSL as the model source, with ADRs linked into the model**
- **Option D: Adopt C4 with PlantUML and the C4-PlantUML standard library**

## Decision Outcome

Chosen option: "**Option B: Adopt C4 notation using the existing Mermaid toolchain**", because it alone gives ADRs a shared architectural vocabulary without adding anything to the documentation build.

The toolchain is in place and proven for ADRs: `sphinxcontrib.mermaid` is enabled in `docs/conf.py`, pinned in `pyproject.toml` (`sphinxcontrib-mermaid>=2.0.0,<3.0.0`, resolved to 2.1.1 in `uv.lock`), and [ADR-0009](0009-decide-how-to-sync-github-repository-settings-with-terraform.md) already renders a `{mermaid}` block through it. The extension defaults `mermaid_version` to 11.12.1 and `docs/conf.py` does not override it, so the published docs load a Mermaid release shipping the `C4Context`/`C4Container`/`C4Component` types. Slidev loads its own Mermaid (`^11.16.1` in `slides/package.json`), so the same source works in the deck.

Options C and D each add a runtime the project does not otherwise need — a JVM plus Structurizr Lite, or Java plus Graphviz plus `sphinxcontrib-plantuml` — for model-level features a repository with a dozen ADRs does not yet need. Option A is today's practice, which prompted the question.

Adopting C4 means:

- Architecture diagrams in ADRs use C4 notation at **System Context** or **Container** level; Component level only when the decision is about internal structure.
- **Code level is never drawn.** `src/pyvista_wasm/__init__.pyi` and the `autosummary` API reference cover it and stay correct automatically.
- Diagrams live in the ADR that needs them, in a `{mermaid}` block. No central model to sync.
- ADRs without an architectural component need no diagram. C4 is a notation for when you draw, not an obligation to draw.

### Consequences

- Good, because diagrams become comparable across records instead of taking whatever shape each one invented.
- Good, because nothing is added to the docs build, so Read the Docs previews keep working unchanged.
- Good, because the source is Markdown inside the record, reviewed in the same diff and unable to drift into a separate artifact.
- Good, because the same source can be reused in `slides/slides.md`, which already renders Mermaid.
- Bad, because Mermaid's C4 support is flagged experimental upstream: the syntax may change between releases, and `mermaid_version` is unpinned, so a default bump could break rendering. Mitigation is cheap — pin it.
- Bad, because Mermaid gives little layout control for C4, so large diagrams look worse. That pushes records toward few, small diagrams, the intended outcome anyway.
- Bad, because with no central model, an element in two ADRs can be described inconsistently. Accepted: records are decisions fixed in time, not a live model, and Option C stays available.
- Neutral, because existing non-C4 diagrams are not retrofitted. C4 governs *architecture* diagrams; sequence and flow diagrams still show a workflow over time.

### Confirmation

The documentation build confirms this, not inspection: the diagram below is a C4 System Context diagram of pyvista-wasm, and the Read the Docs preview for the introducing pull request must render it. If it does not, Mermaid's experimental C4 support is unusable here and this record should be rejected rather than merged with a broken diagram.

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

Thereafter compliance is a review concern: a PR adding an architecture diagram in another notation, or drawing Code level, contradicts this record.

## Pros and Cons of the Options

### Option A: Status quo — ad-hoc Mermaid diagrams, no C4 notation

Today's practice: a `sequenceDiagram` in [ADR-0009](0009-decide-how-to-sync-github-repository-settings-with-terraform.md), diagrams in `slides/slides.md`, no rule for architecture diagrams.

- Good, because it costs nothing to adopt, learn, or configure.
- Good, because Mermaid's non-C4 types are stable and render reliably in both Sphinx and Slidev.
- Neutral, because it is not *wrong* — a small project can carry architecture in prose for a long time.
- Bad, because abstraction level is chosen per diagram, so records cannot be compared.
- Bad, because nothing distinguishes "a system", "a deployable unit", and "a module" in a project whose whole story is the boundary between Python, TypeScript, and WebAssembly.

### Option B: Adopt C4 notation using the existing Mermaid toolchain

C4 vocabulary in Mermaid `C4Context` / `C4Container` blocks, rendered by the already-enabled `sphinxcontrib.mermaid`.

- Good, because the toolchain exists and an ADR already uses it, so adoption costs one paragraph here and nothing in CI.
- Good, because C4's four levels answer "how far should I zoom", which the status quo leaves open.
- Good, because the notation is small: four element types, not a diagramming language.
- Neutral, because it gives notation only — nothing validates that two diagrams describe the system consistently.
- Bad, because Mermaid's C4 support is experimental upstream and its layout engine is weak beyond a modest diagram.

### Option C: Adopt C4 with Structurizr DSL as the model source, with ADRs linked into the model

[Structurizr](https://structurizr.com/) DSL describes the system once and generates views from it; Structurizr Lite can also ingest `docs/decisions/` via `!adrs`, rendering ADRs beside the diagrams and scoped to the element they concern.

- Good, because one model generates every view, so Context and Container diagrams cannot contradict each other.
- Good, because `!adrs` directly answers "integrate C4 and ADRs": decisions become navigable from the element they are about.
- Good, because layout and export are far better than Mermaid's.
- Neutral, because the DSL is still plain text under version control.
- Bad, because seeing or publishing anything means running Structurizr Lite, a JVM application normally run via Docker — a new toolchain for the docs build and every contributor.
- Bad, because rendering into Read the Docs means exporting images in CI or hosting a second site; either way the diagram stops being reviewable as a diff.
- Bad, because a central model pays off only at a scale this project has not reached.

### Option D: Adopt C4 with PlantUML and the C4-PlantUML standard library

[C4-PlantUML](https://github.com/plantuml-stdlib/C4-PlantUML) provides C4 macros for PlantUML, rendered in Sphinx through `sphinxcontrib-plantuml`.

- Good, because it is the most mature C4 implementation: stable syntax, full element set, good layout control.
- Good, because the source stays plain text in the record, like Option B.
- Neutral, because it would sit alongside Mermaid rather than replace it, since the deck and existing sequence diagrams stay on Mermaid.
- Bad, because it adds `sphinxcontrib-plantuml` plus Java and Graphviz to the docs build, which Read the Docs must install on every PR.
- Bad, because the project would carry two toolchains for one notation, and contributors would have to know which block goes where.

## More Information

- C4 model: [https://c4model.com/](https://c4model.com/)
- Mermaid C4 syntax (flagged experimental): [https://mermaid.js.org/syntax/c4.html](https://mermaid.js.org/syntax/c4.html)
- Structurizr DSL, including `!adrs`: [https://docs.structurizr.com/dsl](https://docs.structurizr.com/dsl)
- C4-PlantUML: [https://github.com/plantuml-stdlib/C4-PlantUML](https://github.com/plantuml-stdlib/C4-PlantUML)
- What makes Option B free: `extensions` in [`docs/conf.py`](../conf.py); `sphinxcontrib-mermaid` in the `docs` dependency group of [`pyproject.toml`](../../pyproject.toml)
- Prior art here: the `{mermaid}` block in [ADR-0009](0009-decide-how-to-sync-github-repository-settings-with-terraform.md)
- Revisit triggers: Mermaid changing or dropping C4 syntax; a need for one model rendered into many synchronized views; or diagrams outgrowing Mermaid's layout — any of which argues for Option C.
