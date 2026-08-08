---
status: accepted
date: 2026-08-07
decision-makers: [tkoyama010]
consulted: []
informed: []
---

# Decide how to internationalize and sync the README

## Context and Problem Statement

The project README (`README.md`, at the repo root) is English-only today. It is a Markdown file distinct from the Sphinx ReadTheDocs documentation ([ADR-0005](https://github.com/tkoyama010/pyvista-wasm/issues/439)) and the Slidev talk deck ([ADR-0006](https://github.com/tkoyama010/pyvista-wasm/issues/442), [ADR-0003](0003-decide-how-to-internationalize-the-slidev-deck.md)), so it needs its own internationalization strategy rather than reusing Sphinx gettext or `slidev-addon-i18nb`. Issue [#444](https://github.com/tkoyama010/pyvista-wasm/issues/444) captures the user-facing need to internationalize the README (e.g. JA, zh_CN, es) and keep translations in sync automatically, so non-English-speaking users can understand the project without a language barrier and translations never go stale when the English README changes. GitHub renders localized READMEs via `README.<lang>.md` files at the repo root and shows a language switcher automatically, and [#293](https://github.com/tkoyama010/pyvista-wasm/issues/293) is aligning the README with the [Standard Readme](https://github.com/RichardLitt/standard-readme) specification — so the i18n structure must preserve that layout in every language. The repo already enforces the Standard Readme spec on `README.md` through a [`standard-readme`](https://github.com/tkoyama010/standard-readme-pre-commit) pre-commit hook. Which README i18n + sync strategy should we adopt so that translations are GitHub-native, layout-consistent, and drift is detected automatically?

## Decision Drivers

- **English is the authoritative source of truth**: The English `README.md` is the source; every `README.<lang>.md` is derived from it. A localized README never leads the English README in content. This is a knock-out criterion.
- **Compatibility with GitHub's native `README.<lang>.md` rendering**: GitHub renders `README.<lang>.md` files at the repo root and shows an automatic language switcher. The solution must produce real, committed `README.<lang>.md` files so the native switcher works with no custom UI.
- **Preserving the [Standard Readme](https://github.com/RichardLitt/standard-readme) layout in every language**: [#293](https://github.com/tkoyama010/pyvista-wasm/issues/293) is aligning `README.md` with the Standard Readme specification. Every localized README must preserve the same section/heading structure so the spec holds across languages.
- **Detecting structural drift**: A translation that is missing or adds sections, or whose headings diverge from the English README, must be surfaced automatically — not left for a reviewer to spot by eye.
- **Detecting content drift**: When the English `README.md` is updated, a translation that is not regenerated or updated must be flagged automatically, so stale translations cannot silently persist.
- **Automatic vs. manual sync; CI enforcement vs. PR-review-only**: The project favours automated, verifiable enforcement over reliance on reviewer vigilance, consistent with the pre-commit + CI pattern already used throughout the repo.
- **Zero-cost / GitHub-native tooling**: Per the drivers in [ADR-0003](0003-decide-how-to-internationalize-the-slidev-deck.md) and [ADR-0006](https://github.com/tkoyama010/pyvista-wasm/issues/442), the baseline must not require paid external services, API keys, or accounts beyond what is already in the repository.
- **Minimal maintenance burden for a single-maintainer open-source project**: The solution must be maintainable by one person; it should not introduce a heavy build pipeline or a tool that demands ongoing babysitting.
- **Consistency with ADR-0005 ([#439](https://github.com/tkoyama010/pyvista-wasm/issues/439), ReadTheDocs i18n) and ADR-0006 ([#442](https://github.com/tkoyama010/pyvista-wasm/issues/442), slide locale sync)**: The README strategy should reuse the same drift-detection philosophy where sensible, so the project has one coherent i18n-sync story across docs, slides, and README.

## Considered Options

- **EN-authoritative with CI structural-parity check** — a script or pre-commit hook comparing section/heading structure between `README.md` and each `README.<lang>.md`, failing CI if they differ
- **EN-authoritative with CI structural-parity + stale-translation check** — also flags localized READMEs not updated after the English README changes, via git-history/commit-date comparison
- **EN-authoritative with automated translation GitHub Action** — an LLM- or API-based Action that opens a PR regenerating `README.<lang>.md` on every English README change
- **Dual-maintenance with no enforcement** — status quo; rely on PR review to keep translations in sync
- **Single-source-of-truth with build-time locale generation** — one `README.md` source plus a build step producing per-language files

## Decision Outcome

Chosen option: **"EN-authoritative with CI structural-parity + stale-translation check"**, because it is the only option that satisfies every decision driver simultaneously — it keeps English as the authoritative source, produces real committed `README.<lang>.md` files so GitHub's native language switcher works, enforces the Standard Readme section/heading structure across languages via structural parity, surfaces both structural drift and content (stale-translation) drift automatically, runs as zero-cost GitHub Actions plus a pre-commit hook (no paid services or API keys), imposes minimal burden on a single maintainer, and reuses the same drift-detection philosophy as ADR-0005 and ADR-0006. Translations are authored manually by contributors; CI flags drift rather than generating translations, so human judgement stays in the loop and no external dependency is introduced.

### Consequences

- Good, because GitHub's native `README.<lang>.md` rendering and automatic language switcher work with no custom UI — the localized files are real Markdown at the repo root.
- Good, because the structural-parity check guarantees every localized README preserves the Standard Readme section/heading structure, so [#293](https://github.com/tkoyama010/pyvista-wasm/issues/293) alignment holds across languages.
- Good, because the stale-translation check surfaces content drift automatically — a localized README not updated after an English README change is flagged in CI, so stale translations cannot pass silently.
- Good, because the checks run both as a pre-commit hook (fast local feedback before push) and a CI workflow (enforcement on every PR), matching the repo's existing quality-control pattern.
- Good, because it is zero-cost and GitHub-native — a small stdlib-only script invoked by GitHub Actions and pre-commit, with no paid services, API keys, or external accounts.
- Good, because manual translation keeps human judgement in the loop and introduces no LLM/API dependency or generated-PR review load.
- Bad, because translations are not generated automatically, so a contributor must manually update each `README.<lang>.md` when the English README changes; the stale-translation check reminds them but does not do the work.
- Bad, because the structural-parity check compares structure, not translation quality — a correctly-structured but poorly translated README passes the check, so translation quality still relies on PR review.
- Neutral, because the stale-translation check uses git commit dates, which can produce false positives if an English README change is cosmetic (e.g. a badge URL) and does not require translation; contributors dismiss these by touching the localized file or the check's allowlist.

### Confirmation

Compliance with this decision will be confirmed by:

1. At least one localized README (e.g. `README.ja.md`) exists at the repo root alongside `README.md`.
1. GitHub renders the language switcher on the repository page and selecting a language displays the corresponding `README.<lang>.md`.
1. Each `README.<lang>.md` follows the [Standard Readme](https://github.com/RichardLitt/standard-readme) layout, verified by the existing `standard-readme` pre-commit hook passing on every README file.
1. A CI workflow file (e.g. `.github/workflows/readme-i18n-check.yml`) exists and passes, invoking the drift-detection script.
1. The structural-parity check compares the heading/section structure of `README.md` against each `README.<lang>.md` and fails on divergence (missing, extra, or renamed sections/headings).
1. The stale-translation check flags any `README.<lang>.md` whose last commit predates the latest `README.md` change, and fails CI until the translation is updated or explicitly allowlisted.
1. The drift-detection script has no third-party runtime dependencies (Python stdlib only) or reuses tooling already present in the repo.
1. The translation and sync workflow is documented in `CONTRIBUTING.md`, including how to add a new language and how to resolve a stale-translation failure.
1. The check also runs as a pre-commit hook so drift is caught locally before a push.

## Pros and Cons of the Options

### EN-authoritative with CI structural-parity check — compare section/heading structure, fail on divergence

A zero-dependency script parses the headings/sections of `README.md` and each `README.<lang>.md` and fails if the structure differs. Runs in CI and/or as a pre-commit hook.

- Good, because it keeps English authoritative and catches structural drift (missing, extra, or renamed sections) automatically.
- Good, because it preserves the Standard Readme layout across languages — every localized README must mirror the English section structure.
- Good, because it is zero-cost and GitHub-native: a stdlib-only script in GitHub Actions, no paid services or API keys.
- Good, because it is low maintenance for a single maintainer — one small script, no build pipeline.
- Good, because it is consistent with the drift-detection philosophy of ADR-0005 and ADR-0006.
- Neutral, because it can run as both a pre-commit hook and a CI workflow, giving fast local feedback and PR enforcement.
- Bad, because it detects only structural drift, not content drift — a translation can be stale (English README updated, translation not) yet structurally identical, so it passes the check silently. This fails the content-drift decision driver.

### EN-authoritative with CI structural-parity + stale-translation check — also flag translations not updated after the English README changes

Builds on the structural-parity check by also comparing git history: if `README.md` was committed after a given `README.<lang>.md`, the translation is flagged as stale and CI fails until it is updated or explicitly allowlisted.

- Good, because it satisfies every decision driver: English authoritative, GitHub-native `README.<lang>.md` rendering, Standard Readme layout preserved, structural drift detected, content drift detected, zero-cost, low maintenance, and consistent with ADR-0005/ADR-0006.
- Good, because it catches both kinds of drift — a localized README that diverges in structure or that falls behind the English README is surfaced automatically.
- Good, because it is zero-cost and GitHub-native: a stdlib-only script using `git log`/commit dates, run in GitHub Actions and pre-commit, with no paid services or API keys.
- Good, because it keeps human judgement in the loop — translations are manual, so no LLM/API dependency and no generated-PR review load.
- Good, because it is low maintenance for a single maintainer — one small script covering both checks, no build pipeline or external service to babysit.
- Neutral, because the stale-translation check uses commit dates and can false-flag cosmetic English changes (e.g. a badge URL); an allowlist or a trivial touch of the localized file dismisses these.
- Bad, because it does not generate translations — a contributor must still update each `README.<lang>.md` by hand; the check reminds them but does not do the work.
- Bad, because it does not assess translation quality — a correctly structured but poorly translated README passes.

### EN-authoritative with automated translation GitHub Action — LLM/API-based Action opens a PR regenerating README.<lang>.md

A GitHub Action watches `README.md` changes and uses an LLM or translation API to regenerate each `README.<lang>.md`, opening a PR with the result for review.

- Good, because it eliminates manual translation effort for the initial generation and reduces content drift — the Action regenerates translations on every English change.
- Good, because it keeps English authoritative and can produce committed `README.<lang>.md` files for GitHub's native switcher.
- Good, because content drift is largely eliminated — the Action runs on every English README change.
- Neutral, because it can produce committed `README.<lang>.md` files, but the generated Markdown may not exactly preserve the Standard Readme layout without prompt engineering and review.
- Bad, because it violates the zero-cost / GitHub-native driver — LLM and translation APIs require paid API keys or accounts beyond what is in the repository.
- Bad, because every generated PR must be reviewed by a human for accuracy and layout, adding a recurring review load that is not "minimal maintenance" for a single maintainer.
- Bad, because LLM translations can hallucinate or drop content (e.g. code blocks, badge URLs), so structural-parity is not guaranteed without an additional check — meaning this option needs the structural-parity check on top anyway.
- Bad, because it is inconsistent with the drift-detection philosophy of ADR-0005/ADR-0006, which favour detection over automatic generation.

### Dual-maintenance with no enforcement — status quo, rely on PR review

Localized READMEs are maintained by hand with no automated checks; keeping them in sync is left to reviewer vigilance during PR review.

- Good, because it requires no tooling, scripts, or CI workflow — zero implementation effort.
- Good, because it is zero-cost and introduces no dependencies.
- Good, because it is low effort to start — a contributor simply adds a `README.<lang>.md`.
- Neutral, because it is the default state of a repo with localized READMEs and no automation.
- Bad, because it fails the structural-drift and content-drift drivers — nothing detects a missing section or a stale translation, so drift accumulates silently.
- Bad, because it fails the CI-enforcement driver — reliance on reviewer vigilance is exactly what the project's pre-commit + CI pattern exists to avoid.
- Bad, because it is inconsistent with ADR-0005/ADR-0006, which both automate drift detection rather than relying on review.
- Bad, because for a single maintainer there often is no other reviewer, so "rely on PR review" reduces to "rely on the same person remembering every language," which does not scale.

### Single-source-of-truth with build-time locale generation — one README source, build step produces per-language files

A single source (e.g. a template or a structured source file with translatable strings) is built into `README.md` and each `README.<lang>.md` at build time, so all languages share one structure by construction.

- Good, because structural drift is impossible by construction — every language is generated from the same template, so headings and sections always match.
- Good, because content drift is eliminated — regeneration from the source keeps every language current.
- Good, because it keeps English authoritative and can produce committed `README.<lang>.md` files for GitHub's native switcher.
- Neutral, because the generated `README.<lang>.md` files are build artifacts that must be committed for GitHub to render them, which is unusual (committed artifacts) and can cause noisy diffs.
- Bad, because it violates the minimal-maintenance driver — it introduces a build pipeline (template engine, string store, generation script) that a single maintainer must build and maintain, far heavier than a drift-detection script.
- Bad, because it conflicts with the existing `standard-readme` pre-commit hook, which lints `README.md` directly; if `README.md` becomes a generated artifact, the hook must be reworked to lint the source or the generated output, adding complexity.
- Bad, because contributors edit a template/string store rather than `README.md` itself, which is unfamiliar and raises the contribution barrier for a simple README fix.
- Bad, because it is only partially zero-cost / GitHub-native — the generation tooling must be added and run in CI, adding build time and workflow complexity beyond the stdlib-only script of the drift-detection options.

## More Information

### Comparison matrix

The table below summarises how each option scores against the evaluation criteria. ✓ = strong, ~ = partial, ✗ = weak.

| Criterion | Structural parity only | Structural parity + stale check | Automated translation action | Dual-maintenance (status quo) | Single-source build-time |
|---|:---:|:---:|:---:|:---:|:---:|
| English authoritative source | ✓ | ✓ | ✓ | ~ | ✓ |
| GitHub native README.<lang>.md rendering | ✓ | ✓ | ✓ | ✓ | ✓ |
| Standard Readme layout preserved | ✓ | ✓ | ~ | ~ | ✓ |
| Structural drift detected | ✓ | ✓ | ✗ | ✗ | ✓ |
| Content drift detected | ✗ | ✓ | ✓ | ✗ | ✓ |
| Zero-cost / GitHub-native | ✓ | ✓ | ✗ | ✓ | ~ |
| Low maintenance burden | ✓ | ✓ | ~ | ✓ | ✗ |
| Consistency with ADR-0005/0006 | ✓ | ✓ | ~ | ✗ | ~ |

### Links

- Standard Readme specification: [https://github.com/RichardLitt/standard-readme](https://github.com/RichardLitt/standard-readme)
- GitHub localized READMEs: [https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file-for-your-organization](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file-for-your-organization)
- `standard-readme` pre-commit hook: [https://github.com/tkoyama010/standard-readme-pre-commit](https://github.com/tkoyama010/standard-readme-pre-commit)
- Parent issue: [#444](https://github.com/tkoyama010/pyvista-wasm/issues/444) (i18n the README and keep translations in sync automatically)
- Standard Readme alignment: [#293](https://github.com/tkoyama010/pyvista-wasm/issues/293) (Align README with the Standard Readme specification)
- This decision: [#445](https://github.com/tkoyama010/pyvista-wasm/issues/445)
- Related: [ADR-0003](0003-decide-how-to-internationalize-the-slidev-deck.md) (i18n decision for the Slidev deck — same zero-cost / GitHub-native philosophy)
- Related: ADR-0005 [#439](https://github.com/tkoyama010/pyvista-wasm/issues/439) (deciding how to internationalize the ReadTheDocs documentation)
- Related: ADR-0006 [#442](https://github.com/tkoyama010/pyvista-wasm/issues/442) (deciding how to keep slide locale files in sync)
