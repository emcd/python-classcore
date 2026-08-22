## Context

Enforcement already scopes machinery exemptions per metaclass:
`class_mutables = abc_class_mutables` is declared only on ABC-carrying
metaclasses, so a plain class naming an attribute `_abc_cache` receives
no exemption. Marking, however, matches names globally in
`is_internal_name`, which would mislabel that same attribute. Both
downstream inventories (Accretive, Frigid, 2026-08-22) report static,
uniformly prefixed internal names produced by `calculate_attrname`
namers — identical in structure to classcore's own — with no
MRO-dependent names. `_dynadoc_fragments_` is confirmed by the Dynadoc
owner as a documented user-settable declaration convention.

## Goals / Non-Goals

**Goals:**
- Truthful internal marking for classcore, stdlib machinery, and
  downstream frameworks' names, with responsibility carried by the
  machinery that builds each class.
- Marking scope mirroring enforcement scope (per-metaclass, inherited).
- Detector registration through the existing `attributes_namer` seam —
  no new factory/decorator argument slots.
- Determiners pure `(name) -> bool`-style callables (native-storage
  constraint).

**Non-Goals:**
- Attribution on explanation records (which framework's contribution
  marked the name) — deliberate 2.0 revisit.
- A global fixed-name registry or fallback tier (no consumer exists;
  additive later if one appears).
- Wiring contributions into `class_mutables` enforcement decisions.
  (Contributions become the shared store that enforcement *could* later
  read, but enforcement semantics are unchanged here.)
- MRO-dependent registrant signatures beyond what the ABC set needs
  internally.

## Decisions

- Metaclass-carried contributions attach at factory/decoration time:
  the factory closure records its namer's detector; `AbstractClass`
  wiring contributes the ABC set. Subclasses in any package inherit
  contributions via the metaclass, which resolves multi-package
  inheritance by construction.
- The namer detector attribute is canonically `is_internal_name`,
  mirroring the module-level function it specializes. Namer detectors
  over prefix arguments: a detector callable validates
  shape, not just prefix — classcore's mangled names carry 64-hex
  digest suffixes, and a detector can require them, so a lookalike
  name without a valid digest does not mark. Classcore's
  `calculate_attrname` is annotated as the model implementation.
- `is_internal_name(target, name)`: marking consults the metaclass
  MRO. For a class target `C` this is `type(C).__mro__`; for an
  instance target `x` it is `type(type(x)).__mro__` — the metaclass
  MRO of the instance's type. Note `type(x).__mro__` is the *class*
  MRO (C's bases) and never enumerates the metaclass where
  contributions live; the double-type transformation is required and
  is an explicit test scenario. Cost is one MRO walk per call;
  cacheable later without API change.

- Namer detector contract (canonical): an optional `is_internal_name`
  attribute on the namer callable, signature `(name: str) -> bool`,
  invoked on full stored attribute names. Exactly two name forms
  exist, and detectors accept them as their emitted shapes dictate:
  (1) static stems — `_classcore_{level}_{core}_`, trailing
  underscore, no digest (e.g. `_classcore_class_behaviors_`);
  (2) mangled names — stem followed immediately by exactly 64
  lowercase hexadecimal digits, NO trailing underscore after the
  digest, because `utilities.mangle_name` appends the digest directly
  (e.g. `_classcore_class_in_progress_` + digest; verified form:
  `_classcore_class_in_progress_6e6f...7ee`). Transient mangled
  names (construction markers) match form (2) while they exist.
  Grammar-constrained static stems (mirroring the model downstream
  confirmed for Accretive): a stem marks internal only when its level
  is one of the closed set class, classes, instance, instances, and
  its core is one of the enumerated set classcore generates —
  behaviors, construction_arguments, dynadoc_configuration,
  in_progress, mutables_names, mutables_predicates, mutables_regexes,
  visibles_names, visibles_predicates, visibles_regexes,
  assigner_core, deleter_core, surveyor_core. The enumeration lives
  beside the namer in the same module, and a consistency test asserts
  every namer call site's arguments are covered. Mangled forms: two
  stems are stored through the mangling accessors and therefore carry
  exactly 64 lowercase hex with no trailing underscore —
  `_classcore_class_behaviors_<digest>` (class behaviors, stored via
  setattr0 by the initialization completer) and
  `_classcore_class_in_progress_<digest>` (the construction marker).
  The static `_classcore_instance_behaviors_` form is distinct and
  unmangled; instance-level storage does not use digest mangling on
  standard classes (verified against Object.__dict__). Names with the prefix
  that fail the grammar — `_classcore_not_a_generated_core_`,
  `_classcore_class_lookalike_`, malformed digests (wrong length,
  uppercase, trailing underscore), `_classcore_class_in_progress_`
  bare stem — MUST NOT match. The classcore model detector is the
  reference implementation of this convention. Downstream detectors
  follow their own emitted shapes: Accretive requires its static-stem
  forms AND its exact mangled-progress form
  (`_accretive_class_in_progress_<64hex>`), because that marker is
  generated by the shared classcore factory under Accretive's namer;
  Frigid requires the same three-form family for `_frigid_`
  (confirmed forms: `_frigid_{level}_{core}_`;
  `_frigid_class_behaviors_{64hex}`;
  `_frigid_class_in_progress_{64hex}`), mirroring classcore's two
  mangled stems. Frigid additionally notes
  transient names may appear in `__protocol_attrs__` rather than
  `__dict__` post-construction; marking applies wherever the name is
  explained, independent of storage location.
- `_dynadoc_fragments_` excluded everywhere: public declaration
  convention, analogous to `__slots__`.
- No global state, no locking, no registry injection. Tests construct
  metaclasses with contributions directly.

## Risks / Trade-offs

- `is_internal_name` signature change is free only pre-release; the
  change targets the 1.13 window (noted in the proposal).
- A downstream namer without a detector contributes nothing — its names
  stay unmarked, which is the status quo and fails safe (a false
  "internal" claim is worse than a false "user" claim; the latter is
  today's behavior for downstreams anyway).
- Metaclass MRO consultation on every explanation adds a small constant
  cost; acceptable for a diagnostics API, cacheable if profiling ever
  demands.
