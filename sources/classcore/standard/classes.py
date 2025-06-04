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
# TODO: Mitigate issue with decoration obscuring signature of '__new__'
#       to typecheckers:
#       https://github.com/microsoft/pyright/discussions/10537.
#       Get rid of '__init_subclass__' hack which only addresses problem
#       for subclasses but not base classes.


from . import __
from . import decorators as _decorators
# from . import nomina as _nomina


_dynadoc_introspection_limit_ = (
    # Standard classes are immutable. Exclude from docstring updates.
    __.dynadoc.IntrospectionLimit(
        targets_exclusions = __.dynadoc.IntrospectionTargets.Class ) )


# class _CfcExtraArguments( __.typx.TypedDict, total = False ):
#
#     class_mutables: _nomina.BehaviorExclusionVerifiersOmni
#     class_visibles: _nomina.BehaviorExclusionVerifiersOmni
#     decorators: _nomina.Decorators
#     dynadoc_configuration: _nomina.DynadocConfiguration
#     instances_mutables: _nomina.BehaviorExclusionVerifiersOmni
#     instances_visibles: _nomina.BehaviorExclusionVerifiersOmni


@_decorators.decoration_by( *_decorators.class_factory_decorators )
class Class( type ): pass

    # def __new__(
    #     clscls: type[ __.T ],
    #     name: str,
    #     bases: tuple[ type, ... ],
    #     namespace: dict[ str, __.typx.Any ],
    #     *,
    #     instances_mutables: _nomina.BehaviorExclusionVerifiersOmni = ( ),
    # ) -> __.T:
    #     return super( ).__new__( clscls, name, bases, namespace )


@_decorators.decoration_by( *_decorators.class_factory_decorators )
@__.typx.dataclass_transform( frozen_default = True, kw_only_default = True )
class Dataclass( type ): pass


@_decorators.decoration_by( *_decorators.class_factory_decorators )
@__.typx.dataclass_transform( kw_only_default = True )
class DataclassMutable( type ): pass


@_decorators.decoration_by( *_decorators.class_factory_decorators )
class ProtocolClass( type( __.typx.Protocol ) ): pass


@_decorators.decoration_by( *_decorators.class_factory_decorators )
@__.typx.dataclass_transform( frozen_default = True, kw_only_default = True )
class ProtocolDataclass( type( __.typx.Protocol ) ): pass


@_decorators.decoration_by( *_decorators.class_factory_decorators )
@__.typx.dataclass_transform( kw_only_default = True )
class ProtocolDataclassMutable( type( __.typx.Protocol ) ): pass


class Object( metaclass = Class ):

    def __init_subclass__( # Typechecker appeasement.
        cls: type, /, **arguments: __.typx.Any
    ) -> None: super( ).__init_subclass__( **arguments )


class ObjectMutable( # pyright: ignore[reportGeneralTypeIssues]
    metaclass = Class,
    instances_mutables = '*', # pyright: ignore[reportCallIssue]
):

    def __init_subclass__( # Typechecker appeasement.
        cls: type, /, **arguments: __.typx.Any
    ) -> None: super( ).__init_subclass__( **arguments )


class DataclassObject( metaclass = Dataclass ): pass


class DataclassObjectMutable( metaclass = DataclassMutable ): pass


class Protocol( __.typx.Protocol, metaclass = ProtocolClass ):

    def __init_subclass__( # Typechecker appeasement.
        cls: type, /, **arguments: __.typx.Any
    ) -> None: super( ).__init_subclass__( **arguments )


class ProtocolMutable( # pyright: ignore[reportGeneralTypeIssues]
    __.typx.Protocol,
    metaclass = ProtocolClass,
    instances_mutables = '*', # pyright: ignore[reportCallIssue]
):

    def __init_subclass__( # Typechecker appeasement.
        cls: type, /, **arguments: __.typx.Any
    ) -> None: super( ).__init_subclass__( **arguments )


class DataclassProtocol(
    __.typx.Protocol, metaclass = ProtocolDataclass,
): pass


class DataclassProtocolMutable(
    __.typx.Protocol, metaclass = ProtocolDataclassMutable,
): pass
