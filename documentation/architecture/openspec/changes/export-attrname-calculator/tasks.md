## 1. Calculator prefix seam

- [ ] 1.1 Add `package_name` constructor argument to
  `AttrnameCalculator` (default preserves classcore behavior) and
  resolve it via `self` in `__call__` and `is_internal_name`.
- [ ] 1.2 Document the prefix as construction-time configuration,
  the reserved-grammar vocabulary, and the
  generation-detection asymmetry in the class docstring.

## 2. Public export

- [ ] 2.1 Re-export `AttrnameCalculator` from
  `classcore.standard.nomina` (alias of the hub-canonical object).
- [ ] 2.2 Add identity test (`is` hub object) plus default-behavior
  conformance to the internals tests.

## 3. Downstream-pattern tests

- [ ] 3.1 Rework the downstream-pattern test to the no-override
  form (constructor-configured or subclassed prefix, both methods
  untouched): positive, negative (`_frigid_custom_`), and mangled
  conformance cases.
- [ ] 3.2 Verify per-project AST drift scan still passes
  unchanged.

## 4. Release artifacts

- [ ] 4.1 Add towncrier `enhance` fragment for the public export.
- [ ] 4.2 Validate full gates (make-all, QA matrix, strict
  OpenSpec) and route Tier-1 (Reviewer General + Frigid Owner).
