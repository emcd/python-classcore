## Why

Downstream packages need the reference attribute-name calculator to
contribute grammar-conformant internal names, but `AttrnameCalculator`
lives in private `classcore.__.nomina`. Frigid's local copy of the
related mutables sets already drifted once (the 3.15 typing-dunder
refusal); a local copy of the detector grammar would reintroduce the
same failure mode. Exporting the calculator with a configurable
package prefix lets downstream share the grammar by construction.

## What Changes

- Export `AttrnameCalculator` from public `classcore.standard.nomina`
  (canonical home remains `classcore.__.nomina`; the export is the
  identical object, as with the mutables sets).
- Add a constructor `package_name` argument (default preserves
  current classcore behavior) consumed by both `__call__` and
  `is_internal_name`, so downstream configures the prefix without
  overriding either method. The prefix is construction-time
  configuration and must not change after registration.
- Keep `_levels`, `_cores`, `_mangled_cores`, and `_hex_digits`
  private; document the grammar as reserved framework vocabulary
  (shape conformance, not proof of generation).
- Update the downstream-pattern test to the no-override subclass
  form; per-project grammar-conformance tests live upstream, and
  call-site inventories live downstream (no shared test API).

## Capabilities

### New Capabilities

- `downstream-namer-calculator`: public calculator export with
  configurable package prefix for downstream internal-name
  contributions.

### Modified Capabilities

- None. No existing spec requirements change; detection behavior
  for classcore's own names is unchanged.

## Impact

- `sources/classcore/__/nomina.py` (prefix seam, grammar
  documentation), `sources/classcore/standard/nomina.py`
  (re-export), downstream-pattern tests.
- Downstream: Frigid 4.4 consumes the export instead of mirroring
  the grammar; no classcore runtime behavior changes.
