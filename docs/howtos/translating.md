# Translating the documentation

This guide explains how translations for the pyvista-wasm documentation are managed.

The project uses Sphinx native gettext + Read the Docs translations, as decided in [ADR-0008](../decisions/0008-decide-how-to-internationalize-the-readthedocs-documentation.md). Translations are managed in [Transifex](https://app.transifex.com/tkoyama010/pyvista-wasm/), following the same approach as [pyvista-js](https://github.com/tkoyama010/pyvista-js).

The committed `docs/pot/` templates and `docs/locale/` catalogs are machine-generated files — never edit them by hand.

## Workflow

### 1. `.pot` templates are updated automatically

When a pull request that touches `docs/` merges to `main`, the [Transifex Sync workflow](https://github.com/tkoyama010/pyvista-wasm/blob/main/.github/workflows/transifex.yml) runs `sphinx-build -b gettext` and opens a `chore: update pot files` pull request that updates `docs/pot/`.

### 2. Translate in Transifex

Merge that pull request, then translate the new strings in the Transifex editor, or with the Transifex pi extension (`.pi/extensions/transifex.ts`), which exposes `transifex_list_resources`, `transifex_get_untranslated`, and `transifex_translate` tools backed by the Transifex API.

### 3. Sync `.po` catalogs back to the repository

Pull the translated catalogs from Transifex and commit them, as in [#812](https://github.com/tkoyama010/pyvista-wasm/pull/812):

```console
$ tx pull -l ja
$ git add docs/locale && git commit -m "fix: sync ja translation catalogs from Transifex"
```

When a feature pull request adds a new documented API page, the matching `.po` catalog must land with that pull request, otherwise the Read the Docs ja build has no catalog for the new page.

## Read the Docs configuration

Each language is built as a separate Read the Docs translation project, linked to the parent (English) project via the Read the Docs dashboard. The flyout-menu language switcher appears automatically once the translation project is linked.
