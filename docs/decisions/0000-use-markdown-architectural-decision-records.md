______________________________________________________________________

## status: accepted date: 2026-07-16 decision-makers: [tkoyama010] consulted: [] informed: []

# Use Markdown Architectural Decision Records

## Context and Problem Statement

pyvista-wasm is accumulating architecturally significant decisions — e.g. the choice of vtk-wasm as the C++ VTK binding layer, the TypeScript glue architecture that bridges vtk-wasm bindings to the Python-facing PyVista API, and the WebAssembly runtime strategy for running PyVista entirely in the browser. Today these decisions live only in issue threads and PR descriptions, which makes the rationale hard to find later and easy to lose. We want to record architectural decisions made in this project — whether they concern the architecture, the code, or other fields — in a consistent, version-controllable way. Which format and structure should these records follow?

## Decision Drivers

- **Explicit rationale**: Implicit assumptions should be made explicit so future contributors can understand *why* a decision was made, not just *what* was decided. See also ["A rational design process: How and why to fake it"](https://doi.org/10.1109/TSE.1986.6312940).
- **Version control friendliness**: Records must be plain text that diffs and reviews well in Git alongside the code they govern.
- **Low overhead**: pyvista-wasm is a small project; the format must be lean enough that writing a record does not feel like a burden.
- **Comprehensibility**: The structure should be easy to read and scan for both authors and reviewers.
- **Tooling availability**: Prefer a format with active maintenance and supporting tooling.
- **Generality**: The format should capture any decision — architectural, design, or tooling — not only a narrow class.

## Considered Options

- [MADR](https://adr.github.io/madr/) 4.0.0 — The Markdown Architectural Decision Records
- [Michael Nygard's template](http://thinkrelevance.com/blog/2011/11/15/documenting-architecture-decisions) — The first incarnation of the term "ADR"
- [Sustainable Architectural Decisions](https://www.infoq.com/articles/sustainable-architectural-design-decisions) — The Y-Statements
- Other templates listed at [https://github.com/joelparkerhenderson/architecture_decision_record](https://github.com/joelparkerhenderson/architecture_decision_record)
- Formless — No conventions for file format and structure

## Decision Outcome

Chosen option: "MADR 4.0.0", because it best fits the decision drivers. It is a lean Markdown template with optional sections, captures any decision (not only pure architecture), and is actively maintained with tooling support.

### Consequences

- Good, because architectural rationale will live alongside the code in `docs/decisions/` and travel through the same review/PR flow.
- Good, because the consistent `NNNN-title-with-dashes.md` filename convention makes records discoverable and sortable.
- Good, because the MADR template's optional sections (Decision Drivers, Pros and Cons of the Options, Confirmation, More Information) keep short decisions short while scaling to complex ones.
- Good, because YAML front matter (`status`, `date`, `decision-makers`, `consulted`, `informed`) gives lightweight metadata for tracking decision lifecycle.
- Bad, because contributors must learn the template and remember to open a record for significant decisions.
- Neutral, because we adopt the MADR conventions as-is rather than forking the template, trading a little flexibility for staying on a maintained upstream.

### Confirmation

Compliance with this decision will be confirmed by:

1. A `docs/decisions/` directory exists in the repository containing the MADR template (`adr-template.md`) copied from the [MADR 4.0.0 release](https://github.com/adr/madr/tree/4.0.0/template).
1. The first concrete record, `docs/decisions/0000-use-markdown-architectural-decision-records.md`, mirrors this issue's content and is merged via PR.
1. Subsequent architecturally significant proposals (e.g. the TypeScript glue layer design for bridging vtk-wasm bindings to the PyVista API) are accompanied by a MADR record linked from the issue.
1. A CI step (e.g. markdownlint with MADR's `.markdownlint` config) lints records on PRs touching `docs/decisions/`.

## Pros and Cons of the Options

### MADR 4.0.0 — The Markdown Architectural Decision Records

See [https://adr.github.io/madr/](https://adr.github.io/madr/)

- Good, because it is plain Markdown, satisfying the version-control-friendliness and low-overhead drivers.
- Good, because the structure (Context and Problem Statement → Decision Drivers → Considered Options → Decision Outcome → Pros and Cons of the Options → More Information) is comprehensible and scales from one-paragraph to multi-page decisions.
- Good, because the project is vivid: 4.0.0 released 2024-09-17, with examples, a changelog, and tooling (markdownlint config, init scripts).
- Good, because it captures *any* decision, satisfying the generality driver.
- Neutral, because it ships optional YAML front matter that we will adopt but is not strictly required.
- Bad, because it introduces a small documentation convention contributors must learn.

### Michael Nygard's template

See [http://thinkrelevance.com/blog/2011/11/15/documenting-architecture-decisions](http://thinkrelevance.com/blog/2011/11/15/documenting-architecture-decisions)

- Good, because it is the original ADR template and is widely cited.
- Good, because it is minimal: Title, Context, Decision, Status, Consequences.
- Neutral, because its brevity is appealing but leaves no room for comparing options or capturing drivers.
- Bad, because it lacks a "Considered Options" / "Pros and Cons" section, so alternatives and their trade-offs are not recorded.
- Bad, because there is no maintained tooling or canonical Markdown source; many variants exist.

### Sustainable Architectural Decisions — The Y-Statements

See [https://www.infoq.com/articles/sustainable-architectural-design-decisions](https://www.infoq.com/articles/sustainable-architectural-design-decisions)

- Good, because the Y-Statement (In the context of `Z`, facing `Q`, we decided `S` to achieve `B`, accepting `D`) is concise and forces explicit trade-offs.
- Neutral, because the format is more of a single-sentence pattern than a full document template.
- Bad, because it does not scale to multi-option comparisons with detailed pros and cons.
- Bad, because it is less widely adopted and has less tooling than MADR.

### Other templates listed at joelparkerhenderson/architecture_decision_record

See [https://github.com/joelparkerhenderson/architecture_decision_record](https://github.com/joelparkerhenderson/architecture_decision_record)

- Good, because the list offers many variants (Planguage, MADR, Nygard, Y-Statement, etc.) so we could pick a niche fit.
- Neutral, because choosing one of the lesser-known templates would mean self-maintaining it.
- Bad, because the variety itself is a cost: contributors would need to learn whichever one we pick with less community documentation behind it.

### Formless — No conventions for file format and structure

- Good, because there is zero upfront cost and no template to learn.
- Bad, because records drift in style, omit rationale, and become hard to find — failing the explicit-rationale and comprehensibility drivers.
- Bad, because without a `docs/decisions/` convention and filename pattern, decisions stay scattered across issues and PRs, which is the situation we are trying to escape.

## More Information

- MADR homepage: [https://adr.github.io/madr/](https://adr.github.io/madr/)
- MADR 4.0.0 release: [https://github.com/adr/madr/releases/tag/4.0.0](https://github.com/adr/madr/releases/tag/4.0.0)
- MADR template (development): [https://github.com/adr/madr/blob/develop/template/adr-template.md](https://github.com/adr/madr/blob/develop/template/adr-template.md)
- Initialization snippet: `npm install madr && mkdir -p docs/decisions && cp node_modules/madr/template/* docs/decisions/`
- This record, once accepted, will live at `docs/decisions/0000-use-markdown-architectural-decision-records.md` mirroring MADR's own ADR-0000.
