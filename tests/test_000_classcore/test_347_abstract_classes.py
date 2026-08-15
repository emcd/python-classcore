# vim: set filetype=python fileencoding=utf-8:
# -*- coding: utf-8 -*-

#============================================================================#
#                                                                            #
#  Licensed under the Apache License, Version 2.0 (the "License");           #
#  you may not use this file except in compliance with the License.          #
#  You may obtain a copy of the License at                                   #
#                                                                            #
#      http://www.apache.org/licenses/LICENSE-2.0                            #
#                                                                            #
#  Unless required by applicable law or agreed to in writing, software       #
#  distributed under the License is distributed on an "AS IS" BASIS,         #
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#  See the License for the specific language governing permissions and       #
#  limitations under the License.                                            #
#                                                                            #
#============================================================================#


''' Tests for abstract base class support. '''


import abc
import typing

from .__ import PACKAGE_NAME, cache_import_module

MODULE_QNAME = f"{PACKAGE_NAME}.standard.classes"


# =========================================================================== #
# Metaclass Hierarchy
# =========================================================================== #


def test_500_abstractclass_hierarchy( ):
    ''' AbstractClass combines Class with ABCMeta in a diamond. '''
    module = cache_import_module( MODULE_QNAME )
    assert issubclass( module.AbstractClass, module.Class )
    assert issubclass( module.AbstractClass, abc.ABCMeta )
    # Class itself remains backed by plain type: no ABC machinery on
    # ordinary classes.
    assert not issubclass( module.Class, abc.ABCMeta )


def test_501_protocolclass_unified_taxonomy( ):
    ''' ProtocolClass descends from AbstractClass and Class. '''
    module = cache_import_module( MODULE_QNAME )
    assert issubclass( module.ProtocolClass, module.Class )
    assert issubclass( module.ProtocolClass, module.AbstractClass )
    assert issubclass( module.ProtocolClass, abc.ABCMeta )


# =========================================================================== #
# AbstractObject
# =========================================================================== #


def test_510_abstractobject_standard_behaviors( ):
    ''' AbstractObject applies standard behaviors to subclasses. '''
    module = cache_import_module( MODULE_QNAME )

    class Widget( module.AbstractObject ):
        ''' Concrete widget. '''

        def provide( self ) -> int:
            return 42

    assert type( Widget ) is module.AbstractClass
    widget = Widget( )
    assert widget.provide( ) == 42
    try:
        widget.provide = lambda: 0  # type: ignore[method-assign]
        mutated = True
    except Exception:
        mutated = False
    assert not mutated, 'instance immutability not enforced'


def test_511_abstractobject_mixes_with_external_abc( ):
    ''' AbstractObject subclasses mix with external ABC-based classes. '''
    module = cache_import_module( MODULE_QNAME )

    class ExternalABC( abc.ABC ):
        @abc.abstractmethod
        def provide( self ) -> int: ...

    class Mixed( module.AbstractObject, ExternalABC ):
        def provide( self ) -> int:
            return 7

    assert type( Mixed ) is module.AbstractClass
    assert Mixed( ).provide( ) == 7


def test_512_abstract_method_enforcement( ):
    ''' Incomplete subclasses of abstract classes cannot instantiate. '''
    module = cache_import_module( MODULE_QNAME )

    class ExternalABC( abc.ABC ):
        @abc.abstractmethod
        def provide( self ) -> int: ...

    class Incomplete( module.AbstractObject, ExternalABC ):
        ''' Does not implement "provide". '''

    try:
        Incomplete( )
        raised = False
    except TypeError:
        raised = True
    assert raised, 'abstract method enforcement missing'


def test_513_registration( ):
    ''' Virtual subclass registration works and does not trip
        immutability enforcement. '''
    module = cache_import_module( MODULE_QNAME )

    class Registrable( module.AbstractObject ):
        pass

    class Standalone:
        pass

    Registrable.register( Standalone )
    assert issubclass( Standalone, Registrable )
    assert isinstance( Standalone( ), Registrable )


# =========================================================================== #
# Protocol Functionality Preserved
# =========================================================================== #


def test_520_protocol_suite_through_unified_hierarchy( ):
    ''' Protocol detection and structural subtyping still work after
        ProtocolClass re-parenting. '''
    module = cache_import_module( MODULE_QNAME )

    class GreeterProto( module.Protocol ):
        def greet( self ) -> str: ...

    assert GreeterProto.__dict__.get( '_is_protocol' ) is True

    typing.runtime_checkable( GreeterProto )

    class Impl:
        def greet( self ) -> str:
            return 'hello'

    assert isinstance( Impl( ), GreeterProto )


def test_521_single_decoration_through_hierarchy( ):
    ''' Decorators apply exactly once through the unified
        ProtocolClass -> AbstractClass -> Class hierarchy. '''
    module = cache_import_module( MODULE_QNAME )
    invocations: list[ str ] = [ ]

    def recorder( cls: type ) -> type:
        invocations.append( cls.__name__ )
        return cls

    class Decorated(
        metaclass = module.ProtocolClass,
        decorators = ( recorder, ),
    ):
        ''' Class created through three factory levels. '''

    assert invocations == [ 'Decorated' ]


def test_522_concrete_classes_satisfy_protocols( ):
    ''' Concrete classcore classes are structurally compatible with
        classcore protocols. '''
    module = cache_import_module( MODULE_QNAME )

    class GreeterProto(
        module.Protocol,
        decorators = ( typing.runtime_checkable, ),
    ):
        def greet( self ) -> str: ...

    class GreeterClass( module.Object ):
        def greet( self ) -> str:
            return 'concrete'

    assert isinstance( GreeterClass( ), GreeterProto )
