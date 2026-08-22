## 1. Namer Detector Convention

- [ ] 1.1 Annotate classcore's `calculate_attrname` namer with an
      `is_internal_name` detector attribute implementing the
      grammar-constrained convention: closed level set, enumerated
      core set, and both exact mangled forms
      (`class_behaviors` and `class_in_progress` stems with 64
      lowercase hex); prefix lookalikes that fail the grammar do not
      mark
- [ ] 1.2a Add a consistency test asserting every namer call site's
      level and core arguments are covered by the detector grammar
- [ ] 1.2 Document the namer detector convention: an optional
      `is_internal_name` attribute on the namer, read by factory
      wiring; no new factory/decorator arguments


## 2. Contribution Wiring

- [ ] 2.1 Record the namer's detector as a metaclass contribution at
      factory/decoration time, inherited by produced metaclasses
- [ ] 2.2 Contribute the stdlib ABC machinery set on the
      `AbstractClass` wiring (mirroring `class_mutables` scoping)
- [ ] 2.3 Exclude `_dynadoc_fragments_` from every contribution

## 3. Marking Consultation

- [ ] 3.1 Change `is_internal_name` to accept the target and consult
      the metaclass method resolution order for contributions
- [ ] 3.2 Integrate consultation into `explain_attribute`; instance
      targets consult `type(type(x)).__mro__` (the metaclass MRO of
      the instance's type), never `type(x).__mro__` (the class MRO,
      which does not enumerate the metaclass)

## 4. Conformance and Documentation

- [ ] 4.1 Scenario tests: framework-internal coverage of static stems
      and both mangled forms (`class_behaviors` and
      `class_in_progress` digests), downstream detector, machinery
      name without machinery, inherited contribution across packages,
      instance-target metaclass-chain consultation (proving the
      double-type lookup), shape-invalid lookalikes, declaration
      convention exclusion, plain user attribute
- [ ] 4.2 Update the internal-marking section of the README; add the
      towncrier fragment
- [ ] 4.3 Full validation: make-all and the PyPy environment; strict
      OpenSpec validation
