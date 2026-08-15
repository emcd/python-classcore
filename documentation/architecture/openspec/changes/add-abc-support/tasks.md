## 1. Implementation

- [ ] 1.1 Add `abc` to the import hub (`sources/classcore/__/imports.py`)
- [ ] 1.2 Define `AbstractClass( Class, __.abc.ABCMeta )` in
  `sources/classcore/standard/classes.py`: `@_class_factory( )`,
  `__new__` typechecker stub, `_dynadoc_fragments_`
- [ ] 1.3 Define `AbstractObject` with `metaclass = AbstractClass` and
  `class_mutables = _abc_class_mutables`, with `_dynadoc_fragments_`
- [ ] 1.4 Re-parent `ProtocolClass` to
  `( AbstractClass, type( __.typx.Protocol ) )`
- [ ] 1.5 Add documentation fragment entries in
  `sources/classcore/__/doctab.py` as needed
- [ ] 1.6 Update `sources/classcore/README.md` taxonomy if it lists the
  metaclass family

## 2. Tests

- [ ] 2.1 Hierarchy: `issubclass( AbstractClass, Class )`,
  `issubclass( AbstractClass, abc.ABCMeta )`; unified
  `issubclass( ProtocolClass, Class )` and
  `issubclass( ProtocolClass, AbstractClass )`
- [ ] 2.2 `AbstractObject` creation with standard behaviors (class
  immutability enforceable)
- [ ] 2.3 Mixing: class inheriting `AbstractObject` and an external
  `abc.ABC`-based class is created without `TypeError`; metaclass is
  `AbstractClass`
- [ ] 2.4 Abstract method enforcement: incomplete subclass raises
  `TypeError` on instantiation; complete subclass instantiates
- [ ] 2.5 Registration: `register()` on an `AbstractObject` descendant;
  registered class satisfies `isinstance()`; no immutability errors
- [ ] 2.6 Protocol functionality preserved: existing protocol suite
  passes unchanged (detection, `runtime_checkable`, `isinstance`)
- [ ] 2.7 Exact-once decoration: recording decorator applied through the
  unified `ProtocolClass → AbstractClass → Class` hierarchy invokes once
- [ ] 2.8 Structural compatibility: a concrete classcore class implementing
  all members of a `@runtime_checkable` classcore protocol satisfies
  `isinstance()` for that protocol

## 3. Validation

- [ ] 3.1 `hatch --env develop run make-all` — all green, 100% coverage
- [ ] 3.2 Towncrier fragment for the new capability
- [ ] 3.3 `openspec validate add-abc-support --strict`
