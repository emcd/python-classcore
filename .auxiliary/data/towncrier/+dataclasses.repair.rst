Standard: Ensure that behaviors tracking attribute is not part of comparisons,
hashes, or ``repr`` calculations for dataclasses. Attributes with "private"
names which resemble the CPython scheme for class-local (non-inheritable)
attributes can create confusion for the internal machinery of ``dataclasses``.
