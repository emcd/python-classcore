Standard: Add ``ignore_init_arguments`` decorator argument and
``instances_ignore_init_arguments`` class argument to support cases, such as
inheritance from ``urllib.parse.ParseResult`` which inherits from ``tuple`` and
overrides ``__new__`` instead of ``__init__``. In such cases, ``__new__``
processes the instance production arguments rather than ``__init__``. However,
the standard Python behavior is to present the arguments to both ``__new__``
and ``__init__``, which is problematic since we always provide an ``__init__``
head.
