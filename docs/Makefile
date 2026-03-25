# Minimal makefile for Sphinx documentation

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SPHINXINTL    ?= sphinx-intl
SOURCEDIR     = .
BUILDDIR      = _build
LOCALEDIR     = locale
POTDIR        = pot

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Generate message catalogs (.pot files) for translation
gettext:
	@$(SPHINXBUILD) -b gettext "$(SOURCEDIR)" "$(POTDIR)" $(SPHINXOPTS) $(O)
	@echo
	@echo "Build finished. The message catalogs are in $(POTDIR)."

# Update .po files from .pot files for specified language
# Usage: make update-po LANG=ja
update-po:
	@$(SPHINXINTL) update -p "$(POTDIR)" -l $(LANG)
	@echo
	@echo "Updated .po files for language: $(LANG)"

# Build HTML documentation in specified language
# Usage: make html-lang LANG=ja
html-lang:
	@$(SPHINXBUILD) -b html -D language=$(LANG) "$(SOURCEDIR)" "$(BUILDDIR)/html/$(LANG)" $(SPHINXOPTS) $(O)
	@echo
	@echo "Build finished. The HTML pages for language '$(LANG)' are in $(BUILDDIR)/html/$(LANG)."

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
