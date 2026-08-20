Add attribute explanations: ``explain_attribute`` in
``classcore.standard.explanations`` returns the decision trace for one
attribute of one target — active behaviors per evaluated level and, for
each operation, a verdict carrying the deciding rule under precedence
semantics (assign, delete) or all matched rules under union semantics
(survey). Explanation records are immutable with immutable nested
collections, rule details render as stable text, and framework-owned
and stdlib-machinery attributes are marked internal.
