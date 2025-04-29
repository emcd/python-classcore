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
Standard Dataclasses
*******************************************************************************


Introduction
===============================================================================

The ``standard`` subpackage provides base classes, decorators, and class
factories (metaclasses) to imbue :py:mod:`dataclasses`, and the instances which
they produce, with attributes concealment and immutability.

.. doctest:: Standard.Dataclasses

    >>> import classcore.standard as ccstd
    >>> import dataclasses

Inheriting from a standard base:

.. doctest:: Standard.Dataclasses

    >>> class Point2d( ccstd.DataclassObject ):
    ...     x: float
    ...     y: float
    ...
    >>> point = Point2d( x = 3, y = 4 )
    >>> dataclasses.is_dataclass( Point2d )
    True
    >>> type( Point2d )
    <class 'classcore.standard.classes.Dataclass'>

is essentially equivalent to producing a new class with a standard metaclass:

.. doctest:: Standard.Dataclasses

    >>> class Point2d( metaclass = ccstd.Dataclass ):
    ...     x: float
    ...     y: float
    ...
    >>> point = Point2d( x = 5, y = 12 )
    >>> dataclasses.is_dataclass( Point2d )
    True

As can be seen above, dataclasses are produced without the need to explicitly
decorate with the :py:func:`dataclasses.dataclass` decorator.


Concealment and Immutability
===============================================================================

Both classes have immutable attributes. For example, we cannot delete the
annotations from which the dataclass attributes were derived:

.. doctest:: Standard.Dataclasses

    >>> del Point2d.__annotations__
    Traceback (most recent call last):
    ...
    classcore.exceptions.AttributeImmutability: Could not assign or delete attribute '__annotations__' on class ...

Nor, for example, can we add a default value for ``x``:

.. doctest:: Standard.Dataclasses

    >>> Point2d.x = 3
    Traceback (most recent call last):
    ...
    classcore.exceptions.AttributeImmutability: Could not assign or delete attribute 'x' on class ...

Also, all non-public attributes on the class are concealed from :py:func:`dir`:

.. doctest:: Standard.Dataclasses

    >>> dir( Point2d )
    ['x', 'y']

The instances of these classes also have immutable attributes:

.. doctest:: Standard.Dataclasses

    >>> point.x = 3
    Traceback (most recent call last):
    ...
    classcore.exceptions.AttributeImmutability: Could not assign or delete attribute 'x' on instance of class ...

And concealed non-public attributes:

.. doctest:: Standard.Dataclasses

    >>> dir( point )
    ['x', 'y']


Decoration versus Production
===============================================================================

By contrast, if we decorate an existing dataclass, then it retains the default
Python behavior (full mutability and visibility) with respect to its
class attributes:

.. doctest:: Standard.Dataclasses

    >>> @ccstd.dataclass_with_standard_behaviors( )
    ... class Point2d:
    ...     x: float
    ...     y: float
    ...
    >>> point = Point2d( x = 8, y = 15 )
    >>> dataclasses.is_dataclass( Point2d )
    True
    >>> type( Point2d )
    <class 'type'>
    >>> '__annotations__' in dir( Point2d )
    True
    >>> del Point2d.__annotations__

However, attributes on its instances are immutable and concealed, which is the
same behavior as for the classes we produced:

.. doctest:: Standard.Dataclasses

    >>> dir( point )
    ['x', 'y']
    >>> point.x = 5
    Traceback (most recent call last):
    ...
    classcore.exceptions.AttributeImmutability: Could not assign or delete attribute 'x' on instance of class ...

Thus, if you do not desire class attributes concealment and immutability, you
can choose to decorate classes rather than produce them.


Decoration Details
===============================================================================

By default, the dataclasses are decorated with ``dataclasses.dataclass(
kw_only = True, slots = True )``. The implications of this are:

* The choice of keyword-only arguments (``kw_only = True``) ensures that
  inheritance works correctly... at the expense of compact initialization from
  positional arguments.

* The choice of instance attribute allocations over instance dictionaries
  (``slots = True``) can improve performance and helps enforce the `Open-closed
  principle <https://en.wikipedia.org/wiki/Open%E2%80%93closed_principle>`_.
  Also, the package ensures that ``super`` can work correctly inside of the
  bodies of methods on slotted dataclasses, addressing a bug in the standard
  library dataclasses implementation of CPython versions up to 3.13.

* Although the dataclasses are not decorated with ``frozen = True``, they do
  enforce immutability on instance attributes after initialization has
  completed. The instance attributes are also recognized as immutable by static
  type checkers, such as Pyright. By not explicitly decorating with ``frozen =
  True``, we allow the dataclasses to successfully execute ``__post_init__``
  hooks which modify their attributes and enforce immutability in the same way
  that it is enforced throughout the package.

The following example helps illustrate the difference in immutability
enforcement:

.. doctest:: Standard.Dataclasses

    >>> import math
    >>> @ccstd.dataclass_with_standard_behaviors( )
    ... class Point2d:
    ...     x: float
    ...     y: float
    ...     hypotenuse: float = dataclasses.field( init = False )
    ...     def __post_init__( self ) -> None:
    ...         self.hypotenuse = math.sqrt( self.x*self.x + self.y*self.y )
    ...
    >>> point = Point2d( x = 3, y = 4 )
    >>> point.hypotenuse
    5.0

As can be seen, the hypotenuse of the triangle was calculated and successfully
assigned during initialization. Of course, after initialization, the hypotenuse
or any other instance attribute cannot be modified:

.. doctest:: Standard.Dataclasses

    >>> point.hypotenuse = 6
    Traceback (most recent call last):
    ...
    classcore.exceptions.AttributeImmutability: Could not assign or delete attribute 'hypotenuse' on instance of class ...

Trying the same thing with ``dataclasses.dataclass( frozen = True )``, results
in an error during initialization:

.. doctest:: Standard.Dataclasses

    >>> import math
    >>> @dataclasses.dataclass( frozen = True, kw_only = True, slots = True )
    ... class Point2d:
    ...     x: float
    ...     y: float
    ...     hypotenuse: float = dataclasses.field( init = False )
    ...     def __post_init__( self ) -> None:
    ...         self.hypotenuse = math.sqrt( self.x*self.x + self.y*self.y )
    ...
    >>> point = Point2d( x = 5, y = 12 )
    Traceback (most recent call last):
    ...
    dataclasses.FrozenInstanceError: cannot assign to field 'hypotenuse'


Mutable Instances
===============================================================================

To produce classes with immutable attributes but instances with mutable
attributes, there is a convenience class, ``DataclassObjectMutable``.

.. doctest:: Standard.Dataclasses

    >>> class Point2d( ccstd.DataclassObjectMutable ):
    ...     x: float
    ...     y: float
    ...
    >>> point = Point2d( x = 7, y = 24 )
    >>> point.x, point.y = 20, 21
    >>> point.x, point.y
    (20, 21)
