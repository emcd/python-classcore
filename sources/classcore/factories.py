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
InitializerLigation: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[ ..., None ],
    __.typx.Doc(
        ''' Bound initializer function.

            Usually from ``super( ).__init__``, but may also be a partial
            function.
        ''' ),
]
AssignerLigation: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[ [ str, __.typx.Any ], None ],
    __.typx.Doc(
        ''' Bound attributes assigner function.

            Usually from ``super( ).__setattr__``, but may also be a partial
            function.
        ''' ),
]
DeleterLigation: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[ [ str ], None ],
    __.typx.Doc(
        ''' Bound attributes deleter function.

            Usually from ``super( ).__delattr__``, but may also be a partial
            function.
        ''' ),
]
SurveyorLigation: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[ [ ], __.cabc.Iterable[ str ] ],
    __.typx.Doc(
        ''' Bound attributes surveyor function.

            Usually from ``super( ).__dir__``, but may also be a partial
            function.
        ''' ),
]

# TODO: ConstructionPreprocessor (arguments/bases/namespace mutation)
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

Initializer: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[
        [
            type,
            InitializerLigation,
            __.PositionalArguments,
            __.NominativeArguments,
        ],
        None
    ],
    __.typx.Doc( ''' Initializer to use with metaclass. ''' ),
]
Assigner: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[ [ type, AssignerLigation, str, __.typx.Any ], None ],
    __.typx.Doc( ''' Attribute assigner to use with metaclass. ''' ),
]
Deleter: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[ [ type, DeleterLigation, str ], None ],
    __.typx.Doc( ''' Attribute deleter to use with metaclass. ''' ),
]
Surveyor: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[ [ type, SurveyorLigation ], __.cabc.Iterable[ str ] ],
    __.typx.Doc( ''' Attribute surveyor to use with metaclass. ''' ),
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


ProduceFactoryConstructorArgument: __.typx.TypeAlias = __.typx.Annotated[
    Constructor,
    __.typx.Doc( ''' Default constructor to use with metaclasses. ''' ),
]
ProduceFactoryInitializerArgument: __.typx.TypeAlias = __.typx.Annotated[
    Initializer,
    __.typx.Doc( ''' Default initializer to use with metaclasses. ''' ),
]
ProduceFactoryAssignerArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.typx.Optional[ Assigner ],
    __.typx.Doc(
        ''' Default attributes assigner to use with metaclasses. ''' ),
]
ProduceFactoryDeleterArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.typx.Optional[ Deleter ],
    __.typx.Doc(
        ''' Default attributes deleter to use with metaclasses. ''' ),
]
ProduceFactorySurveyorArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.typx.Optional[ Surveyor ],
    __.typx.Doc(
        ''' Default attributes surveyor to use with metaclasses. ''' ),
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


progress_name = '_class_IN_PROGRESS_'
decorators_name = '_class_decorators_'
initializer_name = '_class_initializer_'
assigner_name = '_class_attributes_assigner_'
deleter_name = '_class_attributes_deleter_'
surveyor_name = '_class_attributes_surveyor_'


def produce_constructor(
    postprocessors: ProduceConstructorPostprocsArgument = ( ),
) -> Constructor:
    ''' Produces constructors for classes. '''
    # TODO? Support pre-construction hooks which can mutate various things.

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
        cls = superf( clscls, name, bases, namespace, **arguments )
        # Some decorators create new classes, which invokes this method again.
        # Short-circuit to prevent recursive decoration and other tangles.
        in_progress = _utilities.getattr0( cls, progress_name, False )
        if in_progress: return cls
        setattr( cls, progress_name, True )
        setattr( cls, decorators_name, decorators )
        decorators_ = list( decorators )
        for postprocessor in postprocessors:
            postprocessor( cls, decorators_ )
        for decorator in decorators_:
            cls_ = decorator( cls )
            if cls is cls_: continue
            _utilities.repair_class_reproduction( cls, cls_ )
            cls = cls_
        setattr( cls, progress_name, False )
        return cls

    return construct


def produce_initializer(
    completers: ProduceInitializerCompletersArgument = ( ),
) -> Initializer:
    ''' Produces initializers for classes. '''

    def initialize(
        cls: type,
        superf: InitializerLigation,
        posargs: __.PositionalArguments,
        nomargs: __.NominativeArguments,
    ) -> None:
        ''' Initializes class, applying hooks. '''
        superf( *posargs, **nomargs )
        in_progress = _utilities.getattr0( cls, progress_name, False )
        if in_progress: return # If non-empty, then not top-level.
        delattr( cls, progress_name )
        for completer in completers: completer( cls )

    return initialize


constructor_default = produce_constructor( )
initializer_default = produce_initializer( )


def produce_class_factory( # noqa: PLR0913
    clscls_base: type[ _T ], *,
    # TODO: clscls_decorators (e.g., 'with_docstring')
    constructor: ProduceFactoryConstructorArgument = constructor_default,
    initializer: ProduceFactoryInitializerArgument = initializer_default,
    assigner: ProduceFactoryAssignerArgument = None,
    deleter: ProduceFactoryDeleterArgument = None,
    surveyor: ProduceFactorySurveyorArgument = None,
) -> type:
    ''' Produces customized metaclasses from arbitrary base metaclasses. '''

    class Class( clscls_base ):

        def __new__(
            clscls: type[ Class ],
            name: str,
            bases: tuple[ type, ... ],
            namespace: dict[ str, __.typx.Any ], *,
            decorators: _nomina.Decorators = ( ),
            **arguments: __.typx.Any,
        ) -> Class:
            return constructor(
                clscls, super( ).__new__,
                name, bases, namespace, arguments, decorators )

        def __init__(
            cls: type,
            *posargs: __.typx.Any,
            **nomargs: __.typx.Any,
        ) -> None:
            init_base = super( ).__init__
            if initializer is None: init_base( *posargs, **nomargs )
            else: initializer( cls, init_base, posargs, nomargs )

        def __setattr__( cls: type, name: str, value: __.typx.Any ) -> None:
            setattr_base = super( ).__setattr__
            if assigner is None: setattr_base( name, value )
            else: assigner( cls, setattr_base, name, value )

        def __delattr__( cls: type, name: str ) -> None:
            delattr_base = super( ).__delattr__
            if deleter is None: delattr_base( name )
            else: deleter( cls, delattr_base, name )

        def __dir__( cls: type ) -> __.cabc.Iterable[ str ]:
            dir_base = super( ).__dir__
            if surveyor is None: return dir_base( )
            return surveyor( cls, dir_base )


    # TODO: Run decorators on metaclass.
    return Class


def produce_decorator(
    decorators: _nomina.Decorators = ( ),
    preprocessors: _nomina.DecorationPreprocessors = ( ),
    postprocessors: _nomina.DecorationPostprocessors = ( ),
) -> _nomina.Decorator:
    ''' Generic decorator factory.

        Can wrap to adapt specialized arguments into preprocessors and
        postprocessors.
    '''
    def decorate( cls: type[ _T ] ) -> type[ _T ]:
        decorators_ = list( decorators )
        for preprocessor in preprocessors:
            preprocessor( cls, decorators_ )
        for decorator in decorators_:
            cls_ = decorator( cls )
            if cls is cls_: continue
            _utilities.repair_class_reproduction( cls, cls_ )
            cls = cls_
        for postprocessor in postprocessors:
            postprocessor( cls )
        return cls

    return decorate
