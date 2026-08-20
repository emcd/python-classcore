## ADDED Requirements

### Requirement: Attribute Explanation

The `explain_attribute` function MUST return the decision trace for the
named attribute on the target: the active behaviors for each evaluated
level, and for each operation the applicable verdict. Assign and delete
verdicts MUST carry the single deciding rule under precedence — wildcard
or names membership, then the first matching predicate, then the first
matching regex — or no rule when the governing behavior is inactive.
Survey verdicts carry the ordered sequence of matched rules under union
semantics — where a names match short-circuits to the single names
rule and otherwise a rule may match any number of predicates and
regexes in evaluation order.
For class targets, the classes-level configuration MUST be evaluated.
For instance targets, the instances-level configuration MUST be
evaluated against the instance's class hierarchy. Survey verdicts MUST
explain the visibility of the supplied name only. Explanations MUST be
observational: they MUST NOT bypass or alter concealment or
immutability.

#### Scenario: Mutable attribute
- **WHEN** the active behaviors for the evaluated level lack
  immutability
- **THEN** the assign and delete verdicts MUST be permitted with no
  deciding rule

#### Scenario: Excluded by name
- **WHEN** the attribute name is in the exclusion names for the
  operation's level
- **THEN** the verdict MUST be permitted with a rule of kind `names` and
  detail rendering the name

#### Scenario: Excluded by regex
- **WHEN** an exclusion regex fullmatches the attribute name
- **THEN** the verdict MUST be permitted with a rule of kind `regex` and
  detail rendering the pattern text

#### Scenario: Excluded by predicate
- **WHEN** an exclusion predicate matches the attribute name
- **THEN** the verdict MUST be permitted with a rule of kind `predicate`
  and detail rendering the predicate's fully-qualified name, or
  `<anonymous>` when unavailable

#### Scenario: Wildcard exclusion
- **WHEN** the exclusion names for assign or delete equal `'*'`
- **THEN** the verdict MUST be permitted with a rule of kind `wildcard`
  and detail `'*'`

#### Scenario: Immutable attribute
- **WHEN** immutability is active and no rule permits the operation
- **THEN** the assign and delete verdicts MUST NOT be permitted and MUST
  carry no deciding rule

#### Scenario: Concealed attribute
- **WHEN** concealment is active and no visibles rule matches the name
- **THEN** the survey verdict MUST NOT be permitted and its matched
  sequence MUST be empty

#### Scenario: Survey multi-match
- **WHEN** the attribute name matches both a predicate and a regex and
  is not in the exclusion names
- **THEN** the survey matched sequence MUST contain both rules, in
  evaluation order

#### Scenario: Survey names short-circuit
- **WHEN** the attribute name is in the exclusion names for the survey
  level and also matches a predicate or regex
- **THEN** the survey matched sequence MUST contain only the single
  names rule, and predicates and regexes MUST NOT be evaluated for that
  name

#### Scenario: Survey wildcard
- **WHEN** concealment is active and the visibles names equal `'*'`
- **THEN** the survey verdict MUST be permitted with the single wildcard
  rule and no predicate or regex rules, because the wildcard
  short-circuits predicate and regex evaluation in the survey core

#### Scenario: Survey concealment inactive
- **WHEN** the active behaviors for the evaluated level lack concealment
- **THEN** the survey verdict MUST be permitted with an empty matched
  sequence

### Requirement: Record Immutability

The explanation records MUST be immutable: `AttributeExplanation`,
`AssignVerdict`, `DeleteVerdict`, `SurveyVerdict`, and `DecisionRule`
MUST NOT permit field assignment, and every nested collection they
contain MUST be an immutable structure.

#### Scenario: Frozen records
- **WHEN** a field is assigned on any explanation record
- **THEN** an immutability error MUST be raised

#### Scenario: Immutable nested collections
- **WHEN** the operations mapping, the behaviors mapping, or a matched
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
