# Attribute Immutability

## Purpose
This capability provides mechanisms to make class and instance attributes immutable after initialization, preventing accidental state modification and enabling safer concurrent access. It also allows for selective mutability where specific attributes need to remain mutable.

## Requirements

### Requirement: Immutable Attributes
Classes and instances SHALL have immutable attributes after initialization is complete.

Priority: Critical

#### Scenario: Modify Immutable Attribute
- **WHEN** a user attempts to modify an attribute on a standard class or instance after initialization
- **THEN** an `AttributeImmutability` exception is raised
- **AND** the attribute value remains unchanged

#### Scenario: Delete Immutable Attribute
- **WHEN** a user attempts to delete an attribute on a standard class or instance after initialization
- **THEN** an `AttributeImmutability` exception is raised
- **AND** the attribute remains present

### Requirement: Selective Mutability
Users SHALL be able to specify exceptions to immutability rules using names, regexes, or custom predicates.

Priority: High

#### Scenario: Define Mutable Attributes
- **WHEN** a user defines `class_mutables` or `instances_mutables` with specific names, regexes, or predicates
- **THEN** matching attributes can be modified or deleted without raising an exception

#### Scenario: Disable Immutability
- **WHEN** a user sets `class_mutables` or `instances_mutables` to `'*'`
- **THEN** all attributes on the class or instance are mutable
