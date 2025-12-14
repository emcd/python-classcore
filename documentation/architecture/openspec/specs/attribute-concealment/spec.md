# Attribute Concealment

## Purpose
This capability provides mechanisms to conceal non-public attributes from `dir()` output, reducing API noise and clearly communicating public interfaces.

## Requirements

### Requirement: Default Concealment
By default, only public attributes (those not starting with `_`) SHALL be visible in `dir()` output.

Priority: High

#### Scenario: Inspect Object with dir()
- **WHEN** `dir()` is called on a standard class or instance
- **THEN** attributes starting with `_` are not included in the output
- **BUT** attributes starting with `_` are still accessible if referenced directly

### Requirement: Selective Visibility
Users SHALL be able to customize visibility rules using names, regexes, or custom predicates.

Priority: Medium

#### Scenario: Custom Visibility Rules
- **WHEN** a user defines `class_visibles` or `instances_visibles` with specific rules
- **THEN** attributes matching the rules are included in `dir()` output regardless of their name

#### Scenario: Full Visibility
- **WHEN** a user sets `class_visibles` or `instances_visibles` to `'*'`
- **THEN** all attributes (including those starting with `_`) are visible in `dir()` (standard Python behavior)
