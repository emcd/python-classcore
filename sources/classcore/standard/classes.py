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


''' Standard classes and class factories. '''


from . import __
from . import decorators as _decorators
from . import dynadoc as _dynadoc
from . import nomina as _nomina


# Standard library ABC machinery attribute names which the class-level
# immutability behavior permits. The C _abc implementation writes these
# cache and protocol bookkeeping attributes through direct dict access,
# so they must remain assignable on standard classes. Also used by the
# explanations module to mark such names as internal.
abc_class_mutables = (
    '_abc_cache',
    '_abc_negative_cache',
    '_abc_negative_cache_version',
    '_abc_registry',
    '_is_runtime_protocol',
    '__non_callable_proto_members__',
)
_abc_class_mutables = abc_class_mutables # Historical private alias.
_protocol_cls_set = frozenset( { __.typx.Protocol } )
# Attributes never considered declared protocol members: typing internals,
# class-creation machinery, and framework attributes declared in classcore
# base class bodies.
_protocol_attr_excluded = frozenset( {
    '_is_protocol', '_is_runtime_protocol',
    '__protocol_attrs__', '__subclasshook__',
    '__non_callable_proto_members__',
    '_dynadoc_fragments_',
    # Injected during class creation by ABC, Generic, and typing machinery.
    # '__init__' is '_no_init' on protocol bases; as a structural member it
    # is vacuous since every candidate object has an '__init__'.
    '__abstractmethods__', '__parameters__', '__init__', '__orig_bases__',
} )
_protocol_attr_prefixes = ( '_classcore_', '_abc_' )
# Standard Python attributes present in every pre-decoration namespace.
_python_class_defaults = frozenset( {
    '__module__', '__qualname__', '__doc__', '__dict__', '__weakref__',
    '__slots__', '__annotations__',
    '__firstlineno__', '__static_attributes__', # Python 3.13+
} )


def _snapshot_declared_protocol_attrs( cls: type ) -> None:
    ''' Records protocol members declared before framework decoration.

        Called in metaclass '__new__' immediately after class creation,
        before behavior decorators and dataclass machinery inject their
        attributes. The pre-decoration namespace contains exactly the
        members declared by the author, so a user-declared dunder (e.g.,
        '__repr__') is preserved while framework-generated ones are absent.
    '''
    # Dataclass slot machinery reproduces classes, copying '__dict__'.
    # Retain the original snapshot; the reproduction's namespace already
    # contains decorated attributes.
    if '_classcore_protocol_declared_' in cls.__dict__: return
    declared = (
        set( cls.__dict__ )
        | set( __.inspect.get_annotations( cls ) ) )
    declared -= _python_class_defaults
    declared = {
        attr for attr in declared
        if attr not in _protocol_attr_excluded
        and not any( attr.startswith( p ) for p in _protocol_attr_prefixes )
    }
    setattr( cls, '_classcore_protocol_declared_', frozenset( declared ) )

_dynadoc_configuration = (
    _dynadoc.produce_dynadoc_configuration( table = __.fragments ) )
_class_factory = __.funct.partial(
    _decorators.class_factory, dynadoc_configuration = _dynadoc_configuration )


class ClassFactoryExtraArguments( __.typx.TypedDict, total = False ):
    ''' Extra arguments accepted by standard metaclasses. '''

    class_mutables: _nomina.BehaviorExclusionVerifiersOmni
    class_visibles: _nomina.BehaviorExclusionVerifiersOmni
    dynadoc_configuration: _nomina.DynadocConfiguration
    instances_assigner_core: _nomina.AssignerCore
    instances_deleter_core: _nomina.DeleterCore
    instances_surveyor_core: _nomina.SurveyorCore
    instances_ignore_init_arguments: bool
    instances_mutables: _nomina.BehaviorExclusionVerifiersOmni
    instances_visibles: _nomina.BehaviorExclusionVerifiersOmni


@_class_factory( )
class Class( type ):
    ''' Metaclass for standard classes. '''

    _dynadoc_fragments_ = (
        'cfc class conceal', 'cfc class protect', 'cfc dynadoc',
        'cfc instance conceal', 'cfc instance protect' )

    def __new__( # Typechecker stub.
        clscls: type[ __.T ],
        name: str,
        bases: tuple[ type, ... ],
        namespace: dict[ str, __.typx.Any ], *,
        decorators: _nomina.Decorators[ __.T ] = ( ),
        **arguments: __.typx.Unpack[ ClassFactoryExtraArguments ],
    ) -> __.T:
        return super( ).__new__( clscls, name, bases, namespace )


@_class_factory( )
class AbstractClass( Class, __.abc.ABCMeta ):
    ''' Metaclass for abstract classes with standard behaviors.

        Combines the standard behaviors of `Class` with the machinery of
        `abc.ABCMeta` (abstract method enforcement, virtual subclass
        registration) via a diamond hierarchy. `Class` itself remains
        backed by plain `type`, so ABC machinery applies only where this
        metaclass is used.
    '''

    _dynadoc_fragments_ = (
        'cfc class conceal', 'cfc class protect', 'cfc dynadoc',
        'cfc instance conceal', 'cfc instance protect' )

    def __new__( # Typechecker stub.
        clscls: type[ __.T ],
        name: str,
        bases: tuple[ type, ... ],
        namespace: dict[ str, __.typx.Any ], *,
        decorators: _nomina.Decorators[ __.T ] = ( ),
        **arguments: __.typx.Unpack[ ClassFactoryExtraArguments ],
    ) -> __.T:
        return super( ).__new__( clscls, name, bases, namespace )


@_class_factory( )
@__.typx.dataclass_transform( frozen_default = True, kw_only_default = True )
class Dataclass( Class ):
    ''' Metaclass for standard dataclasses. '''

    _dynadoc_fragments_ = (
        'cfc produce dataclass',
        'cfc class conceal', 'cfc class protect', 'cfc dynadoc',
        'cfc instance conceal', 'cfc instance protect' )

    def __new__( # Typechecker stub.
        clscls: type[ __.T ],
        name: str,
        bases: tuple[ type, ... ],
        namespace: dict[ str, __.typx.Any ], *,
        decorators: _nomina.Decorators[ __.T ] = ( ),
        **arguments: __.typx.Unpack[ ClassFactoryExtraArguments ],
    ) -> __.T:
        return super( ).__new__( clscls, name, bases, namespace )


@_class_factory( )
@__.typx.dataclass_transform( kw_only_default = True )
class DataclassMutable( Dataclass ):
    ''' Metaclass for dataclasses with mutable instance attributes. '''

    _dynadoc_fragments_ = (
        'cfc produce dataclass',
        'cfc class conceal', 'cfc class protect', 'cfc dynadoc',
        'cfc instance conceal' )

    def __new__( # Typechecker stub.
        clscls: type[ __.T ],
        name: str,
        bases: tuple[ type, ... ],
        namespace: dict[ str, __.typx.Any ], *,
        decorators: _nomina.Decorators[ __.T ] = ( ),
        **arguments: __.typx.Unpack[ ClassFactoryExtraArguments ],
    ) -> __.T:
        return super( ).__new__( clscls, name, bases, namespace )


@_class_factory( )
class ProtocolClass( AbstractClass, type( __.typx.Protocol ) ):
    ''' Metaclass for standard protocol classes. '''

    _dynadoc_fragments_ = (
        'cfc produce protocol class',
        'cfc class conceal', 'cfc class protect', 'cfc dynadoc',
        'cfc instance conceal', 'cfc instance protect' )

    def __new__( # Typechecker stub.
        clscls: type[ __.T ],
        name: str,
        bases: tuple[ type, ... ],
        namespace: dict[ str, __.typx.Any ], *,
        decorators: _nomina.Decorators[ __.T ] = ( ),
        **arguments: __.typx.Unpack[ ClassFactoryExtraArguments ],
    ) -> __.T:
        cls = super( ).__new__( clscls, name, bases, namespace )
        # typing_extensions.Protocol.__init_subclass__ uses identity comparison
        # (b is Protocol) to set _is_protocol on subclasses. Classcore protocol
        # base classes are not typing.Protocol, so subclasses incorrectly get
        # _is_protocol = False. Detect protocol base classes structurally and
        # fix _is_protocol before decorators are applied
        # (e.g., runtime_checkable).
        if not cls.__dict__.get( '_is_protocol', False ):
            for base in cls.__bases__:
                if ( base.__dict__.get( '_is_protocol', False )
                    and bool( _protocol_cls_set & set( base.__bases__ ) ) ):
                    setattr( cls, '_is_protocol', True )
                    break
        if cls.__dict__.get( '_is_protocol', False ):
            _snapshot_declared_protocol_attrs( cls )
        return cls

    def __init__(
        cls,
        name: str,
        bases: tuple[ type, ... ],
        namespace: dict[ str, __.typx.Any ],
        **kwargs: __.typx.Any,
    ) -> None:
        super( ).__init__( name, bases, namespace, **kwargs )
        # Replace _ProtocolMeta's scan of the decorated namespace with the
        # pre-decoration snapshot, so isinstance() only checks declared
        # protocol members. Snapshot persists because metaclass __init__ can
        # run more than once when dataclass machinery reproduces classes.
        if getattr( cls, '_is_protocol', False ):
            declared: frozenset[ str ] = cls.__dict__.get(
                '_classcore_protocol_declared_', frozenset( ) )
            inherited: set[ str ] = set( )
            for base in cls.__mro__[ 1: ]:
                if not isinstance( base, ProtocolClass ): continue
                inherited.update( base.__dict__.get(
                    '__protocol_attrs__', ( ) ) )
            attrs = {
                attr for attr in declared | inherited
                if attr not in _protocol_attr_excluded
                and not any(
                    attr.startswith( p ) for p in _protocol_attr_prefixes )
            }
            setattr( cls, '__protocol_attrs__', attrs )


@_class_factory( )
@__.typx.dataclass_transform( frozen_default = True, kw_only_default = True )
class ProtocolDataclass( ProtocolClass ):
    ''' Metaclass for standard protocol dataclasses. '''

    _dynadoc_fragments_ = (
        'cfc produce protocol class', 'cfc produce dataclass',
        'cfc class conceal', 'cfc class protect', 'cfc dynadoc',
        'cfc instance conceal', 'cfc instance protect' )

    def __new__( # Typechecker stub.
        clscls: type[ __.T ],
        name: str,
        bases: tuple[ type, ... ],
        namespace: dict[ str, __.typx.Any ], *,
        decorators: _nomina.Decorators[ __.T ] = ( ),
        **arguments: __.typx.Unpack[ ClassFactoryExtraArguments ],
    ) -> __.T:
        return super( ).__new__( clscls, name, bases, namespace )


@_class_factory( )
@__.typx.dataclass_transform( kw_only_default = True )
class ProtocolDataclassMutable( ProtocolDataclass ):
    ''' Metaclass for protocol dataclasses with mutable instance attributes.
    '''

    _dynadoc_fragments_ = (
        'cfc produce protocol class', 'cfc produce dataclass',
        'cfc class conceal', 'cfc class protect', 'cfc dynadoc',
        'cfc instance conceal' )

    def __new__( # Typechecker stub.
        clscls: type[ __.T ],
        name: str,
        bases: tuple[ type, ... ],
        namespace: dict[ str, __.typx.Any ], *,
        decorators: _nomina.Decorators[ __.T ] = ( ),
        **arguments: __.typx.Unpack[ ClassFactoryExtraArguments ],
    ) -> __.T:
        return super( ).__new__( clscls, name, bases, namespace )


class Object( metaclass = Class ):
    ''' Standard base class. '''

    _dynadoc_fragments_ = (
        'class concealment', 'class protection', 'class dynadoc',
        'class instance conceal', 'class instance protect' )


class ObjectMutable( metaclass = Class, instances_mutables = '*' ):
    ''' Base class with mutable instance attributes. '''

    _dynadoc_fragments_ = (
        'class concealment', 'class protection', 'class dynadoc',
        'class instance conceal' )


class AbstractObject(
    metaclass = AbstractClass,
    class_mutables = _abc_class_mutables,
):
    ''' Base class for abstract classes with standard behaviors.

        Supports abstract method enforcement and virtual subclass
        registration, and mixes with external classes whose metaclass is
        `abc.ABCMeta`.
    '''

    _dynadoc_fragments_ = (
        'class concealment', 'class protection', 'class dynadoc',
        'class instance conceal', 'class instance protect' )


class DataclassObject( metaclass = Dataclass ):
    ''' Standard base dataclass. '''

    _dynadoc_fragments_ = (
        'dataclass',
        'class concealment', 'class protection', 'class dynadoc',
        'class instance conceal', 'class instance protect' )


class DataclassObjectMutable( metaclass = DataclassMutable ):
    ''' Base dataclass with mutable instance attributes. '''

    _dynadoc_fragments_ = (
        'dataclass',
        'class concealment', 'class protection', 'class dynadoc',
        'class instance conceal' )


class Protocol(
    __.typx.Protocol,
    metaclass = ProtocolClass,
    class_mutables = _abc_class_mutables,
):
    ''' Standard base protocol class. '''

    _dynadoc_fragments_ = (
        'protocol class',
        'class concealment', 'class protection', 'class dynadoc',
        'class instance conceal', 'class instance protect' )


class ProtocolMutable(
    __.typx.Protocol,
    metaclass = ProtocolClass,
    class_mutables = _abc_class_mutables,
    instances_mutables = '*',
):
    ''' Base protocol class with mutable instance attributes. '''

    _dynadoc_fragments_ = (
        'protocol class',
        'class concealment', 'class protection', 'class dynadoc',
        'class instance conceal' )


class DataclassProtocol(
    __.typx.Protocol,
    metaclass = ProtocolDataclass,
    class_mutables = _abc_class_mutables,
):
    ''' Standard base protocol dataclass. '''

    _dynadoc_fragments_ = (
        'dataclass', 'protocol class',
        'class concealment', 'class protection', 'class dynadoc',
        'class instance conceal', 'class instance protect' )


class DataclassProtocolMutable(
    __.typx.Protocol,
    metaclass = ProtocolDataclassMutable,
    class_mutables = _abc_class_mutables,
):
    ''' Base protocol dataclass with mutable instance attributes. '''

    _dynadoc_fragments_ = (
        'dataclass', 'protocol class',
        'class concealment', 'class protection', 'class dynadoc',
        'class instance conceal' )


# =========================================================================== #
# Type checker canaries. Private declarations, excluded from the public API
# and the test suite. They exist so that Pyright (and other type checkers)
# evaluates the structures declared above; regressions in checker support
# surface as diagnostics on these declarations during routine linting.
# =========================================================================== #


class _CanaryAbstractObject( AbstractObject ):
    ''' Canary for abstract base classes. '''

    def provide( self ) -> int:
        return 42


class _CanaryProtocolUse( Protocol ):
    ''' Canary for protocol definitions. '''

    value: int

    def greet( self ) -> str: ...


class _CanaryProtocolImpl( _CanaryProtocolUse ):
    ''' Canary for concrete protocol implementations. '''

    def __init__( self ) -> None:
        self.value = 7

    def greet( self ) -> str:
        return 'canary'


_canary_abstract: int = _CanaryAbstractObject( ).provide( )
_canary_protocol_iface: _CanaryProtocolUse = _CanaryProtocolImpl( )
_canary_greeting: str = _canary_protocol_iface.greet( )
