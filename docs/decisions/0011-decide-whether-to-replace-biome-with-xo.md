# Decide whether to replace Biome with xo

* Status: proposed
* Date: 2026-09-13
* Decision-makers: tkoyama010

## Context and Problem Statement

The repository currently uses [Biome](https://biomejs.dev/) (`biome.json`, `@biomejs/biome` in `package.json`) to lint and format all TypeScript, JavaScript, JSON, and Markdown files. Biome is a single Rust binary invoked through `npm run lint` / `npm run format` and wired into pre-commit.ci. A community discussion raised [xo](https://github.com/xojs/xo) — an ESLint-based zero-config linter with the Prettier-backed `xo --fix` formatter — as a possible alternative. Should we migrate the JavaScript/TypeScript toolchain from Biome to xo, or stay on Biome?

## Decision Drivers

- **Zero-config experience**: Both tools advertise themselves as configuration-free. Any migration must not increase the amount of lint configuration the project maintains.
- **TypeScript support**: The hand-written glue layer lives in `ts/` (including a large ambient declaration file, `ts/vtk.d.ts`). The tool must lint modern TypeScript well, including ambient declarations.
- **Speed**: CI runs the full test suite on every PR; lint steps should stay fast.
- **Ecosystem and rule coverage**: The project relies on the linter to catch correctness issues (unused variables, unsafe assertions, a11y for renderer code) rather than to enforce opinionated style.
- **Maintenance overhead**: pyvista-wasm is a small project. Additional dependencies, plugins, or config drift are a real cost.

## Considered Options

- **Option A: Stay on Biome (status quo)**
- **Option B: Migrate to xo**

## Decision Outcome

Chosen option: "**Option A: Stay on Biome (status quo)**", because Biome already satisfies every decision driver while xo regresses on TypeScript depth, speed, and configuration effort for this repository.

- TypeScript support: Biome's first-class TS parser handles `ts/vtk.d.ts` natively. xo is ESLint underneath; deep TS checking requires `@typescript-eslint` with type-aware rules, which adds setup and is slow.
- Speed: Biome is a single Rust binary and finishes in well under a second on this repo. xo/Prettier runs the Node-based ESLint pipeline, measurably slower in CI on every PR.
- Configuration: The project already carries `biome.json` with per-file overrides for `ts/renderer.ts` and `ts/vtk.d.ts`. Migrating means re-expressing those overrides as ESLint configuration plus a Prettier config to match the current formatting (2-space indent, width 80, semicolons) — net more configuration, not less.
- Dependencies: Biome replaces ESLint + Prettier in one package. xo bundles ESLint, plugins, and Prettier, but the project would keep `eslint-plugin-jsdoc` as a separate dev dependency to preserve JSDoc linting, and would add Prettier's ecosystem on top.
- Formatting parity: Biome both lints and formats with one tool and one config. xo delegates formatting to Prettier, splitting the pipeline in two for no gain here.

xo remains a good default for greenfield JavaScript-only projects that want the ESLint plugin ecosystem. This repository is not that: it is TypeScript-heavy, already formatted by Biome, and does not need ESLint-only plugins.

### Consequences

- Good, because no migration work is needed and CI keeps its current fast lint step.
- Good, because formatting stays stable — no repo-wide reformat diff that would pollute `git blame`.
- Bad, because Biome's rule catalogue is smaller than ESLint's; if a future need requires an ESLint-only plugin, this decision should be revisited.

### Confirmation

Compliance is verified by the existing CI: `npm run lint` / `npm run format` (Biome) run through pre-commit.ci and GitHub Actions on every PR. If `biome.json` or `@biomejs/biome` is removed from the repository without a superseding ADR, this decision is violated.

## Pros and Cons of the Options

### Option A: Stay on Biome (status quo)

[Biome](https://biomejs.dev/) — single Rust toolchain for linting and formatting.

- Good, because it is already installed, configured, and passing in CI.
- Good, because first-class TypeScript parsing covers `ts/*.ts` and ambient declarations without extra plugins.
- Good, because lint + format come from one binary and one config file.
- Bad, because the plugin ecosystem is smaller than ESLint's; niche rules may not exist.

### Option B: Migrate to xo

[xo](https://github.com/xojs/xo) — opinionated ESLint wrapper with Prettier formatting.

- Good, because it exposes the full ESLint plugin ecosystem (including `eslint-plugin-jsdoc` natively).
- Good, because its presets are well known in the JS community and it supports `--fix` autofix workflows.
- Neutral, because the project does not currently use any ESLint-only plugin beyond JSDoc, which is already installed alongside Biome.
- Bad, because TypeScript type-aware linting requires extra `@typescript-eslint` setup and is slow.
- Bad, because formatting moves to Prettier, adding a second tool and config to keep style identical to today's Biome output.
- Bad, because migration cost (config rewrite, repo-wide reformat, CI churn) buys no capability the project needs today.

## More Information

- Current Biome configuration: [`biome.json`](../../biome.json)
- Lint/format entry points: `lint` and `format` scripts in [`package.json`](../../package.json)
- Biome is referenced as the code-style badge in [`CONTRIBUTING.md`](../../CONTRIBUTING.md); if this decision is ever revisited, that badge and the pre-commit configuration must change together.
- Revisit triggers: a need for an ESLint-only rule or plugin, or a Biome breaking change that removes a rule the project relies on.
