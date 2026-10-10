# Decide whether to use QA Orchestra for QA review of pull requests

* Status: proposed
* Date: 2026-09-27
* Decision-makers: tkoyama010

## Context and Problem Statement

pyvista-wasm verifies every pull request with a full CI test suite (pytest with pytest-cov and pytest-playwright), pre-commit.ci linting, Read the Docs previews, and AGENTS.md quality checks (see [ADR-0005](0005-verify-agents-md-quality-in-ci.md)). These checks answer "does the code pass?" but nothing in the repository answers QA questions such as: does this diff actually implement the stated intent, which existing tests should have caught this change, and what user-visible scenarios are missing? [QA Orchestra](https://qa-orchestra.com/) ([GitHub](https://github.com/anasss/qa-orchestra)) is a Claude Code plugin of ten specialized QA agents that answer exactly these questions per pull request and write a Markdown report (e.g. `qa-output/functional-review.md`) that can be pasted into GitHub. Should we adopt QA Orchestra as part of the pyvista-wasm review process?

## Decision Drivers

- **Fit with the existing review flow**: The repository's authoritative checks are automated CI gates; any QA addition must complement, not replace or gate on top of, the pytest suite.
- **Agent runtime compatibility**: The Codespace development environment is built around the pi coding agent ([ADR-0013](0013-decision-to-add-a-pi-coding-agent-development-environment-to-github-codespaces.md)), while QA Orchestra is Claude Code-first and only best-effort on other runtimes that honor `AGENTS.md`.
- **Acceptance-criteria dependency**: QA Orchestra's core agents (diff vs AC analysis, functional review) require written acceptance criteria per change; the repository does not currently maintain ACs in issues or PRs.
- **Low overhead**: Adding a plugin must not require new CI infrastructure, services, or mandatory review steps for every contributor.
- **Institutional memory**: Findings should persist in Git rather than evaporate with a chat session.

## Considered Options

- **Adopt QA Orchestra as an opt-in, non-gating QA review layer**
- Adopt QA Orchestra as a required QA gate on every pull request
- Keep the status quo (CI suite, pre-commit, AGENTS.md checks only)
- Add a hand-written QA checklist to the pull request template

## Decision Outcome

Chosen option: "**Adopt QA Orchestra as an opt-in, non-gating QA review layer**", because it adds the missing QA perspective (intent coverage, scenario gaps, test selection) at near-zero infrastructure cost, while keeping it opt-in avoids blocking contributors on a Claude Code-first plugin that runs only best-effort in the repository's pi-based environment. We run it manually on significant pull requests (user-visible behavior, WASM/runtime, CLI) and evaluate the reports after a trial period before deciding whether to promote, keep opt-in, or drop it.

### Consequences

- Good, because QA questions (does the diff implement the intent? which scenarios are missing?) get a structured, per-PR answer instead of relying on reviewer memory.
- Good, because reports are plain Markdown files (`qa-output/`) that can be pasted directly into GitHub PRs and live alongside the code.
- Good, because the learning loop (findings written to `context/annotations/` as Markdown) compounds in Git across sessions, matching the repository's plain-text, version-controlled conventions.
- Good, because nothing changes for contributors who do not opt in: CI, pre-commit, and Read the Docs flows are untouched.
- Bad, because QA Orchestra is Claude Code-first; on the pi coding agent it works only best-effort through `AGENTS.md`, so report quality may vary.
- Bad, because its most valuable agents depend on acceptance criteria that the repository does not yet write; until ACs exist, agents answer weaker questions.
- Bad, because `qa-output/` artifacts could clutter the tree; they must be gitignored or pasted into the PR description and deleted.
- Neutral, because the pytest suite remains the only merge gate; QA Orchestra output is advisory.

## Pros and Cons of the Options

### Adopt QA Orchestra as an opt-in, non-gating QA review layer

Run selected QA agents manually on significant pull requests; their Markdown reports inform review and PR descriptions but never gate merges.

- Good, because it delivers the QA perspective with zero new CI infrastructure.
- Good, because it can be evaluated against real pull requests before any commitment.
- Neutral, because it works through the plugin's `AGENTS.md` support rather than as a first-class pi integration.
- Bad, because opt-in usage means inconsistent QA coverage across pull requests.

### Adopt QA Orchestra as a required QA gate on every pull request

Wire the QA agents into CI and block merges until the report is clean.

- Good, because every pull request gets the same QA scrutiny.
- Bad, because the plugin is Claude Code-first and has no supported CI story; faking a gate from best-effort agent output produces flaky, unactionable blocking checks.
- Bad, because blocking merges on advisory LLM output conflicts with the repository's deterministic-gates philosophy (pytest, pre-commit).

### Keep the status quo (CI suite, pre-commit, AGENTS.md checks only)

- Good, because the current gates are deterministic, fast, and already trusted.
- Bad, because nothing in the flow checks whether a diff implements the stated intent or which scenarios and tests it should have touched — the questions QA review exists to answer.

### Add a hand-written QA checklist to the pull request template

- Good, because a checklist is free, runtime-agnostic, and needs no plugin.
- Bad, because checklists shift effort to every contributor and still do not analyze the diff, select tests, or design scenarios.

## More Information

- [QA Orchestra](https://qa-orchestra.com/) — project site; [GitHub repository](https://github.com/anasss/qa-orchestra); [the learning loop](https://qa-orchestra.com/learning-loop)
- [ADR-0005](0005-verify-agents-md-quality-in-ci.md) — AGENTS.md quality is verified in CI, so the `AGENTS.md` QA Orchestra relies on is already guarded.
- [ADR-0013](0013-decision-to-add-a-pi-coding-agent-development-environment-to-github-codespaces.md) — the pi coding agent environment this decision must fit into.
- Revisit this decision after the trial period (a handful of significant pull requests): promote to a documented step, keep opt-in, or reject with the findings recorded here.
