# Project Context

## Purpose
This package provides foundational class factories and decorators for providing classes with attribute immutability, concealment, and other custom behaviors. It aims to make Python programs safer by encouraging immutability and controlled attribute access, while integrating seamlessly with standard Python features like dataclasses and protocols.

## Tech Stack
- **Languages**: Python 3.10+
- **Build System**: Hatch
- **Package Management**: uv (recommended installation), pip
- **Testing**: pytest, coverage
- **Linting/Formatting**: ruff, isort, pyright, vulture
- **Documentation**: Sphinx, dynadoc
- **Release**: towncrier

## Project Conventions

### Code Style
- **Line Length**: 79 characters.
- **Imports**: Sorted by `isort` with specific configuration (see `pyproject.toml`).
- **Linting**: Enforced by `ruff` and `pyright`.
- **Typing**: Strict type checking with `pyright`.
- **Import Hub Pattern**: Centralized import management via `sources/classcore/__/`.

### Architecture Patterns
- **Metaclass & Decorator Factories**: Use of factory functions to produce metaclass components and decorators.
- **Composable Behaviors**: Behaviors are applied via composable decorators and metaclasses.
- **Verifier Pattern**: Use of verifiers (names, regexes, predicates) for behavior configuration.
- **Core Function Replacement**: Dependency injection for core behaviors.
- **Module Reclassification**: Applying class behaviors to modules.
- See [System Overview](../summary.rst) for a comprehensive architectural summary.

### Filesystem Organization
- The project follows a strict filesystem organization pattern.
- See [Filesystem Organization](../filesystem.rst) for detailed conventions.
- **Source**: `sources/classcore/`
- **Tests**: `tests/`
- **Docs**: `documentation/`
- **Dev**: `.auxiliary/`

### Testing Strategy
- **Runner**: `pytest`
- **Coverage**: Strict coverage requirements enforced.
- **Structure**: Tests located in `tests/`, files named `test_*.py`.
- **Naming**: Test functions named `test_[0-9][0-9][0-9]_*`.

### Git Workflow
- **Changelog**: Managed by `towncrier` with fragments in `.auxiliary/data/towncrier`.
- **Commit Messages**: Should align with `towncrier` categories (enhance, notify, remove, repair).
- **Versioning**: Managed by Hatch.

## Domain Context
- **Immutability in Python**: Python does not support true immutability. This library provides "advisory" immutability that can be circumvented but prevents accidental modification.
- **Metaprogramming**: Heavy use of metaclasses (`__new__`, `__init__`) and decorators.
- **Mangled Names**: Use of SHA-256 for name mangling to avoid collisions.

## Important Constraints
- **Python Version Compatibility**: Must support Python 3.10 through 3.14 (and PyPy).
- **Performance**: Runtime overhead must be minimized; import costs centralized.

## External Dependencies
- **Standard Library**: `dataclasses`, `typing`, `functools`, `inspect`, etc.
- **Runtime**: `dynadoc`, `typing-extensions`.
