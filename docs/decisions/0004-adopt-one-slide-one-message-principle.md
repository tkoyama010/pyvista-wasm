---
status: accepted
date: 2026-08-01
decision-makers: [tkoyama010]
consulted: []
informed: []
---

# Adopt the "1 slide, 1 message" principle for the slide deck

## Context and Problem Statement

The PyCon JP 2026 talk deck (`slides/slides.md`, selected in [ADR-0001](0001-use-slidev-for-pycon-jp-2026-talk-slides.md) and internationalized in [ADR-0003](0003-decide-how-to-internationalize-the-slidev-deck.md)) is a 23-slide presentation that must convey a complex technical story — PyVista running in the browser via WebAssembly, the TypeScript-glue architecture, live demos, and a call to action — within a fixed conference time slot. When a single slide tries to carry more than one core idea, the audience is forced to split its attention between competing messages, comprehension drops, and the speaker must rush to cover everything on screen. Issue [#332](https://github.com/tkoyama010/pyvista-wasm/issues/332) captures the need to audit the deck against the well-known **"1 slide, 1 message"** presentation principle so that overloaded slides are identified and split or trimmed. However, no architecture decision record exists yet that evaluates presentation-design principles and records the rationale for adopting "1 slide, 1 message" as the governing rule for this deck. Which presentation-design principle should govern how content is organised across slides?

## Decision Drivers

- **Audience focus and comprehension**: A conference audience can only absorb one core idea per slide at presentation pace. Overloaded slides force the audience to split attention, diluting the takeaway and reducing comprehension. This is a knock-out criterion.
- **Narrative clarity**: The deck must tell a coherent story with a clear throughline. A principle that forces each slide to advance the narrative by exactly one step produces a tighter, more logical flow.
- **Live-presentation pacing**: The speaker must move through slides at a pace that matches a spoken talk. Slides that pack in multiple ideas either slow the talk (the speaker dwells too long) or skim content (the audience cannot keep up).
- **Readability of slide source under version control**: The deck is authored in Markdown and reviewed through PRs (see [ADR-0000](0000-use-markdown-architectural-decision-records.md)). A governing principle should make the slide source easier to review — one idea per Markdown block boundary makes diffs cleaner and intent clearer.
- **Alignment with established presentation-design best practices**: The principle should be grounded in widely recognised presentation-design guidance so that the rationale is defensible and reproducible by future contributors.

## Considered Options

- **"1 slide, 1 message"** — each slide carries exactly one core idea; overloaded slides are split into separate slides
- **"1 slide, 1 topic"** — a looser rule allowing a topic and its related sub-points to coexist on one slide
- **Free-form** — no governing principle; slide content and density are left to author discretion
- **Lessig method** — minimal-text slides with very short phrases (often a single word), rapidly advanced; many short slides per talk
- **Takahashi method** — slides with only a few very large words (often a single word) per slide; the spoken delivery carries the substance

## Decision Outcome

Chosen option: **"1 slide, 1 message"**, because it directly satisfies the knock-out criterion — each slide conveys exactly one core idea, maximising audience focus and comprehension — while also producing a clearer narrative, more predictable pacing, and cleaner Markdown diffs under version control. Unlike the Lessig and Takahashi methods, which impose a rigid *format* (minimal text, large font) on top of the one-idea principle, "1 slide, 1 message" governs only the *semantic content* per slide and leaves the author free to use the layouts, code blocks, and live demos that the PyVista WASM talk requires. Unlike "1 slide, 1 topic" and free-form, it provides a concrete, verifiable rule that can be applied during the [#332](https://github.com/tkoyama010/pyvista-wasm/issues/332) deck audit.

### Consequences

- Good, because each slide carries one unmistakable takeaway, so the audience never has to choose between competing messages on a single screen.
- Good, because the narrative advances one logical step at a time, making the talk easier to follow and easier to rehearse.
- Good, because pacing becomes more predictable — the speaker can move on once the single message is delivered, without leaving unexplained content on screen.
- Good, because the slide source is easier to review in PRs: one idea per `---` boundary means diffs touch the slide relevant to the change, and a reviewer can immediately see which message a slide conveys.
- Good, because the principle is verifiable — a reviewer can ask "what is the one message of this slide?" and an ambiguous answer flags a slide to split.
- Bad, because applying the principle to the existing 23-slide deck may increase the slide count as overloaded slides are split, which requires rebalancing the talk's time budget.
- Bad, because splitting slides can create transitions that feel choppy if the narrative flow between the new slides is not carefully designed.
- Neutral, because the principle governs semantic content per slide, not visual format — the author retains freedom over layout, font size, and use of diagrams or code, consistent with the Slidev-based deck structure.

### Confirmation

Compliance with this decision will be confirmed by:

1. Every slide in `slides/slides.md` conveys a single core message that can be stated in one short sentence.
2. Slides identified as overloaded in the [#332](https://github.com/tkoyama010/pyvista-wasm/issues/332) audit have been split or trimmed so that no slide carries more than one core idea.
3. Each slide's headline (title or primary heading) states its single message clearly.
4. Supporting detail that does not constitute the slide's core message has been moved to speaker notes (`Speaker notes` / Slidev note blocks) rather than cramming it onto the slide.
5. Bullet lists on each slide support only the slide's single message; lists that introduce a second idea have been split into a separate slide.
6. A deck review confirms that the talk's time budget still fits the PyCon JP 2026 slot after any slide splits.

## Pros and Cons of the Options

### "1 slide, 1 message" — each slide carries exactly one core idea; overloaded slides are split

Each slide is responsible for exactly one takeaway. If a draft slide introduces two ideas, it is split into two slides. The slide's headline states the message; supporting detail lives in speaker notes or compact visual elements.

- Good, because it directly satisfies the knock-out criterion: the audience is never asked to absorb more than one idea per screen, maximising focus and comprehension.
- Good, because it produces a clear narrative — the deck is a sequence of single steps, each advancing the story by one increment.
- Good, because pacing is predictable: the speaker advances once the single message is delivered, and no unexplained content is left on screen.
- Good, because it is verifiable — a reviewer asks "what is the one message?" and a clear answer confirms compliance; an ambiguous answer flags a slide to split.
- Good, because it produces cleaner Markdown diffs: one idea per `---` boundary means a content change touches only the slide for that idea.
- Good, because it is grounded in widely recognised presentation-design guidance (e.g. Garr Reynolds's *Presentation Zen*, Nancy Duarte's *Slide:ology*) that advocates one idea per slide.
- Neutral, because it governs semantic content, not visual format — the author retains freedom over layout, diagrams, and code blocks, which is important for a demo-heavy technical talk.
- Bad, because splitting overloaded slides increases the slide count, which must be rebalanced against the talk's time budget.
- Bad, because an over-literal application can fragment a tightly coupled argument into choppy micro-slides if transitions are not designed carefully.

### "1 slide, 1 topic" — a looser rule allowing related sub-points on one slide

A slide may cover a topic together with its related sub-points. The rule is looser than "1 slide, 1 message": a topic with several facets is permitted on one slide as long as the facets are related.

- Good, because it is less disruptive to the existing deck — slides that group a concept with its sub-points do not need to be split.
- Good, because it preserves a natural grouping when sub-points are tightly coupled and best understood together.
- Neutral, because it is easier to apply without increasing slide count, keeping the time budget unchanged.
- Bad, because "topic" is ambiguous — a topic can contain multiple distinct messages, so the rule does not satisfy the audience-focus knock-out criterion: a slide can still be overloaded with several takeaways under the guise of "one topic."
- Bad, because it is hard to verify — a reviewer cannot easily judge whether a set of sub-points constitutes "one topic" or multiple messages, making compliance subjective.
- Bad, because it does not force the narrative to advance one step at a time; a topic-level slide can bundle several steps, blurring the throughline.
- Bad, because pacing becomes less predictable — the speaker may need to dwell on a multi-point slide, or skim sub-points the audience cannot absorb.

### Free-form — no governing principle; slide content left to author discretion

No rule constrains how many ideas a slide may carry. Content density and structure are decided by the author on a per-slide basis.

- Good, because it imposes no constraints, giving the author maximum freedom to design each slide as they see fit.
- Good, because it requires no audit or restructuring effort — the deck is accepted as authored.
- Neutral, because it is the default state of an unaudited deck; no process is needed to enforce it.
- Bad, because it fails the audience-focus knock-out criterion — nothing prevents overloaded slides that dilute attention and reduce comprehension.
- Bad, because narrative clarity is uncontrolled; the deck may have uneven pacing and unclear throughline.
- Bad, because it is not verifiable — with no rule, there is no compliance criterion, so the [#332](https://github.com/tkoyama010/pyvista-wasm/issues/332) audit cannot be performed.
- Bad, because it is not grounded in presentation-design best practices, which uniformly advise constraining content per slide.

### Lessig method — minimal-text slides with very short phrases, rapidly advanced

Named after Lawrence Lessig. Slides contain very short text — often a single word or short phrase — and are advanced rapidly, producing many brief slides per talk. The visual pace reinforces the spoken narrative.

- Good, because it strongly satisfies audience focus: each slide carries a minimal text fragment, so the audience is never overwhelmed by on-screen content.
- Good, because the rapid visual cadence can create a dynamic, engaging presentation rhythm.
- Good, because it is grounded in a recognised, influential presentation style.
- Neutral, because it is compatible with version control (slides are short Markdown blocks), though the high slide count makes diffs larger.
- Bad, because it imposes a rigid *format* — minimal text, no diagrams, no code blocks — that conflicts with the PyVista WASM talk's need for code snippets, architecture diagrams, and live in-browser demos (see [ADR-0001](0001-use-slidev-for-pycon-jp-2026-talk-slides.md)).
- Bad, because the high slide count (often hundreds for a single talk) would make the deck unwieldy to author, review, and maintain for this project's PR-based workflow.
- Bad, because the style demands significant rehearsal to deliver well; the rapid cadence can feel rushed if the speaker is not practiced in it.

### Takahashi method — slides with only a few very large words per slide

Named after Masayoshi Takahashi. Each slide contains only a few words — often a single word — rendered in very large type. The spoken delivery carries the substance; the slide reinforces one keyword at a time.

- Good, because it maximises audience focus: a single large word leaves no ambiguity about the slide's message.
- Good, because it forces the narrative into clear, keyword-sized steps.
- Good, because it is grounded in a recognised Japanese presentation style with natural community familiarity at PyCon JP.
- Neutral, because the minimal slides are easy to version-control, though the deck becomes many short slides.
- Bad, like the Lessig method, because it imposes a rigid *format* — large text only, no diagrams, no code blocks, no live demos — that is incompatible with the technical and demo-heavy nature of the PyVista WASM talk.
- Bad, because it strips the deck of the code snippets, architecture diagrams, and live browser demos that are the talk's centerpiece, undermining the value of selecting Slidev in [ADR-0001](0001-use-slidev-for-pycon-jp-2026-talk-slides.md).
- Bad, because the speaker must carry nearly all content verbally, increasing rehearsal burden and leaving no on-screen reference for technical detail.

## More Information

### Comparison matrix

The table below summarises how each option scores against the evaluation criteria. ✓ = strong, ~ = partial, ✗ = weak.

| Criterion | 1 slide, 1 message | 1 slide, 1 topic | Free-form | Lessig method | Takahashi method |
|---|:---:|:---:|:---:|:---:|:---:|
| Audience focus and comprehension | ✓ | ~ | ✗ | ✓ | ✓ |
| Narrative clarity | ✓ | ~ | ✗ | ✓ | ✓ |
| Live-presentation pacing | ✓ | ~ | ✗ | ~ | ~ |
| Slide-source readability under VCS | ✓ | ~ | ✗ | ~ | ~ |
| Alignment with best practices | ✓ | ~ | ✗ | ✓ | ✓ |
| Compatibility with code/diagram/demo slides | ✓ | ✓ | ✓ | ✗ | ✗ |
| Verifiable compliance criterion | ✓ | ✗ | ✗ | ~ | ~ |

### Links

- Parent issue: [#332](https://github.com/tkoyama010/pyvista-wasm/issues/332) (follow "1 slide, 1 message" principle in the slide deck)
- This decision: [#391](https://github.com/tkoyama010/pyvista-wasm/issues/391)
- Garr Reynolds, *Presentation Zen* — advocates one idea per slide and minimal text
- Nancy Duarte, *Slide:ology* — guides slide design around a single message per slide
- Lawrence Lessig's presentation style — [https://www.lessig.org/](https://www.lessig.org/)
- Masayoshi Takahashi's presentation method — [https://www.slideshare.net/takahashim/takahashi-method](https://www.slideshare.net/takahashim/takahashi-method)
- Related: [ADR-0001](0001-use-slidev-for-pycon-jp-2026-talk-slides.md) (selected Slidev and bootstrapped the deck under `slides/`)
- Related: [ADR-0002](0002-decide-slide-preview-and-deployment-strategy.md) (established the GitHub Pages + pr-preview deployment pipeline)
- Related: [ADR-0003](0003-decide-how-to-internationalize-the-slidev-deck.md) (established the i18n structure for the deck)
