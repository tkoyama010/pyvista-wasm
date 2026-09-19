# Decision not to use Nix in the Codespace environment

* Status: proposed
* Date: 2026-09-19
* Decision-makers: tkoyama010

## Context and Problem Statement

[ADR-0013](0013-decision-to-add-a-pi-coding-agent-development-environment-to-github-codespaces.md) adopts a GitHub Codespaces devcontainer for developing pyvista-wasm with the pi coding agent. That devcontainer must install Python (via uv), Node.js (via npm), and pre-commit with all hooks. [Nix](https://nixos.org/) (including [devenv](https://devenv.sh/) and [devbox](https://www.jetify.com/devbox)) can define the whole toolchain declaratively and reproducibly, and Nix-based devcontainer features exist for Codespaces. Should the Codespace environment be built with Nix instead of the plain devcontainer features CI already uses?

## Decision Drivers

- **Reproducibility**: the pi agent should always see the exact tool versions CI sees.
- **Single source of truth**: the repository already pins its toolchain in `uv.lock` and `package-lock.json`; a second, parallel pin format invites drift.
- **Maintenance cost**: pyvista-wasm is a small project; every extra tool in the environment definition is a real ongoing cost.
- **Onboarding friction**: contributors and the pi agent must be able to start without learning a new package manager.
- **CI parity**: [`AGENTS.md`](../../AGENTS.md) promises CI verifies the environment on every PR; the Codespace should reuse the CI install steps, not fork them.

## Considered Options

- **Option A: Use Nix (devenv/devbox) to define the Codespace environment**
- **Option B: Use plain devcontainer features with uv and npm (status quo)**

## Decision Outcome

Chosen option: "**Option B: Use plain devcontainer features with uv and npm (status quo)**", because the lockfiles CI already enforces give the reproducibility Nix would provide, without adding a second package manager to maintain.

- Reproducibility is already covered: `uv.lock`, `package-lock.json`, and pinned pre-commit hook revisions pin every tool version. Nix would pin them a second time in a second format.
- CI runs `uv`, `npm`, and `pre-commit` directly. A Nix-based environment replaces those entry points with Nix wrappers, so the Codespace and CI would diverge in *how* they run the same tools — the exact drift ADR-0013's confirmation step is meant to catch.
- Nix adds a learning curve for every contributor who debugs the environment, and Nix builds inside Codespaces need care (the store lives outside the container filesystem, caches are non-trivial).
- The project has no packages to distribute and no need for hermetic builds beyond what the lockfiles and CI already provide.

### Consequences

- Good, because the Codespace reuses the CI install steps verbatim; one source of truth per toolchain.
- Good, because no contributor needs to learn Nix to fix the environment.
- Good, because Codespace image builds stay simple and fast.
- Bad, because byte-identical environments across machines are not guaranteed the way a Nix store would guarantee them; platform differences (glibc, shell) can still leak in.
- Bad, because if the project later needs hermetic, multi-language pinning beyond lockfiles (e.g. system-level native dependencies for VTK/WASM builds), this decision should be revisited.

### Confirmation

Compliance is confirmed by the absence of Nix files (`flake.nix`, `devenv.nix`, `devbox.json`, `default.nix`) and by the devcontainer installing its toolchain through uv/npm features or the same steps CI runs. If a Nix definition appears under `.devcontainer/` or the repository root without a superseding ADR, this decision is violated.

## Pros and Cons of the Options

### Option A: Use Nix (devenv/devbox) to define the Codespace environment

Nix (possibly via devenv or devbox) defines Python, Node.js, and pre-commit in one declarative, content-addressed environment.

- Good, because environments become byte-for-byte reproducible across machines and over time.
- Good, because one declarative file could replace per-manager lockfiles as the single pin.
- Bad, because it duplicates pinning: `uv.lock` and `package-lock.json` would still exist for CI and local use.
- Bad, because Nix adds a package manager, a language, and a cache layer that every maintainer must understand.
- Bad, because CI does not run Nix today; adopting it in the Codespace forks the environment definition from CI.

### Option B: Use plain devcontainer features with uv and npm (status quo)

The devcontainer installs the toolchain with the same commands CI uses, backed by the existing lockfiles.

- Good, because lockfiles and pinned hook revisions already pin tool versions; reproducibility is adequate.
- Good, because Codespace, local, and CI environments run identical commands.
- Good, because nothing new to learn or maintain beyond the devcontainer file itself.
- Neutral, because system-level dependencies beyond uv/npm's reach would need ad-hoc Dockerfile lines if they ever appear.
- Bad, because cross-platform reproducibility is not bit-exact the way Nix provides.

## More Information

- Prerequisite decision: [ADR-0013 — Decision to add a pi coding agent development environment to GitHub Codespaces](0013-decision-to-add-a-pi-coding-agent-development-environment-to-github-codespaces.md).
- Toolchain pins: `uv.lock`, `package-lock.json`, and the pinned revisions in [`.pre-commit-config.yaml`](../../.pre-commit-config.yaml).
- Revisit triggers: a need for hermetic system-level dependencies (e.g. native toolchains for the VTK/WASM build) that uv and npm cannot pin, or repeated environment drift between Codespace and CI.
