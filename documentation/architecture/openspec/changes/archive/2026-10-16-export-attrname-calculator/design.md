# Design: Export Attrname Calculator

## Context

`AttrnameCalculator` in `classcore.__.nomina` is the reference
implementation of the attribute-namer convention: `__call__`
generates `_{package}_{level}_{core}_` names and `is_internal_name`
detects them (plus digest-mangled forms), both closed over a
module-level `package_name`. Downstream packages (Frigid 4.4) need
the same grammar under their own prefix. A local mirror reintroduces
the drift failure mode already observed with the mutables sets.
Stakeholders: Classcore Owner (implements), Frigid Owner (consumes,
Tier-1 reviewer), Advisor (Cc, design input given).

## Goals / Non-Goals

Goals: one public import path for the calculator; prefix
configuration without method overrides; grammar stays single-sourced
and evolvable; no behavior change for classcore's own names.
Non-goals: no grammar snapshot exports; no shared test harness; no
changes to the contributions collection mechanism or the
`calculate_contribution_name` function.

## Decisions

1. **Constructor `package_name` argument (default: current module
   derivation), not class attribute or factory.** Constructor
   configuration makes registration-time stability structural: the
   value is fixed where the namer is created, and nothing invites
   later reassignment. Class-attribute form was considered (matches
   framework class-attribute configuration idiom; preserves IS-A
   without instantiation) but rejected: mutable attributes are
   exactly what this package family avoids, and Frigid needs no
   subclass at all — instantiation suffices. Factory
   (`produce_attrname_calculator`) was considered and rejected: a
   new public function for one value adds surface without function.
2. **Grammar containers stay private.** `_levels`, `_cores`,
   `_mangled_cores`, `_hex_digits` remain module-private in
   `classcore.__.nomina`. The public promise is the shared
   naming/detection convention, not frozen vocabulary. Documented
   as reserved framework grammar: shape conformance, not proof an
   attribute was generated.
3. **Preserve the generation/detection asymmetry.** `__call__`
   emits the two class-level mangling stems; the detector accepts
   only their completed 64-hex digest forms, never bare stems.
   Parameterization must not require
   `detector( __call__( ... ) )` round-trips.
4. **Alias export, as with the mutables sets.**
   `AttrnameCalculator = __.AttrnameCalculator` in
   `classcore.standard.nomina`; canonical home stays
   `classcore.__.nomina`. Identity (not copy) preserved.
5. **Per-project conformance tests, no shared harness.** Upstream
   tests the public calculator (positive/negative/mangled cases
   plus the no-override downstream-subclass form); Frigid inventories
   its own call sites. The existing AST drift scan stays
   per-project (it covers only bare-name literal calls).

## Risks / Trade-offs

- [Risk] Downstream mutates `package_name` post-registration, so
  previously generated names stop matching. → Mitigation: document
  as construction-time configuration; no setter or helper invites
  mutation.
- [Risk] Grammar evolution breaks downstream expectations (new core
  classifies additional names as internal). → Mitigation: that IS
  the lockstep contract; document that classification follows the
  newest grammar by construction.
- [Risk] `type`-statement-style laziness or introspection
  differences. → Mitigation: none needed; plain class, no aliases
  involved.

## Migration Plan

Additive only: existing `AttrnameCalculator()` behavior unchanged;
existing downstream pattern (subclass + overrides) keeps working.
No migration, no rollback beyond revert.

## Open Questions

- None for implementation. Frigid (Tier-1) may surface
  consumption-shape feedback at review; Advisor may re-enter.
