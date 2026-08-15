## Context

Classcore provides protocol metaclasses that combine `typing.Protocol` with
standard behaviors (immutability, concealment, dynadoc). Three defects in the
current implementation prevent these protocol classes from functioning
correctly at runtime.

### Root Cause Analysis

**Metaclass hierarchy**: All three protocol metaclasses independently inherit
from `_ProtocolMeta`:

```
ProtocolClass → _ProtocolMeta
ProtocolDataclass → _ProtocolMeta  (sibling of ProtocolClass)
ProtocolDataclassMutable → _ProtocolMeta  (sibling of both)
```

Python requires all metaclasses of a class's bases to be in a subclass
relationship. Since the protocol metaclasses are siblings, multi-base
inheritance involving classes backed by different protocol metaclasses raises
`TypeError: metaclass conflict`.

**Protocol detection**: `typing_extensions.Protocol.__init_subclass__` contains:

```python
def __init_subclass__(cls, *args, **kwargs):
    super().__init_subclass__(*args, **kwargs)
    if not cls.__dict__.get('_is_protocol', False):
        cls._is_protocol = any(b is Protocol for b in cls.__bases__)
```

The identity check `b is Protocol` (where `Protocol` is
`typing_extensions.Protocol`) fails for classcore subclasses because
classcore's `Protocol` is a different class object. The `__init_subclass__`
explicitly sets `_is_protocol = False` on subclasses, shadowing the inherited
`True` value. This breaks `@runtime_checkable`, `isinstance()` structural
checks, and `__protocol_attrs__` collection.

Confirmed: classcore's own `Protocol` has `_is_protocol = True` (it directly
inherits from `typing_extensions.Protocol`, satisfying the identity check).
The problem only manifests on subclasses of classcore protocol base classes.

Confirmed: pyright is unaffected (0 errors) because it performs static
structural analysis without relying on `_is_protocol`.

**Double-processing risk**: The class factory's constructor
(`factories.py:produce_class_constructor`) has an `in_progress` short-circuit
to prevent recursive decoration. However, it checks the flag *after*
`superf()` returns. When metaclasses form a hierarchy, the parent metaclass's
constructor sets `in_progress = True`, processes, then sets it to `False`
before the child metaclass's constructor checks it. This causes
preprocessors, postprocessors, and decorators to be applied once per
metaclass in the MRO.

## Goals / Non-Goals

- Goals:
  - Establish a proper metaclass hierarchy for all standard metaclasses
    (protocol and non-protocol), for consistency (Principle of Least
    Surprise).
  - Ensure subclasses of classcore protocol base classes are recognized as
    protocols at runtime (`_is_protocol = True`).
  - Ensure `@runtime_checkable` works with classcore protocol classes.
  - Ensure `isinstance()` structural subtyping works with
    `@runtime_checkable` classcore protocols.
  - Prevent double-processing when metaclass constructors form a hierarchy.
- Non-Goals:
  - Type-checker-side `.pyi` stub changes. Pyright already handles
    classcore protocols correctly via static analysis.

## Decisions

### Decision 1: Metaclass hierarchy

Establish proper inheritance hierarchies for both protocol and non-protocol
metaclasses, for consistency.

**Protocol metaclasses:**

```
ProtocolClass → _ProtocolMeta → _ProtocolMeta(typing) → ABCMeta → type
ProtocolDataclass → ProtocolClass
ProtocolDataclassMutable → ProtocolDataclass
```

**Non-protocol metaclasses:**

```
Class → type
Dataclass → Class
DataclassMutable → Dataclass
```

When forming these hierarchies, `@dataclass_transform` metadata on mutable
metaclasses must be verified. Confirmed: `@dataclass_transform` sets
`__dataclass_transform__` in the class's own `__dict__`, which shadows any
inherited value. `ProtocolDataclassMutable` (which omits `frozen_default`)
will correctly have `frozen_default = False` in its own
`__dataclass_transform__`, not inheriting `True` from `ProtocolDataclass`.

- Alternatives considered: A metaclass `__init_subclass__` shim to resolve
  conflicts dynamically. Rejected — proper hierarchy is simpler and more
  correct.

### Decision 2: Protocol detection fix

Detect protocol base classes structurally, in the `ProtocolClass.__new__`
stub. A base is a protocol base class when it has `_is_protocol = True`
in its own `__dict__` (not merely inherited) and has a typing `Protocol`
class as a direct base (`_protocol_cls_set & set(base.__bases__)`).
When found, set `_is_protocol = True` on the new class before any
decorators are applied, so `decorators = (typing.runtime_checkable,)`
sees the correct value.

- Semantics: `class MyProto(classcore.Protocol)` gets `_is_protocol = True`.
  `class Impl(MyProto)` gets `_is_protocol = False` (concrete implementation,
  no protocol base class in `__bases__`).
- This matches standard `typing` semantics where a class is a protocol only
  if it directly inherits from `Protocol`.
- Third-party extensibility: adding a typing `Protocol` to the bases of a
  classcore protocol subclass makes it a protocol base class in turn,
  mirroring standard typing usage.
- Alternatives considered:
  - Sentinel attribute (`_classcore_protocol_base`) on each protocol base
    class's `__dict__`. Rejected — visible via `__getattribute__` on all
    subclasses (namespace pollution), and redundant with the structural
    signal already present.
  - Module-level registry (`frozenset`). Rejected — a frozen registry
    precludes extension by third-party packages; a mutable registry invites
    mutation by callers who should instead use the framework properly.
  - Checking metaclass type (`isinstance(b, ProtocolClass)`). Rejected —
    cannot distinguish protocol definitions from concrete implementations,
    since both use the same metaclass.

### Decision 3: Where to implement the detection fix

Split across the two metaclass hook sites, each for a distinct reason:

- `ProtocolClass.__new__`: corrects `_is_protocol` immediately after class
  creation. Must run before decorator application (inside the constructor's
  `superf()` chain) so `typing.runtime_checkable` via `decorators=` sees
  `_is_protocol = True`.
- `ProtocolClass.__init__`: replaces `__protocol_attrs__` after
  `_ProtocolMeta.__init__` computes it (see Decision 5).

`__init_subclass__` was rejected as the site: it would need to be defined
on all four protocol base classes (they do not inherit from each other at
the class level), and it runs before decorators are known.

### Decision 4: Double-processing prevention

Implement hierarchy delegation in the decorator wrappers
(`decorators.py`), not in the produced constructors/initializers. Each
wrapper already holds the defining metaclass in its closure (`clscls`)
and receives the most-derived metaclass as its call context (`clscls_`
for construction, `type(cls)` for initialization). On mismatch, the
wrapper delegates directly past its own constructor/initializer — the
parent metaclass's machinery never runs a second time.

`ClassConstructor` and `ClassInitializer` keep their original public
signatures; no major release is required for this change.

- Alternatives considered:
  - `origin`/`defining_clscls` parameter threaded from wrapper to
    constructor (`if origin is not clscls: return`). Implemented and
    reviewed first, then withdrawn — it changed the public callback
    signatures for an internal concern, forcing a major version.
  - Only applying `@_class_factory()` to `ProtocolClass` and having child
    metaclasses inherit factory behaviors. Rejected — the `__new__` stub
    in each metaclass's class body would shadow the inherited
    factory-injected `__new__`, bypassing preprocessing; also the wrappers'
    closure variables would reference the parent metaclass, defeating
    start-of-MRO behavior enforcement.

### Decision 5: Snapshot-based `__protocol_attrs__`

`typing_extensions` computes `__protocol_attrs__` by scanning the
decorated namespace (all of `__dict__` and `__annotations__` across the
MRO), which collects framework-injected attributes (behavior dunders,
dataclass-generated methods, classcore internals). Reordering decoration
cannot help: `_ProtocolMeta.__init__` always runs after `__new__`,
after all decoration, and `runtime_checkable` itself sets attributes on
the finished class.

Instead, snapshot the declared members in `ProtocolClass.__new__`
immediately after class creation — the pre-decoration namespace contains
exactly what the author declared. `ProtocolClass.__init__` then replaces
the computed attrs with `declared | union(inherited)` over
`ProtocolClass`-family bases.

- A user-declared dunder (e.g., `__repr__`) is preserved as a protocol
  member; framework-generated dunders never enter the snapshot, so no
  dataclass-dunder blacklist is needed.
- Exclusions are limited to class-creation machinery (`__abstractmethods__`,
  `__parameters__`, `__init__`, `__orig_bases__`), typing internals, and
  `_classcore_`/`_abc_` prefixes.
- The snapshot is idempotent and survives dataclass class reproduction
  (`_add_slots` copies `__dict__`, including the snapshot attribute).
- Alternatives considered: filtering the post-decoration attrs with a
  blacklist of framework dunder names. Implemented and reviewed first, then
  withdrawn — unmaintainable and silently drops user-declared dunders.

## Risks / Trade-offs

- **Metaclass hierarchy change is backward-compatible**: Existing code using a
  single protocol metaclass is unaffected. The change only enables
  previously-impossible multi-metaclass inheritance.
- **`_is_protocol` fix changes runtime behavior**: Subclasses of classcore
  protocol base classes will now have `_is_protocol = True` instead of
  `False`. This is a bug fix — the previous behavior was incorrect. But any
  code relying on the buggy behavior (unlikely) would break.
- **`__protocol_attrs__` snapshot is broader than the standard scan**: A
  user-declared dunder now counts toward structural checks, so a candidate
  lacking it fails `isinstance`. This matches standard `typing`, which also
  includes declared dunders, so behavior diverges only from the interim
  blacklist, not from standard typing semantics.

## Open Questions

None remaining. All resolved during review.
