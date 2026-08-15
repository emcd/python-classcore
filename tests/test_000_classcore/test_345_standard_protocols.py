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


''' Tests for protocol classes and metaclass hierarchy. '''


import typing

from .__ import PACKAGE_NAME, cache_import_module

MODULE_QNAME = f"{PACKAGE_NAME}.standard.classes"

# Module-level cross-metaclass class: inherits from bases backed by
# ProtocolClass and ProtocolDataclass. Defined at module level to avoid
# the qualname/in_progress mangling interaction with dataclass _add_slots
# replacement that affects function-local classes.
_ccstd = cache_import_module( MODULE_QNAME )


class _CrossMetaclassProto( _ccstd.Protocol, _ccstd.DataclassProtocol ):
    ''' Exercises cross-metaclass inheritance. '''

    def greet( self ) -> str: ...


class _ModuleDataclassProto( _ccstd.DataclassProtocol ):
    ''' Module-level dataclass protocol (avoids function-local qualname). '''

    value: int

    def greet( self ) -> str: ...


# =========================================================================== #
# Metaclass Hierarchy
# =========================================================================== #


def test_400_protocol_metaclass_hierarchy( ):
    ''' Protocol metaclasses form a proper inheritance hierarchy. '''
    module = cache_import_module( MODULE_QNAME )
    assert issubclass( module.ProtocolDataclass, module.ProtocolClass )
    assert issubclass( module.ProtocolDataclassMutable, module.ProtocolClass )
    assert issubclass(
        module.ProtocolDataclassMutable, module.ProtocolDataclass )


def test_401_nonprotocol_metaclass_hierarchy( ):
    ''' Non-protocol metaclasses form a proper inheritance hierarchy. '''
    module = cache_import_module( MODULE_QNAME )
    assert issubclass( module.Dataclass, module.Class )
    assert issubclass( module.DataclassMutable, module.Dataclass )


def test_410_cross_metaclass_no_conflict( ):
    ''' Metaclass hierarchy resolves conflicts between protocol metaclasses.
        A class inheriting from bases backed by ProtocolClass and
        ProtocolDataclass is created successfully, with ProtocolDataclass
        (most derived) as its metaclass.
    '''
    module = cache_import_module( MODULE_QNAME )
    assert issubclass( module.ProtocolDataclass, module.ProtocolClass )
    # The module-level class below exercises actual cross-metaclass
    # inheritance without TypeError.
    assert _CrossMetaclassProto._is_protocol
    assert type( _CrossMetaclassProto ) is module.ProtocolDataclass


# =========================================================================== #
# Protocol Detection
# =========================================================================== #


def test_420_protocol_subclass_is_protocol( ):
    ''' Direct subclasses of protocol base classes are recognized as
        protocols at runtime. '''
    module = cache_import_module( MODULE_QNAME )

    class DirectProto( module.Protocol ):
        def method( self ) -> int: ...

    assert DirectProto.__dict__.get( '_is_protocol' ) is True

    class DirectMutableProto( module.ProtocolMutable ):
        def method( self ) -> int: ...

    assert DirectMutableProto.__dict__.get( '_is_protocol' ) is True


# NOTE: DataclassProtocol subclasses are tested separately because the
# dataclass machinery's _add_slots creates a replacement class whose
# __qualname__ differs from the original when defined inside a function,
# which interacts with the in_progress mangling. This is a pre-existing
# issue unrelated to the protocol metaclass hierarchy fix.



def test_421_concrete_implementation_not_protocol( ):
    ''' Concrete implementation subclasses are not protocols. '''
    module = cache_import_module( MODULE_QNAME )

    class ProtoIface( module.Protocol ):
        def method( self ) -> int: ...

    class ConcreteImpl( ProtoIface ):
        def method( self ) -> int:
            return 42

    assert ConcreteImpl.__dict__.get( '_is_protocol' ) is None or \
        ConcreteImpl.__dict__.get( '_is_protocol' ) is False


# =========================================================================== #
# Runtime Checkable Protocols
# =========================================================================== #


def test_430_runtime_checkable_via_decorators( ):
    ''' @runtime_checkable works when applied via decorators= argument. '''
    module = cache_import_module( MODULE_QNAME )

    class CheckableProto(
        module.Protocol,
        decorators = ( typing.runtime_checkable, ),
    ):
        def greet( self ) -> str: ...

    assert CheckableProto._is_runtime_protocol


def test_431_runtime_checkable_direct_application( ):
    ''' @runtime_checkable works when applied directly after creation. '''
    module = cache_import_module( MODULE_QNAME )

    class DirectProto( module.Protocol ):
        def greet( self ) -> str: ...

    typing.runtime_checkable( DirectProto )
    assert DirectProto._is_runtime_protocol


def test_432_runtime_checkable_isinstance( ):
    ''' isinstance() structural subtyping works with runtime_checkable. '''
    module = cache_import_module( MODULE_QNAME )

    class GreeterProto(
        module.Protocol,
        decorators = ( typing.runtime_checkable, ),
    ):
        def greet( self ) -> str: ...

    class GreeterImpl:
        def greet( self ) -> str:
            return "hello"

    assert isinstance( GreeterImpl( ), GreeterProto )


# =========================================================================== #
# Protocol Attributes
# =========================================================================== #


def test_440_protocol_attrs_exclude_internals( ):
    ''' __protocol_attrs__ does not contain classcore internal attributes. '''
    module = cache_import_module( MODULE_QNAME )

    class MyProto( module.Protocol ):
        def greet( self ) -> str: ...

    attrs = MyProto.__dict__.get( '__protocol_attrs__' )
    assert attrs is not None
    assert 'greet' in attrs
    assert not any( a.startswith( '_classcore_' ) for a in attrs )
    assert '__setattr__' not in attrs
    assert '__delattr__' not in attrs
    assert '__dir__' not in attrs


def test_441_runtime_checkable_all_four_bases( ):
    ''' Runtime structural subtyping (isinstance) works for direct
        subclasses of all four protocol base classes. '''
    module = cache_import_module( MODULE_QNAME )

    class Impl:
        def greet( self ) -> str:
            return "hello"

    for base in (
        module.Protocol,
        module.ProtocolMutable,
        module.DataclassProtocol,
        module.DataclassProtocolMutable,
    ):
        proto_cls = type( f"{base.__name__}Greeter", ( base, ), {
            'greet': lambda self: 'hello',
            '_is_protocol': True,
        } )
        typing.runtime_checkable( proto_cls )
        assert proto_cls._is_runtime_protocol, (
            f"{base.__name__}: _is_runtime_protocol not set" )
        assert isinstance( Impl( ), proto_cls ), (
            f"{base.__name__}: isinstance failed" )


def test_442_declared_dunder_preserved( ):
    ''' Protocol members declared by the author, including dunders, are
        preserved in __protocol_attrs__. Framework-generated dunders
        (dataclass, behaviors) are excluded via the pre-decoration
        snapshot, not a dunder blacklist. '''
    module = cache_import_module( MODULE_QNAME )

    class DunderProto( module.Protocol ):
        def __repr__( self ) -> str: ...
        def greet( self ) -> str: ...

    attrs = DunderProto.__dict__[ '__protocol_attrs__' ]
    assert '__repr__' in attrs
    assert 'greet' in attrs
    assert '__eq__' not in attrs


def test_443_dataclass_protocol_attrs_declared_only( ):
    ''' Dataclass protocol attrs contain declared fields and methods,
        excluding dataclass-generated dunders. '''
    attrs = _ModuleDataclassProto.__dict__[ '__protocol_attrs__' ]
    assert 'value' in attrs
    assert 'greet' in attrs
    assert '__repr__' not in attrs
    assert '__dataclass_fields__' not in attrs


def test_444_factory_hierarchy_delegation( ):
    ''' Custom metaclass hierarchies delegate construction without
        duplicating postprocessing. Covers the no-stub wrapper branch:
        a parent metaclass without '__new__' in its own dict. A class
        decorator must record exactly one invocation. '''
    from classcore.standard.decorators import class_factory

    @class_factory( )
    class ParentMeta( type ):
        ''' No '__new__' stub: factory installs construct_with_super. '''

    @class_factory( )
    class ChildMeta( ParentMeta ):

        def __new__( # Typechecker stub.
            clscls, name, bases, namespace, **kwargs
        ):
            return super( ).__new__( clscls, name, bases, namespace )

    invocations: list[ str ] = [ ]

    def recorder( cls: type ) -> type:
        invocations.append( cls.__name__ )
        return cls

    class Product(
        metaclass = ChildMeta, decorators = ( recorder, )
    ):
        ''' Created through both factory levels. '''

    assert type( Product ) is ChildMeta
    assert invocations == [ 'Product' ]


# =========================================================================== #
# Dataclass Transform Preservation
# =========================================================================== #


def test_450_dataclass_transform_frozen_preserved( ):
    ''' ProtocolDataclass has frozen_default=True. '''
    module = cache_import_module( MODULE_QNAME )
    spec = module.ProtocolDataclass.__dict__.get( '__dataclass_transform__' )
    assert spec is not None
    assert spec.get( 'frozen_default' ) is True


def test_451_dataclass_transform_mutable_not_frozen( ):
    ''' ProtocolDataclassMutable has frozen_default=False, not inherited
        from ProtocolDataclass. '''
    module = cache_import_module( MODULE_QNAME )
    spec = (
        module.ProtocolDataclassMutable.__dict__.get(
            '__dataclass_transform__' ) )
    assert spec is not None
    assert spec.get( 'frozen_default' ) is False
