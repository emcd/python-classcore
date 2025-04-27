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
                                   classcore
*******************************************************************************

.. image:: https://img.shields.io/pypi/v/classcore
   :alt: Package Version
   :target: https://pypi.org/project/classcore/

.. image:: https://img.shields.io/pypi/status/classcore
   :alt: PyPI - Status
   :target: https://pypi.org/project/classcore/

.. image:: https://github.com/emcd/python-classcore/actions/workflows/tester.yaml/badge.svg?branch=master&event=push
   :alt: Tests Status
   :target: https://github.com/emcd/python-classcore/actions/workflows/tester.yaml

.. image:: https://emcd.github.io/python-classcore/coverage.svg
   :alt: Code Coverage Percentage
   :target: https://github.com/emcd/python-classcore/actions/workflows/tester.yaml

.. image:: https://img.shields.io/github/license/emcd/python-classcore
   :alt: Project License
   :target: https://github.com/emcd/python-classcore/blob/master/LICENSE.txt

.. image:: https://img.shields.io/pypi/pyversions/classcore
   :alt: Python Versions
   :target: https://pypi.org/project/classcore/


🏭 A Python library package which provides **foundational class factories and
decorators** for providing classes with attributes immutability and concealment
and other custom behaviors.


Key Features ⭐
===============================================================================

* 🔧 **Class Customization**: Composable decorators and metaclasses providing
  classes with customizable behaviors.
* 🔒 **Attribute Immutability**: Standard collection of metaclasses and
  decorators to provide immutability for class and instance attributes, with
  support for selective mutability via names, regexes, or predicates.
* 👁️ **Attribute Concealment**: Standard collection of metaclasses and
  decorators to provide concealment for class and instance attributes, with
  support for selective visibility via names, regexes, or predicates.
* 📚 **Dataclass Integration**: Decorators like
  ``dataclass_with_standard_behaviors`` make standard Python dataclasses with
  immutability and concealment. (Unlike ``dataclass( frozen = True )``,
  attributes can still be manipulated via ``__post_init__`` when one of these
  decorators is applied.)
* 🧩 **Protocol Support**: Immutable protocol classes for defining static type
  interfaces, compatible with ``typing.Protocol``. Immutability and concealment
  are inherited by subclassed implementations of these protocols.
* 🗂️ **Module Reclassification**: Apply immutability and concealment to entire
  modules.


Installation 📦
===============================================================================

::

    pip install classcore


Note on Immutability 📢
===============================================================================

   Enforcement of immutability is quite difficult in Python. While this library
   encourages immutability by default, it can be circumvented by anyone who has
   intermediate knowledge of Python machinery and who is determined to
   circumvent the immutability. Use the library in the spirit of making
   programs safer, but understand that it cannot truly prevent unwanted state
   tampering.


Examples 💡
===============================================================================


Immutable Dataclasses 📊
-------------------------------------------------------------------------------

Seamlessly integrate with Python's dataclass system for immutable data classes.

.. code-block:: python

    from classcore.standard import DataclassObject

    class Point( DataclassObject ):
        x: int
        y: int

    point = Point( x = 10, y = 20 )
    point.x = 15  # ❌ Error


Selectively Mutable Classes 🔓
-------------------------------------------------------------------------------

Allow specific attributes to be modified while keeping others immutable.

.. code-block:: python

    import re
    from classcore.standard import with_standard_behaviors

    @with_standard_behaviors(
        mutables = ( 'counter', re.compile( r'temp_.*' ) )
    )
    class Analytics:
        def __init__( self ):
            self.data = { }  # Immutable
            self.counter = 0  # Mutable (explicitly allowed)
            self.temp_buffer = [ ]  # Mutable (matches regex pattern)

    analytics = Analytics( )
    analytics.counter = 1             # ✅ Works
    analytics.temp_buffer.append(42)  # ✅ Works
    analytics.data = { }              # ❌ Error


Module Immutability 📦
-------------------------------------------------------------------------------

Make modules (or entire packages) immutable to prevent modification of their
contents.

.. code-block:: python

    from classcore.standard import reclassify_modules

    reclassify_modules( __name__ )


Use Cases 🎯
===============================================================================

* 📊 **Data Transfer Objects**: Ensure data integrity with immutable DTOs.
* 🏛️ **API Interfaces**: Define stable, well-controlled interfaces.
* 🧩 **Plugin Systems**: Plugin systems with controlled extension points.
* 📦 **Frameworks**: Frameworks with controlled extension and modification.


`More Flair <https://www.imdb.com/title/tt0151804/characters/nm0431918>`_
===============================================================================

.. image:: https://img.shields.io/github/last-commit/emcd/python-classcore
   :alt: GitHub last commit
   :target: https://github.com/emcd/python-classcore

.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/copier-org/copier/master/img/badge/badge-grayscale-inverted-border-orange.json
   :alt: Copier
   :target: https://github.com/copier-org/copier

.. image:: https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg
   :alt: Hatch
   :target: https://github.com/pypa/hatch

.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit
   :alt: pre-commit
   :target: https://github.com/pre-commit/pre-commit

.. image:: https://microsoft.github.io/pyright/img/pyright_badge.svg
   :alt: Pyright
   :target: https://microsoft.github.io/pyright

.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
   :alt: Ruff
   :target: https://github.com/astral-sh/ruff

.. image:: https://img.shields.io/pypi/implementation/classcore
   :alt: PyPI - Implementation
   :target: https://pypi.org/project/classcore/

.. image:: https://img.shields.io/pypi/wheel/classcore
   :alt: PyPI - Wheel
   :target: https://pypi.org/project/classcore/


Other Projects by This Author 🌟
===============================================================================


* `python-absence <https://github.com/emcd/python-absence>`_
    - PyPI: `absence <https://pypi.org/project/absence/>`_

    🕳️ A Python library package which provides a **sentinel for absent values** - a falsey, immutable singleton that represents the absence of a value in contexts where ``None`` or ``False`` may be valid values.
* `python-accretive <https://github.com/emcd/python-accretive>`_
    - PyPI: `accretive <https://pypi.org/project/accretive/>`_

    🌌 A Python library package which provides **accretive data structures** - collections which can grow but never shrink.
* `python-falsifier <https://github.com/emcd/python-falsifier>`_
    - PyPI: `falsifier <https://pypi.org/project/falsifier/>`_

    🎭 A very simple Python library package which provides a **base class for falsey objects** - objects that evaluate to ``False`` in boolean contexts.
* `python-frigid <https://github.com/emcd/python-frigid>`_
    - PyPI: `frigid <https://pypi.org/project/frigid/>`_

    🔒 A Python library package which provides **immutable data structures** - collections which cannot be modified after creation.
* `python-icecream-truck <https://github.com/emcd/python-icecream-truck>`_
    - PyPI: `icecream-truck <https://pypi.org/project/icecream-truck/>`_

    🍦 **Flavorful Debugging** - A Python library which enhances the powerful and well-known ``icecream`` package with flavored traces, configuration hierarchies, customized outputs, ready-made recipes, and more.
* `python-mimeogram <https://github.com/emcd/python-mimeogram>`_
    - PyPI: `mimeogram <https://pypi.org/project/mimeogram/>`_

    📨 A command-line tool for **exchanging collections of files with Large Language Models** - bundle multiple files into a single clipboard-ready document while preserving directory structure and metadata... good for code reviews, project sharing, and LLM interactions.
