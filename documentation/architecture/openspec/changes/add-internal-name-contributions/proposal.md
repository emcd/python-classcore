## Why

`explain_attribute` marks internal names using a hardcoded pair: the
classcore prefix and the ABC machinery set. Downstream frameworks built
on classcore (Accretive, Frigid) produce identically structured internal
attributes (`_accretive_*`, `_frigid_*` via their `calculate_attrname`
namers), so explaining a downstream class today makes false statements
about the nature of downstream attributes. The explanation API is only
as truthful as its knowledge of the ecosystem, and responsibility for
knowing a framework's names belongs with that framework's machinery.

## What Changes

Replace global name matching with metaclass-carried internal-name
contributions:

- Internal-name knowledge attaches at metaclass/factory decoration
  time — the classcore prefix rides classcore's factory wiring, the ABC
  set rides the `AbstractClass`/`ProtocolClass` wiring (mirroring how
  enforcement already scopes `class_mutables` per metaclass), and
  downstream prefixes ride their `class_factory`-produced metaclasses
  via namer-provided detectors.
- `explain_attribute` and `is_internal_name(target, name)` consult the
  target's metaclass MRO for contributions; decorator-path classes
  (built by plain `type`) carry their contribution on the class itself
  and are consulted through the class resolution order. No public
  factory or decorator argument is added.
- `_dynadoc_fragments_` is never marked internal: it is a documented,
  user-settable declaration convention, analogous to `__slots__`.
- No global registry: no shared store, no locking, no injection
  parameter. A global fixed-name fallback tier remains possible later
  and additive if a real non-classcore-attached consumer appears.

Resolved by construction: a non-ABC class defining `_abc_cache` sees it
unmarked (no ABC contribution in its metaclass chain), and a class in
one package deriving from another framework's base inherits that
framework's contribution via the metaclass.

## Capabilities

### New Capabilities
<!-- None. -->

### Modified Capabilities
- `attribute-explanations`: Internal Attribute Marking requirement is
  modified — marking is determined by metaclass-carried contributions
  rather than hardcoded name sources, and the public declaration
  convention `_dynadoc_fragments_` is excluded.

## Impact

- `sources/classcore/standard/explanations.py`: `is_internal_name`
  gains a target parameter and consults metaclass contributions.
- `sources/classcore/factories.py` and/or `standard/decorators.py`:
  contribution wiring at factory/decoration time.
- `sources/classcore/standard/classes.py`: ABC contribution on
  `AbstractClass` wiring.
- Namer convention: optional detector exposed by `calculate_attrname`
  namers (classcore's own annotated as the model implementation).
- Tests: non-ABC `_abc_cache`, multi-package inheritance, digest-suffix
  shape validation, `_dynadoc_fragments_` exclusion.
- README and a towncrier fragment.

Timing note: `is_internal_name` gains a target parameter — a signature
change that is free only while explanations have not shipped; this
change targets the 1.13 pre-release window.
