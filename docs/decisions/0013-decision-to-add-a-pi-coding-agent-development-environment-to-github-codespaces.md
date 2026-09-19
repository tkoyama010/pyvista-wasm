# Decision to add a pi coding agent development environment to GitHub Codespaces

* Status: proposed
* Date: 2026-09-19
* Decision-makers: tkoyama010

## Context and Problem Statement

Contributors currently set up the development environment locally: the project uses [uv](https://docs.astral.sh/uv/) for Python dependencies, npm for the TypeScript glue layer, and [pre-commit](https://pre-commit.com/) hooks (including the `pyadr` hooks that generate and check [`docs/decisions/`](./index.md)). [`AGENTS.md`](../../AGENTS.md) states that "no local setup is required" because CI verifies the environment on every PR, but a contributor or an AI coding agent still needs a working toolchain before the first commit. [pi](https://github.com/earendil-works/pi-coding-agent) is the coding agent harness used to develop this repository, and [GitHub Codespaces](https://github.com/features/codespaces) can provision a ready-to-use browser or VS Code environment from a `devcontainer.json` file. Should we add a Codespaces development environment configured for the pi coding agent?

## Decision Drivers

- **Low-friction onboarding**: a contributor should be able to start hacking (or run the pi agent) with one click, without installing uv, Node, or pre-commit locally.
- **Agent parity**: the pi agent works best when the environment it edits in matches CI exactly, so agent-made PRs pass on the first run.
- **Single source of truth**: the environment definition must live in the repository and be versioned with the code, like every other tool decision here.
- **Maintenance cost**: pyvista-wasm is a small project; a second environment definition that drifts from the local/CI one is a real liability.
- **No local setup required**: [`AGENTS.md`](../../AGENTS.md) promises CI verifies the environment; a Codespace must not become a requirement to contribute.

## Considered Options

- **Option A: Add a Codespaces devcontainer configured for the pi coding agent**
- **Option B: Keep local setup only (status quo)**

## Decision Outcome

Chosen option: "**Option A: Add a Codespaces devcontainer configured for the pi coding agent**", because it is the only option that makes the environment reproducible for both human contributors and the pi agent at zero marginal CI cost.

- The devcontainer installs the same toolchain CI uses: Python via uv, Node.js via npm, and pre-commit with all hooks from [`.pre-commit-config.yaml`](../../.pre-commit-config.yaml).
- The pi CLI is installed in the image, so an agent session starts with the repository, [`AGENTS.md`](../../AGENTS.md), and the lint/test commands already available.
- The environment definition is one `devcontainer.json` (plus a small Dockerfile if needed) under `.devcontainer/`, versioned in the repository.
- CI remains the source of truth for "does the environment work": the Codespace reuses the same install steps, so drift is visible in PRs.

### Consequences

- Good, because contributors and the pi agent get a working, CI-equivalent environment in minutes with no local installation.
- Good, because agent-driven changes (the primary development workflow for this repository) start from the same tool versions CI enforces.
- Good, because the Codespace definition documents the environment as code; setup steps stop living in people's heads.
- Bad, because a second environment surface can drift from CI; any toolchain change must update CI and the devcontainer together.
- Bad, because Codespaces consumption is billed per core-hour; occasional contributors may prefer local setup.

### Confirmation

Compliance is confirmed by the presence of `.devcontainer/` in the repository and by launching a Codespace from a PR preview: `uv run pytest`, `npm run lint`, and `pre-commit run --all-files` must succeed inside it without manual installation steps. If `.devcontainer/` is removed, or if it no longer reproduces the CI toolchain, this decision is violated.

## Pros and Cons of the Options

### Option A: Add a Codespaces devcontainer configured for the pi coding agent

A `devcontainer.json` under `.devcontainer/` that installs uv, Node.js, pre-commit, and the pi CLI.

- Good, because onboarding becomes one click for humans and one `gh codespace create` for agents.
- Good, because the pi agent can be pointed at a fresh Codespace per task, keeping sessions isolated and reproducible.
- Good, because the definition is versioned and reviewed like code.
- Neutral, because the devcontainer reuses the same commands CI already runs; it adds no new tool to maintain.
- Bad, because Codespaces usage costs money and requires a GitHub account with the feature enabled.
- Bad, because image build time must be kept in check or Codespace startup becomes slow.

### Option B: Keep local setup only (status quo)

Contributors and agents run against local machines; CI verifies the result on every PR.

- Good, because no new files or image builds are maintained.
- Good, because [`AGENTS.md`](../../AGENTS.md) already promises CI covers environment verification.
- Bad, because every contributor and every fresh agent session repeats setup manually, with version drift between machines.
- Bad, because the pi agent cannot reliably start from a clean, known-good state; agent PR quality depends on the host machine it happens to run on.

## More Information

- Toolchain sources of truth: [`pyproject.toml`](../../pyproject.toml) / `uv.lock`, [`package.json`](../../package.json) / `package-lock.json`, [`.pre-commit-config.yaml`](../../.pre-commit-config.yaml).
- Environment promises in [`AGENTS.md`](../../AGENTS.md) must be kept in sync if this decision is revisited.
- Revisit triggers: Codespace costs become a problem, or the devcontainer drifts from CI and the drift cannot be closed cheaply.
- Follow-up decision: [ADR-0014 — Decision not to use Nix in the Codespace environment](0014-decision-not-to-use-nix-in-the-codespace-environment.md).
