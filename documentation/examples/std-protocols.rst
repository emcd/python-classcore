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
Standard Protocol Classes
*******************************************************************************


Introduction
===============================================================================

As static type analysis in Python evolved, structural subtyping (aka., static
duck-typing) was introduced by :pep:`544`. This PEP defined
:py:class:`typing.Protocol` classes. In addition to being a special form
recognized by type checkers to support structural subtyping, protocol classes
are also instances of :py:class:`abc.ABCMeta`, which means that they can be
used as abstract bases for classes which implement their protocols via nominal
subtyping. Thus, it makes sense to support them within the context of the
standard behaviors: concealment and immutability.

Because protocol classes are produced by a different metaclass than
:py:class:`type`, they cannot be produced by ``Class`` or ``Dataclass``.
Instead, ``ProtocolClass`` and ``ProtocolDataclass`` are provided as
metaclasses which are compatible with :py:class:`typing.Protocol` and its
descendants. Similarly, the ``Protocol`` and ``DataclassProtocol`` classes can
be used as bases, which are produced from metaclasses that are compatible with
``type( Protocol )``.

.. doctest:: Standard.Protocols

    >>> import abc
    >>> import urllib.parse
    >>> import typing_extensions as typx
    >>> import classcore.standard as ccstd

For example, one can make a protocol class via inheritance:

.. doctest:: Standard.Protocols

    >>> class FileAccessor( ccstd.Protocol, typx.Protocol ):
    ...     urlparts: urllib.parse.ParseResult
    ...     @abc.abstractmethod
    ...     async def acquire( self ) -> bytes: raise NotImplementedError
    ...     @abc.abstractmethod
    ...     async def update( self, content: bytes ) -> None: raise NotImplementedError

This protocol cannot be instantiated or mutated:

.. doctest:: Standard.Protocols

    >>> accessor = FileAccessor( )
    Traceback (most recent call last):
    ...
    TypeError: Can't instantiate abstract class FileAccessor with abstract methods acquire, update
    >>> FileAccessor.urlparts = urllib.parse.urlparse( '' )
    Traceback (most recent call last):
    ...
    classcore.exceptions.AttributeImmutability: Could not assign or delete attribute 'urlparts' on class ...

However, a concrete subtype of it can be instantiated but is still concealed
and immutable:

.. doctest:: Standard.Protocols

    >>> from os import PathLike
    >>> class AiofilesFileAccessor( FileAccessor ):
    ...     def __init__( self, location: bytes | str | PathLike ) -> None:
    ...         if isinstance( location, bytes ):
    ...             location_ = location.decode( )
    ...         elif isinstance( location, PathLike ):
    ...             location_ = str( location )
    ...         else: location_ = location
    ...         self.location = urllib.parse.urlparse( location_ )
    ...     async def acquire( self ) -> bytes: return b'' # TODO: implement
    ...     async def update( self, content: bytes ) -> None: pass # TODO: implement
    >>> AiofilesFileAccessor.location = urllib.parse.urlparse( '' )
    Traceback (most recent call last):
    ...
    classcore.exceptions.AttributeImmutability: Could not assign or delete attribute 'location' on class ...
    >>> dir( AiofilesFileAccessor )
    ['acquire', 'update']

Likewise, instances thereof are also concealed and immutable:

.. doctest:: Standard.Protocols

    >>> accessor = AiofilesFileAccessor( 'file:///foo.txt' )
    >>> accessor.location
    ParseResult(scheme='file', netloc='', path='/foo.txt', params='', query='', fragment='')
    >>> accessor.location = urllib.parse.urlparse( '/bar.txt' )
    Traceback (most recent call last):
    ...
    classcore.exceptions.AttributeImmutability: Could not assign or delete attribute 'location' on instance of class ...
    >>> dir( accessor )
    ['acquire', 'location', 'update']


Protocol Dataclasses
===============================================================================

.. todo:: Contents
