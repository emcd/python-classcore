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
from . import nomina as _nomina
from . import utilities as _utilities


_T = __.typx.TypeVar( '_T', bound = type )
_U = __.typx.TypeVar( '_U' )


ConstructorLigation: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[ ..., type ],
    __.typx.Doc( ''' Constructor method from base metaclass. ''' ),
]
ConstructionPreprocessor: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[
        [
            type[ type ],               # metaclass
            str,                        # class name
            list[ type ],               # bases (mutable)
            dict[ str, __.typx.Any ],   # namespace (mutable)
            dict[ str, __.typx.Any ],   # arguments (mutable)
            _nomina.DecoratorsMutable,  # decorators (mutable)
        ],
        None
    ],
    __.typx.Doc(
        ''' Processes class data before construction.

            For use cases, such as argument conversion.
        ''' ),
]
ConstructionPostprocessor: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[ [ type, _nomina.DecoratorsMutable ], None ],
    __.typx.Doc(
        ''' Processes class before decoration.

            For use cases, such as decorator list manipulation.
        ''' ),
]
# TODO: InitializationPreparer (arguments mutation)
InitializationCompleter: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[ [ type ], None ],
    __.typx.Doc(
        ''' Completes initialization of class.

            For use cases, such as enabling immutability once all other
            initialization has occurred.
        ''' ),
]


Constructor: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[
        [
            type,
            ConstructorLigation,
            str,
            tuple[ type, ... ],
            dict[ str, __.typx.Any ],
            __.NominativeArguments,
            _nomina.Decorators,
        ],
        type
    ],
    __.typx.Doc( ''' Constructor to use with metaclass. ''' ),
]
Initializer: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[
        [
            type,
            _nomina.InitializerLigation,
            __.PositionalArguments,
            __.NominativeArguments,
        ],
        None
    ],
    __.typx.Doc( ''' Initializer to use with metaclass. ''' ),
]
Assigner: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[
        [ type, _nomina.AssignerLigation, str, __.typx.Any ], None ],
    __.typx.Doc( ''' Attribute assigner to use with metaclass. ''' ),
]
Deleter: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[
        [ type, _nomina.DeleterLigation, str ], None ],
    __.typx.Doc( ''' Attribute deleter to use with metaclass. ''' ),
]
Surveyor: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[
        [ type, _nomina.SurveyorLigation ], __.cabc.Iterable[ str ] ],
    __.typx.Doc( ''' Attribute surveyor to use with metaclass. ''' ),
]


ProduceConstructorPreprocsArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Sequence[ ConstructionPreprocessor ],
    __.typx.Doc( ''' Processors to apply before construction of class. ''' ),
]
ProduceConstructorPostprocsArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Sequence[ ConstructionPostprocessor ],
    __.typx.Doc( ''' Processors to apply before decoration of class. ''' ),
]
ProduceInitializerCompletersArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Sequence[ InitializationCompleter ],
    __.typx.Doc(
        ''' Processors to apply at final stage of class initialization. ''' ),
]


_progress_name = '_class_IN_PROGRESS_'


def apply_decorators( cls: type, decorators: _nomina.Decorators ) -> type:
    ''' Applies sequence of decorators to class.

        If decorators replace classes (e.g., ``dataclass( slots = True )``),
        then any necessary repairs are performed on the replacement class with
        respect to the original. E.g., on CPython, the class closure cell is
        repaired so that ``super`` operates correctly in methods of the
        replacement class.
    '''
    for decorator in decorators:
        cls_ = decorator( cls )
        if cls is cls_: continue # Simple mutation. No replacement.
        _utilities.repair_class_reproduction( cls, cls_ )
        cls = cls_ # Use the replacement class.
    return cls


def produce_constructor(
    preprocessors: ProduceConstructorPreprocsArgument = ( ),
    postprocessors: ProduceConstructorPostprocsArgument = ( ),
) -> Constructor:
    ''' Produces constructors for classes. '''

    def construct( # noqa: PLR0913
        clscls: type[ _T ],
        superf: ConstructorLigation,
        name: str,
        bases: tuple[ type, ... ],
        namespace: dict[ str, __.typx.Any ],
        arguments: __.NominativeArguments,
        decorators: _nomina.Decorators,
    ) -> type:
        ''' Constructs class, applying decorators and hooks. '''
        bases_ = list( bases )
        arguments_ = dict( arguments )
        decorators_ = list( decorators )
        for prep in preprocessors:
            prep( clscls, name, bases_, namespace, arguments_, decorators_ )
        cls = superf( clscls, name, tuple( bases_ ), namespace, **arguments_ )
        # Some decorators create new classes, which invokes this method again.
        # Short-circuit to prevent recursive decoration and other tangles.
        in_progress = _utilities.getattr0( cls, _progress_name, False )
        if in_progress: return cls
        setattr( cls, _progress_name, True )
        for postp in postprocessors: postp( cls, decorators_ )
        cls = apply_decorators( cls, decorators_ )
        setattr( cls, _progress_name, False )
        return cls

    return construct


def produce_initializer(
    completers: ProduceInitializerCompletersArgument = ( ),
) -> Initializer:
    ''' Produces initializers for classes. '''

    def initialize(
        cls: type,
        superf: _nomina.InitializerLigation,
        posargs: __.PositionalArguments,
        nomargs: __.NominativeArguments,
    ) -> None:
        ''' Initializes class, applying hooks. '''
        superf( *posargs, **nomargs )
        in_progress = _utilities.getattr0( cls, _progress_name, False )
        if in_progress: return # If non-empty, then not top-level.
        delattr( cls, _progress_name )
        for completer in completers: completer( cls )

    return initialize


constructor_default = produce_constructor( )
initializer_default = produce_initializer( )


def produce_class_construction_decorator(
    constructor: Constructor = constructor_default
) -> _nomina.Decorator:
    ''' Produces metaclass decorator to control class construction.

        Decorator overrides ``__new__`` on metaclass.
    '''
    def decorate( clscls: type[ _T ] ) -> type[ _T ]:
        original = getattr( clscls, '__new__' )

        def construct(
            clscls_: type[ _T ],
            name: str,
            bases: tuple[ type, ... ],
            namespace: dict[ str, __.typx.Any ], *,
            decorators: _nomina.Decorators = ( ),
            **arguments: __.typx.Any,
        ) -> type:
            return constructor(
                clscls_, original,
                name, bases, namespace, arguments, decorators )

        clscls.__new__ = construct # pyright: ignore[reportAttributeAccessIssue]
        return clscls

    return decorate


def produce_class_initialization_decorator(
    initializer: Initializer = initializer_default
) -> _nomina.Decorator:
    ''' Produces metaclass decorator to control class initialization.

        Decorator overrides ``__init__`` on metaclass.
    '''
    def decorate( clscls: type[ _T ] ) -> type[ _T ]:
        original = getattr( clscls, '__init__' )

        def initialize(
            cls: type,
            *posargs: __.typx.Any,
            **nomargs: __.typx.Any,
        ) -> None:
            initializer(
                cls, __.funct.partial( original, cls ), posargs, nomargs )

        clscls.__init__ = initialize
        return clscls

    return decorate


def produce_class_mutation_control_decorator(
    assigner: Assigner, deleter: Deleter
) -> _nomina.Decorator:
    ''' Produces metaclass decorator for class mutation control.

        Decorator overrides ``__delattr__`` and ``__setattr__`` on metaclass.
    '''
    def decorate( clscls: type[ _T ] ) -> type[ _T ]:
        original_assigner = getattr( clscls, '__setattr__' )
        original_deleter = getattr( clscls, '__delattr__' )

        def assign( cls: type, name: str, value: __.typx.Any ) -> None:
            ligation = __.funct.partial( original_assigner, cls )
            assigner( cls, ligation, name, value )

        def delete( cls: type, name: str ) -> None:
            ligation = __.funct.partial( original_deleter, cls )
            deleter( cls, ligation, name )

        clscls.__delattr__ = delete
        clscls.__setattr__ = assign
        return clscls

    return decorate


def produce_class_visibility_control_decorator(
    surveyor: Surveyor
) -> _nomina.Decorator:
    ''' Produces metaclass decorator for class visibility control.

        Decorator overrides ``__dir__`` on metaclass.
    '''
    def decorate( clscls: type[ _T ] ) -> type[ _T ]:
        original = getattr( clscls, '__dir__' )

        def survey( cls: type ) -> __.cabc.Iterable[ str ]:
            ligation = __.funct.partial( original, cls )
            return surveyor( cls, ligation )

        clscls.__dir__ = survey # pyright: ignore[reportAttributeAccessIssue]
        return clscls

    return decorate


class_construction_decorator_default = (
    produce_class_construction_decorator( ) )
class_initialization_decorator_default = (
    produce_class_initialization_decorator( ) )
decorators_default = (
    class_construction_decorator_default,
    class_initialization_decorator_default,
)


def decoration_by(
    decorators: _nomina.Decorators = ( )
) -> _nomina.Decorator:
    ''' Class decorator which applies other class decorators.

        Useful to apply a stack of decorators as a sequence.
    '''
    def decorate( cls: type ) -> type:
        return apply_decorators( cls, decorators )

    return decorate


def produce_decorator(
    decorators: _nomina.Decorators = ( ),
    preprocessors: _nomina.DecorationPreprocessors = ( ),
    postprocessors: _nomina.DecorationPostprocessors = ( ),
) -> _nomina.Decorator:
    ''' Generic decorator factory.

        Can be wrapped to adapt specialized arguments into preprocessors and
        postprocessors.
    '''
    def decorate( cls: type[ _T ] ) -> type[ _T ]:
        decorators_ = list( decorators )
        for preprocessor in preprocessors:
            preprocessor( cls, decorators_ )
        cls = apply_decorators( cls, decorators_ )
        for postprocessor in postprocessors:
            postprocessor( cls )
        return cls

    return decorate
