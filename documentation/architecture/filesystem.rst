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
Filesystem Organization
*******************************************************************************

This document describes the specific filesystem organization for the project,
showing how the standard organizational patterns are implemented for this
project's configuration. For the underlying principles and rationale behind
these patterns, see the `common architecture documentation
<https://raw.githubusercontent.com/emcd/python-project-common/refs/tags/docs-1/documentation/common/architecture.rst>`_.

Project Structure
===============================================================================

Root Directory Organization
-------------------------------------------------------------------------------

The project implements the standard filesystem organization:

.. code-block::

    python-classcore/
    ├── LICENSE.txt              # Project license
    ├── README.rst               # Project overview and quick start
    ├── pyproject.toml           # Python packaging and tool configuration
    ├── documentation/           # Sphinx documentation source
    ├── sources/                 # All source code
    ├── tests/                   # Test suites
    └── .auxiliary/              # Development workspace

Source Code Organization
===============================================================================

Package Structure
-------------------------------------------------------------------------------

The main Python package follows the standard ``sources/`` directory pattern:

.. code-block::

    sources/
    └── classcore/                   # Main Python package
        ├── __/                      # Centralized import hub
        │   ├── __init__.py          # Re-exports core utilities
        │   ├── imports.py           # External library imports
        │   ├── nomina.py            # Naming constants
        │   └── doctab.py            # Documentation table fragments
        ├── __init__.py              # Package entry point
        ├── py.typed                 # Type checking marker
        ├── decorators.py            # Class decorator utilities
        ├── exceptions.py            # Package exception classes
        ├── factories.py             # Metaclass factory functions
        ├── nomina.py                # Public naming types and utilities
        ├── utilities.py             # Class manipulation utilities
        └── standard/                # Standard behaviors subpackage
            ├── __.py                # Inherits parent imports
            ├── __init__.py          # Subpackage entry point
            ├── behaviors.py         # Immutability and concealment logic
            ├── classes.py           # Standard metaclasses and base classes
            ├── decorators.py        # Standard class decorators
            ├── dynadoc.py           # Documentation configuration
            ├── modules.py           # Module reclassification utilities
            └── nomina.py            # Standard-specific naming types

Module Responsibilities
-------------------------------------------------------------------------------

Core Package (``sources/classcore/``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``__/__init__.py``
    Re-exports commonly used imports from ``imports.py`` for convenient access
    via ``from . import __`` in all package modules.

``__/imports.py``
    Centralizes all external library imports. Provides abbreviated aliases for
    frequently used types and modules (e.g., ``cabc`` for
    ``collections.abc``, ``typx`` for ``typing``).

``__/nomina.py``
    Package-specific naming constants and utilities used internally by the
    ``__`` import hub.

``__/doctab.py``
    Documentation table with reusable fragments for dynadoc interpolation.

``__init__.py``
    Package entry point. Exports public API, applies standard behaviors to
    package module, sets version.

``decorators.py``
    Class decorator utilities:

    - ``apply_decorators``: Apply decorator sequences with class replacement
      handling
    - ``decoration_by``: Compose multiple decorators
    - ``produce_class_construction_decorator``: Create metaclass ``__new__``
      decorators
    - ``produce_class_initialization_decorator``: Create metaclass ``__init__``
      decorators

``exceptions.py``
    Package exception hierarchy. All exceptions use standard behaviors
    (immutability and concealment) themselves.

``factories.py``
    Metaclass component factories:

    - ``produce_class_constructor``: Generate customizable ``__new__`` with
      hooks
    - ``produce_class_initializer``: Generate customizable ``__init__`` with
      hooks

``nomina.py``
    Public naming types, type aliases, and protocols used throughout the
    package. Defines interfaces for hooks, verifiers, and core functions.

``utilities.py``
    Class manipulation utilities:

    - ``mangle_name``: Create unique attribute names
    - ``getattr0/setattr0/delattr0``: Mangled attribute access
    - ``repair_class_reproduction``: Fix closures after class replacement
    - ``describe_object``: Generate error message descriptions

Standard Subpackage (``sources/classcore/standard/``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``__.py``
    Inherits all imports from parent ``__`` via ``from ..__ import *``.
    Demonstrates the cascading import pattern for subpackages.

``__init__.py``
    Subpackage entry point. Exports all standard classes, decorators, and
    utilities. Applies standard behaviors to subpackage module.

``behaviors.py``
    Core implementation of standard behaviors:

    - ``assign_attribute_if_mutable``: Conditional attribute assignment
    - ``delete_attribute_if_mutable``: Conditional attribute deletion
    - ``survey_visible_attributes``: Filter attributes for ``dir()``
    - Verifier processing for names, regexes, and predicates

``classes.py``
    Standard metaclasses and base classes:

    - ``Class`` / ``Object``: Standard class with full behaviors
    - ``Dataclass`` / ``DataclassObject``: Auto-dataclass with behaviors
    - ``Protocol`` / ``ProtocolObject``: Protocol with behaviors
    - Mutable variants for each

``decorators.py``
    Standard class decorators:

    - ``class_with_standard_behaviors``: Apply behaviors to existing class
    - ``dataclass_with_standard_behaviors``: Create dataclass with behaviors
    - ``protocol_with_standard_behaviors``: Create protocol with behaviors
    - ``class_factory``: Generic factory for creating custom metaclasses

``dynadoc.py``
    Dynadoc configuration for standard behaviors. Provides documentation
    fragments that describe behaviors automatically applied to classes.

``modules.py``
    Module reclassification utilities:

    - ``reclassify_module``: Apply behaviors to single module
    - ``finalize_module``: Complete module initialization (used by package)

``nomina.py``
    Standard-specific naming types and constants. Defines behavior labels
    and attribute naming functions.

All package modules use the standard ``__`` import pattern as documented
in the common architecture guide.

Component Integration
===============================================================================

Import Hub Usage
-------------------------------------------------------------------------------

All modules access common dependencies through the ``__`` import hub:

.. code-block:: python

    # In any module at sources/classcore/
    from . import __

    # Use abbreviated imports
    def example( items: __.cabc.Sequence[ str ] ) -> __.typx.Any:
        return __.funct.partial( some_function, items )

This pattern:

- Eliminates redundant import statements
- Provides consistent naming across modules
- Centralizes import changes to ``__/imports.py``
- Reduces module namespace pollution

Subpackage Extension
-------------------------------------------------------------------------------

The ``standard/`` subpackage demonstrates the cascading import pattern.
Its ``__.py`` inherits parent imports and can add specialized dependencies:

.. code-block:: python

    # sources/classcore/standard/__.py
    from ..__ import *              # Inherit all parent imports
    from ..exceptions import *      # Add package exceptions

Modules in ``standard/`` use the same import pattern but gain access to both
parent and subpackage-specific imports.

Architecture Evolution
===============================================================================

This filesystem organization provides a foundation that architect agents can
evolve as the project grows. For questions about organizational principles,
subpackage patterns, or testing strategies, refer to the comprehensive common
documentation:

* `Architecture Patterns <https://raw.githubusercontent.com/emcd/python-project-common/refs/tags/docs-1/documentation/common/architecture.rst>`_
* `Development Practices <https://raw.githubusercontent.com/emcd/python-project-common/refs/tags/docs-1/documentation/common/practices.rst>`_
* `Test Development Guidelines <https://raw.githubusercontent.com/emcd/python-project-common/refs/tags/docs-1/documentation/common/tests.rst>`_
