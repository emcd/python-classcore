# Extensibility

## Purpose
This capability provides hooks and factory functions for users to create custom behaviors and metaclasses, allowing the core machinery to be reused for custom implementations.

## Requirements

### Requirement: Factory Functions
The library SHALL provide factory functions for creating custom metaclasses and decorators.

Priority: Medium

#### Scenario: Create Custom Metaclass
- **WHEN** a user invokes `class_factory` with custom arguments
- **THEN** a new metaclass is produced that incorporates the specified behaviors

### Requirement: Custom Hooks
The library SHALL support hooks for class construction, initialization, and decoration.

Priority: Medium

#### Scenario: Custom Class Construction
- **WHEN** a user provides a custom preprocessor or postprocessor
- **THEN** it is executed during the class creation process

### Requirement: Core Function Replacement
Users SHALL be able to replace core behavior functions (assigner, deleter, surveyor).

Priority: Low

#### Scenario: Custom Assigner
- **WHEN** a user provides a `instances_assigner_core` argument
- **THEN** that function is used to handle attribute assignment instead of the default implementation
