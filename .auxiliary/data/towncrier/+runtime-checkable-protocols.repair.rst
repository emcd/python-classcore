Fix ``typing.runtime_checkable`` support for classcore protocol classes.
``@runtime_checkable`` can now be applied via the ``decorators=``
metaclass argument or directly after class creation.
``isinstance()`` structural subtyping works correctly with
``@runtime_checkable`` classcore protocols.
