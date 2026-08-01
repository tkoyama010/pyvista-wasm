# Slide Title and Subtitle Guideline

This guideline defines the roles of the **title** and **subtitle** fields for every
slide layout used in the PyCon JP 2026 talk deck (`slides/slides.md`).

It is grounded in the ["1 slide, 1 message" principle](../decisions/0004-adopt-one-slide-one-message-principle.md)
(ADR-0004) and in the `<!-- Single message: ... -->` HTML comments that already
exist in `slides/slides.md`. The subtitle restates that single message in
audience-facing language.

## General Rule

| Field | Role | Answers |
|-------|------|---------|
| **title** | The slide's topic or question — a short label that tells the audience *what this slide is about*. | "What is this slide about?" |
| **subtitle** | The slide's single core message — a one-sentence takeaway that tells the audience *what they should learn* from this slide. | "What does the audience learn from this slide?" |

The subtitle is the on-screen expression of the `<!-- Single message: ... -->`
HTML comment for that slide. When authoring or reviewing a slide, read the
single-message comment and restate it as a concise, audience-facing sentence in
the subtitle.

### Title Styles

A title may take either of two forms:

- **Topic label** — a noun phrase naming the subject of the slide
  (e.g. "The Problem", "Agenda", "Capabilities").
- **Question** — a question that the slide answers
  (e.g. "What is PyVista?", "Why WASM?").

Both are acceptable; the key requirement is that the title is a *label*, not a
*message*. The message lives in the subtitle.

### Subtitle Requirements

- Must be a **complete sentence or clause** that conveys a takeaway — not a
  vague descriptive phrase (e.g. avoid "Where the edges still are").
- Must restate the `<!-- Single message: ... -->` comment in audience-facing
  language.
- Must be **one sentence** (em-dashes and semicolons are allowed for
  compound takeaways).
- Must be **consistent across locales** — `en.yml` and `ja.yml` must carry the
  same message in each subtitle key.

## Layout-Specific Rules

### Cover layout (`layout: cover`)

The cover slide has three text fields: `title`, `subtitle`, and `tagline`.

| Field | Role |
|-------|------|
| `title` | The talk name — the topic of the entire presentation. |
| `subtitle` | The talk's single thesis sentence — the one-sentence takeaway for the whole talk. |
| `tagline` | A short supporting line that adds context without repeating the subtitle. Must **not** duplicate the single message. |

### Default / `text-left` layout

Most content slides use the default layout with `class: text-left`.

| Field | Role |
|-------|------|
| `title` | The slide's topic label or question. |
| `subtitle` | The slide's single core message — the one-sentence takeaway. |

### `two-cols-header` layout

Two-column slides use `layout: two-cols-header`.

| Field | Role |
|-------|------|
| `title` | The slide's topic label or question (spans both columns). |
| `subtitle` | The slide's single core message — the one-sentence takeaway (spans both columns). |

The two columns contain **supporting evidence** for the single message; they
must not introduce a second core message.

### Split-section slides

Some YAML namespaces provide title/subtitle pairs for two consecutive slides
that form a section (e.g. `caps` has `caps_title`/`caps_subtitle` for the
capabilities slide and `lim_title`/`lim_subtitle` for the limitations slide).

Each sub-slide follows the general rule independently:

| Field | Role |
|-------|------|
| `*_title` | The sub-slide's topic label. |
| `*_subtitle` | The sub-slide's single core message — the one-sentence takeaway. |

The parent-level `title` and `subtitle` keys (e.g. `caps.title`,
`caps.subtitle`) are section labels, not rendered on any slide. They should
still follow the general rule for consistency.

## Examples

### Conforming

| Slide | Title (topic) | Subtitle (message) |
|-------|---------------|--------------------|
| pyvista | What is PyVista? | 30 years of VTK's 3D power — made Pythonic |
| problem | The Problem | Sharing 3D results on the web still means running a server |
| why_wasm | Why WASM? | The browser can do it all — every barrier falls away at once |
| arch | Architecture: SSR vs Wasm | SSR puts a server in the loop — Wasm closes the loop inside the browser |

### Non-conforming (before → after)

| Slide | Before | After | Reason |
|-------|--------|-------|--------|
| cover | subtitle: "Server-less 3D Visualization" | "Running PyVista entirely in the browser — no server required" | Descriptive label, not a takeaway |
| agenda | subtitle: "A 30-minute tour, from the why to the how" | "A four-part tour, from the why to the how" | "30-minute" is scheduling detail, not the message |
| caps | caps_subtitle: "What vtk.wasm can do today" | "The full VTK pipeline, mesh loading, interactive camera, and Python — all in the browser" | Vague phrase, not a takeaway |
| caps | lim_subtitle: "Where the edges still are" | "Real limitations exist — but ~100K elements run at practical interactive speed" | Vague phrase, not a takeaway |
| constraints | workarounds_subtitle: "The workaround that clears each one" | "Every constraint has a proven workaround — none block a working demo" | Vague phrase, not a takeaway |

## Review Checklist

When reviewing a slide against this guideline:

1. Read the `<!-- Single message: ... -->` comment for the slide.
1. Check that the **title** is a topic label or question — not a message.
1. Check that the **subtitle** restates the single message as a one-sentence
   takeaway — not a vague descriptive phrase.
1. Check that the **subtitle** in `en.yml` and `ja.yml` carry the same message.
1. If the subtitle is non-conforming, rewrite it to restate the single message.
