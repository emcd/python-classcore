## Why

Classcore's attribute behaviors are opaque. When an attribute surprises a
user — immutable when expected mutable, absent from `dir()` when expected
visible — the reason lives in a decision cascade spread across
`behaviors.py`: the active-behaviors sets (immutability and concealment
labels), per-level exclusion configuration (names, the `'*'` wildcard,
predicates, regexes), and stdlib machinery exemptions. There is no way to
ask classcore *why*; users must reverse-engineer from source, and even
maintainers re-derive the cascade from scratch each time (the recent
mangling work confirmed this).

Formalizing the decision model as a first-class, inspectable artifact has
standalone value, and it is a prerequisite for the deferred Rust
native-storage work: semantic pinning before any native commitment.

## What Changes

Add a public attribute explanations capability to `classcore.standard`,
in a new `explanations.py` module:

- `explain_attribute( target, name )` — returns the complete decision
  trace for attribute `name` on `target` (class or instance): active
  behaviors per evaluated level, and per-operation verdicts, each
  carrying exactly one decision.
- A closed decision hierarchy — `PermitByInapplicability`,
  `PermitByOmni`, `PermitByNames`, `PermitByPredicate`,
  `PermitByRegex`, and `Prohibit` — with typed payloads; `Verdict` and
  its per-operation subclasses (`AssignVerdict`, `DeleteVerdict`,
  `SurveyVerdict`) with derived permissibility; and
  `AttributeExplanation` — all immutable (frozen, concealed) records,
  with nested collections genuinely immutable. All operations, survey
  included, follow precedence semantics (omni, names, first matching
  predicate, first matching regex).
- The decision cascade in `behaviors.py` is extracted into pure helpers
  consumed by both the behavior cores and the explanations, so the
  helpers are shared wherever semantics coincide. Survey is the
  deliberate exception: the explanation reports normalized first-match
  semantics while the core preserves the once-per-matching-rule
  duplication, which is characterized as a defect with its repair
  deferred separately.

Scope boundaries for the first release: `explain_attribute` only (no
whole-object surveys); rule details render as plain strings with a
specified policy (no `eval` round-trip promised); explanations are
observational and do not bypass or alter concealment or immutability;
framework-internal and stdlib-machinery attributes are explainable and
marked as internal.

## Capabilities

### New Capabilities
- `attribute-explanations`: public API for explaining attribute behavior
  decisions — verdicts, decision rules, level semantics, record
  immutability, and internal-attribute marking.

### Modified Capabilities
<!-- No existing capability's requirements change; the behavior cascade
     extraction preserves current behavior exactly, including its known
     duplicate-yield quirk, which is characterized by tests and left for
     a separate repair. -->

## Impact

- New module `sources/classcore/standard/explanations.py`; records are
  defined there directly, without nomina aliases.
- `sources/classcore/standard/behaviors.py`: decision-cascade extraction
  (behavior-preserving refactor).
- README (taxonomy/API sections); towncrier fragment
  `+attribute-explanations.enhance.rst`.
- No public API changes to existing capabilities.
