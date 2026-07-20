# Attribute Concealment

## Purpose

The library SHALL provide mechanisms to conceal non-public attributes from
`dir()` output, reducing API noise and clearly communicating public interfaces.

## Requirements

### Requirement: Default Visibility Filtering

By default, only public attributes (not starting with `_`) MUST be visible
in `dir()` output for classes and instances using standard behaviors.

#### Scenario: Public attributes visible
- **WHEN** `dir()` is called on a class or instance with standard behaviors
- **THEN** attributes not starting with `_` MUST appear in the result

#### Scenario: Non-public attributes concealed
- **WHEN** `dir()` is called on a class or instance with standard behaviors
- **THEN** attributes starting with `_` MUST NOT appear in the result

#### Scenario: Non-public attributes still accessible
- **WHEN** a concealed attribute is accessed directly by name
- **THEN** the attribute MUST be accessible

### Requirement: Class Visibility Customization

Users MUST be able to specify which class attributes are visible via
`class_visibles`.

#### Scenario: Named visible attribute
- **WHEN** an attribute name is listed in `class_visibles`
- **THEN** that attribute MUST appear in `dir()` even if non-public

#### Scenario: Non-visible attribute
- **WHEN** an attribute name is NOT in `class_visibles`
- **THEN** concealment rules apply normally

### Requirement: Instance Visibility Customization

Users MUST be able to specify which instance attributes are visible via
`instances_visibles`.

#### Scenario: Named visible instance attribute
- **WHEN** an attribute name is listed in `instances_visibles`
- **THEN** that attribute MUST appear in `dir()` even if non-public

### Requirement: Visibility Verifiers

Visibility verifiers MUST support names, regexes, and predicates, matching
the mutability verifier interface.

#### Scenario: Regex-based visibility
- **WHEN** an attribute name matches a regex in `class_visibles` or `instances_visibles`
- **THEN** that attribute MUST appear in `dir()`

#### Scenario: Predicate-based visibility
- **WHEN** a predicate returns `True` for an attribute name
- **THEN** that attribute MUST appear in `dir()`

### Requirement: Wildcard Visibility

Users MUST be able to disable concealment entirely using a literal `'*'`.

#### Scenario: Wildcard shows all attributes
- **WHEN** `class_visibles` or `instances_visibles` is set to `'*'`
- **THEN** all attributes MUST appear in `dir()` (Python default behavior)

### Requirement: Visibility Verifier Inheritance

Visibility verifiers MUST be inherited and composable across class
hierarchies.

#### Scenario: Inherited visibility names
- **WHEN** a subclass inherits from a class with custom visibles
- **THEN** the subclass MUST inherit those visible names

#### Scenario: Composed visibility names
- **WHEN** a subclass defines additional visibles
- **THEN** both parent and child visibles MUST be active
