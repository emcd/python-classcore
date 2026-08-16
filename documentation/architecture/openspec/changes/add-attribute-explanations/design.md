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
- Naming: `DecisionRule` (Latinate; not Germanic `DecidingRule`).
- Verdict shapes follow operation semantics: assign/delete short-circuit
  by precedence (wildcard/names, first matching predicate, first matching
  regex) and carry a single `decider` or `None` when the governing
  behavior is inactive; survey is union logic and carries the ordered
  sequence of all matched rules. The survey core has two early-return
  paths that the verdict shapes must distinguish: concealment inactive
  (permitted, empty matched sequence, no governing rule) and concealment
  active with visibles wildcard (permitted, the single wildcard rule and
  no predicate or regex matches, because the wildcard short-circuits
  predicate and regex evaluation).
- Level semantics: class targets evaluate the `classes`-level
  configuration; instance targets evaluate the `instances`-level
  configuration against the instance's class hierarchy. Exclusion
  configuration uses the raw level; the normalized behavior level is
  recorded separately on the explanation.
- `DecisionRule.detail` rendering policy: names/wildcard — the name or
  `'*'`; regex — pattern text; predicate — fully-qualified name with an
  `'<anonymous>'` fallback.
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
