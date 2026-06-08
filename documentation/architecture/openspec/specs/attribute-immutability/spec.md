# Attribute Immutability

## Purpose

The library SHALL provide mechanisms to make class and instance attributes
immutable after initialization, with support for selective mutability via
names, regexes, or predicates.

## Requirements

### Requirement: Class Attribute Immutability

Class attributes produced by standard metaclasses MUST be immutable after
class construction completes.

#### Scenario: Assignment to immutable class attribute
- **WHEN** assignment is attempted on a class attribute after construction
- **THEN** `AttributeImmutability` MUST be raised

#### Scenario: Deletion of immutable class attribute
- **WHEN** deletion is attempted on a class attribute
- **THEN** `AttributeImmutability` MUST be raised

### Requirement: Instance Attribute Immutability

Instance attributes of standard classes MUST be immutable after `__init__`
and `__post_init__` complete.

#### Scenario: Assignment to immutable instance attribute
- **WHEN** assignment is attempted on an instance attribute after initialization
- **THEN** `AttributeImmutability` MUST be raised

#### Scenario: Deletion of immutable instance attribute
- **WHEN** deletion is attempted on an instance attribute
- **THEN** `AttributeImmutability` MUST be raised

#### Scenario: Mutability during initialization
- **WHEN** attributes are assigned within `__init__` or `__post_init__`
- **THEN** assignment MUST succeed

### Requirement: Selective Mutability by Name

Users MUST be able to specify mutable attributes by exact name.

#### Scenario: Named mutable attribute
- **WHEN** an attribute name is listed in `class_mutables` or `instances_mutables`
- **THEN** that attribute MUST be mutable

#### Scenario: Non-mutable attribute with name-based exceptions
- **WHEN** an attribute name is NOT in the mutables list
- **THEN** immutability MUST be enforced

### Requirement: Selective Mutability by Regex

Users MUST be able to specify mutable attributes by compiled regex pattern.

#### Scenario: Regex-matched mutable attribute
- **WHEN** an attribute name matches a regex in `class_mutables` or `instances_mutables`
- **THEN** that attribute MUST be mutable

#### Scenario: Regex non-match
- **WHEN** an attribute name does not match any regex
- **THEN** immutability MUST be enforced

### Requirement: Selective Mutability by Predicate

Users MUST be able to specify mutable attributes by predicate function.

#### Scenario: Predicate-matched mutable attribute
- **WHEN** a predicate function returns `True` for an attribute name
- **THEN** that attribute MUST be mutable

#### Scenario: Predicate non-match
- **WHEN** all predicates return `False` for an attribute name
- **THEN** immutability MUST be enforced

### Requirement: Wildcard Mutability

Users MUST be able to disable immutability entirely using a literal `'*'`.

#### Scenario: Wildcard disables immutability
- **WHEN** `class_mutables` or `instances_mutables` is set to `'*'`
- **THEN** all attributes of that level MUST be mutable

### Requirement: Mutability Verifier Inheritance

Mutability verifiers (names, regexes, predicates) MUST be inherited and
composable across class hierarchies.

#### Scenario: Inherited mutability names
- **WHEN** a subclass inherits from a class with named mutables
- **THEN** the subclass MUST inherit those mutable names

#### Scenario: Composed mutability names
- **WHEN** a subclass defines additional mutables
- **THEN** both parent and child mutables MUST be active
