# Type Safety

## Purpose

The library SHALL ensure full compatibility with static type checkers and
multiple Python implementations, with graceful degradation for
implementation-specific features.

## Requirements

### Requirement: Complete Type Annotations

All public APIs MUST have complete type annotations.

#### Scenario: Public function annotated
- **WHEN** a public function is defined
- **THEN** all parameters and return types MUST have annotations

#### Scenario: Public class annotated
- **WHEN** a public class is defined
- **THEN** all public methods MUST have complete annotations

### Requirement: Dataclass Transform Signaling

Metaclasses MUST use `@dataclass_transform` to signal dataclass behavior
to type checkers.

#### Scenario: Type checker recognizes dataclass
- **WHEN** a class uses a standard dataclass metaclass
- **THEN** type checkers MUST infer dataclass fields and methods

### Requirement: Generic Type Variables

Generic type variables MUST be properly constrained.

#### Scenario: Constrained TypeVar
- **WHEN** a TypeVar is used in a public API
- **THEN** it MUST have appropriate constraints or bounds

### Requirement: Pyright Strict Mode

The package MUST comply with Pyright strict mode.

#### Scenario: Pyright strict check passes
- **WHEN** Pyright runs in strict mode on the package
- **THEN** no errors MUST be reported

### Requirement: Py.typed Marker

The package MUST include a `py.typed` marker file.

#### Scenario: PEP 561 compliance
- **WHEN** the package is installed
- **THEN** type checkers MUST recognize it as typed

### Requirement: CPython Compatibility

Core functionality MUST work on CPython 3.10+.

#### Scenario: CPython 3.10 test pass
- **WHEN** tests run on CPython 3.10
- **THEN** all tests MUST pass

#### Scenario: CPython 3.13 test pass
- **WHEN** tests run on CPython 3.13
- **THEN** all tests MUST pass

### Requirement: PyPy Compatibility

Core functionality MUST work on PyPy 3.10+.

#### Scenario: PyPy test pass
- **WHEN** tests run on PyPy 3.10
- **THEN** all tests MUST pass

### Requirement: Platform-Specific Feature Detection

Platform-specific optimizations (closure repair) MUST be detected and
applied conditionally.

#### Scenario: CPython closure repair
- **WHEN** running on CPython
- **THEN** CPython-specific closure repair MUST be applied

#### Scenario: PyPy closure repair
- **WHEN** running on PyPy
- **THEN** PyPy-specific closure repair MUST be applied

### Requirement: No Unsafe Operations

The package MUST NOT use `exec`, `eval`, or `ctypes`.

#### Scenario: No exec usage
- **WHEN** the source code is analyzed
- **THEN** no `exec` calls MUST be found

#### Scenario: No eval usage
- **WHEN** the source code is analyzed
- **THEN** no `eval` calls MUST be found

### Requirement: Comprehensive Test Coverage

The package MUST maintain comprehensive test coverage across all supported
implementations.

#### Scenario: Coverage threshold
- **WHEN** coverage is measured
- **THEN** coverage MUST be at least 95%
