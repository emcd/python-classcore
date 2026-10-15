Attribute internal marking now follows metaclass-carried
contributions: the attribute namer's ``is_internal_name`` detector
marks framework names (grammar-constrained static stems and both
digest-mangled forms), the abstract-base wiring marks stdlib ABC
machinery names only where that machinery operates, and downstream
``class_factory`` namers contribute their own detectors, so
``explain_attribute`` reports downstream framework attributes
truthfully. ``is_internal_name`` takes the target and consults the
metaclass chain; lookalike names that fail the detector grammar stay
unmarked, and the public ``_dynadoc_fragments_`` declaration
convention is never marked.
