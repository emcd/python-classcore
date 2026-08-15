# Project Guidance

Project-owned knowledge the generated `AGENTS.md` entrypoint must not own.
Structured tracking stays in `nb`.

## Purpose

classcore provides class construction infrastructure for Python: metaclasses
and base classes that apply standard behaviors — immutability and concealment —
with integrated dataclass, protocol, and abstract base class support. The
standard taxonomy unifies `Class`-rooted metaclasses (including
`AbstractClass` and `ProtocolClass`) and `*Object` base classes so
behaviorally-rich classes mix cleanly with stdlib `abc` and
`typing.Protocol` machinery without metaclass conflicts.

## Tech Stack

- Python >= 3.10, pure Python (no C extensions), sources under
  `sources/classcore/`
- Hatch for build and environments; full validation gate is
  `hatch --env develop run make-all`
- pytest with a 100% coverage requirement, pyright, ruff, vulture
- Towncrier news fragments in `.auxiliary/data/towncrier/`
- OpenSpec (OPSX) for specs and change proposals; `nb` and `agentmux` MCP
  for notes and coordination

## Notes

- Architecture and design docs: `documentation/architecture/`
- Release process: `.auxiliary/agents/standards/releases.rst`
- Team org, role ownership, and rolling handoff: `coordination/general/1`
  (nb note)
- Use `hatch run python ...`, never bare `python`.
- All stdlib and third-party imports flow through the import hub
  `sources/classcore/__/imports.py`; `__.typx` is the typing_extensions
  superset — do not import `typing` separately in sources (tests may).
- Nomenclature: metaclasses are named `<Purpose>Class`, bases `*Object`;
  avoid compound underscore-separated parameter names in favor of simple
  Latin-derived names.
- Every standard metaclass needs `@_class_factory()`; a child metaclass
  `__new__` stub without it shadows the inherited injected `__new__` and
  silently drops decoration.
- Downstream consumers: Accretive, Frigid — verify before public API
  changes.
