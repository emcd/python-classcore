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

Mutability can be customized for both the attributes of a class and the
attributes of its instances. This is done by supplying an argument which is a
sequence of mutability verifiers. These verifiers may be attribute names,
compiled regular expressions, or predicates. Attribute names are strings;
compiled regular expressions are :py:class:`re.Pattern` objects which match
attribute names; predicates evaluate an attribute name argument. Also, normal
Python mutability can be granted to a class. This is done by supplying the
omnimutability marker (``'*'``) as an argument instead of a sequence.

Attribute names are gathered into a set and checked first. Predicates are
gathered into a sequence, matching the order in which they were supplied; they
are checked if nothing in the attribute names set matches. Pattern objects are
gathered into a sequence, matching the order in which they were supplied; they
are checked if no predicate matches.

.. doctest:: Standard.Mutability

    >>> import dataclasses
    >>> import classcore.standard as ccstd


Argument Names
-------------------------------------------------------------------------------

The ``class_mutables`` metaclass argument controls mutability of attributes on
the produced class itself.

.. doctest:: Standard.Mutability

    >>> class Point2d( ccstd.DataclassObject, class_mutables = '*' ):
    ...     x: float
    ...     y: float
    ...
    >>> Point2d.x, Point2d.y = 3, 4
    >>> Point2d.x, Point2d.y
    (3, 4)
    >>> del Point2d.x

The ``instances_mutables`` metaclass argument controls mutablity of attributes
on instances of the produced class.

.. doctest:: Standard.Mutability

    >>> class Point2d( ccstd.DataclassObject, instances_mutables = '*' ):
    ...     x: float
    ...     y: float
    ...
    >>> point = Point2d( x = 3, y = 4 )
    >>> point.x, point.y
    (3, 4)
    >>> point.x, point.y = 5, 12
    >>> point.x, point.y
    (5, 12)
    >>> del point.x

The ``mutables`` decorator factory argument controls mutability of attributes
on instances of the decorated class.

.. doctest:: Standard.Mutability

    >>> @ccstd.dataclass_with_standard_behaviors( mutables = '*' )
    ... class Point2d:
    ...     x: float
    ...     y: float
    ...
    >>> point = Point2d( x = 5, y = 12 )
    >>> point.x, point.y
    (5, 12)
    >>> point.x, point.y = 8, 15
    >>> point.x, point.y
    (8, 15)
    >>> del point.x


Selective Visibility
-------------------------------------------------------------------------------

Explicit attribute names for selective mutability:

.. doctest:: Standard.Mutability

    >>> @ccstd.dataclass_with_standard_behaviors( mutables = ( 'x', 'y' ) )
    ... class Point2d:
    ...     x: float
    ...     y: float
    ...
    >>> point = Point2d( x = 8, y = 15 )
    >>> point.x, point.y = 7, 24
    >>> point.x, point.y
    (7, 24)
    >>> del point.x
    >>> point.__slots__ = ( )
    Traceback (most recent call last):
    ...
    classcore.exceptions.AttributeImmutability: Could not assign or delete attribute '__slots__' on instance of class ...

With a regular expression in the mix:

.. doctest:: Standard.Mutability

    >>> import re
    >>> regex = re.compile( r'''cache_.*''' )
    >>> @ccstd.dataclass_with_standard_behaviors( mutables = ( 'x', 'y', regex ) )
    ... class Point2d:
    ...     x: float
    ...     y: float
    ...     cache_area: float = dataclasses.field( init = False )
    ...     cache_hypotenuse: float = dataclasses.field( init = False )
    ...
    >>> point = Point2d( x = 7, y = 24 )
    >>> point.x, point.y = 20, 21
    >>> point.x, point.y
    (20, 21)
    >>> point.cache_hypotenuse = 29
    >>> del point.cache_hypotenuse
    >>> point.__slots__ = ( )
    Traceback (most recent call last):
    ...
    classcore.exceptions.AttributeImmutability: Could not assign or delete attribute '__slots__' on instance of class ...
    >>> del point.__annotations__
    Traceback (most recent call last):
    ...
    classcore.exceptions.AttributeImmutability: Could not assign or delete attribute '__annotations__' on instance of class ...

Or with a predicate:

.. doctest:: Standard.Mutability

    >>> def predicate( name: str ) -> bool:
    ...     return not name.startswith( '_' ) or name.startswith( 'cache_' )
    ...
    >>> @ccstd.dataclass_with_standard_behaviors( mutables = ( predicate, ) )
    ... class Point2d:
    ...     x: float
    ...     y: float
    ...     cache_area: float = dataclasses.field( init = False )
    ...     cache_hypotenuse: float = dataclasses.field( init = False )
    ...
    >>> point = Point2d( x = 20, y = 21 )
    >>> point.x, point.y = 12, 35
    >>> point.x, point.y
    (12, 35)
    >>> point.cache_hypotenuse = 37
    >>> del point.cache_hypotenuse
    >>> point.__slots__ = ( )
    Traceback (most recent call last):
    ...
    classcore.exceptions.AttributeImmutability: Could not assign or delete attribute '__slots__' on instance of class ...
    >>> del point.__annotations__
    Traceback (most recent call last):
    ...
    classcore.exceptions.AttributeImmutability: Could not assign or delete attribute '__annotations__' on instance of class ...

Invalid mutability verifiers will cause an error to be raised:

.. doctest:: Standard.Mutability

    >>> @ccstd.with_standard_behaviors( mutables = ( 13, ) )
    ... class C: pass
    ...
    Traceback (most recent call last):
    ...
    classcore.exceptions.BehaviorExclusionInvalidity: Invalid behavior exclusion verifier: 42

Inheritance
-------------------------------------------------------------------------------

Classes inherit and merge mutability from their bases.

.. doctest:: Standard.Mutability

    >>> @ccstd.dataclass_with_standard_behaviors( mutables = ( 'x', 'y' ) )
    ... class Point2d:
    ...     x: float
    ...     y: float
    ...
    >>> @ccstd.dataclass_with_standard_behaviors( mutables = ( 'z', ) )
    ... class Point3d( Point2d ):
    ...     z: float
    ...
    >>> point3 = Point3d( x = 12, y = 35, z = 47 )
    >>> point3.x, point3.y, point3.z = 9, 40, 49
    >>> point3.x, point3.y, point3.z
    (9, 40, 49)

Omnimutability is also inherited; it short-circuits all other mutablity
evaluations.

.. doctest:: Standard.Mutability

    >>> @ccstd.dataclass_with_standard_behaviors( mutables = '*' )
    ... class Point2d:
    ...     x: float
    ...     y: float
    ...
    >>> @ccstd.dataclass_with_standard_behaviors( mutables = ( 'z', ) )
    ... class Point3d( Point2d ):
    ...     z: float
    ...
    >>> point3 = Point3d( x = 9, y = 40, z = 49 )
    >>> point3.x, point3.y, point3.z = 28, 45, 73
    >>> point3.x, point3.y, point3.z
    (28, 45, 73)


Visibility
===============================================================================

Visibility can be customized for both the attributes of a class and the
attributes of its instances. This is done by supplying an argument which is a
sequence of visibility verifiers. These verifiers may be attribute names,
compiled regular expressions, or predicates. Attribute names are strings;
compiled regular expressions are :py:class:`re.Pattern` objects which match
attribute names; predicates evaluate an attribute name argument. Also, normal
Python visibility can be granted to a class. This is done by supplying the
omnivisibility marker (``'*'``) as an argument instead of a sequence.

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
    >>> point = Point2d( x = 8, y = 15 )
    >>> dir( point )
    ['__slots__', 'x']
    >>> point.y
    15

With a regular expression in the mix:

.. doctest:: Standard.Visibility

    >>> import re
    >>> regex = re.compile( r'''__dataclass_.*__''' )
    >>> @ccstd.dataclass_with_standard_behaviors( visibles = ( 'x', 'y', regex ) )
    ... class Point2d:
    ...     x: float
    ...     y: float
    ...
    >>> point = Point2d( x = 7, y = 24 )
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
    >>> point = Point2d( x = 20, y = 21 )
    >>> dir( point )
    ['__dataclass_fields__', '__dataclass_params__', 'x', 'y']

Invalid visibility verifiers will cause an error to be raised:

.. doctest:: Standard.Visibility

    >>> @ccstd.with_standard_behaviors( visibles = ( 13, ) )
    ... class C: pass
    ...
    Traceback (most recent call last):
    ...
    classcore.exceptions.BehaviorExclusionInvalidity: Invalid behavior exclusion verifier: 42


Inheritance
-------------------------------------------------------------------------------

Classes inherit and merge visibility from their bases.

.. doctest:: Standard.Visibility

    >>> @ccstd.dataclass_with_standard_behaviors( visibles = ( '__slots__', ) )
    ... class Point3d( Point2d ):
    ...     z: float
    ...
    >>> point3 = Point3d( x = 12, y = 35, z = 47 )
    >>> dir( point3 )
    ['__dataclass_fields__', '__dataclass_params__', '__slots__', 'x', 'y', 'z']

Omnivisibility is also inherited; it short-circuits all other visiblity
evaluations.

.. doctest:: Standard.Visibility

    >>> @ccstd.dataclass_with_standard_behaviors( visibles = '*' )
    ... class Point2d:
    ...     x: float
    ...     y: float
    ...
    >>> @ccstd.dataclass_with_standard_behaviors( visibles = ( 'z', ) )
    ... class Point3d( Point2d ):
    ...     z: float
    ...
    >>> point3 = Point3d( x = 9, y = 40, z = 49 )
    >>> '__slots__' in dir( point3 )
    True


Inline Decoration
===============================================================================

Class decorators often mutate the state of the classes which they decorate. If
a class is immutable, then this can be problematic. Fortunately, there are
several workarounds, depending on the scenario:

* Apply mutating decorators before the standard behaviors decorator.

* Supply mutating decorators to the standard behaviors decorator so that it can
  apply them inline before enforcing immutability.

.. doctest:: Standard.Decoration

    >>> import abc
    >>> import urllib.parse
    >>> import typing_extensions as typx
    >>> import classcore.standard as ccstd

For example, one can make a decorated protocol by stacking decorators:

.. doctest:: Standard.Decoration

    >>> @ccstd.with_standard_behaviors( )
    ... @typx.runtime_checkable
    ... class FileAccessor( typx.Protocol ):
    ...     urlparts: urllib.parse.ParseResult
    ...     @abc.abstractmethod
    ...     async def acquire( self ) -> bytes: raise NotImplementedError
    ...     @abc.abstractmethod
    ...     async def update( self, content: bytes ) -> None: raise NotImplementedError

Or, by inline decoration:

.. doctest:: Standard.Decoration

    >>> @ccstd.with_standard_behaviors( decorators = ( typx.runtime_checkable, ) )
    ... class FileAccessor( typx.Protocol ):
    ...     urlparts: urllib.parse.ParseResult
    ...     @abc.abstractmethod
    ...     async def acquire( self ) -> bytes: raise NotImplementedError
    ...     @abc.abstractmethod
    ...     async def update( self, content: bytes ) -> None: raise NotImplementedError

If a class is being produced from a standard behaviors metaclass, then there is
no option to apply mutating decorators first, since class initialization would
be complete by the time that are applied. In this case, mutating decorators
must be supplied metaclass argument, so that they can be applied inline.

.. doctest:: Standard.Decoration

    >>> class FileAccessor( ccstd.Protocol, typx.Protocol, decorators = ( typx.runtime_checkable, ) ):
    ...     urlparts: urllib.parse.ParseResult
    ...     @abc.abstractmethod
    ...     async def acquire( self ) -> bytes: raise NotImplementedError
    ...     @abc.abstractmethod
    ...     async def update( self, content: bytes ) -> None: raise NotImplementedError
