## Context

Python resolves the metaclass of a new class by taking the most derived
metaclass among its bases, requiring that metaclass to be a (non-strict)
subclass of every base's metaclass. The check lives in `type.__new__`
and uses C-level MRO subtype tests — `__subclasscheck__` overrides on
candidate metaclasses are ignored. Consequently the only clean way to
make two metaclass families compatible is genuine inheritance.

Today `Class → type` and `abc.ABCMeta → type` are siblings, so
`class Foo( classcore.Object, SomeABC )` raises `TypeError: metaclass
conflict`. Likewise `ProtocolClass → _ProtocolMeta → ABCMeta` never
passes through `Class`, so protocol bases cannot mix with ordinary
classcore classes.

## Goals / Non-Goals

- Goals:
  - Allow `class Foo( classcore.AbstractObject, SomeABC )` without
    metaclass conflict, preserving standard behaviors.
  - Preserve abstract method enforcement and virtual subclass
    registration (`register()`, `isinstance()` on registered classes).
  - Keep `Class`-backed classes free of ABC machinery (opt-in only).
  - Unify the metaclass taxonomy: `ProtocolClass` becomes a descendant
    of `Class`, enabling `class Foo( classcore.Protocol,
    classcore.Object )`.
- Non-Goals:
  - Making `Class` itself an `ABCMeta` descendant — would impose the ABC
    contract (registration caches, `__instancecheck__` machinery) on
    every classcore class.
  - Mutable or dataclass abstract variants (`AbstractObjectMutable`,
    `AbstractDataclassObject`) — natural follow-ups once the minimal pair
    proves itself.
  - Auto-reconciliation of conflicting metaclasses by synthesizing
    combined metaclasses at class creation — implicit magic that
    manufactures unlisted metaclasses, contrary to the package's
    explicit-everything philosophy.

## Decisions

### Decision 1: Opt-in diamond metaclass

```python
@_class_factory( )
class AbstractClass( Class, __.abc.ABCMeta ): ...

class AbstractObject(
    metaclass = AbstractClass,
    class_mutables = _abc_class_mutables,
): ...
```

C3 linearization is consistent:
`AbstractClass → Class → ABCMeta → type → object`. Verified empirically:
mixed-base creation with an external ABC succeeds, abstract method
enforcement raises `TypeError` on instantiation of incomplete classes,
and `register()` plus `isinstance()` behave correctly.

- Alternatives considered:
  - `Class( ABCMeta )`. Rejected — changes the contract of `Class`;
    every ordinary class would carry ABC machinery.
  - Intercepting construction to synthesize a combined metaclass.
    Rejected — `type.__new__` performs the conflict check with C-level
    subtype tests that bypass `__subclasscheck__`, and manufacturing
    unlisted metaclasses is implicit magic.
  - Naming `ABCFactory`. Rejected — every metaclass in the family is
    named `<Purpose>Class` (`Class`, `ProtocolClass`); `AbstractClass`
    follows the convention, as `AbstractObject` follows `*Object`.

### Decision 2: `class_mutables` on `AbstractObject`

CPython's C `_abc` module updates the registration caches (`_abc_registry`,
`_abc_cache`, `_abc_negative_cache`) via direct dictionary writes that
bypass metaclass `__setattr__`, so `register()` happens to work without
exemptions on CPython. The pure-Python fallback (`_py_abc`) used by some
interpreters assigns via `setattr`, which classcore immutability would
block. `class_mutables = _abc_class_mutables` (the existing tuple, already
extended for `runtime_checkable`) is cheap, defensive, and consistent
with the four protocol base classes. It also propagates to subclasses
through MRO attribute lookup.

### Decision 3: `ProtocolClass` re-parenting

```python
@_class_factory( )
class ProtocolClass( AbstractClass, type( __.typx.Protocol ) ): ...
```

MRO becomes
`ProtocolClass → AbstractClass → Class → _ProtocolMeta(te) →
_ProtocolMeta(typing) → ABCMeta → type → object`.

This is enabled by the wrapper-level delegation from
`update-protocol-recognition`: parent-metaclass wrappers on the chain
(`AbstractClass`, `Class`) see the closure/context mismatch and delegate
directly to the next `__new__`/`__init__`, so construction hooks and
decorators still execute exactly once (verified with a recording
decorator through the three-level hierarchy). `ProtocolClass` must keep
`@_class_factory( )`; a body-defined `__new__` stub without factory
application shadows the inherited injected `__new__` and silently
bypasses decoration (observed in prototyping).

Out of scope: directly inheriting a protocol definition base together
with an ordinary base (e.g., `class Foo( Protocol, Object )`). Empirical
finding: `typing_extensions._ProtocolMeta.__new__` rejects ordinary
bases when `typing.Protocol` is a *direct* base ("Protocols can only
inherit from other protocols"), and metaclass unification does not lift
that rule. Intermediating through a classcore protocol base technically
bypasses the direct-base check (the class is creatable), but the result
is a protocol definition carrying concrete implementation ancestors —
contrary to PEP 544's intent and fragile against future typing
validation tightening. Concrete classcore classes remain structurally
compatible with classcore protocols, which is the supported way to mix
the families.

## Risks / Trade-offs

- **`ProtocolClass` metaclass MRO deepens** (`AbstractClass`, `Class`
  inserted before `_ProtocolMeta`). Behavior is guarded by the existing
  delegation exact-once tests plus the full protocol suite.
- **Interpreter variance**: the C `_abc` fast-path bypasses
  `__setattr__` on CPython; PyPy or the `_py_abc` fallback may not.
  Exemptions (Decision 2) cover both. PyPy has surfaced subtle classcore
  bugs before; worth including in any multi-interpreter test matrix.
- **`AbstractObject` is a fresh root** (does not inherit `Object`),
  matching the existing convention (`DataclassObject`, `Protocol`).
  Mixing `class Foo( AbstractObject, Object )` resolves correctly since
  `AbstractClass` is a subclass of `Class`.

## Open Questions

None. Naming, hierarchy, and exemption approach settled with the human
(2026-08-14): `AbstractClass` preferred over `ABCFactory`; protocol
re-parenting in scope.
