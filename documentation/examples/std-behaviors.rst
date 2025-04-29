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
Standard Behaviors
*******************************************************************************


Mutability
===============================================================================

.. todo:: Contents


Visibility
===============================================================================

Visibility can be customized for both the attributes of a class and the
attributes of its instances. This is done by supplying an argument which is a
sequence of attribute names, compiled regular expressions, or predicates.
Standard Python visibility can be granted to a class which would have standard
concealment of attributes. This is done by supplying the omnivisibility marker
(``*``) as an argument instead of a sequence. Attribute names are strings;
compiled regular expressions are :py:class:`re.Pattern` objects; predicates
take an attribute name argument.

Attribute names are gathered into a set and checked first. Predicates are
gathered into a sequence, matching the order in which they were supplied; they
are checked if nothing in the attribute names set matches. Pattern objects are
gathered into a sequence, matching the order in which they were supplied; they
are checked if no predicate matches.

.. doctest:: Standard.Visibility

    >>> import classcore.standard as ccstd


Argument Names
-------------------------------------------------------------------------------

The ``class_visibles`` metaclass argument controls visibility of attributes on
the produced class itself.

.. doctest:: Standard.Visibility

    >>> class Point2d( ccstd.DataclassObject, class_visibles = '*' ):
    ...     x: float
    ...     y: float
    ...
    >>> '__annotations__' in dir( Point2d )
    True

The ``instances_visibles`` metaclass argument controls visiblity of attributes
on instances of the produced class.

.. doctest:: Standard.Visibility

    >>> class Point2d( ccstd.DataclassObject, instances_visibles = '*' ):
    ...     x: float
    ...     y: float
    ...
    >>> point = Point2d( x = 3, y = 4 )
    >>> '__slots__' in dir( point )
    True

The ``visibles`` decorator factory argument controls visibility of attributes
on instances of the decorated class.

.. doctest:: Standard.Visibility

    >>> @ccstd.dataclass_with_standard_behaviors( visibles = '*' )
    ... class Point2d:
    ...     x: float
    ...     y: float
    ...
    >>> point = Point2d( x = 5, y = 12 )
    >>> '__slots__' in dir( point )
    True


Selective Visibility
-------------------------------------------------------------------------------

Explicit attribute names for selective visibility:

.. doctest:: Standard.Visibility

    >>> @ccstd.dataclass_with_standard_behaviors( visibles = ( 'x', '__slots__' ) )
    ... class Point2d:
    ...     x: float
    ...     y: float
    ...
    >>> point = Point2d( x = 5, y = 12 )
    >>> dir( point )
    ['__slots__', 'x']
    >>> point.y
    12

With a regular expression in the mix:

.. doctest:: Standard.Visibility

    >>> import re
    >>> regex = re.compile( r'''__dataclass_.*__''' )
    >>> @ccstd.dataclass_with_standard_behaviors( visibles = ( 'x', 'y', regex ) )
    ... class Point2d:
    ...     x: float
    ...     y: float
    ...
    >>> point = Point2d( x = 5, y = 12 )
    >>> dir( point )
    ['__dataclass_fields__', '__dataclass_params__', 'x', 'y']

Or with a predicate:

.. doctest:: Standard.Visibility

    >>> def predicate( name: str ) -> bool:
    ...     return not name.startswith( '_' ) or name.startswith( '__dataclass' )
    ...
    >>> @ccstd.dataclass_with_standard_behaviors( visibles = ( predicate, ) )
    ... class Point2d:
    ...     x: float
    ...     y: float
    ...
    >>> point = Point2d( x = 5, y = 12 )
    >>> dir( point )
    ['__dataclass_fields__', '__dataclass_params__', 'x', 'y']


Inheritance
-------------------------------------------------------------------------------

Classes inherit and merge visibility from their bases.

.. doctest:: Standard.Visibility

    >>> @ccstd.dataclass_with_standard_behaviors( visibles = ( '__slots__', ) )
    ... class Point3d( Point2d ):
    ...     z: float
    ...
    >>> point3 = Point3d( x = 3, y = 5, z = 6 )
    >>> dir( point3 )
    ['__dataclass_fields__', '__dataclass_params__', '__slots__', 'x', 'y', 'z']

Omnivisibility is also inherited; it short-circuits all other visiblity
evaluations.


Inline Decoration
===============================================================================

.. todo:: Contents. Add `typing_extension.runtime_checkable`.


Class Factory Decoration
===============================================================================

.. todo:: Demonstrate idempotence of applying on subclass of metaclass.
