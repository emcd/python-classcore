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

:tocdepth: 4


*******************************************************************************
API
*******************************************************************************


Package ``classcore``
===============================================================================

Foundational class factories and decorators.

Provides ability to create class decorators and metaclasses with customization
hooks. The metaclasses can apply class decorators inline during the class
construction and initialization process, properly handling cases where
decorators replace classes (e.g., ``dataclasses.dataclass( slots = True )``).
They also backport the repair mechanism from newer versions of CPython to
ensure that the class closure cells are rectified on replaced classes, so that
zero-argument ``super`` calls function correctly in them.

The ``classcore.standard`` subpackage is an example of the decorators and
customization hooks being used to provide a set of practical classes and class
decorators. Furthermore, the exception classes in the
:py:mod:`classcore.exceptions` module inherit from one of the standard classes,
making both the exception classes, themselves, and their instances immutable
and concealing their non-public attributes to reduce API noise. I.e., this
package "eats its own dog food" and provides practical examples in so doing.

This package is not as magical as it might seem. It does **not** rely on any
``exec`` or ``eval`` calls and it does **not** do anything with ``ctypes`` or
similar surgical instruments. It relies completely on the documented Python
data model and the machinery that it provides. While it is true that
metaclasses can be tricky, this package is developed with a deep,
highly-evolved understanding of them. We seek simplicity over cleverness and
maintain robust tests across multiple Python implementations and versions. The
package is also very clean in terms of static type checking (via Pyright).


Module ``classcore.decorators``
-------------------------------------------------------------------------------

.. automodule:: classcore.factories


Module ``classcore.factories``
-------------------------------------------------------------------------------

.. automodule:: classcore.factories


Module ``classcore.exceptions``
-------------------------------------------------------------------------------

.. automodule:: classcore.exceptions


Module ``classcore.nomina``
-------------------------------------------------------------------------------

.. automodule:: classcore.nomina


Module ``classcore.utilities``
-------------------------------------------------------------------------------

.. automodule:: classcore.utilities


Subpackage ``classcore.standard``
===============================================================================

Decorators and class factories which imbue concealment and immutability.

Concealment restricts the visibility of attributes on classes and their
instances. By default, only public attributes (ones which do not start with
``_``) are revealed for :py:func:`dir` calls. This behavior can be overriden by
supplying visibility verifiers as a decorator factory argument or metaclass
argument. These can be a sequence of attribute names, regular expression
:py:class:`re.Pattern` objects which match attribute names, or predicate
functions which match attribute names. Or, total visibility (per the Python
default) can be achieved by supplying ``visibles = '*'`` instead of a sequence
of verifiers.

Immutability prevents assignment (including reassignment) or deletion of
attrubtes on classes and their instances after they have been completely
initialized. In addition to any standard Python class, this can be applied to
dataclasses, allowing them to use ``__post_init__`` to set attributes, which
``dataclasses.dataclass( frozen = True )`` prevents. The immutability behavior
can be overridden by supplying mutability verifiers as a decorator factory
argument or metaclass argument. These behave similarly to the visibility
verifiers described above.

Hooks to modify the concealment and immutability behaviors are also available.


Module ``classcore.standard.classes``
-------------------------------------------------------------------------------

.. automodule:: classcore.standard.classes


Module ``classcore.standard.decorators``
-------------------------------------------------------------------------------

.. automodule:: classcore.standard.decorators


Module ``classcore.standard.modules``
-------------------------------------------------------------------------------

.. automodule:: classcore.standard.modules


Module ``classcore.standard.behaviors``
-------------------------------------------------------------------------------

.. automodule:: classcore.standard.behaviors


Module ``classcore.standard.nomina``
-------------------------------------------------------------------------------

.. automodule:: classcore.standard.nomina
