# abc-support Specification

## Purpose

Opt-in abstract base class support: combine standard behaviors with
`abc.ABCMeta` machinery for abstract classes that mix with external
ABC-based classes, and unify the protocol metaclass taxonomy under
`Class`.

## Requirements

### Requirement: Abstract Class Metaclass

The `AbstractClass` metaclass MUST combine the standard behaviors of
`Class` with `abc.ABCMeta` via a diamond inheritance hierarchy. `Class`
itself MUST remain backed by plain `type` so that ordinary classcore
classes carry no ABC machinery.

#### Scenario: Abstract class creation
- **WHEN** a class uses the `AbstractClass` metaclass
- **THEN** the resulting class MUST support standard behaviors
  (immutability, concealment) and ABC machinery (abstract method
  enforcement, virtual subclass registration)

#### Scenario: Metaclass hierarchy
- **WHEN** `AbstractClass` is inspected
- **THEN** it MUST be a subclass of both `Class` and `abc.ABCMeta`

#### Scenario: Ordinary classes unaffected
- **WHEN** a class uses the `Class` metaclass
- **THEN** it MUST NOT gain ABC machinery

### Requirement: Abstract Base Class

`AbstractObject` MUST serve as a base class for abstract classes with
standard behaviors, created with `AbstractClass` and exempting ABC cache
attributes from class immutability.

#### Scenario: Inheritance
- **WHEN** a class inherits from `AbstractObject`
- **THEN** the class MUST be created with `AbstractClass` as its
  metaclass, with standard behaviors active

#### Scenario: Mixing with external abstract base classes
- **WHEN** a class inherits from both `AbstractObject` and an external
  class whose metaclass is `abc.ABCMeta`
- **THEN** class creation MUST succeed without
  `TypeError: metaclass conflict`

#### Scenario: Abstract method enforcement
- **WHEN** a class inherits abstract methods from an external ABC and
  does not implement them
- **THEN** instantiation MUST raise `TypeError`
- **AND** a subclass implementing all abstract methods MUST instantiate

#### Scenario: Virtual subclass registration
- **WHEN** `register()` is called on a class derived from
  `AbstractObject`
- **THEN** the registered class MUST satisfy `isinstance()` checks
- **AND** ABC cache mutations MUST NOT raise immutability errors

### Requirement: Unified Protocol Metaclass

`ProtocolClass` MUST inherit from both `AbstractClass` and the metaclass
of `typing.Protocol`, unifying the metaclass taxonomy under `Class`.

#### Scenario: Unified taxonomy
- **WHEN** `ProtocolClass` is inspected
- **THEN** it MUST be a subclass of `Class`, `AbstractClass`, and
  `abc.ABCMeta`

#### Scenario: Protocol functionality preserved
- **WHEN** the `protocol-support` capability scenarios are exercised
- **THEN** runtime protocol detection, `@runtime_checkable`, and
  `isinstance()` structural subtyping MUST continue to behave as
  specified

#### Scenario: Single decoration through hierarchy
- **WHEN** a class is created through the unified protocol metaclass
  hierarchy with a decorator
- **THEN** the decorator MUST be applied exactly once

#### Scenario: Concrete classes structurally satisfy protocols
- **WHEN** a concrete classcore class (e.g., backed by `Class` or
  `AbstractClass`) implements all members of a `@runtime_checkable`
  classcore protocol
- **THEN** `isinstance()` MUST return `True` for that protocol
