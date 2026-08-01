---
status: accepted
date: 2026-08-01
decision-makers: [tkoyama010]
consulted: []
informed: []
---

# Verify AGENTS.md quality in CI

## Context and Problem Statement

`AGENTS.md` is the system-prompt / instruction file that guides AI coding agents working on pyvista-wasm. Issue [#397](https://github.com/tkoyama010/pyvista-wasm/issues/397) defines a quality checklist for this file — project overview, architecture, dev-environment setup, local build/run commands, testing instructions, code-style conventions, file/directory layout, security guidelines, and contribution workflow — and audits the current file against it. However, quality criteria documented only in an issue are enforced through manual review, which is inconsistent and easy to skip. Regressions — a section accidentally trimmed, a stale command left in, a security guideline removed — can slip through review unnoticed. We need a CI mechanism that automatically verifies `AGENTS.md` against the quality criteria on every PR so that compliance is enforced consistently rather than relying on a reviewer remembering to check. Which approach should we adopt for automated CI verification of `AGENTS.md` quality? (See [#398](https://github.com/tkoyama010/pyvista-wasm/issues/398).)

## Decision Drivers

- **Regression prevention**: Edits to `AGENTS.md` should not silently remove required sections or shrink them below a useful threshold. The mechanism must catch regressions automatically on every PR that touches the file. This is a knock-out criterion.
- **Manual-review burden**: Reviewers should not have to remember a mental checklist of required sections. The CI check should encode the checklist so that a green run means "all required sections are present and adequately filled."
- **Usefulness for AI agents**: The verification must check *content-level* qualities (required sections, minimum content per section), not just *formatting* (line length, trailing whitespace). A file that passes markdownlint but omits the "Security guidelines" section is not useful for agents.
- **Low maintenance overhead**: pyvista-wasm is a small project. The verification mechanism should be easy to maintain and update when the quality criteria evolve (e.g., a new section is added to the checklist in [#397](https://github.com/tkoyama010/pyvista-wasm/issues/397)).
- **Integration with existing CI**: The mechanism should fit naturally alongside the existing GitHub Actions workflows (`.github/workflows/test.yml`) and pre-commit.ci pipeline without requiring heavyweight infrastructure.

## Considered Options

- **Option A: Custom CI job with a quality-check script** — a dedicated GitHub Actions job runs a script (e.g., Python) that parses `AGENTS.md` and asserts required sections exist with minimum content per section
- **Option B: Existing linter with custom rules** — extend markdownlint (or a community agent-instruction validator) with custom rules that check for required headings and minimum content
- **Option C: Pre-commit hooks only** — rely solely on the existing pre-commit.ci hooks (mdformat, codespell, etc.) without any content-level checks

## Decision Outcome

Chosen option: **Option A — Custom CI job with a quality-check script**, because it is the only option that satisfies the knock-out criterion of *content-level* verification. The script can assert that each required section from the [#397](https://github.com/tkoyama010/pyvista-wasm/issues/397) checklist (Project overview, Architecture, Dev environment, Testing instructions, Test conventions, Issue instructions, PR instructions, Code-style conventions, File/directory layout, Security guidelines) is present as a Markdown heading and contains a minimum number of words or bullet points. markdownlint (Option B) is designed for formatting rules, not semantic content checks; writing a custom markdownlint plugin for "heading X must have ≥ N words" is more complex than a standalone script. Pre-commit hooks alone (Option C) verify formatting only and cannot detect a missing section. A custom script is also easy to maintain — updating the checklist means editing one Python file — and integrates naturally as a step in the existing `test.yml` workflow or a lightweight standalone workflow.

### Consequences

- Good, because every PR that touches `AGENTS.md` is automatically checked for section completeness and minimum content, preventing silent regressions.
- Good, because the quality checklist is encoded in code rather than existing only in an issue thread, making it executable and self-documenting.
- Good, because the script is a single Python file that is easy to read, update, and test, keeping maintenance overhead low for a small project.
- Good, because a CI failure produces an actionable message (e.g., "Section 'Security guidelines' is missing" or "Section 'Testing instructions' has fewer than 20 words") that tells the contributor exactly what to fix.
- Bad, because the script introduces a small amount of custom infrastructure that must be maintained alongside the quality criteria.
- Bad, because a word-count threshold is a proxy for quality, not quality itself — a section can meet the minimum word count yet still be unhelpful. The check catches structural regressions, not prose quality.
- Neutral, because the script runs in CI only; local pre-commit hooks continue to handle formatting, so contributors do not need to install the checker locally unless they want to.

### Confirmation

Compliance with this decision will be confirmed by:

1. A Python script (e.g., `ci/check_agents_md.py`) exists in the repository and parses `AGENTS.md` to verify that every required section heading is present.
2. The script asserts a minimum content threshold (e.g., minimum word count or bullet count) for each required section so that empty or stub sections fail the check.
3. A GitHub Actions workflow (either a step in `.github/workflows/test.yml` or a dedicated workflow file) runs the script on every PR that touches `AGENTS.md`.
4. A PR that removes a required section or shrinks it below the minimum threshold causes the CI job to fail with a message naming the offending section.
5. The script's required-sections list mirrors the quality checklist defined in [#397](https://github.com/tkoyama010/pyvista-wasm/issues/397) and can be updated in one place when the checklist evolves.

## Pros and Cons of the Options

### Option A: Custom CI job with a quality-check script

A dedicated Python script (e.g., `ci/check_agents_md.py`) parses `AGENTS.md`, checks that each required section heading exists, and asserts a minimum content threshold per section. The script runs as a step in the existing `test.yml` workflow or a standalone workflow on every PR touching `AGENTS.md`.

- Good, because it performs *content-level* verification — required sections, minimum content — which is the knock-out criterion that the other options cannot meet.
- Good, because the failure message is actionable: the script can print "Section 'Security guidelines' is missing" or "Section 'Testing instructions' has 5 words; minimum is 20," telling the contributor exactly what to fix.
- Good, because the required-sections list and thresholds live in a single Python file that is trivial to update when the [#397](https://github.com/tkoyama010/pyvista-wasm/issues/397) checklist evolves.
- Good, because a Python script can be unit-tested (e.g., feed it a fixture `AGENTS.md` with a missing section and assert the script exits non-zero), giving confidence that the checker itself works.
- Good, because it integrates naturally with the existing GitHub Actions setup — a `run: python ci/check_agents_md.py` step alongside the existing lint and test jobs.
- Neutral, because the script is custom infrastructure that must be maintained, but the scope is small (one file, a list of sections, a word-count threshold).
- Bad, because a word-count threshold is a proxy: a section can meet the minimum yet still be low quality. The check catches structural regressions, not prose quality.
- Bad, because the script is project-specific and not reusable across other repositories without modification.

### Option B: Existing linter with custom rules

Extend markdownlint (already run via pre-commit.ci through mdformat) or adopt a community agent-instruction validator (e.g., a tool from the [agents.md](https://agents.md/) ecosystem) with custom rules that check for required headings and minimum content.

- Good, because it reuses the existing markdownlint / pre-commit infrastructure, so no new CI job is needed.
- Good, because markdownlint is well-maintained and widely understood by contributors.
- Neutral, because markdownlint's rule DSL is designed for formatting (line length, heading style, blank lines), not semantic content checks.
- Bad, because writing a custom markdownlint plugin for "heading 'Security guidelines' must exist and contain ≥ N words" is significantly more complex than a standalone Python script — the rule API is not designed for content thresholds.
- Bad, because no mature, community-maintained validator for AI-agent instruction files exists at the time of this decision; the [agents.md](https://agents.md/) ecosystem is nascent and does not offer a linter with configurable quality criteria.
- Bad, because coupling content-level checks to markdownlint blurs the line between formatting (markdownlint's job) and content (the quality checklist's job), making the linting configuration harder to reason about.

### Option C: Pre-commit hooks only

Rely solely on the existing pre-commit.ci hooks — mdformat, codespell, standard-readme, etc. — without adding any content-level checks. Formatting and spelling are verified; section completeness is left to manual review.

- Good, because it requires zero additional work — the hooks already run on every PR via pre-commit.ci.
- Good, because it avoids introducing any custom infrastructure.
- Neutral, because the existing hooks already catch formatting issues in `AGENTS.md` (mdformat normalises Markdown, codespell catches typos).
- Bad, because it fails the knock-out criterion: pre-commit hooks verify *formatting*, not *content*. A PR that deletes the "Security guidelines" section entirely would pass all hooks.
- Bad, because it leaves section-completeness verification to manual review, which is exactly the inconsistent, skip-prone process that [#398](https://github.com/tkoyama010/pyvista-wasm/issues/398) seeks to replace.
- Bad, because it does not encode the [#397](https://github.com/tkoyama010/pyvista-wasm/issues/397) quality checklist in any executable form, so the criteria remain advisory rather than enforced.

## More Information

### Links

- Parent issue: [#397](https://github.com/tkoyama010/pyvista-wasm/issues/397) (verify AGENTS.md against standard quality criteria and improve where gaps exist)
- This decision: [#398](https://github.com/tkoyama010/pyvista-wasm/issues/398) (create ADR for CI verification of AGENTS.md quality)
- Related: [ADR-0000](0000-use-markdown-architectural-decision-records.md) (established the ADR process and `docs/decisions/` convention)
- Agent-instruction best practices: [https://agents.md/](https://agents.md/), [https://google.github.io/agents-in-repo/](https://google.github.io/agents-in-repo/)
