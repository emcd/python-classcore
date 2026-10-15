Permit CPython 3.15+ typing machinery dunder on immutable classes.
``typing`` sets ``__typing_is_deprecated_inherited_runtime_protocol__``
during class decoration and in the ``runtime_checkable`` decorator; the
class-level immutability behavior now exempts it, and the protocol
member snapshot excludes it from ``__protocol_attrs__``.
