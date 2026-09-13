---
status: accepted
date: 2026-07-17
decision-makers: [tkoyama010]
consulted: []
informed: []
---

# Decide how to preview slides in pull requests and deploy the deck from main

## Context and Problem Statement

[ADR-0001](0001-use-slidev-for-pycon-jp-2026-talk-slides.md) selected Slidev for the PyCon JP 2026 talk deck. The deck entry point will be `slides/slides.md`, and `slidev build` produces a static SPA that can be deployed as a static site. We need two deployment flows: (1) a **per-PR preview** so reviewers can visually verify slide changes during the PR review process (issues [#294](https://github.com/tkoyama010/pyvista-wasm/issues/294)–[#316](https://github.com/tkoyama010/pyvista-wasm/issues/316)), and (2) a **main-branch deployment** so a live deck URL is available from `main` without manual local builds. The repository already deploys a redirect page to the `gh-pages` branch via [`deploy-redirect.yml`](https://github.com/tkoyama010/pyvista-wasm/blob/main/.github/workflows/deploy-redirect.yml) (using `peaceiris/actions-gh-pages`), pointing to Read the Docs. The decision must be compatible with or replace this existing deployment. Which hosting platform and CI workflow strategy should we adopt for both per-PR slide previews and main-branch deck deployment?

## Decision Drivers

- **Zero-cost hosting**: The project is an open-source, community-driven effort; the hosting solution must be free for public repositories.
- **Automatic deployment on push to main**: The deck should update automatically when slide source is merged to `main`, with no manual deploy step.
- **Per-PR preview uniqueness**: Each pull request must get a unique, stable preview URL that reflects its own branch state, so reviewers can compare slides without building locally.
- **Ease of setup**: The solution should require minimal external accounts, API tokens, or configuration beyond what is already in the repository.
- **Maintenance burden**: Prefer a solution with few moving parts and well-maintained dependencies, so the deployment pipeline does not become a source of toil.
- **Compatibility with the existing `gh-pages` redirect workflow**: The existing `deploy-redirect.yml` pushes a redirect `index.html` to the `gh-pages` branch (Pages source: "Deploy from branch"). The slide deployment must coexist with or cleanly replace this workflow without breaking the Read the Docs redirect.

## Considered Options

- [GitHub Pages (Deploy from branch)](https://docs.github.com/en/pages/getting-started-with-github-pages) + [rossjrw/pr-preview-action](https://github.com/rossjrw/pr-preview-action) — Main deck deployed to the `gh-pages` branch via `peaceiris/actions-gh-pages`; PR previews deployed to `gh-pages/pr-preview/pr-N/` via `rossjrw/pr-preview-action`
- [GitHub Pages (GitHub Actions source)](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages) + [`actions/upload-pages-artifact`](https://github.com/actions/upload-pages-artifact) / [`actions/deploy-pages`](https://github.com/actions/deploy-pages) — Main deck deployed via the official Pages artifact pipeline; PR previews as downloadable build artifacts (no live URL)
- [Netlify](https://www.netlify.com/) — Main deck deployed to Netlify on push to main; PR previews via Netlify's automatic deploy previews
- [Vercel](https://vercel.com/) — Main deck deployed to Vercel on push to main; PR previews via Vercel's automatic preview deployments
- [Cloudflare Pages](https://pages.cloudflare.com/) — Main deck deployed to Cloudflare Pages on push to main; PR previews via Cloudflare Pages preview deployments
- GitHub Actions build artifact only — No live deployment; build the deck on PRs and upload as a GitHub Actions artifact that reviewers download and serve locally
- [Read the Docs](https://readthedocs.org/) subpath — Deploy the slide deck within the existing Read the Docs documentation site as a subpath

## Decision Outcome

Chosen option: "GitHub Pages (Deploy from branch) + rossjrw/pr-preview-action", because it is the only option that satisfies every decision driver simultaneously — it is zero-cost, fully GitHub-native (no external accounts or tokens), provides unique per-PR live preview URLs with automatic cleanup, deploys automatically on push to main, and is fully compatible with the existing `gh-pages` redirect workflow that already uses `peaceiris/actions-gh-pages` on the `gh-pages` branch.

### Consequences

- Good, because per-PR previews get unique, stable live URLs at `https://<owner>.github.io/<repo>/pr-preview/pr-<N>/` with an automatic PR comment containing the link, so reviewers can visually verify slide changes without cloning or building locally.
- Good, because `rossjrw/pr-preview-action` automatically cleans up preview deployments when a PR is closed, preventing the `gh-pages` branch from accumulating stale preview directories.
- Good, because the main deck deploys automatically on push to `main` at `https://<owner>.github.io/<repo>/slides/`, giving a shareable live deck URL with no manual step.
- Good, because both workflows use the same `gh-pages` branch with "Deploy from branch" Pages source as the existing `deploy-redirect.yml`, so the Read the Docs redirect at the root is preserved and the slide deck lives at a `/slides/` subpath.
- Good, because no external service accounts, API tokens, or credit cards are required — everything runs through `GITHUB_TOKEN` and GitHub's free Pages offering for public repositories.
- Bad, because the `deploy-redirect.yml` workflow must be updated to set `keep_files: true` (or add `clean-exclude: pr-preview/`) so its current `keep_files: false` does not delete PR preview directories and the `slides/` directory on every redirect deployment.
- Bad, because Slidev must be built with the correct `--base` path (`/pyvista-wasm/slides/` for main, `/pyvista-wasm/pr-preview/pr-<N>/` for previews) so that asset URLs resolve correctly under the subpath deployment.
- Neutral, because `rossjrw/pr-preview-action` does not support PRs from forks (the action notes this as a v2 roadmap item), so external contributors' PRs would not get automatic previews — acceptable for this project where slide PRs (#294–#316) are expected from the maintainer.

### Confirmation

Compliance with this decision will be confirmed by:

1. A `deploy-slides.yml` workflow exists in `.github/workflows/` that builds the Slidev deck with `slidev build --base /pyvista-wasm/slides/` on push to `main` (when `slides/**` changes) and deploys to the `gh-pages` branch under a `slides/` subdirectory via `peaceiris/actions-gh-pages` with `keep_files: true`.
1. A `preview-slides.yml` workflow exists in `.github/workflows/` that builds the Slidev deck on `pull_request` events (opened, synchronize, reopened, closed) when `slides/**` changes, and deploys via `rossjrw/pr-preview-action` to `gh-pages/pr-preview/pr-<N>/`, posting a comment on the PR with the preview URL.
1. The existing `deploy-redirect.yml` is updated to use `keep_files: true` (or equivalent `clean-exclude`) so it no longer removes the `slides/` and `pr-preview/` directories.
1. The main deck is accessible at `https://tkoyama010.github.io/pyvista-wasm/slides/` after a push to `main`.
1. A PR touching `slides/` receives a comment with a preview URL at `https://tkoyama010.github.io/pyvista-wasm/pr-preview/pr-<N>/`, and the preview directory is removed when the PR is closed.

## Pros and Cons of the Options

### GitHub Pages (Deploy from branch) + rossjrw/pr-preview-action

See [https://github.com/rossjrw/pr-preview-action](https://github.com/rossjrw/pr-preview-action)

- Good, because it is fully GitHub-native — no external accounts, API tokens, or credit cards are needed; everything runs through `GITHUB_TOKEN` and GitHub's free Pages offering.
- Good, because `rossjrw/pr-preview-action` deploys each PR to a unique subpath (`pr-preview/pr-<N>/`) on the existing GitHub Pages site, posts a comment with the preview URL on the PR, updates the preview on new commits, and cleans up automatically when the PR is closed.
- Good, because it is compatible with the existing `deploy-redirect.yml` workflow, which already uses `peaceiris/actions-gh-pages` to push to the `gh-pages` branch with "Deploy from branch" Pages source — no Pages source migration is needed.
- Good, because the main deck can be deployed to a `slides/` subpath on the same `gh-pages` branch, preserving the root redirect to Read the Docs.
- Good, because Slidev's official hosting documentation provides a GitHub Pages deploy example using `peaceiris/actions-gh-pages`, so this approach is well-documented and battle-tested.
- Neutral, because `rossjrw/pr-preview-action` requires the repository's Pages source to be "Deploy from branch" (not "GitHub Actions"), which is already the case for this repository.
- Bad, because the existing `deploy-redirect.yml` uses `keep_files: false`, which would delete the `pr-preview/` and `slides/` directories — a one-line change to `keep_files: true` is required.
- Bad, because PRs from forks do not get automatic previews (a known limitation of `rossjrw/pr-preview-action`).

### GitHub Pages (GitHub Actions source) + actions/upload-pages-artifact / actions/deploy-pages

See [https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)

- Good, because it uses GitHub's first-party, officially maintained Pages deployment actions (`actions/upload-pages-artifact` and `actions/deploy-pages`), which are well-documented and actively maintained.
- Good, because it is zero-cost and GitHub-native, requiring no external accounts or tokens.
- Good, because Slidev's official hosting documentation includes a sample workflow using `actions/upload-pages-artifact` + `actions/deploy-pages`.
- Neutral, because it requires switching the repository's Pages source from "Deploy from branch" to "GitHub Actions", which means the existing `deploy-redirect.yml` workflow (using `peaceiris/actions-gh-pages`) would no longer work and must be replaced by incorporating the redirect page into the Pages artifact.
- Bad, because `actions/deploy-pages` is restricted to the default branch for the `github-pages` environment, so per-PR live preview URLs are not natively supported — PR builds can only be uploaded as downloadable artifacts, which reviewers must download and serve locally, failing the per-PR-preview-uniqueness driver for a *live* URL.
- Bad, because migrating the Pages source breaks the existing redirect workflow and adds migration complexity.

### Netlify

See [https://www.netlify.com/](https://www.netlify.com/) and [Slidev Netlify hosting](https://sli.dev/guide/hosting.html#netlify)

- Good, because Netlify automatically creates unique preview deployment URLs for each PR with no extra workflow configuration, strongly satisfying the per-PR-preview-uniqueness driver.
- Good, because Netlify deploys on push to main automatically and provides a free tier for public projects.
- Good, because Slidev's official hosting documentation provides a `netlify.toml` template for Netlify deployment.
- Good, because Netlify handles SPA routing (redirects to `index.html`) out of the box, which Slidev's SPA build requires.
- Neutral, because the free tier has build-minute and bandwidth limits that are generous but not unlimited.
- Bad, because it requires creating a Netlify account, linking the repository, and storing an API token as a repository secret — adding external dependency and setup overhead.
- Bad, because it is not compatible with the existing `gh-pages` redirect workflow; the redirect would need to be migrated or the deck would live on a separate Netlify domain, splitting the project's web presence.

### Vercel

See [https://vercel.com/](https://vercel.com/) and [Slidev Vercel hosting](https://sli.dev/guide/hosting.html#vercel)

- Good, because Vercel automatically creates unique preview deployment URLs for each PR with no extra workflow configuration.
- Good, because Vercel deploys on push to main automatically and provides a free tier for hobby projects.
- Good, because Slidev's official hosting documentation provides a `vercel.json` template for Vercel deployment.
- Neutral, because the free tier has usage limits and Vercel's commercial focus may introduce future pricing pressure for open-source projects.
- Bad, because it requires creating a Vercel account, linking the repository, and storing an API token — adding external dependency and setup overhead.
- Bad, because it is not compatible with the existing `gh-pages` redirect workflow; the deck would live on a separate Vercel domain.

### Cloudflare Pages

See [https://pages.cloudflare.com/](https://pages.cloudflare.com/)

- Good, because Cloudflare Pages provides automatic preview deployments for each PR and deploys on push to main.
- Good, because the free tier is generous with unlimited bandwidth and build requests for public projects.
- Neutral, because Slidev's official hosting documentation does not include a Cloudflare Pages template, so the configuration must be written from scratch.
- Bad, because it requires creating a Cloudflare account, linking the repository, and storing an API token — adding external dependency and setup overhead.
- Bad, because it is not compatible with the existing `gh-pages` redirect workflow; the deck would live on a separate Cloudflare Pages domain.

### GitHub Actions build artifact only

- Good, because it requires no hosting platform at all — the built deck is uploaded as a GitHub Actions artifact on PRs, and reviewers download and serve it locally with `npx vite preview` or any static server.
- Good, because it is zero-cost and fully GitHub-native with no external accounts.
- Neutral, because it is trivial to set up: a single `actions/upload-artifact` step after `slidev build`.
- Bad, because reviewers must download, extract, and serve the artifact locally, which is friction-heavy and fails the per-PR-preview-uniqueness driver for a *live* URL that can be shared with non-technical reviewers.
- Bad, because there is no automatic main-branch deployment — the deck is not accessible at a live URL without manual artifact download, failing the automatic-deployment driver.

### Read the Docs subpath

See [https://readthedocs.org/](https://readthedocs.org/)

- Good, because the project already uses Read the Docs for documentation (`pyvista-js.readthedocs.io`), so deploying the deck as a subpath would keep all project web presence in one place.
- Good, because Read the Docs is free for open-source projects and deploys automatically on push to main.
- Neutral, because Read the Docs is designed for Sphinx/MkDocs documentation, not arbitrary static SPAs — embedding a Slidev SPA would require a custom build step or iframe embedding within an Sphinx page.
- Bad, because Slidev's SPA build is not a documentation site, so integrating it into Read the Docs would be an awkward fit requiring workarounds (e.g., committing the built `dist/` to the repo and serving it as static files within the Sphinx build).
- Bad, because Read the Docs does not provide per-PR preview deployments for arbitrary subpaths, failing the per-PR-preview-uniqueness driver.

## More Information

### Comparison matrix

The table below summarises how each option scores against the evaluation criteria. ✓ = strong, ~ = partial, ✗ = weak.

| Criterion | GH Pages (branch) + pr-preview | GH Pages (Actions) + deploy-pages | Netlify | Vercel | Cloudflare Pages | Build artifact only | Read the Docs subpath |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Zero-cost hosting | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Auto-deploy on push to main | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ |
| Per-PR live preview URL | ✓ | ✗ | ✓ | ✓ | ✓ | ✗ | ✗ |
| Ease of setup | ✓ | ~ | ~ | ~ | ~ | ✓ | ✗ |
| Low maintenance burden | ✓ | ✓ | ~ | ~ | ~ | ✓ | ✗ |
| Compatibility with existing `gh-pages` redirect | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ | ~ |

### Concrete CI workflows to implement in a follow-up PR

1. **`deploy-slides.yml`** (deploy-on-main): Triggered on push to `main` when `slides/**` changes (plus `workflow_dispatch`). Steps: checkout → setup Node.js → install Slidev dependencies → `slidev build --base /pyvista-wasm/slides/` → deploy to `gh-pages` branch under `slides/` via `peaceiris/actions-gh-pages` with `destination_dir: slides` and `keep_files: true`.
1. **`preview-slides.yml`** (preview-on-PR): Triggered on `pull_request` (opened, synchronize, reopened, closed) when `slides/**` changes. Steps: checkout → setup Node.js → install Slidev dependencies → `slidev build --base /pyvista-wasm/pr-preview/pr-<N>/` → deploy via `rossjrw/pr-preview-action` to `gh-pages/pr-preview/pr-<N>/`, which posts a PR comment with the preview URL and cleans up on PR close.
1. **Update `deploy-redirect.yml`**: Change `keep_files: false` to `keep_files: true` so the redirect deployment does not delete the `slides/` and `pr-preview/` directories maintained by the other two workflows.

### Links

- Slidev hosting documentation: [https://sli.dev/guide/hosting.html](https://sli.dev/guide/hosting.html)
- rossjrw/pr-preview-action: [https://github.com/rossjrw/pr-preview-action](https://github.com/rossjrw/pr-preview-action)
- peaceiris/actions-gh-pages: [https://github.com/peaceiris/actions-gh-pages](https://github.com/peaceiris/actions-gh-pages)
- actions/upload-pages-artifact: [https://github.com/actions/upload-pages-artifact](https://github.com/actions/upload-pages-artifact)
- actions/deploy-pages: [https://github.com/actions/deploy-pages](https://github.com/actions/deploy-pages)
- GitHub Pages documentation: [https://docs.github.com/en/pages](https://docs.github.com/en/pages)
- Parent issue: [#275](https://github.com/tkoyama010/pyvista-wasm/issues/275)
- This decision: [#318](https://github.com/tkoyama010/pyvista-wasm/issues/318)
- Related: [ADR-0001](0001-use-slidev-for-pycon-jp-2026-talk-slides.md) (selected Slidev and bootstrapped the deck under `slides/`)
- Unblocks: [#278](https://github.com/tkoyama010/pyvista-wasm/issues/278) (slide deck creation) — reviewers need visual previews for the 23 slide PRs ([#294](https://github.com/tkoyama010/pyvista-wasm/issues/294)–[#316](https://github.com/tkoyama010/pyvista-wasm/issues/316))
