# Dataclass Integration

## Purpose

The library SHALL automatically convert classes to dataclasses while
applying immutability and concealment, preserving all dataclass functionality
including `__post_init__` attribute modification.

## Requirements

### Requirement: Metaclass Auto-Conversion

The `Dataclass` metaclass MUST automatically apply `@dataclass` decorator
during class construction.

#### Scenario: Dataclass produced by metaclass
- **WHEN** a class uses the `Dataclass` metaclass
- **THEN** the resulting class MUST be a dataclass with standard behaviors

#### Scenario: DataclassObject base class
- **WHEN** a class inherits from `DataclassObject`
- **THEN** the resulting class MUST be a dataclass with standard behaviors

### Requirement: Decorator-Based Creation

The `dataclass_with_standard_behaviors` decorator MUST create a dataclass
with standard behaviors applied.

#### Scenario: Decorated dataclass
- **WHEN** `@dataclass_with_standard_behaviors()` is applied to a class
- **THEN** the resulting class MUST be a dataclass with immutability and concealment

### Requirement: Post-Init Modification

`__post_init__` MUST be able to modify attributes before immutability is
enforced.

#### Scenario: Post-init attribute assignment
- **WHEN** `__post_init__` assigns attributes
- **THEN** assignment MUST succeed

#### Scenario: Post-init immutability enforcement
- **WHEN** `__post_init__` completes
- **THEN** attributes MUST become immutable

### Requirement: Dataclass Argument Compatibility

Standard metaclasses and decorators MUST be compatible with `dataclass`
arguments including `frozen`, `slots`, `kw_only`, etc.

#### Scenario: Slots mode
- **WHEN** `slots=True` is passed to a standard dataclass metaclass
- **THEN** the resulting class MUST use `__slots__` and maintain behaviors

#### Scenario: Kw-only mode
- **WHEN** `kw_only=True` is passed to a standard dataclass metaclass
- **THEN** all fields MUST be keyword-only

### Requirement: Class Replacement Handling

When `slots=True` causes class replacement, the library MUST properly
handle closure repair so that `super()` continues to function.

#### Scenario: Super after class replacement
- **WHEN** a dataclass with `slots=True` replaces the class
- **THEN** `super()` calls in methods MUST continue to work correctly

### Requirement: Type Checker Recognition

Metaclasses MUST use `@dataclass_transform` to signal dataclass behavior
to type checkers.

#### Scenario: Type checker infers dataclass
- **WHEN** a class uses a standard dataclass metaclass
- **THEN** type checkers MUST recognize it as a dataclass
