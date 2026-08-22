## Context

Attribute behavior decisions are computed in
`standard/behaviors.py` by three cores — assign, delete, survey — each
walking the same cascade: read the active-behaviors set for the level
(labels `immutability` and `concealment`), then consult per-level
exclusion configuration (names with `'*'` wildcard, predicates,
regexes) for the operation (mutables for assign/delete, visibles for
survey). Cores receive the raw level (`instances`/`classes`) and use it
for exclusion configuration lookup, normalizing only the active-behaviors
lookup. The survey core additionally has a known quirk: its per-name
matching loops `continue` the inner loop only, so a name matching
multiple rules is yielded multiple times; CPython `dir()` does not
deduplicate custom `__dir__` output, so duplicates reach users.

## Goals / Non-Goals

**Goals:**
- Extract the decision cascade into pure helpers shared by the cores and
  the new explanations API, preserving behavior exactly.
- Provide `explain_attribute( target, name )` returning immutable records
  with genuine nested immutability.
- Specify stable, deterministic rendering for rule details.
- Mark framework-internal and stdlib-machinery attributes.

**Non-Goals:**
- Whole-object explanation sweeps (`survey_explanations`).
- Repairing the survey duplicate-yield quirk (separate change).
- Caching/performance work (`/8` follow-up; claims deferred until
  extraction boundaries exist and are profiled).
- Error-message integration (deferred, separately decided).
- `eval`-able rule detail strings.

## Decisions

- Module: `standard/explanations.py` (Latinate, matches the
  `explain_attribute` verb; avoids stdlib `inspect` confusion).
- Naming: decision hierarchy PermitBy* / Prohibit (Latinate verbs);
  `PermitByOmni` follows the package's `*Omni` wildcard vocabulary
  (BehaviorExclusionNamesOmni).
- Verdict shapes follow a single closed decision hierarchy for all
  three operations: PermitByInapplicability (behavior inactive),
  PermitByOmni, PermitByNames, PermitByPredicate, PermitByRegex, and
  Prohibit (behavior active, nothing permitted). All operations apply
  precedence semantics (omni, names, first predicate, first regex).
  Permissibility is a derived property of the verdict
  (not isinstance(decision, Prohibit)) — no stored boolean, no
  __bool__. Payloads are typed per decision (name, qualified predicate
  text, pattern text) so a name colliding with a genus label or pattern
  cannot be confused with one.
- Survey first-match is an owner decision reversing the earlier
  union-trace design: the union trace existed to faithfully describe
  the duplicate-yield behavior, which is itself characterized as a
  defect with normalization deferred. Specifying the explanation to
  the normalized (first-match) semantics now makes explanation and
  repaired behavior coincide; until the repair, the survey core keeps
  survey_matched_rules internally to reproduce current behavior.
- Level semantics: class targets evaluate the `classes`-level
  configuration; instance targets evaluate the `instances`-level
  configuration against the instance's class hierarchy. Exclusion
  configuration uses the raw level; the normalized behavior level is
  recorded separately on the explanation.
- Decision payload policy: names decisions carry the matched name;
  predicate decisions carry qualified-name text with an `'<anonymous>'`
  fallback; regex decisions carry pattern text; omni and prohibition
  decisions carry no payload. Payloads are typed per decision class,
  so a name colliding with a pattern or label cannot be confused.
- `AttributeExplanation.internal` marks classcore-owned named/mangled
  attributes and stdlib ABC machinery (class mutables exemption sets).
- Survey duplicate-yield is preserved by the extraction and
  characterized by a test asserting current behavior.

## Risks / Trade-offs

- Extraction refactor could subtly change core behavior; mitigated by
  characterizing tests (including the duplicate-yield case) written
  before and kept after the refactor.
- String-only rule details limit programmatic consumers; accepted for
  serializability and implementation hiding.
- The explanations API expands public surface that a future native
  backend must keep answering; accepted as the semantic pinning that
  makes that migration safe.
