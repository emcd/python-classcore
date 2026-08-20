## 1. Decision Cascade Extraction

- [x] 1.1 Write characterizing tests for the current core behavior in
  `behaviors.py`, including the survey duplicate-yield quirk (a name
  matching a predicate and a regex is yielded twice)
- [x] 1.2 Extract the assign/delete decision cascade and the survey
  matching logic into pure helpers with explicitly designed boundaries,
  consumed by the cores; behavior MUST be preserved exactly
- [x] 1.3 Validate: full suite on develop and qa.pypy3.11 unchanged

## 2. Explanations Module

- [x] 2.1 Define the explanation records directly in
  standard/explanations.py (AttributeExplanation, AssignVerdict,
  DeleteVerdict, SurveyVerdict, DecisionRule) with documentation
  annotations; nomina aliases omitted as the records are classes, not
  aliases, and are colocated with explain_attribute
- [x] 2.2 Implement `standard/explanations.py`: the records as frozen,
  concealed classes with genuinely immutable nested collections, and
  `explain_attribute( target, name )` built on the extracted helpers
- [x] 2.3 Implement internal-attribute marking: classcore-owned
  named/mangled attributes and stdlib class-mutables exemption sets

## 3. Specification Conformance

- [x] 3.1 Tests for every scenario in the attribute-explanations delta:
  verdict semantics per operation and precedence, union semantics for
  survey, level evaluation for class versus instance targets,
  observational (non-bypass) behavior, record and nested immutability,
  internal marking
- [x] 3.2 Validate detail rendering policy: name/`'*'`/pattern text/
  qualified predicate name with `<anonymous>` fallback

## 4. Documentation

- [x] 4.1 README: taxonomy and API sections for the explanations module
- [x] 4.2 Towncrier fragment `+attribute-explanations.enhance.rst`
- [x] 4.3 Full validation: make-all plus qa.pypy3.11
