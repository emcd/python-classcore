# Protocol Support

## Purpose

The library SHALL provide protocol classes with immutability and concealment
that work with structural subtyping, preserving protocol functionality
including runtime checks.

## Requirements

### Requirement: Protocol Metaclass

The `Protocol` metaclass MUST combine `typing.Protocol` with standard
behaviors.

#### Scenario: Protocol class creation
- **WHEN** a class uses the `Protocol` metaclass
- **THEN** the resulting class MUST support structural subtyping with immutability and concealment

### Requirement: Protocol Base Class

`ProtocolObject` MUST serve as a base class for protocol definitions with
standard behaviors.

#### Scenario: Protocol inheritance
- **WHEN** a class inherits from `ProtocolObject`
- **THEN** the resulting class MUST be a protocol with immutability and concealment

### Requirement: Protocol Decorator

The `protocol_with_standard_behaviors` decorator MUST create protocol classes
with standard behaviors.

#### Scenario: Decorated protocol
- **WHEN** `@protocol_with_standard_behaviors()` is applied to a class
- **THEN** the resulting class MUST be a protocol with immutability and concealment

### Requirement: Structural Subtyping Preservation

Protocol functionality MUST be preserved, including structural subtyping
and runtime checks.

#### Scenario: Structural subtyping
- **WHEN** a class implements all protocol methods
- **THEN** `isinstance()` MUST return `True` for that protocol

#### Scenario: Runtime checkable protocols
- **WHEN** a protocol is decorated with `@runtime_checkable`
- **THEN** `isinstance()` checks MUST work correctly

### Requirement: ABC Attribute Exemptions

ABC-related mutable attributes (`_abc_cache`, `_abc_registry`, etc.) MUST
be allowed by default to ensure protocol functionality.

#### Scenario: ABC cache mutation
- **WHEN** Python internals modify `_abc_cache` on a protocol class
- **THEN** no immutability error MUST be raised

### Requirement: Implementation Inheritance

Immutability and concealment MUST be inherited by classes implementing
protocol interfaces.

#### Scenario: Implementation inherits behaviors
- **WHEN** a class implements a protocol with standard behaviors
- **THEN** the implementation MUST inherit immutability and concealment
