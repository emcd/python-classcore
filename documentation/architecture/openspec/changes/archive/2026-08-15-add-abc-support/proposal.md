# Change: Add Abstract Base Class Support

## Why

Classes created by classcore metaclasses cannot be combined with external
abstract base classes. `Class` inherits from `type` while `abc.ABCMeta`
also inherits from `type`, so `class Foo( classcore.Object, SomeABC )`
fails with `TypeError: metaclass conflict` — the two metaclasses are
siblings. The same gap separates `ProtocolClass` from `Class`: the
protocol metaclass family never passes through `Class`, so protocol
definition bases cannot share a metaclass lineage with ordinary
classcore classes.

## What Changes

- **Add `AbstractClass` metaclass**: combines `Class` with `abc.ABCMeta`
  via a diamond hierarchy. Opt-in — `Class` itself remains backed by
  plain `type`, so the contract of ordinary classcore classes is
  unchanged (no ABC machinery, no registration caches).
- **Add `AbstractObject` base class**: created with `AbstractClass` and
  carrying the ABC cache mutable exemptions, for authoring abstract
  classes with standard behaviors that mix with external ABCs.
- **Re-parent `ProtocolClass`**: from `type( typx.Protocol )` to
  `( AbstractClass, type( typx.Protocol ) )`, unifying the metaclass
  taxonomy under `Class`. Protocol behavior is preserved by the
  wrapper-level delegation introduced in `update-protocol-recognition`.
  Concrete classcore classes remain structurally compatible with
  classcore protocols. Direct inheritance of a protocol definition base
  alongside an ordinary base (e.g., `Protocol` and `Object` together)
  remains unsupported: typing independently rejects ordinary bases in
  protocol definitions, and the metaclass unification does not (and
  should not) change that.

## Impact

- Affected specs: `abc-support` (new capability)
- Affected code:
  - `sources/classcore/__/imports.py` — add `abc` to import hub
  - `sources/classcore/standard/classes.py` — `AbstractClass`,
    `AbstractObject`, `ProtocolClass` re-parenting
  - `sources/classcore/__/doctab.py` — documentation fragments as needed
  - New tests for hierarchy, mixing, enforcement, registration
- Empirically verified via scratch prototypes (diamond MRO, mixed-base
  creation, abstract enforcement, `register()`, exact-once decoration
  through the unified hierarchy)
