# Decide to use pytest-bdd for behavior-driven tests

* Status: proposed
* Date: 2026-07-19
* Decision-makers: tkoyama010

## Context and Problem Statement

pyvista-wasm already has an extensive pytest suite covering the Python-facing PyVista API, CLI commands, and browser rendering (via pytest-playwright). As the project grows, some tests describe user-visible behavior — "when the user creates a sphere, then a mesh with the expected bounds exists", "when the user captures a screenshot, then the browser renders the scene" — and the scenario nature of these tests is currently implicit in class- and function-named tests. Behavior-driven development (BDD) makes such scenarios explicit, executable specifications that non-programmers (designers, product owners, documentation readers) can read and review. Should we adopt a BDD layer on top of pytest, and if so, which tool?

## Decision Drivers

- **Executable specifications**: Scenarios should be readable by non-programmers and reviewable in PRs, written in Gherkin (Given/When/Then).
- **Single test runner**: The project already standardizes on pytest (with pytest-cov, pytest-playwright). A second runner would split CI, fixtures, and reporting.
- **Fixture reuse**: Scenario steps must be able to reuse the existing pytest fixtures (`mesh_factory`, Playwright page fixtures, etc.).
- **Low overhead**: pyvista-wasm is a small project; adopting BDD must not add a parallel test architecture or significant maintenance cost.
- **Maintenance**: The tool should be actively maintained and compatible with current pytest versions.

## Considered Options

- [pytest-bdd](https://pytest-bdd.readthedocs.io/en/stable/) — Gherkin feature files driven by pytest fixtures
- [behave](https://behave.readthedocs.io/en/stable/) — Standalone BDD framework with its own runner
- Plain pytest (status quo) — Keep describing scenarios in test function and class names only

## Decision Outcome

Chosen option: "pytest-bdd", because it runs Gherkin scenarios inside pytest itself — the project keeps one runner, one fixture model, and one CI pipeline. Existing pytest fixtures and plugins (pytest-playwright, pytest-cov) work in scenario steps without any bridging, and feature files make user-visible behavior reviewable by non-programmers. behave is rejected because it requires a second runner and re-implementing the fixture model, and the status quo is rejected because scenario intent remains implicit as the suite grows.

### Consequences

- Good, because feature files (`.feature`) become living documentation of user-visible behavior, reviewable in the normal PR flow.
- Good, because steps reuse existing pytest fixtures and plugins directly — no bridge layer needed.
- Good, because pytest-cov and pytest-playwright keep working unchanged; CI configuration does not fork.
- Bad, because contributors must learn Gherkin syntax and the step-definition mapping.
- Bad, because scenarios that are pure unit checks (e.g. numeric bounds of `Sphere`) gain nothing from Gherkin; the team must judge where BDD applies.
- Neutral, because pytest-bdd is a pytest plugin, not a runner: if the decision is revisited, feature files and steps migrate easily.

### Confirmation

Review PRs for new user-visible behavior: scenarios for such behavior should be added as `.feature` files with pytest-bdd step definitions under `tests/`, while pure unit tests stay as plain pytest. CI continues to run the full suite on every PR, so any feature file that fails to parse or run fails the build.

## Pros and Cons of the Options

### pytest-bdd

[Gherkin](https://cucumber.io/docs/gherkin/reference/) feature files executed by pytest via `scenarios()` and step-decorated fixtures.

- Good, because it is a pytest plugin: one runner, one fixture model, one CI pipeline.
- Good, because steps are plain pytest fixtures, so `mesh_factory` and Playwright page fixtures are directly usable.
- Good, because pytest-cov measures coverage of scenario-driven code automatically.
- Neutral, because the Gherkin parser is limited to cucumber's core keywords (no complex tag expressions beyond standard support).
- Bad, because feature files and step definitions live in separate files, adding one indirection.

### behave

Standalone BDD framework with its own runner and environment model.

- Good, because it is mature, well documented, and runner-independent of pytest.
- Bad, because it requires a second test runner: separate CI invocation, separate reporting, separate fixture model.
- Bad, because behave's context object is not pytest fixtures, so existing fixtures would need duplication or adapters.

### Plain pytest (status quo)

Keep describing behavior through class names like `TestCreateGif` and parametrized test functions.

- Good, because there is no new tool, syntax, or indirection to learn.
- Bad, because scenario intent stays implicit; non-programmers cannot review behavior without reading Python.
- Bad, because as the suite grows, the same Given/When/Then structure is re-encoded inconsistently in test names, docstrings, and comments.

## More Information

- pytest-bdd documentation: <https://pytest-bdd.readthedocs.io/en/stable/>
- The project's test conventions in `AGENTS.md` (class-per-function grouping) continue to apply to plain pytest tests; BDD scenarios are reserved for user-visible behavior.
- Adoption is incremental: existing tests are not rewritten; new user-visible scenarios may use feature files.
