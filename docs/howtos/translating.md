# Translating the documentation

This guide explains how to add or update translations for the pyvista-wasm documentation.

The project uses Sphinx native gettext + Read the Docs translations, as decided in [ADR-0008](../decisions/0008-decide-how-to-internationalize-the-readthedocs-documentation.md).

## Prerequisites

Install the documentation extras:

```console
$ pip install -e ".[docs]"
```

This installs `sphinx`, `sphinx-intl`, and all other tools needed to build the documentation.

## Workflow

### 1. Generate `.pot` templates

Extract translatable strings from the documentation source:

```console
$ make -C docs gettext
```

This runs `sphinx-build -b gettext` and produces `.pot` files under `docs/_build/gettext/`.

### 2. Update `.po` catalogs

Update the `.po` files for a specific language (e.g. `ja`):

```console
$ make -C docs update-po LANG=ja
```

This runs `sphinx-intl update -p docs/_build/gettext -l ja` and updates `docs/locale/ja/LC_MESSAGES/*.po`.

New `msgid` entries appear with empty `msgstr` fields. Existing translations are preserved.

### 3. Translate `.po` files

Edit the `.po` files under `docs/locale/<lang>/LC_MESSAGES/` with a text editor or `.po`-aware editor (e.g. Poedit, VS Code with gettext extensions).

Fill in the `msgstr` field for each `msgid` entry:

```po
msgid "Installation"
msgstr "インストール"
```

Preserve reStructuredText/MyST syntax inside `msgstr` entries (links, roles, directives, etc.).

### 4. Build locally to verify

Build the documentation in the target language:

```console
$ make -C docs html-lang LANG=ja
```

Open `docs/_build/html/ja/index.html` in a browser to verify the translation.

### 5. Submit a pull request

Commit the updated `.po` files and open a pull request. The translation will be built on Read the Docs after merge.

## Read the Docs configuration

Each language is built as a separate Read the Docs translation project, linked to the parent (English) project via the Read the Docs dashboard. The flyout-menu language switcher appears automatically once the translation project is linked.

To add a new language:

1. Create a Read the Docs project (e.g. `pyvista-wasm-<lang>`), set its Language to the target language, and point it at the same repository.
2. Add it as a "Translation" of the parent (English) project via the Read the Docs dashboard.
3. Bootstrap the `.po` catalogs: `make -C docs update-po LANG=<lang>`.
4. Translate the `.po` files and submit a pull request.
