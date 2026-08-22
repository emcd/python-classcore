# attribute-explanations Specification

## Purpose

Explain attribute behavior decisions: expose the decision cascade —
active behaviors, per-operation verdicts, and the single decision that
determined each outcome — as inspectable, immutable records, so users
and tooling can ask why an attribute is mutable or immutable, visible
or concealed.

## Requirements
### Requirement: Attribute Explanation

The `explain_attribute` function MUST return the decision trace for the
named attribute on the target: the active behaviors for each evaluated
level, and for each operation the applicable verdict. Every verdict MUST
carry exactly one decision, drawn from a closed hierarchy: permitted by
inapplicability (the governing behavior is inactive), permitted by the
omni marker, permitted by names membership, permitted by a predicate,
permitted by a regex, or prohibited (the behavior is active and no rule
permits). All three operations — assign, delete, and survey — MUST
apply the same precedence semantics: omni, then names membership, then
the first matching predicate, then the first matching regex.

For class targets, the classes-level configuration MUST be evaluated.
For instance targets, the instances-level configuration MUST be
evaluated against the instance's class hierarchy. Survey verdicts MUST
explain the visibility of the supplied name only. Explanations MUST be
observational: they MUST NOT bypass or alter concealment or
immutability.

Note: survey explanations describe the normalized first-match semantics.
The survey core currently yields a name once per matching rule; that
duplication is characterized as a defect and deferred to a separate
repair, after which core behavior and explanation semantics coincide.

#### Scenario: Mutable attribute
- **WHEN** the active behaviors for the evaluated level lack
  immutability
- **THEN** the assign and delete verdicts MUST be permitted by
  inapplicability

#### Scenario: Excluded by name
- **WHEN** the attribute name is in the exclusion names for the
  operation's level
- **THEN** the verdict MUST be permitted by names, carrying the matched
  name

#### Scenario: Excluded by regex
- **WHEN** an exclusion regex fullmatches the attribute name
- **THEN** the verdict MUST be permitted by regex, carrying the pattern
  text

#### Scenario: Excluded by predicate
- **WHEN** an exclusion predicate matches the attribute name
- **THEN** the verdict MUST be permitted by predicate, carrying the
  predicate's fully-qualified name, or `<anonymous>` when unavailable

#### Scenario: Omni exclusion
- **WHEN** the exclusion names for assign or delete equal `'*'`
- **THEN** the verdict MUST be permitted by omni

#### Scenario: Immutable attribute
- **WHEN** immutability is active and no rule permits the operation
- **THEN** the assign and delete verdicts MUST be prohibited

#### Scenario: Concealed attribute
- **WHEN** concealment is active and no visibles rule matches the name
- **THEN** the survey verdict MUST be prohibited

#### Scenario: Survey multi-rule precedence
- **WHEN** the attribute name matches a predicate and a regex and is not
  in the exclusion names
- **THEN** the survey verdict MUST be permitted by the predicate, the
  first rule under precedence, and MUST NOT carry the regex

#### Scenario: Survey names precedence
- **WHEN** the attribute name is in the exclusion names for the survey
  level and also matches a predicate or regex
- **THEN** the survey verdict MUST be permitted by names and predicates
  and regexes MUST NOT be evaluated for that name

#### Scenario: Survey omni
- **WHEN** concealment is active and the visibles names equal `'*'`
- **THEN** the survey verdict MUST be permitted by omni and predicates
  and regexes MUST NOT be evaluated

#### Scenario: Survey concealment inactive
- **WHEN** the active behaviors for the evaluated level lack concealment
- **THEN** the survey verdict MUST be permitted by inapplicability

#### Scenario: Permissible derivation
- **WHEN** any verdict's decision is not prohibited
- **THEN** the verdict MUST report itself as permissible

### Requirement: Decision Payload Distinction

Decision payloads MUST be distinguished by type, so that a name which
coincides with a genus label or pattern text cannot be confused with
it. The names decision MUST carry the matched name; the predicate
decision MUST carry qualified-name text; the regex decision MUST carry
pattern text. Payloads MUST be plain text.

#### Scenario: Names payload collision
- **WHEN** the explained attribute is literally named `regex` and is
  permitted by names membership
- **THEN** the decision MUST be a names decision carrying the name
  `regex`, distinct from any regex decision carrying pattern text

### Requirement: Record Immutability

The explanation records MUST be immutable: the decision hierarchy, the
verdicts, and `AttributeExplanation` MUST NOT permit field assignment,
and every nested collection they contain MUST be an immutable
structure. Verdict permissibility MUST be derived from the decision,
not stored.

#### Scenario: Frozen records
- **WHEN** a field is assigned on any explanation record
- **THEN** an immutability error MUST be raised

#### Scenario: Immutable nested collections
- **WHEN** the operations mapping, the behaviors mapping, or a payload
  sequence is mutated
- **THEN** an error MUST be raised

### Requirement: Internal Attribute Marking

Explanations MUST mark attributes that are framework-owned — classcore
named or mangled attributes — or stdlib machinery — class mutables
exemption sets — as internal.

#### Scenario: Framework-internal attribute
- **WHEN** the explained name is framework-owned or stdlib machinery
- **THEN** the explanation MUST be marked internal

#### Scenario: User attribute
- **WHEN** the explained name is neither framework-owned nor stdlib
  machinery
- **THEN** the explanation MUST NOT be marked internal
