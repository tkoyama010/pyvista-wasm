---
status: accepted
date: 2026-08-07
decision-makers: [tkoyama010]
consulted: []
informed: []
---

# Decide how to internationalize the ReadTheDocs documentation

## Context and Problem Statement

The pyvista-wasm documentation is built with Sphinx + JupyterLite + sphinx-book-theme and hosted on Read the Docs (`pyvista-js.readthedocs.io`). The Sphinx i18n infrastructure is already configured in `docs/conf.py` (`locale_dirs = ["locale/"]` and `gettext_compact = False` at lines 81–82), but `language = "en"` (line 80) is the only locale and no translation catalogs (`.pot`/`.po`), localized builds, or Read the Docs translation projects exist. Issue [#389](https://github.com/tkoyama010/pyvista-wasm/issues/389) captures the user-facing need to internationalize the documentation (e.g., `ja`, `zh_CN`, `es`) so non-English-speaking users can learn and use pyvista-wasm in their native language. However, no architecture decision record exists yet that evaluates the available Sphinx/Read the Docs i18n strategies against the project's decision drivers and records the rationale for the chosen approach. Which i18n strategy should we adopt for the Read the Docs documentation?

## Decision Drivers

- **Single-language rendering per locale on Read the Docs**: A reader must be able to view the entire documentation rendered in one language at a time (e.g., Japanese at `/ja/latest/`), without the other language cluttering the page. Read the Docs must serve each language at its own URL and provide a language switcher (flyout menu). This is a knock-out criterion.
- **Independent maintenance of each translation**: Editing one language's translation must not require touching the source `.rst`/`.md` files or another language's translation, so each version can be maintained and reviewed independently in PRs.
- **Compatibility with the existing Read the Docs build**: The i18n solution must work with the current `.readthedocs.yaml` (Sphinx + JupyterLite, `ubuntu-24.04`, Python 3.13, Node.js 22) and the `sphinx-book-theme`, without breaking the JupyterLite interactive examples or the `pre_build`/`post_build` jobs.
- **Zero-cost / GitHub-native tooling**: The project is an open-source, community-driven effort; the i18n solution must not require paid services, external API keys, or accounts beyond what is already in the repository and Read the Docs.
- **Contributor ergonomics for translators**: Translators should be able to contribute translations through a familiar workflow — ideally editing text files that diff and review well in Git PRs, without requiring specialised proprietary tooling.
- **Build-time / config-complexity impact**: The i18n solution should not significantly increase build time or add complex configuration, since the docs are built on Read the Docs on every push and PR.

## Considered Options

- **Sphinx native gettext + Read the Docs translations** — `sphinx-build -b gettext` produces `.pot` templates, `sphinx-intl` initialises/updates `.po` catalogs per locale under `locale/<lang>/LC_MESSAGES/`, and Read the Docs builds each language as a separate translation project (configured via the Read the Docs dashboard) with the flyout menu providing the language switcher.
- **Per-language source trees (`docs/ja/`, `docs/en/`)** — full source duplication; each language's source tree is built as a separate Read the Docs subproject.
- **External translation management service (e.g., Crowdin / Transifex / Weblate)** — a hosted platform manages translation memory, glossaries, and a web-based translation UI; translated `.po` files are synced back to the repository via automated PRs, and Read the Docs builds each language from the synced catalogs.
- **Keep the current English-only approach** — no i18n; documentation stays English-only.

## Decision Outcome

Chosen option: "Sphinx native gettext + Read the Docs translations", because it is the only option that satisfies every decision driver simultaneously — it reuses the Sphinx i18n infrastructure already configured in `docs/conf.py` (`locale_dirs`, `gettext_compact`), produces per-locale `.po` catalogs that are maintained independently in Git PRs, builds each language as a separate Read the Docs project with the flyout-menu language switcher, requires no paid services or external accounts beyond Read the Docs itself, and adds no build-time overhead beyond Sphinx's native gettext compilation step.

### Consequences

- Good, because each language is served at its own Read the Docs URL (e.g., `/ja/latest/`, `/en/latest/`) with a flyout-menu language switcher, satisfying the single-language-rendering knock-out criterion.
- Good, because translations live in separate `.po` files under `locale/<lang>/LC_MESSAGES/`, so editing one language does not require touching the English source or another language's translation — fully satisfying the independent-maintenance driver.
- Good, because it reuses the i18n infrastructure already present in `docs/conf.py` (`locale_dirs = ["locale/"]`, `gettext_compact = False`), requiring no new Sphinx configuration beyond setting `language` per Read the Docs translation project.
- Good, because the gettext workflow is zero-cost and GitHub-native: `sphinx-intl` is a free PyPI package, `.po` files are plain text that diffs and reviews in PRs, and Read the Docs' localization feature is free for open-source projects.
- Good, because it is compatible with the existing Read the Docs build — Sphinx's gettext compilation runs as part of the normal `sphinx-build` step, and JupyterLite interactive examples and `sphinx-book-theme` are unaffected since they are not translated (code and API docs stay language-neutral).
- Good, because contributor ergonomics are strong: translators edit `.po` files in a text editor or `.po`-aware editor (e.g., Poedit, VS Code with gettext extensions) and submit changes via standard Git PRs, with no proprietary tooling required.
- Bad, because every translatable string in the documentation source (`.rst`/`.md` files, `conf.py` `project`/`copyright`/`author`, theme strings) must be extracted into `.pot` templates and then into `.po` catalogs — a one-time bootstrap effort, plus ongoing maintenance when English source text changes.
- Bad, because Read the Docs requires a separate project per language, configured via the Read the Docs dashboard (not via `.readthedocs.yaml`), adding a small amount of project-management overhead when adding a new language.
- Bad, because `.po` files can drift from the English source if the `.pot` regeneration + `sphinx-intl update` workflow is not run after English text changes, producing stale or missing translations — this requires a documented contributor workflow and CI discipline.
- Neutral, because Sphinx's gettext extraction splits translatable content at paragraph/block boundaries, which is good for granularity but means translators must preserve reStructuredText/MyST syntax inside `msgstr` entries — a standard gettext constraint, not unique to this approach.

### Confirmation

Compliance with this decision will be confirmed by:

1. Running `sphinx-build -b gettext docs docs/_build/gettext` produces `.pot` template files under `docs/_build/gettext/`.
1. `sphinx-intl update -p docs/_build/gettext -l ja` creates `docs/locale/ja/LC_MESSAGES/*.po` catalog files for at least Japanese (`ja`).
1. At least one `.po` file under `docs/locale/ja/LC_MESSAGES/` contains translated `msgstr` entries (not just placeholder `FILL HERE` text).
1. A Read the Docs translation project for `ja` is created and linked as a translation of the parent (English) project via the Read the Docs dashboard.
1. The Japanese documentation build succeeds on Read the Docs and is accessible at a `/ja/latest/` URL.
1. The Read the Docs flyout-menu language switcher is visible in the built documentation, allowing the reader to switch between `en` and `ja`.
1. The existing English documentation build and JupyterLite interactive examples continue to work unchanged on Read the Docs.
1. A contributor guide documenting the `.pot` regeneration + `sphinx-intl update` + `.po` translation workflow is added to `docs/`.

## Pros and Cons of the Options

### Sphinx native gettext + Read the Docs translations — `sphinx-build -b gettext`, `sphinx-intl`, Read the Docs localization

See [Sphinx i18n docs](https://www.sphinx-doc.org/en/master/usage/advanced/intl.html) and [Read the Docs localization](https://docs.readthedocs.com/platform/stable/localization.html).

- Good, because it reuses the Sphinx i18n infrastructure already configured in `docs/conf.py` (`locale_dirs = ["locale/"]`, `gettext_compact = False`), requiring no new Sphinx configuration.
- Good, because each language is served at its own Read the Docs URL (e.g., `/ja/latest/`) with the flyout-menu language switcher, fully satisfying the single-language-rendering knock-out criterion.
- Good, because translations live in separate `.po` files under `locale/<lang>/LC_MESSAGES/`, so editing one language does not require touching the English source or another language's translation — fully satisfying the independent-maintenance driver.
- Good, because it is zero-cost and GitHub-native: `sphinx-intl` is a free PyPI package, `.po` files are plain text that diffs and reviews in PRs, and Read the Docs' localization feature is free for open-source projects.
- Good, because it is compatible with the existing Read the Docs build — Sphinx's gettext compilation runs as part of the normal `sphinx-build` step, and JupyterLite interactive examples and `sphinx-book-theme` are unaffected.
- Good, because contributor ergonomics are strong: translators edit `.po` files in a text editor or `.po`-aware editor and submit changes via standard Git PRs, with no proprietary tooling required.
- Good, because it is the workflow recommended by both the [Sphinx i18n documentation](https://www.sphinx-doc.org/en/master/usage/advanced/intl.html#translating-with-sphinx-intl) and the [Read the Docs manage-translations guide](https://docs.readthedocs.com/platform/stable/guides/manage-translations-sphinx.html).
- Neutral, because Read the Docs requires a separate project per language, configured via the dashboard rather than `.readthedocs.yaml`, adding a small amount of project-management overhead when adding a new language.
- Bad, because every translatable string must be extracted into `.pot` templates and `.po` catalogs — a one-time bootstrap effort, plus ongoing maintenance when English source text changes.
- Bad, because `.po` files can drift from the English source if the `.pot` regeneration + `sphinx-intl update` workflow is not run after English text changes, requiring a documented contributor workflow and CI discipline.

### Per-language source trees (docs/ja/, docs/en/) — full source duplication, each built as a separate Read the Docs subproject

- Good, because each language's documentation is a complete, clean single-language source tree — no gettext tooling, no `.po` files, no `sphinx-intl`; authoring stays plain reStructuredText/MyST.
- Good, because each language can be reviewed independently in a PR — a JA text fix touches only `docs/ja/`.
- Good, because it is zero-cost and GitHub-native with no external dependencies beyond Sphinx and Read the Docs.
- Good, because each language gets its own Read the Docs URL and the flyout-menu language switcher, satisfying the single-language-rendering driver.
- Neutral, because the existing `docs/` source can be copied into `docs/en/` mechanically, though the effort is comparable to the gettext bootstrap.
- Bad, because the entire documentation source (`.rst`/`.md` files, `conf.py` settings, JupyterLite content, `index.md` toctree) is duplicated per language, so structural changes must be applied to every language's source tree — multiplying the maintenance burden and creating drift risk.
- Bad, because JupyterLite content (`docs/content/`) and the `conf.py` JupyterLite configuration would need to be duplicated or symlinked per language, adding complexity to the build configuration.
- Bad, because the `.readthedocs.yaml` `pre_build` and `post_build` jobs (jupytext conversion, JupyterLite build) would need to run per language, increasing build time and config complexity.
- Bad, because API documentation generated by `sphinx.ext.autodoc`/`autosummary` from the Python source would be duplicated per language with no translation benefit (API signatures and docstrings are language-neutral), wasting build resources.

### External translation management service (e.g., Crowdin / Transifex / Weblate) — managed translation memory + PR sync, hosted off-repo

See [Crowdin](https://crowdin.com/), [Transifex](https://www.transifex.com/), [Weblate](https://weblate.org/).

- Good, because it provides a web-based translation UI with translation memory, glossaries, and quality checks, improving translator productivity for large documentation sets.
- Good, because it can manage multiple languages and translators with role-based access (translator, reviewer, editor), which is useful for community translation at scale.
- Good, because translated `.po` files are synced back to the repository via automated PRs, so the Read the Docs build still uses Sphinx gettext — compatible with the existing build.
- Good, because each language still gets its own Read the Docs URL and flyout-menu language switcher, satisfying the single-language-rendering driver.
- Neutral, because Weblate offers a free hosted tier for open-source projects, and self-hosted Weblate is also free, so the zero-cost driver can be partially met.
- Bad, because it requires creating an account on an external service, linking the repository, and storing an API token — adding external dependency and setup overhead that violates the zero-cost / GitHub-native driver.
- Bad, because Crowdin and Transifex free tiers have limits on string count and languages, and paid tiers are required for larger projects — introducing potential future cost.
- Bad, because the translation workflow is split between the external service and Git PRs, adding a sync step that can cause conflicts if `.po` files are edited both in the service and directly in PRs.
- Bad, because it adds config complexity (`.tx/config` or equivalent) and a CI step to push `.pot` files and pull `.po` files, increasing build-time and workflow complexity for a small project.

### Keep the current English-only approach — no i18n; documentation stays English-only

- Good, because it requires zero migration effort — the documentation already works this way.
- Good, because it requires no additional tooling, dependencies, or build pipeline changes.
- Good, because a single `docs/` source tree and a single Read the Docs project keep the pipeline simple.
- Neutral, because the Sphinx i18n config in `docs/conf.py` (`locale_dirs`, `gettext_compact`) remains unused but harmless.
- Bad, because non-English-speaking users cannot fully benefit from the documentation, failing the user story in [#389](https://github.com/tkoyama010/pyvista-wasm/issues/389).
- Bad, because it fails the single-language-rendering driver — there is no localized build at all.
- Bad, because it fails the independent-maintenance driver — there are no translations to maintain, because there is no i18n.

## More Information

### Comparison matrix

The table below summarises how each option scores against the evaluation criteria. ✓ = strong, ~ = partial, ✗ = weak.

| Criterion | Sphinx gettext + RTD translations | Per-language source trees | External service (Crowdin/Transifex/Weblate) | Keep English-only |
|---|:---:|:---:|:---:|:---:|
| Single-language rendering per locale (RTD URL + switcher) | ✓ | ✓ | ✓ | ✗ |
| Independent maintenance of each translation | ✓ | ✓ | ✓ | ✗ |
| Compatibility with existing RTD build (Sphinx + JupyterLite) | ✓ | ~ | ✓ | ✓ |
| Zero-cost / GitHub-native | ✓ | ✓ | ~ | ✓ |
| Contributor ergonomics (PR-based, no proprietary tooling) | ✓ | ✓ | ~ | ✓ |
| Low build-time / config complexity | ✓ | ✗ | ~ | ✓ |
| Reuses existing `docs/conf.py` i18n config | ✓ | ✗ | ✓ | ~ |

### Concrete implementation steps for a follow-up PR

1. **Generate `.pot` templates**: Run `sphinx-build -b gettext docs docs/_build/gettext` to extract translatable strings from the documentation source.
1. **Bootstrap Japanese catalogs**: Run `sphinx-intl update -p docs/_build/gettext -l ja` to create `docs/locale/ja/LC_MESSAGES/*.po` files.
1. **Translate `.po` files**: Edit the `.po` files under `docs/locale/ja/LC_MESSAGES/` with translated `msgstr` entries, preserving reStructuredText/MyST syntax.
1. **Configure Read the Docs translation project**: Create a Read the Docs project for `ja` (e.g., `pyvista-wasm-ja`), set its Language to Japanese, point it at the same repository, and add it as a translation of the parent (English) project via the Read the Docs dashboard.
1. **Verify the localized build**: Confirm the Japanese documentation builds on Read the Docs at `/ja/latest/` and the flyout-menu language switcher is visible.
1. **Document the translation workflow**: Add a contributor guide to `docs/` explaining how to regenerate `.pot` files, update `.po` catalogs with `sphinx-intl update`, and submit translations via PRs.

### Read the Docs localization mechanism

Read the Docs localization is configured via the Read the Docs dashboard, not via a `translations` key in `.readthedocs.yaml`. Each language requires its own Read the Docs project, linked as a "Translation" of the parent (English) project. Read the Docs then serves each language at its own URL (e.g., `/ja/latest/`) and provides a flyout-menu language switcher automatically. See the [Read the Docs localization guide](https://docs.readthedocs.com/platform/stable/localization.html) and the [manage-translations for Sphinx guide](https://docs.readthedocs.com/platform/stable/guides/manage-translations-sphinx.html) for details.

### Links

- Sphinx i18n: [https://www.sphinx-doc.org/en/master/usage/advanced/intl.html](https://www.sphinx-doc.org/en/master/usage/advanced/intl.html)
- sphinx-intl: [https://pypi.org/project/sphinx-intl/](https://pypi.org/project/sphinx-intl/)
- Read the Docs localization: [https://docs.readthedocs.com/platform/stable/localization.html](https://docs.readthedocs.com/platform/stable/localization.html)
- Read the Docs manage-translations for Sphinx: [https://docs.readthedocs.com/platform/stable/guides/manage-translations-sphinx.html](https://docs.readthedocs.com/platform/stable/guides/manage-translations-sphinx.html)
- Crowdin: [https://crowdin.com/](https://crowdin.com/)
- Transifex: [https://www.transifex.com/](https://www.transifex.com/)
- Weblate: [https://weblate.org/](https://weblate.org/)
- Parent issue: [#389](https://github.com/tkoyama010/pyvista-wasm/issues/389) (i18n ReadTheDocs documentation)
- This decision: [#439](https://github.com/tkoyama010/pyvista-wasm/issues/439)
- Related: [ADR-0003](0003-decide-how-to-internationalize-the-slidev-deck.md) (i18n decision for the Slidev deck — this ADR covers the separate Read the Docs docs surface)
