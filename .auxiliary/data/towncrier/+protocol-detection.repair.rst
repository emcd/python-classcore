Fix runtime protocol recognition for subclasses of classcore protocol
base classes. Previously, ``typing_extensions.Protocol.__init_subclass__``
set ``_is_protocol = False`` on these subclasses due to an identity check
that did not recognize classcore's own protocol base classes. Subclasses
are now properly detected via structural analysis.
