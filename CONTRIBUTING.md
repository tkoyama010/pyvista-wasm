# Contributing to pyvista-wasm

Thank you for your interest in contributing to pyvista-wasm! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

<!-- mdformat-toc start --slug=github --no-anchors --maxlevel=6 --minlevel=2 -->

- [Table of Contents](#table-of-contents)
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
  - [Prerequisites](#prerequisites)
  - [Initial Setup](#initial-setup)
- [Development Workflow](#development-workflow)
  - [Creating a Branch](#creating-a-branch)
  - [Making Changes](#making-changes)
  - [Committing Changes](#committing-changes)
- [Code Quality Standards](#code-quality-standards)
- [TypeScript Development](#typescript-development)
  - [Setup](#setup)
  - [Building](#building)
- [Testing](#testing)
  - [Running Tests](#running-tests)
  - [Writing Tests](#writing-tests)
  - [Test Requirements](#test-requirements)
- [Pull Request Process](#pull-request-process)
  - [Before Submitting](#before-submitting)
  - [Submitting a Pull Request](#submitting-a-pull-request)
  - [PR Requirements](#pr-requirements)
  - [Continuous Integration](#continuous-integration)
- [Types of Contributions](#types-of-contributions)
  - [Code Contributions](#code-contributions)
  - [Documentation](#documentation)
  - [Community](#community)
  - [Recognition](#recognition)
- [Scientific Python Standards](#scientific-python-standards)
- [Community Resources](#community-resources)
- [Questions?](#questions)

<!-- mdformat-toc end -->

## Code of Conduct

This project adheres to the [Contributor Covenant 3.0](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [@tkoyama010](https://github.com/tkoyama010).

## Getting Started

pyvista-wasm is a PyVista-like API for VTK.wasm that brings intuitive 3D visualization to the browser using WebAssembly. Before contributing:

1. Check the [issue tracker](https://github.com/tkoyama010/pyvista-wasm/issues) for existing issues or create a new one
1. Read through the [README](https://github.com/tkoyama010/pyvista-wasm#readme)

## Development Setup

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

### Prerequisites

- Python 3.12 or higher (3.12, 3.13, or 3.14 recommended for testing)
- [uv](https://github.com/astral-sh/uv) - Ultra-fast Python package installer
- Git

### Initial Setup

1. Fork the repository on GitHub

1. Clone your fork:

   ```bash
   git clone https://github.com/YOUR-USERNAME/pyvista-wasm.git
   cd pyvista-wasm
   ```

1. Install uv if you haven't already:

   ```bash
   # On macOS and Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # On Windows
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

1. Install development dependencies:

   ```bash
   uv sync --group dev
   ```

1. Install pre-commit hooks:

   ```bash
   uv run pre-commit install
   ```

1. Install Playwright browsers (required for browser tests):

   ```bash
   uv run playwright install chromium
   ```

## Development Workflow

[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-%23FE5196?logo=conventionalcommits&logoColor=white)](https://conventionalcommits.org)

### Creating a Branch

Create a descriptive branch name:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

### Making Changes

1. Make your changes in the appropriate files
1. Write or update tests as needed
1. Update documentation if necessary
1. Run pre-commit checks (happens automatically on commit, or manually with `uv run pre-commit run --all-files`)

### Committing Changes

This project uses [Conventional Commits](https://www.conventionalcommits.org/). Your commit messages should follow this format:

```
type(scope): description

[optional body]

[optional footer]
```

Common types:

- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools

Example:

```bash
git commit -m "feat(plotter): add support for physically based rendering"
```

## Code Quality Standards

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/tkoyama010/pyvista-wasm/main.svg)](https://results.pre-commit.ci/latest/github/tkoyama010/pyvista-wasm/main)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![djlint](https://img.shields.io/badge/html%20templates-djLint-blueviolet.svg)](https://www.djlint.com)
[![Biome](https://img.shields.io/badge/code_style-Biome-60A5FA.svg)](https://biomejs.dev)

The project uses pre-commit hooks to ensure code quality.

## TypeScript Development

The JavaScript renderer (`src/pyvista_wasm/templates/renderer.js`) is generated from TypeScript source at `ts/renderer.ts`. Node.js is only required when editing TypeScript files.

### Setup

```bash
npm install
```

### Building

```bash
# One-time build
npm run build

# Watch mode (auto-rebuild on save)
npm run watch

# Type check only (no output)
npm run typecheck
```

The built `renderer.js` is not committed to git. It is generated automatically during `python -m build` via `hatch-build-scripts`. For local development, run `npm run build` after editing TypeScript files.

## Testing

[![codecov](https://codecov.io/gh/tkoyama010/pyvista-wasm/branch/main/graph/badge.svg)](https://codecov.io/gh/tkoyama010/pyvista-wasm)

### Running Tests

```bash
# Run all tests
uv run pytest

# Run tests for specific Python version using tox
uv run tox -e py312
uv run tox -e py313
uv run tox -e py314

# Run tests without Playwright tests
uv run pytest -m "not playwright"

# Run with coverage
uv run pytest --cov=pyvista_wasm --cov-report=html
```

### Writing Tests

- Place tests in the `tests/` directory
- Use `pytest` for test framework
- Follow existing test patterns
- Include tests for new features and bug fixes
- Browser-based tests use `playwright` and should be marked with `@pytest.mark.playwright`

### Test Requirements

- All new features should include tests
- Bug fixes should include regression tests
- Maintain or improve code coverage
- Tests should pass on Python 3.12, 3.13, and 3.14

## Pull Request Process

### Before Submitting

1. Ensure all tests pass locally
1. Run pre-commit hooks: `uv run pre-commit run --all-files`
1. Update documentation if needed
1. Add yourself to the contributors list (maintainers will help with this)

### Submitting a Pull Request

1. Push your changes to your fork
1. Create a pull request against the `main` branch
1. Use a descriptive PR title following [Conventional Commits](https://www.conventionalcommits.org/) format:
   - `feat: add new visualization feature`
   - `fix: resolve rendering issue in Safari`
   - `docs: update installation instructions`
1. Fill out the pull request template
1. Link any related issues (e.g., "Closes #123")
1. Wait for review and address any feedback

### PR Requirements

- **Conventional Commits**: PR title must follow conventional commits format
- **Tests**: All tests must pass (checked by CI)
- **Pre-commit**: All pre-commit checks must pass (pre-commit.ci will auto-fix some issues)
- **Coverage**: Code coverage should not decrease
- **Documentation**: Update documentation for new features

### Continuous Integration

Pull requests are automatically tested using GitHub Actions:

- Linting and formatting checks
- Tests on Python 3.12, 3.13, and 3.14
- Tests on Linux, Windows, and macOS
- Code coverage reporting to Codecov
- Conventional commit PR title validation

## Types of Contributions

We welcome various types of contributions:

### Code Contributions

- New features
- Bug fixes
- Performance improvements
- Code refactoring

### Documentation

- Improving existing documentation
- Adding examples and tutorials
- Fixing typos and clarifications

### Community

- Reporting bugs
- Suggesting new features
- Reviewing pull requests
- Creating demos and examples

### Recognition

All contributions are recognized using [all-contributors](https://allcontributors.org/). Contributions include:

- Code
- Documentation
- Ideas and planning
- Bug reports
- Tests
- Review
- Packaging

## Scientific Python Standards

[![SPEC 0 — Minimum Supported Dependencies](https://img.shields.io/badge/SPEC-0-green?labelColor=%23004811&color=%235CA038)](https://scientific-python.org/specs/spec-0000/)
[![SPEC 1 — Lazy Loading of Submodules and Functions](https://img.shields.io/badge/SPEC-1-green?labelColor=%23004811&color=%235CA038)](https://scientific-python.org/specs/spec-0001/)
[![SPEC 4 — Nightly Tests](https://img.shields.io/badge/SPEC-4-green?labelColor=%23004811&color=%235CA038)](https://scientific-python.org/specs/spec-0004/)
[![SPEC 8 — Securing the Release Process](https://img.shields.io/badge/SPEC-8-green?labelColor=%23004811&color=%235CA038)](https://scientific-python.org/specs/spec-0008/)

This project follows several [Scientific Python SPECs](https://scientific-python.org/specs/).

## Community Resources

- **Issues**: [GitHub Issues](https://github.com/tkoyama010/pyvista-wasm/issues)

## Questions?

If you have questions about contributing, feel free to:

- Check existing [issues](https://github.com/tkoyama010/pyvista-wasm/issues)
- Open a new [issue](https://github.com/tkoyama010/pyvista-wasm/issues/new)

Thank you for contributing to pyvista-wasm!
