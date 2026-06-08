# Module Reclassification

## Purpose

The library SHALL apply immutability and concealment to module objects,
enabling package-level API control and protection of module namespaces.

## Requirements

### Requirement: Single Module Reclassification

The `reclassify_module` function MUST apply immutability and concealment to
a single module object.

#### Scenario: Module attributes become immutable
- **WHEN** `reclassify_module` is applied to a module
- **THEN** module attributes MUST become immutable

#### Scenario: Non-public module attributes concealed
- **WHEN** `dir()` is called on a reclassified module
- **THEN** non-public attributes MUST NOT appear

#### Scenario: Public module API visible
- **WHEN** `dir()` is called on a reclassified module
- **THEN** public attributes MUST appear

### Requirement: Module Finalization

The `finalize_module` function MUST apply behaviors and dynadoc
configuration to complete module initialization.

#### Scenario: Finalized module has behaviors
- **WHEN** `finalize_module` is applied to a module
- **THEN** the module MUST have immutability and concealment

#### Scenario: Finalized module has documentation
- **WHEN** `finalize_module` is applied to a module
- **THEN** dynadoc configuration MUST be applied

### Requirement: Recursive Application

Module reclassification MUST support recursive application to submodules.

#### Scenario: Recursive reclassification
- **WHEN** `reclassify_modules` is called with `recursive=True`
- **THEN** all submodules MUST be reclassified

### Requirement: Module Attribute Immutability

After reclassification, module attributes MUST NOT be modifiable.

#### Scenario: Assignment to reclassified module attribute
- **WHEN** assignment is attempted on a reclassified module attribute
- **THEN** an error MUST be raised

### Requirement: Module Attribute Concealment

After reclassification, non-public module attributes MUST be concealed
from `dir()` output.

#### Scenario: Concealed module attribute
- **WHEN** `dir()` is called on a reclassified module
- **THEN** attributes starting with `_` MUST NOT appear (unless explicitly visible)
