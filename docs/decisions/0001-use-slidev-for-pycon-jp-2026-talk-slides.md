---
status: accepted
date: 2026-07-16
decision-makers: [tkoyama010]
consulted: []
informed: []
---

# Use Slidev for the PyCon JP 2026 talk slide deck

## Context and Problem Statement

pyvista-wasm was accepted as a talk at PyCon JP 2026 — ["PyVista on WebAssembly: サーバーレス3D可視化の実現"](https://pretalx.com/pyconjp2026/talk/review/VVJZFPCFCJCRGGKWEWKPYC3QXF8YE3A9). The talk must demonstrate PyVista running live in the browser via WebAssembly, walk the audience through the TypeScript-glue architecture, and show Python/TypeScript code snippets with syntax highlighting. We need to pick a slide tool that lets us embed those live browser demos directly in the deck, keeps the source version-controllable alongside the rest of the repository, and is easy to author and review through the normal PR flow. Which slide tool should we adopt for this talk?

## Decision Drivers

- **Live web demo embedding**: The talk's centerpiece is a live, in-browser PyVista WASM demo. The slide tool must be able to run or embed that demo inside a slide without leaving the presentation context. This is a knock-out criterion.
- **Code syntax highlighting**: The deck shows Python and TypeScript code; first-class syntax highlighting with line highlighting and code animations is essential for a technical audience.
- **Version-control friendliness**: Slide source must be plain text that diffs and reviews well in Git, so the deck can travel through the same PR flow as code (see [ADR-0000](0000-use-markdown-architectural-decision-records.md)).
- **Ease of authoring**: The deck must be authorable efficiently with hot-reload preview, so iteration is fast before the talk.
- **Portability**: The deck should be presentable offline, exportable to PDF for sharing, and deployable as a static site.
- **Community adoption**: Prefer a tool with an active community, documentation, and a healthy ecosystem to reduce risk.

## Considered Options

- [Slidev](https://sli.dev/) — Vue-powered presentation framework for developers
- [sphinx-revealjs](https://github.com/attakei/sphinx-revealjs) — Sphinx extension to build reveal.js presentations
- [reveal.js](https://revealjs.com/) — The HTML presentation framework
- [Marp](https://marp.app/) — Markdown presentation ecosystem
- Google Slides — Cloud-based WYSIWYG presentation tool
- Microsoft PowerPoint — Desktop WYSIWYG presentation tool
- [JupyterLab Slides / RISE](https://rise.readthedocs.io/) — Live Jupyter notebook slideshow extension

## Decision Outcome

Chosen option: "Slidev", because it is the only option that satisfies the knock-out criterion — embedding live web demos — *and* provides best-in-class code highlighting, Markdown-based version-controllable authoring, and a developer-friendly authoring experience. Slidev is a Vue-based single-page application, so the PyVista WASM demo can be embedded as a live Vue component or iframe and run directly inside a slide.

### Consequences

- Good, because live PyVista WASM demos can run inside slides via Vue components or iframes, making the talk fully interactive.
- Good, because slides are authored in Markdown, diffing cleanly in Git and travelling through the same PR review flow as the rest of the repository.
- Good, because Slidev's Shiki-based syntax highlighting supports line highlighting, code animations, and code blocks with Monaco editor integration — ideal for a technical talk.
- Good, because Slidev exports to PDF, PNG, and a standalone SPA, giving us portable fallbacks for offline presenting and sharing.
- Good, because the deck can be deployed as a static site (e.g. on GitHub Pages) alongside the project documentation.
- Bad, because Slidev requires a Node.js toolchain, adding a build dependency that the Python-only parts of the project do not need.
- Bad, because Slidev's community, while active, is smaller than reveal.js's or Google Slides's, so fewer third-party themes and integrations are available.
- Neutral, because the deck will live in the repository under version control, which is the desired outcome but does require maintaining slide source alongside code.

### Confirmation

Compliance with this decision will be confirmed by:

1. A Slidev project is initialised in the repository (e.g. under a `slides/` directory) with a `slides.md` entry point.
1. At least one slide embeds a live PyVista WASM demo (via Vue component or iframe) that renders a 3D plot in the browser during the presentation.
1. The deck is reviewable through a PR linked to issue [#278](https://github.com/tkoyama010/pyvista-wasm/issues/278).
1. The deck exports successfully to PDF for offline sharing.

## Pros and Cons of the Options

### Slidev — Vue-powered presentation framework for developers

See [https://sli.dev/](https://sli.dev/)

- Good, because it is a Vue/Vite-based SPA, so live web demos — the knock-out criterion — can be embedded as native Vue components or iframes and run inside a slide.
- Good, because it uses Shiki for syntax highlighting with support for line highlighting, diff lines, and code animations, which is ideal for showing Python and TypeScript code.
- Good, because slides are authored in Markdown with YAML frontmatter per slide, satisfying the version-control-friendliness driver.
- Good, because it ships a hot-reload dev server (`slidev dev`) for fast authoring iteration, satisfying the ease-of-authoring driver.
- Good, because it exports to PDF, PNG, and a standalone SPA, satisfying the portability driver.
- Neutral, because it requires a Node.js toolchain, which is a new build dependency for this predominantly Python project.
- Neutral, because its community (~40k GitHub stars) is active and growing but smaller than reveal.js's.

### sphinx-revealjs — Sphinx extension to build reveal.js presentations

See [https://github.com/attakei/sphinx-revealjs](https://github.com/attakei/sphinx-revealjs)

- Good, because it reuses the project's existing Sphinx toolchain (`docs/conf.py` already configures Sphinx + MyST parser), requiring no new build dependency.
- Good, because slides are authored in reStructuredText or MyST Markdown, which is already enabled in this project, satisfying the version-control-friendliness driver.
- Good, because it stays within the Python ecosystem, consistent with a predominantly Python project.
- Good, because the maintainer is a Japanese developer active in the PyCon JP community, offering natural community alignment.
- Neutral, because it wraps reveal.js, so live demo embedding is iframe-based — functional but less seamless than Slidev's native Vue component model.
- Neutral, because code syntax highlighting relies on reveal.js's highlight.js, which lacks Slidev's Shiki features (line highlighting, code animations, Monaco integration).
- Bad, because its community (~129 GitHub stars) is significantly smaller than Slidev's or reveal.js's, meaning fewer third-party themes and less community support.
- Bad, because it lacks a dedicated hot-reload dev server comparable to Slidev's `slidev dev` (only `sphinx-autobuild` is available, which is less tailored to slideshow authoring).

### reveal.js — The HTML presentation framework

See [https://revealjs.com/](https://revealjs.com/)

- Good, because it can embed live web demos via iframes and custom HTML, partially satisfying the knock-out criterion.
- Good, because it has built-in syntax highlighting via highlight.js.
- Good, because it has the largest community (~68k GitHub stars) and a long, proven track record.
- Good, because it is an HTML/JS framework that deploys as a static site, satisfying portability.
- Neutral, because while a Markdown plugin exists, authoring is primarily HTML-based, which is more verbose than Markdown-first tools.
- Bad, because embedding live Vue components is not native — iframes are the main mechanism, which is less seamless than Slidev's component model.
- Bad, because the HTML-centric authoring flow is less ergonomic for a Markdown-heavy project than Slidev or Marp.

### Marp — Markdown presentation ecosystem

See [https://marp.app/](https://marp.app/)

- Good, because it is pure Markdown, maximally satisfying the version-control-friendliness and ease-of-authoring drivers.
- Good, because it exports to PDF, PPTX, and HTML, satisfying portability.
- Good, because it has built-in syntax highlighting and a clean, minimal authoring experience.
- Neutral, because it is primarily a Markdown-to-slide *converter*, not an interactive runtime — live demos must be embedded as iframes.
- Bad, because it cannot run live Vue components or interactive web content natively, making the live-demo embedding less seamless than Slidev.
- Bad, because it lacks presenter features like code animations and live component rendering that a technical talk benefits from.

### Google Slides — Cloud-based WYSIWYG presentation tool

- Good, because it is extremely easy to author with a WYSIWYG editor and requires no toolchain.
- Good, because it has massive general adoption and seamless cloud collaboration.
- Neutral, because it can embed external content via "Insert > Embed link," but support is limited and not designed for live code execution.
- Bad, because it has no native code syntax highlighting, requiring workarounds like images or third-party add-ons.
- Bad, because slide source is a binary cloud document, failing the version-control-friendliness driver — the deck cannot be reviewed in a PR.
- Bad, because embedding a live, interactive WASM demo is unreliable and constrained by the embed sandbox.

### Microsoft PowerPoint — Desktop WYSIWYG presentation tool

- Good, because it is widely adopted and familiar to a general audience.
- Good, because it exports to PDF and runs offline, satisfying portability.
- Neutral, because it supports web add-ins, but these are heavyweight and not designed for live WASM demos.
- Bad, because it has no native code syntax highlighting.
- Bad, because slide source is a binary `.pptx` file, failing the version-control-friendliness driver.
- Bad, because embedding live, interactive browser content is severely limited.

### JupyterLab Slides / RISE — Live Jupyter notebook slideshow extension

See [https://rise.readthedocs.io/](https://rise.readthedocs.io/)

- Good, because it can execute live Python code in notebook cells during the presentation, which is appealing for a Python audience.
- Good, because notebook code cells have syntax highlighting built in.
- Neutral, because notebooks are JSON and can be version-controlled, but diffs are noisy when outputs are saved.
- Bad, because embedding a live, in-browser *WASM application* inside a Jupyter slideshow is awkward — the WASM demo is a web app, not a notebook cell, so it would need an iframe workaround.
- Bad, because RISE is less actively maintained and has a smaller community than the other developer-oriented options.
- Bad, because the slideshow UX (navigation, transitions, layout control) is more limited than purpose-built slide frameworks.

## More Information

### Comparison matrix

The table below summarises how each option scores against the evaluation criteria. ✓ = strong, ~ = partial, ✗ = weak.

| Criterion | Slidev | sphinx-revealjs | reveal.js | Marp | Google Slides | PowerPoint | JupyterLab/RISE |
|-------------------------------|:------:|:---------------:|:---------:|:----:|:-------------:|:----------:|:---------------:|
| Live web demo embedding | ✓ | ~ | ~ | ~ | ✗ | ✗ | ~ |
| Code syntax highlighting | ✓ | ~ | ✓ | ✓ | ✗ | ✗ | ✓ |
| Ease of authoring | ✓ | ~ | ~ | ✓ | ✓ | ✓ | ~ |
| Portability | ✓ | ✓ | ✓ | ✓ | ~ | ✓ | ~ |
| Version-control friendliness | ✓ | ✓ | ~ | ✓ | ✗ | ✗ | ~ |
| Community adoption | ~ | ~ | ✓ | ~ | ✓ | ✓ | ~ |

### Links

- Slidev homepage: [https://sli.dev/](https://sli.dev/)
- Slidev documentation: [https://sli.dev/guide/](https://sli.dev/guide/)
- Slidev GitHub: [https://github.com/slidevjs/slidev](https://github.com/slidevjs/slidev)
- sphinx-revealjs GitHub: [https://github.com/attakei/sphinx-revealjs](https://github.com/attakei/sphinx-revealjs)
- sphinx-revealjs documentation: [https://sphinx-revealjs.readthedocs.io/](https://sphinx-revealjs.readthedocs.io/)
- Parent issue: [#275](https://github.com/tkoyama010/pyvista-wasm/issues/275)
- This decision unblocks [#278](https://github.com/tkoyama010/pyvista-wasm/issues/278) (Design and create the PyCon JP 2026 talk slide deck).
- Talk proposal: [PyVista on WebAssembly: サーバーレス3D可視化の実現](https://pretalx.com/pyconjp2026/talk/review/VVJZFPCFCJCRGGKWEWKPYC3QXF8YE3A9)
