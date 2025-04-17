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


''' Factories which produce metaclasses. '''


from __future__ import annotations

from . import __
from . import bases as _bases
from . import factories as _factories
from . import nomina as _nomina
from . import utilities as _utilities


# TODO: Custom implementations.
#       Concealment and immutability.
#       Dataclass detection.
#       Slots detection.


AttributeMutabilityPredicate: __.typx.TypeAlias = (
    __.cabc.Callable[ [ str, __.typx.Any ], bool ] )
AttributeMutabilityVerifier: __.typx.TypeAlias = (
    str | __.re.Pattern[ str ] | AttributeMutabilityPredicate )
AttributeMutabilityVerifiers: __.typx.TypeAlias = (
    __.cabc.Sequence[ AttributeMutabilityVerifier ] )
AttributeVisibilityPredicate: __.typx.TypeAlias = (
    __.cabc.Callable[ [ str ], bool ] )
AttributeVisibilityVerifier: __.typx.TypeAlias = (
    str | __.re.Pattern[ str ] | AttributeVisibilityPredicate )
AttributeVisibilityVerifiers: __.typx.TypeAlias = (
    __.cabc.Sequence[ AttributeVisibilityVerifier ] )
ErrorClassProvider: __.typx.TypeAlias = (
    __.cabc.Callable[ [ str ], type[ Exception ] ] )


Class = _factories.produce_factory_class( type )
ProtocolClass = (
    _factories.produce_factory_class(
        type( __.typx.Protocol ) ) ) # pyright: ignore[reportArgumentType]


_cfc_behaviors_name = '_class_behaviors_'
_class_behaviors_name = '_behaviors_'
_dataclass_core = __.dcls.dataclass( frozen = True, kw_only = True )
_immutability_label = 'immutability'


def _provide_error_class( name: str ) -> type[ Exception ]:
    ''' Produces error class for this package. '''
    match name:
        case 'AttributeImmutability':
            from .exceptions import AttributeImmutability as error
        case _:
            from .exceptions import ErrorProductionFailure
            raise ErrorProductionFailure( name, reason = 'Does not exist.' )
    return error


def is_public_identifier( name: str ) -> bool:
    ''' Is Python identifier public? '''
    return not name.startswith( '_' )


def dataclass_immutable(
    mutables: AttributeMutabilityVerifiers = ( ),
    visibles: AttributeVisibilityVerifiers = ( is_public_identifier, ),
    error_factory: ErrorClassProvider = _provide_error_class,
    # TODO? attribute value transformer
) -> _nomina.Decorator:
    ''' Decorator factory. Ensures instances have immutable attributes. '''
    # TODO: postprocessor for init completion
    postproc_m = produce_mutables_postprocessor( error_factory, mutables )
    postproc_v = produce_visibles_postprocessor( visibles )
    decorator = _factories.produce_decorator(
        decorators = ( _dataclass_core, ),
        preprocessors = ( _annotate_class, ),
        postprocessors = ( postproc_m, postproc_v ) )

    @__.typx.dataclass_transform(
        frozen_default = True, kw_only_default = True )
    def decorate_as_dataclass( cls: type ) -> type:
        # TODO: Pyright bug report on dataclass_transform not applying.
        return decorator( cls )

    return decorate_as_dataclass


def immutable(
    mutables: AttributeMutabilityVerifiers = ( ),
    visibles: AttributeVisibilityVerifiers = ( is_public_identifier, ),
    error_factory: ErrorClassProvider = _provide_error_class,
    # TODO? attribute value transformer
) -> _nomina.Decorator:
    ''' Decorator factory. Ensures instances have immutable attributes. '''
    # TODO: postprocessor for init completion
    postproc_m = produce_mutables_postprocessor( error_factory, mutables )
    postproc_v = produce_visibles_postprocessor( visibles )
    return _factories.produce_decorator(
        preprocessors = ( _annotate_class, ),
        postprocessors = ( postproc_m, postproc_v ) )


def produce_initialization_postprocessor(
    posargs_injection: __.PositionalArguments = ( ),
    nomargs_injection: __.NominativeArguments = __.dictproxy_empty,
) -> _nomina.DecorationPostprocessor:
    def postprocess( cls: type ) -> None:
        original_init = getattr( cls, '__init__' )

        @__.funct.wraps( original_init )
        def initialize(
            self: object, *posargs: __.typx.Any, **nomargs: __.typx.Any
        ) -> None:
            original_init(
                self,
                *( *posargs_injection, *posargs ),
                **{ **nomargs_injection, **nomargs } )
            behaviors = _utilities.getattr0(
                self, _class_behaviors_name, set( ) )
            if not behaviors: setattr(
                self, _class_behaviors_name, behaviors )
            behaviors.add( _immutability_label )

        cls.__init__ = initialize

    return postprocess


def produce_mutables_postprocessor(
    error_provider: ErrorClassProvider,
    mutables: AttributeMutabilityVerifiers = ( )
) -> _nomina.DecorationPostprocessor:

    # TODO: Bin mutables into set, regexes list, and predicates list.

    def postprocess( cls: type ) -> None:
        # TODO: Associate __delattr__.
        # TODO: Associate __setattr__.
        pass

    return postprocess


def produce_visibles_postprocessor(
    visibles: AttributeVisibilityVerifiers = ( )
) -> _nomina.DecorationPostprocessor:

    # TODO: Bin visibles into set, regexes list, and predicates list.

    def postprocess( cls: type ) -> None:
        # TODO: Associate __dir__.
        pass

    return postprocess


# TODO: Object (with 'immutable' decorator)


class ObjectMutable( metaclass = Class ): pass


class DataclassObject(
    _bases.DataclassObjectBase, metaclass = Class
): pass


class DataclassObjectMutable(
    _bases.DataclassObjectMutableBase, metaclass = Class
): pass


# TODO: Protocol (with 'immutable' decorator)


class ProtocolMutable( __.typx.Protocol, metaclass = ProtocolClass ): pass


class DataclassProtocol(
    _bases.DataclassProtocolBase, __.typx.Protocol,
    metaclass = ProtocolClass,
): pass


class DataclassProtocolMutable(
    _bases.DataclassProtocolMutableBase, __.typx.Protocol,
    metaclass = ProtocolClass,
): pass


def _annotate_class(
    cls: type, decorators: _nomina.DecoratorsMutable
) -> None:
    ''' Annotates class in support of machinery. '''
    annotations = getattr( cls, '__annotations__' )
    # TODO: accretive set instead of set
    annotations[ _class_behaviors_name ] = set[ str ]


def _annotate_cfc(
    cls: type, decorators: _nomina.DecoratorsMutable
) -> None:
    ''' Annotates metaclass in support of machinery. '''
    annotations = getattr( cls, '__annotations__' )
    # TODO: accretive set instead of set
    annotations[ _cfc_behaviors_name ] = __.typx.ClassVar[ set[ str ] ]
