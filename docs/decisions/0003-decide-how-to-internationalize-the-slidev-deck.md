---
status: accepted
date: 2026-08-01
decision-makers: [tkoyama010]
consulted: []
informed: []
---

# Decide how to internationalize the Slidev deck (JA/EN)

## Context and Problem Statement

The PyCon JP 2026 talk deck (`slides/slides.md`, selected in [ADR-0001](0001-use-slidev-for-pycon-jp-2026-talk-slides.md)) currently mixes Japanese and English inline within each slide. For example, the cover slide shows both "Server-less 3D Visualization" and "サーバーレス3D可視化の実現" side by side, and the speaker panel renders both "Tetsuo Koyama" and "小山 哲央" together. This couples the two language versions: editing one language requires touching the same Markdown block as the other, and there is no clean way to present a single-language view of the talk. Issue [#361](https://github.com/tkoyama010/pyvista-wasm/issues/361) captures the user-facing need to internationalize the deck (JA/EN) with a way to switch between languages, and [#333](https://github.com/tkoyama010/pyvista-wasm/issues/333) proposes adopting [`slidev-addon-i18nb`](https://github.com/LarchLiu/slidev-addon-i18n) as one implementation approach. Which i18n strategy should we adopt for the Slidev deck?

## Decision Drivers

- **Single-language rendering**: A viewer must be able to see the entire deck rendered in one language (JA or EN) at a time, without the other language cluttering the slide. This is a knock-out criterion.
- **Independent maintenance of JA/EN content**: Editing one language's text must not require touching the other language's content, so the two versions can be maintained independently and reviewed separately in PRs.
- **Compatibility with the existing deployment pipeline**: The i18n solution must work with the deployment strategy established in [ADR-0002](0002-decide-slide-preview-and-deployment-strategy.md) — GitHub Pages (Deploy from branch) with `peaceiris/actions-gh-pages` for main and `rossjrw/pr-preview-action` for per-PR previews, both building via `slidev build`.
- **Zero-cost / GitHub-native tooling**: The project is an open-source, community-driven effort; the i18n solution must not require paid services, external API keys, or accounts beyond what is already in the repository.
- **Authoring ergonomics**: The bilingual content should be authorable efficiently with hot-reload preview, so iteration is fast before the talk. Slide structure (layout, components, code blocks) should remain easy to write.
- **Build-time impact**: The i18n solution should not significantly increase build time or bundle size, since the deck is built in CI on every PR and on push to main.

## Considered Options

- [`slidev-addon-i18nb`](https://github.com/LarchLiu/slidev-addon-i18n) — Slidev addon built on Vue i18n; provides a per-language translation layer with a runtime language switcher
- Two separate decks (`slides.ja.md` / `slides.en.md`) — full language separation; each deck is built and deployed independently
- Keep the current inline JA/EN approach — both languages on every slide; no i18n tooling
- Custom Vue i18n integration — manually integrate [`vue-i18n`](https://github.com/intlify/vue-i18n) with a custom language-switcher component, without the Slidev addon
- Build-time locale switching — single `slides.md` with conditional content blocks, built twice with a locale environment variable, producing two static deployments

## Decision Outcome

Chosen option: "slidev-addon-i18nb", because it is the only option that satisfies every decision driver simultaneously — it provides runtime single-language rendering with an in-deck language switcher, stores translations in separate YAML files so JA/EN content is maintained independently, integrates with the existing `slidev build` pipeline without deployment changes, requires no paid services or API keys in manual-translation mode, and keeps the slide structure in a single `slides.md` file so layout and code blocks are authored once.

### Consequences

- Good, because a viewer can switch between JA and EN at runtime via a language-switcher control in the Slidev navigation, seeing the entire deck in a single language without the other language on screen.
- Good, because translations live in separate YAML files (`locales/ja.yml`, `locales/en.yml`), so editing one language does not require touching the other or the slide structure file.
- Good, because the slide structure (layouts, Vue components, code blocks, iframes) is authored once in `slides.md` with `{{ $t("key") }}` placeholders, avoiding the duplication and drift risk of two separate decks.
- Good, because the addon is a standard Slidev addon registered in headmatter, so `slidev build` and the existing CI workflows in `deploy-slides.yml` and `preview-slides.yml` continue to work without structural changes.
- Good, because the manual-translation mode requires no API keys or external services, satisfying the zero-cost / GitHub-native driver.
- Bad, because every text string in the current `slides.md` must be extracted into translation keys and replaced with `{{ $t("key") }}` calls, which is a significant one-time migration effort for a 23-slide deck with complex HTML.
- Bad, because the addon has a very small community (2 GitHub stars, v0.2.6 as of 2026-08-01), so there is a risk of the project becoming unmaintained; we accept this risk because the addon is MIT-licensed and thin enough to fork or replace if needed.
- Bad, because the `{{ $t("key") }}` syntax does not work inside HTML attributes or `<script setup>` blocks without additional handling, so some slides with complex inline HTML may need refactoring or custom Vue components for their translated text.
- Neutral, because the addon's AI auto-transform feature (which uses a Gemini API key) is available but optional; we will use manual translation to stay zero-cost and GitHub-native.

### Confirmation

Compliance with this decision will be confirmed by:

1. `slidev-addon-i18nb` is listed in the `addons` frontmatter of `slides/slides.md` and in `slides/package.json` dependencies.
1. A `locales/` directory exists under `slides/` containing `ja.yml` and `en.yml` with translation keys for all user-facing text in the deck.
1. `slides/slides.md` uses `{{ $t("key") }}` placeholders for translatable text, with no inline JA/EN mixing on any slide.
1. Running `slidev dev` locally and switching the language via the addon's language-switcher control renders the entire deck in the selected language (JA or EN).
1. `slidev build --base /pyvista-wasm/slides/` succeeds and the built deck is deployed to GitHub Pages at `https://tkoyama010.github.io/pyvista-wasm/slides/` with the language switcher functional.
1. A per-PR preview built via `preview-slides.yml` renders correctly in both languages.
1. All existing slide content (23 slides) is migrated to the i18n structure without loss of material — verified by comparing the rendered output against the pre-migration deck.

## Pros and Cons of the Options

### slidev-addon-i18nb — Slidev addon built on Vue i18n with a runtime language switcher

See [https://github.com/LarchLiu/slidev-addon-i18n](https://github.com/LarchLiu/slidev-addon-i18n)

- Good, because it provides a runtime language switcher in the Slidev navigation bar, so a viewer can toggle between JA and EN without leaving the deck — fully satisfying the single-language-rendering driver.
- Good, because translations are stored in separate YAML files (`locales/ja.yml`, `locales/en.yml`), so editing one language does not require touching the other — fully satisfying the independent-maintenance driver.
- Good, because the slide structure (layouts, components, code blocks) is authored once in `slides.md` with `{{ $t("key") }}` placeholders, avoiding the duplication and drift risk of two separate decks.
- Good, because it is a standard Slidev addon registered via headmatter `addons:` — no build pipeline changes are needed; `slidev build` continues to produce a single SPA deployment, satisfying compatibility with ADR-0002.
- Good, because the manual-translation mode requires no API keys, external accounts, or paid services — satisfying the zero-cost / GitHub-native driver.
- Good, because it is built on [vue-i18n](https://github.com/intlify/vue-i18n), a widely adopted i18n library for Vue, so the translation mechanism is well-understood.
- Neutral, because the addon's AI auto-transform feature can accelerate the initial translation extraction, but it requires a Gemini API key and is therefore optional rather than a core workflow.
- Bad, because the addon has a very small community (2 GitHub stars, 0 forks, v0.2.6 as of 2026-08-01), so there is a maintenance-risk if the upstream project becomes inactive.
- Bad, because migrating the existing 23-slide deck requires extracting every text string into translation keys and replacing it with `{{ $t("key") }}` — a significant one-time effort, especially for slides with complex inline HTML.
- Bad, because `{{ $t("key") }}` works in Markdown text and Vue template interpolations but not in raw HTML attributes or `<script setup>` logic without additional workarounds, so some slides may need refactoring.

### Two separate decks (slides.ja.md / slides.en.md) — full language separation

- Good, because each deck is a complete, clean single-language file — no i18n tooling, no translation keys, no `$t()` syntax; authoring stays plain Markdown.
- Good, because it is trivially compatible with the existing deployment pipeline: build each deck separately with `slidev build` and deploy to different subpaths (e.g. `/slides/ja/` and `/slides/en/`).
- Good, because it is zero-cost and GitHub-native with no external dependencies beyond what Slidev already provides.
- Good, because each language can be reviewed independently in a PR — a JA text fix touches only `slides.ja.md`.
- Neutral, because the existing `slides/slides.md` can be split into two files mechanically, though the effort is comparable to the addon migration.
- Bad, because the slide structure (layouts, components, code blocks, iframes) is duplicated across two files, so structural changes must be applied twice — doubling the maintenance burden and creating drift risk.
- Bad, because there is no in-deck language switcher; a viewer must navigate to a different URL to switch languages, which is less seamless than a runtime toggle and may not fully satisfy the "switch the presentation language" acceptance criterion in [#361](https://github.com/tkoyama010/pyvista-wasm/issues/361).
- Bad, because the CI workflows (`deploy-slides.yml`, `preview-slides.yml`) must be modified to build and deploy two decks instead of one, adding build-time and workflow complexity.

### Keep the current inline JA/EN approach — both languages on every slide

- Good, because it requires zero migration effort — the deck already works this way.
- Good, because it requires no additional tooling, dependencies, or build pipeline changes.
- Good, because a single `slides.md` file and a single build produce the deployed deck, keeping the pipeline simple.
- Neutral, because both languages are always visible to the audience, which may be acceptable for a bilingual conference like PyCon JP but does not meet the user story in [#361](https://github.com/tkoyama010/pyvista-wasm/issues/361).
- Bad, because the two language versions are coupled — editing a JA string requires touching the same Markdown block as the EN string, failing the independent-maintenance driver.
- Bad, because there is no single-language view; every slide shows both JA and EN simultaneously, failing the single-language-rendering knock-out criterion.
- Bad, because slides become visually cluttered with two languages on screen, reducing readability and presentation quality.

### Custom Vue i18n integration — manually integrate vue-i18n without the Slidev addon

See [https://github.com/intlify/vue-i18n](https://github.com/intlify/vue-i18n)

- Good, because it uses vue-i18n directly — a mature, widely adopted library (~3.5k GitHub stars) with extensive documentation and community support, avoiding the small-community risk of slidev-addon-i18nb.
- Good, like the addon, it provides runtime language switching and separate translation files, satisfying the single-language-rendering and independent-maintenance drivers.
- Good, because it is zero-cost and requires no external API keys or accounts.
- Neutral, because the translation YAML files and `{{ $t("key") }}` syntax are the same as with the addon, so the migration effort for the slide content is identical.
- Bad, because it requires manually writing the Slidev integration layer — a custom language-switcher Vue component, a custom nav-controls override, and the vue-i18n plugin setup — duplicating what slidev-addon-i18nb already provides.
- Bad, because the custom integration is additional code to maintain and test, increasing the project's surface area for a one-time talk deck.
- Bad, because there is no Slidev-specific documentation for manually integrating vue-i18n, so the setup requires trial-and-error and is harder to review.

### Build-time locale switching — single source, built twice with a locale environment variable

- Good, because it keeps a single `slides.md` source file, avoiding the duplication and drift risk of two separate decks.
- Good, because it is zero-cost and GitHub-native — no external dependencies beyond Slidev itself.
- Good, because each build produces a clean single-language deck, satisfying the single-language-rendering driver.
- Neutral, because the conditional content blocks (e.g., `<div v-if="$locale === 'ja'">...</div>`) are straightforward to write but interleave both languages in the same file, partially coupling them.
- Bad, because there is no runtime language switcher — the viewer must navigate to a different URL to switch languages, less seamless than a runtime toggle.
- Bad, because the CI workflows must build the deck twice (once per locale) and deploy to separate subpaths, doubling build time and adding workflow complexity.
- Bad, because interleaving JA and EN content in the same Markdown block (even with `v-if`) means a text edit in one language touches the same block as the other, partially failing the independent-maintenance driver.

## More Information

### Comparison matrix

The table below summarises how each option scores against the evaluation criteria. ✓ = strong, ~ = partial, ✗ = weak.

| Criterion | slidev-addon-i18nb | Two separate decks | Inline JA/EN | Custom vue-i18n | Build-time locale |
|---|:---:|:---:|:---:|:---:|:---:|
| Single-language rendering (runtime switch) | ✓ | ~ | ✗ | ✓ | ~ |
| Independent JA/EN maintenance | ✓ | ✓ | ✗ | ✓ | ~ |
| Compatibility with ADR-0002 deployment | ✓ | ~ | ✓ | ✓ | ~ |
| Zero-cost / GitHub-native | ✓ | ✓ | ✓ | ✓ | ✓ |
| Authoring ergonomics | ~ | ✓ | ✓ | ~ | ~ |
| Low build-time impact | ✓ | ✗ | ✓ | ✓ | ✗ |

### Links

- slidev-addon-i18nb GitHub: [https://github.com/LarchLiu/slidev-addon-i18n](https://github.com/LarchLiu/slidev-addon-i18n)
- slidev-addon-i18nb on npm: [https://www.npmjs.com/package/slidev-addon-i18nb](https://www.npmjs.com/package/slidev-addon-i18nb)
- vue-i18n GitHub: [https://github.com/intlify/vue-i18n](https://github.com/intlify/vue-i18n)
- Slidev documentation: [https://sli.dev/guide/](https://sli.dev/guide/)
- Slidev addons documentation: [https://sli.dev/custom/addons.html](https://sli.dev/custom/addons.html)
- Parent issue: [#361](https://github.com/tkoyama010/pyvista-wasm/issues/361) (Internationalize the Slidev slide deck (JA/EN))
- Related feature request: [#333](https://github.com/tkoyama010/pyvista-wasm/issues/333) (adopt slidev-addon-i18nb for bilingual (JA/EN) slides)
- This decision: [#386](https://github.com/tkoyama010/pyvista-wasm/issues/386)
- Related: [ADR-0001](0001-use-slidev-for-pycon-jp-2026-talk-slides.md) (selected Slidev and bootstrapped the deck under `slides/`)
- Related: [ADR-0002](0002-decide-slide-preview-and-deployment-strategy.md) (established the GitHub Pages + pr-preview deployment pipeline)
