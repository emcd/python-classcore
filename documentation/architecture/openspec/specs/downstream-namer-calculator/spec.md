# downstream-namer-calculator Specification

## Purpose

Public reference calculator letting downstream packages share
classcore's internal-name grammar by construction instead of
mirroring it.
## Requirements
### Requirement: Public calculator export

`AttrnameCalculator` SHALL be importable from public
`classcore.standard.nomina` and SHALL be identically the object
defined in `classcore.__.nomina` (canonical home unchanged).

#### Scenario: Downstream imports without private path

- **WHEN** a downstream package imports `AttrnameCalculator` from
  `classcore.standard.nomina`
- **THEN** the import succeeds and the object is identically
  `classcore.__.nomina.AttrnameCalculator`.

### Requirement: Configurable package prefix

The calculator SHALL accept a `package_name` constructor argument
defaulting to current classcore behavior. Both `__call__` and
`is_internal_name` SHALL resolve the same configured prefix, and
the prefix SHALL be treated as construction-time configuration.

#### Scenario: Default preserves classcore behavior

- **WHEN** `AttrnameCalculator()` is constructed without arguments
- **THEN** `__call__` emits `_{classcore}_{level}_{core}_` names and
  `is_internal_name` detects exactly the names it detected before
  this change.

#### Scenario: Downstream prefix without overrides

- **WHEN** a downstream package constructs
  `AttrnameCalculator( package_name = 'frigid' )` (or subclasses
  without overriding either method)
- **THEN** `__call__` emits `_frigid_` names and
  `is_internal_name` detects grammar-conformant `_frigid_` names
  while rejecting `_classcore_` names and non-grammar lookalikes
  such as `_frigid_custom_`.

#### Scenario: Prefix mismatch does not match

- **WHEN** names are generated under one prefix and checked by a
  detector configured with another prefix
- **THEN** they do not match. Prefix configuration is
  construction-time; post-registration mutation is unsupported.

### Requirement: Private grammar vocabulary

`_levels`, `_cores`, `_mangled_cores`, and `_hex_digits` SHALL
remain private to `classcore.__.nomina`. Documentation SHALL state
the grammar is reserved framework vocabulary (shape conformance),
not proof an attribute was generated.

#### Scenario: Grammar evolves without downstream changes

- **WHEN** classcore adds a core to the private grammar
- **THEN** downstream calculators constructed as specified detect
  the new core's names with no downstream modification.

### Requirement: Generation-detection asymmetry preserved

`__call__` SHALL continue to emit the two class-level mangling
stems, and the detector SHALL continue to accept only their
completed 64-hex digest forms, never bare stems, under any
configured prefix.

#### Scenario: Mangled forms under downstream prefix

- **WHEN** a downstream calculator detects
  `_frigid_class_behaviors_<64 hex>` and `_frigid_class_behaviors_`
- **THEN** the digest form is internal and the bare stem is not.
