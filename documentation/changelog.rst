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
