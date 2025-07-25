.. vim: set fileencoding=utf-8:
.. -*- coding: utf-8 -*-
.. +--------------------------------------------------------------------------+
   |                                                                          |
   | Licensed under the Apache License, Version 2.0 (the "License");          |
   | you may not use this file except in compliance with the License.         |
   | You may obtain a copy of the License at                                  |
   |                                                                          |
   |     http://www.apache.org/licenses/LICENSE-2.0                           |
   |                                                                          |
   | Unless required by applicable law or agreed to in writing, software      |
   | distributed under the License is distributed on an "AS IS" BASIS,        |
   | WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. |
   | See the License for the specific language governing permissions and      |
   | limitations under the License.                                           |
   |                                                                          |
   +--------------------------------------------------------------------------+


*******************************************************************************
Release Notes
*******************************************************************************

.. towncrier release notes start

Classcore 1.8 (2025-07-23)
==========================

Enhancements
------------

- Standard: Modules: Allow certain modules to be excluded from reclassification.
  Also, implement cycle detection.


Repairs
-------

- Standard: Modules: Reclassify modules with proper depth-first traversal.


Classcore 1.7 (2025-07-08)
==========================

Enhancements
------------

- Standard: Add ``ignore_init_arguments`` decorator argument and
  ``instances_ignore_init_arguments`` class argument to support cases, such as
  inheritance from ``urllib.parse.ParseResult`` which inherits from ``tuple`` and
  overrides ``__new__`` instead of ``__init__``. In such cases, ``__new__``
  processes the instance production arguments rather than ``__init__``. However,
  the standard Python behavior is to present the arguments to both ``__new__``
  and ``__init__``, which is problematic since we always provide an ``__init__``
  head.


Classcore 1.6.1 (2025-07-01)
============================

Repairs
-------

- Fix deprecation warnings from finalize_module by refactoring to use private _reclassify_module implementation.


Classcore 1.6 (2025-07-01)
==========================

Enhancements
------------

- Add ``finalize_module`` function to combine Dynadoc docstring generation with module reclassification for immutability and concealment.


Notices
-------

- Deprecate ``reclassify_modules`` function. Use ``finalize_module`` instead.


Classcore 1.5.3 (2025-06-30)
============================

Repairs
-------

- Standard: Do not create duplicate slots for behaviors tracking.
- Standard: Ensure that behaviors tracking attribute is not part of comparisons,
  hashes, or ``repr`` calculations for dataclasses. Attributes with "private"
  names which resemble the CPython scheme for class-local (non-inheritable)
  attributes can create confusion for the internal machinery of ``dataclasses``.


Classcore 1.5.2 (2025-06-29)
============================

Repairs
-------

- Standard Classes: Ensure that Dynadoc decorator applies last, after any
  decorators which may potentially replace classes (e.g., ``dataclass( slots =
  True )``), so that the Dynadoc visitees weak set captures the correct reference
  to prevent multiple decoration.


Classcore 1.5.1 (2025-06-26)
============================

Repairs
-------

- Ensure the inheritance of replacement functions works via metaclasses and not
  just decorators.


Classcore 1.5 (2025-06-24)
==========================

Enhancements
------------

- Improve docstrings for various public type aliases. Also, drop ``Fname``
  references from public type aliases, such as ``Decorators`` so that they can be
  reused in downstream packages.


Repairs
-------

- Ensure that replacement implementations (``assigner_core``, ``deleter_core``,
  and ``surveyor_core``) are inherited so that behaviors do not regress to
  standard baseline behaviors in descendant classes.


Classcore 1.4.2 (2025-06-11)
============================

Repairs
-------

- Ensure that custom attributes namer is passed during recursive module
  reclassification.


Classcore 1.4.1 (2025-06-10)
============================

Repairs
-------

- Enforce attributes concealment and immutability on modules.


Classcore 1.4 (2025-06-10)
==========================

Enhancements
------------

- Fully support slotted classes. Bookkeeping attributes will now be in slots if
  class is slotted. Potential performance improvement since names do not need to
  be mangled for inheritance isolation.
- Publicly expose the ``TypedDict`` which tracks available metaclass arguments
  for the standard classes. This allows for easier extension by downstream
  packages and centralizes documentation on the metaclasses interface.


Repairs
-------

- Bugfix. Ensure idempotent execution in all scenarios: CPython vs PyPy, slotted
  vs non-slotted.
- Bugfix. Ensure that methods added by decoration properly respect class method
  resolution order (MRO) when they are not wrapping existing methods.


Classcore 1.3.1 (2025-06-07)
============================

Repairs
-------

- When reclassifying modules recursively, ensure that replacement class is
  included in recursive invocations.


Classcore 1.3 (2025-06-07)
==========================

Enhancements
------------

- Allow arbitrary class to be supplied to ``reclassify_modules``.
- Simplify production of class decorators.


Repairs
-------

- Bugfix. Propagate error class provider from metaclass to class decorators.


Classcore 1.2 (2025-06-05)
==========================

Enhancements
------------

- Fill out docstrings for all public classes and functions in package.
- Integrate with Dynadoc. Adds special introspection control which avoid
  docstring updates on immutable classes. Adds Dynadoc ``with_docstring``
  decorator to set of decorators on standard classes.


Repairs
-------

- Address Pyright complaints about metaclass arguments in ``class`` statements.


Classcore 1.1 (2025-05-01)
==========================

Repairs
-------

- Fix interaction with slotted dataclasses on Python 3.11+.
- Properly report test coverage by considering doctests too. (Not a user-facing
  fix; however important to note that coverage was 100% on initial release, but
  Github Actions workflow was not properly setup to capture coverage from
  doctests and so it only reported 95% coverage.)


Classcore 1.0 (2025-04-29)
==========================

Enhancements
------------

- Add support for CPython 3.10 to 3.13.
- Add support for PyPy 3.10.
- Base classes and class factory classes which provide standard behaviors
  (immutability of all attributes after initialization, concealment of all
  non-public attributes from ``dir``) by default. Can apply additional decorators
  and can tune for selective or total mutability or visibility. Enforce on class
  attributes and instance attributes.
- Class and dataclass decorators which apply a set of standard behaviors to
  classes so that they produce instances which are immutable and which only
  reveal public attributes by default. Decorators are tunable via arguments to
  provide selective or total attributes mutability and visibility as desired.
- Class decorator which accepts a sequence of other class decorators to apply.
  Reduces height of decorator stacks and improves their reusability.
- Decorators for modifying class factory classes (metaclasses) so that they can
  handle inline application of decorators during production of classes. This
  includes logic for the case where a decorator replaces a class rather than
  modifies it.
- Module class which enforces immutability and visibility limitation on module
  attributes. (Visibility restriction is to reveal only public attributes to
  ``dir``.) Also, conveience function which can reclassify a module or an entire
  package, recursively, to use this class.
