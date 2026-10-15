Expose the class-level mutability exemption sets publicly from
``classcore.standard.nomina``: ``abc_class_mutables`` (stdlib ABC
machinery) and ``typing_class_mutables`` (stdlib typing machinery,
including the CPython 3.15 ``__typing_is_deprecated_inherited_runtime_protocol__``
dunder). Downstream packages share these sets by reference instead of
carrying copies which can drift, as Frigid's did on Python 3.15. The
canonical home remains ``classcore.standard.__``; the nomina aliases
are identically the same objects.
