# Class Factories

## Purpose

The library SHALL provide factory functions and hook systems for users to
create custom metaclasses, behaviors, and decorators with full control over
class construction and initialization lifecycles.

## Requirements

### Requirement: Metaclass Constructor Factory

The `produce_class_constructor` factory MUST generate customizable `__new__`
implementations with hook support.

#### Scenario: Custom constructor with hooks
- **WHEN** `produce_class_constructor` is called with preprocessor and postprocessor hooks
- **THEN** the resulting constructor MUST invoke hooks at the appropriate lifecycle points

### Requirement: Metaclass Initializer Factory

The `produce_class_initializer` factory MUST generate customizable `__init__`
implementations with hook support.

#### Scenario: Custom initializer with completers
- **WHEN** `produce_class_initializer` is called with completer hooks
- **THEN** the resulting initializer MUST invoke completers after initialization

### Requirement: Construction Preprocessors

Preprocessors MUST be able to modify class construction inputs (bases,
namespace, arguments, decorators) before class creation.

#### Scenario: Preprocessor modifies bases
- **WHEN** a preprocessor modifies the bases tuple
- **THEN** the class MUST be created with the modified bases

#### Scenario: Preprocessor modifies namespace
- **WHEN** a preprocessor modifies the namespace dict
- **THEN** the class MUST be created with the modified namespace

### Requirement: Construction Postprocessors

Postprocessors MUST be able to augment constructed classes after creation.

#### Scenario: Postprocessor adds attributes
- **WHEN** a postprocessor adds attributes to the class
- **THEN** the class MUST have those attributes

### Requirement: Initialization Completers

Completers MUST be able to finalize initialized classes (e.g., freezing
behaviors) after `__init__` completes.

#### Scenario: Completer runs after init
- **WHEN** `__init__` completes
- **THEN** completers MUST execute

### Requirement: Decoration Preparers

Preparers MUST be able to adjust decorator lists before application.

#### Scenario: Preparer modifies decorators
- **WHEN** a preparer modifies the decorator list
- **THEN** the modified decorators MUST be applied

### Requirement: Core Function Replacement

Critical behaviors (assignment, deletion, visibility) MUST be replaceable
by providing alternative core functions.

#### Scenario: Custom assigner
- **WHEN** a custom assigner core function is provided
- **THEN** attribute assignment MUST use the custom function

#### Scenario: Custom surveyor
- **WHEN** a custom surveyor core function is provided
- **THEN** `dir()` MUST use the custom function

### Requirement: Decorator Composition

The `decoration_by` function MUST compose multiple decorators with
preparation hooks.

#### Scenario: Composed decorators
- **WHEN** `decoration_by` is called with multiple decorators
- **THEN** all decorators MUST be applied in sequence

### Requirement: Custom Error Classes

Users MUST be able to provide custom error class providers for
immutability violations.

#### Scenario: Custom error raised
- **WHEN** a custom error class provider is configured
- **THEN** immutability violations MUST raise the custom error
