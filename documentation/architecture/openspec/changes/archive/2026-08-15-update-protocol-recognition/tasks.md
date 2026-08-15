## 1. Metaclass Hierarchy

### 1a. Protocol metaclasses

- [x] 1.1 Change `ProtocolDataclass` base from `type(typx.Protocol)` to
  `ProtocolClass` in `sources/classcore/standard/classes.py`
- [x] 1.2 Change `ProtocolDataclassMutable` base from `type(typx.Protocol)`
  to `ProtocolDataclass` in `sources/classcore/standard/classes.py`
- [x] 1.3 Verify `_dynadoc_fragments_` on each metaclass are preserved
  (each overrides in its own `__dict__`)
- [x] 1.4 Verify `dataclass_transform` markers are preserved and correctly
  shadowed: `ProtocolDataclassMutable` must have `frozen_default = False`
  in its own `__dataclass_transform__`

### 1b. Non-protocol metaclasses

- [x] 1.5 Change `Dataclass` base from `type` to `Class` in
  `sources/classcore/standard/classes.py`
- [x] 1.6 Change `DataclassMutable` base from `type` to `Dataclass` in
  `sources/classcore/standard/classes.py`
- [x] 1.7 Verify `_dynadoc_fragments_` and `dataclass_transform` markers
  are preserved on non-protocol metaclasses

## 2. Constructor Double-Processing Guard

- [x] 2.1 Implement hierarchy delegation in the decorator wrappers
  (`produce_class_construction_decorator` and
  `produce_class_initialization_decorator` in
  `sources/classcore/decorators.py`): on mismatch between the closure
  metaclass and the call context (`clscls is not clscls_` for
  construction, `clscls is not type(cls)` for initialization), delegate
  directly past the constructor/initializer.
- [x] 2.2 Keep `ClassConstructor` and `ClassInitializer` public signatures
  unchanged in `sources/classcore/nomina.py` (an `origin` parameter was
  implemented first, then withdrawn to avoid a breaking API change).
- [x] 2.3 Test that a class decorator records exactly one invocation for a
  class created through a custom metaclass hierarchy
  (`test_444_factory_hierarchy_delegation`)
- [x] 2.4 Run existing test suite to verify no regressions from the guard
  change

## 3. Protocol Detection Fix

- [x] 3.1 Add `_protocol_cls_set` constant (`frozenset({typx.Protocol})`)
  to `sources/classcore/standard/classes.py`
- [x] 3.2 Add structural detection in `ProtocolClass.__new__` stub: check
  if any base has `_is_protocol = True` in its `__dict__` AND has a
  typing Protocol class as a direct base. Set `_is_protocol = True`
  before decorators are applied.
- [x] 3.3 Snapshot declared members in `ProtocolClass.__new__` before
  decoration, and replace `__protocol_attrs__` with
  `declared | inherited` in `ProtocolClass.__init__` (after
  `_ProtocolMeta.__init__` computes it).
- [x] 3.4 Add `_is_runtime_protocol` and `__non_callable_proto_members__`
  to `_abc_class_mutables` so `runtime_checkable` can set these attributes
  without triggering immutability errors.
- [x] 3.5 Verify that `_is_protocol` is `True` on direct subclasses and
  `False` on concrete implementation subclasses

## 4. Tests

- [x] 4.1 Test protocol metaclass hierarchy: `issubclass(ProtocolDataclass, ProtocolClass)`
  and `issubclass(ProtocolDataclassMutable, ProtocolDataclass)`
- [x] 4.2 Test non-protocol metaclass hierarchy: `issubclass(Dataclass, Class)`
  and `issubclass(DataclassMutable, Dataclass)`
- [x] 4.3 Test cross-metaclass inheritance: module-level class inheriting
  from `Protocol` and `DataclassProtocol`, created without `TypeError`,
  with `ProtocolDataclass` selected as metaclass
- [x] 4.4 Test `_is_protocol` is `True` on direct subclasses of protocol
  base classes
- [x] 4.5 Test `_is_protocol` is `False` on concrete implementation
  subclasses
- [x] 4.6 Test `@runtime_checkable` succeeds when applied via `decorators=`
  mechanism
- [x] 4.7 Test `@runtime_checkable` succeeds when applied directly
- [x] 4.8 Test `isinstance()` structural subtyping works with
  `@runtime_checkable` classcore protocol
- [x] 4.9 Test `runtime_checkable` and `isinstance` for direct subclasses
  of all four protocol base classes
- [x] 4.10 Test `dataclass_transform` preservation (frozen and mutable)
- [x] 4.11 Test user-declared dunders are preserved in
  `__protocol_attrs__`
- [x] 4.12 Test dataclass protocol attrs contain declared members only
  (module-level class)
- [x] 4.13 Test factory hierarchy delegation applies a decorator exactly
  once (custom metaclass hierarchy)
- [x] 4.14 Run full test suite — all tests pass

## 5. Validation

- [x] 5.1 Run `hatch --env develop run make-all` — all green, 100% coverage
- [x] 5.2 Add towncrier fragments for user-facing behavior changes
- [x] 5.3 Update `issues/classes/1`, `issues/classes/2`, `issues/classes/3`
  in `nb` with resolution status
