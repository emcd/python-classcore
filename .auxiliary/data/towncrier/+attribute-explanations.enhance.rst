Add attribute explanations: ``explain_attribute`` in
``classcore.standard.explanations`` returns the decision trace for one
attribute of one target — active behaviors per evaluated level and, for
each operation, a verdict carrying its decision under precedence
semantics: permission by inapplicability, omni, names, predicate, or
regex, or prohibition. Decision payloads are typed per decision class,
explanation records are immutable with immutable nested collections,
and framework-owned and stdlib-machinery attributes are marked
internal.
