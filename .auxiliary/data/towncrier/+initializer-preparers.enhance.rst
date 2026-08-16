Add initialization preparers to class initializer factory.
``produce_class_initializer`` accepts a ``preparers`` sequence of
``ClassInitializationPreparer`` functions, invoked before initialization
ligation with mutable copies of the positional and nominative class
arguments. The new ``ClassInitializationPreparer`` and
``ClassInitializationPreparers`` type aliases in ``nomina`` document the
hook contract.
