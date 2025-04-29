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
Standard Classes
*******************************************************************************


Introduction
===============================================================================

The ``standard`` subpackage provides base classes, decorators, and class
factories (metaclasses) to imbue classes, and the instances which they produce,
with attributes concealment and immutability.

.. doctest:: Standard.Classes

    >>> import classcore.standard as ccstd

Inheriting from a standard base class:

.. doctest:: Standard.Classes

    >>> class Point2d( ccstd.Object ):
    ...     def __init__( self, x: float, y: float ) -> None:
    ...         self.x = x
    ...         self.y = y
    ...
    >>> point = Point2d( 3, 4 )
    >>> type( Point2d )
    <class 'classcore.standard.classes.Class'>

is essentially equivalent to producing a new class with a standard metaclass:

.. doctest:: Standard.Classes

    >>> class Point2d( metaclass = ccstd.Class ):
    ...     def __init__( self, x: float, y: float ) -> None:
    ...         self.x = x
    ...         self.y = y
    ...
    >>> point = Point2d( 5, 12 )


Concealment and Immutability
-------------------------------------------------------------------------------

Both classes have immutable attributes. For example, we cannot delete the
``__init__`` method that we defined:

.. doctest:: Standard.Classes

    >>> del Point2d.__init__
    Traceback (most recent call last):
    ...
    classcore.exceptions.AttributeImmutability: Could not assign or delete attribute '__init__' on class ...

Nor, for example, can we add a default value for ``x``:

.. doctest:: Standard.Classes

    >>> Point2d.x = 3
    Traceback (most recent call last):
    ...
    classcore.exceptions.AttributeImmutability: Could not assign or delete attribute 'x' on class ...

Also, all non-public attributes on the class are concealed from :py:func:`dir`:

.. doctest:: Standard.Classes

    >>> dir( Point2d )
    []

The instances of these classes also have immutable attributes:

.. doctest:: Standard.Classes

    >>> point.x = 3
    Traceback (most recent call last):
    ...
    classcore.exceptions.AttributeImmutability: Could not assign or delete attribute 'x' on instance of class ...

And concealed non-public attributes:

.. doctest:: Standard.Classes

    >>> dir( point )
    ['x', 'y']


Decoration versus Production
-------------------------------------------------------------------------------

By contrast, if we decorate an existing class, then it retains the default
Python behavior (full mutability and visibility) with respect to its
class attributes:

.. doctest:: Standard.Classes

    >>> @ccstd.with_standard_behaviors( )
    ... class Point2d:
    ...     def __init__( self, x: float, y: float ) -> None:
    ...         self.x = x
    ...         self.y = y
    ...
    >>> point = Point2d( 8, 15 )
    >>> type( Point2d )
    <class 'type'>
    >>> '__init__' in dir( Point2d )
    True
    >>> del Point2d.__init__

However, attributes on its instances are immutable and concealed, which is the
same behavior as for the classes we produced:

.. doctest:: Standard.Classes

    >>> dir( point )
    ['x', 'y']
    >>> point.x = 5
    Traceback (most recent call last):
    ...
    classcore.exceptions.AttributeImmutability: Could not assign or delete attribute 'x' on instance of class ...

Thus, if you do not desire class attributes concealment and immutability, you
can choose to decorate classes rather than produce them.


Mutable Instances
===============================================================================

.. todo:: Contents
