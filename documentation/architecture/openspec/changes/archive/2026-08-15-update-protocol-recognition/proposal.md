# Change: Fix Protocol Metaclass Hierarchy and Runtime Recognition

## Why

Classcore's protocol classes do not properly integrate with `typing.Protocol`'s
runtime machinery. Three interrelated defects prevent subclasses of classcore
protocol base classes from being recognized as protocols at runtime:

1. **Metaclass hierarchy is flat** — `ProtocolClass`, `ProtocolDataclass`, and
   `ProtocolDataclassMutable` all independently inherit from
   `_ProtocolMeta`. They do not form a subclass relationship, causing
   `TypeError: metaclass conflict` when a user attempts to inherit from
   classes backed by different protocol metaclasses (e.g., `Protocol` and
   `DataclassProtocol`).

2. **`_is_protocol` is not set on subclasses** —
   `typing_extensions.Protocol.__init_subclass__` uses identity comparison
   (`b is Protocol`) to determine whether a subclass is a protocol. Because
   classcore's `Protocol` is not `typing_extensions.Protocol`, subclasses of
   classcore protocol base classes get `_is_protocol = False` explicitly set
   on them, shadowing the inherited `True`. This breaks:
   - `@runtime_checkable` (raises `TypeError` at runtime)
   - `isinstance()` structural subtyping checks
   - `__protocol_attrs__` collection

3. **Protocol base class not statically recognized as sufficient** —
   Related to (2); pyright currently handles this correctly via static
   structural analysis, but runtime behavior is broken.

## What Changes

- **Establish metaclass hierarchies**: Both protocol and non-protocol
  metaclasses SHALL form proper inheritance hierarchies for consistency.
  Protocol: `ProtocolDataclass(ProtocolClass)`,
  `ProtocolDataclassMutable(ProtocolDataclass)`.
  Non-protocol: `Dataclass(Class)`, `DataclassMutable(Dataclass)`.
  This eliminates metaclass conflicts for cross-metaclass inheritance.
  `@dataclass_transform` metadata on mutable metaclasses is correctly
  shadowed (verified: each metaclass gets its own `__dataclass_transform__`
  in its `__dict__`).

- **Fix protocol detection for subclasses**: Override protocol detection logic
  so that direct subclasses of classcore protocol base classes
  (`Protocol`, `ProtocolMutable`, `DataclassProtocol`,
  `DataclassProtocolMutable`) are properly recognized as protocols at runtime
  (`_is_protocol = True`). Concrete implementation subclasses (subclasses of
  a protocol that do not themselves inherit from a protocol base class)
  SHALL remain non-protocols, matching standard `typing` semantics.

- **Guard against double-processing in constructors**: When protocol
  metaclasses form a hierarchy, the class factory's constructor wrappers
  could execute preprocessors/postprocessors multiple times (once per
  metaclass in the MRO). The decorator wrappers SHALL delegate directly
  past their constructor/initializer when the defining metaclass differs
  from the call context, so processing runs exactly once. Public
  `ClassConstructor`/`ClassInitializer` signatures are unchanged.

- **Snapshot declared protocol members**: `__protocol_attrs__` SHALL be
  computed from the pre-decoration namespace (what the author declared),
  not from a post-decoration scan that includes framework-injected and
  dataclass-generated attributes. User-declared dunders SHALL be
  preserved as protocol members.

## Impact

- Affected specs: `protocol-support`
- Affected code:
  - `sources/classcore/standard/classes.py` — metaclass hierarchy (both
    protocol and non-protocol), protocol detection, declared-member
    snapshot, `__protocol_attrs__` override
  - `sources/classcore/decorators.py` — wrapper-level hierarchy delegation
  - New tests for runtime protocol recognition, metaclass hierarchy, and
    cross-metaclass inheritance
