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


_T = __.typx.TypeVar( '_T', bound = type )


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
        ''' Bound attribute assigner function.

            Usually from ``super( ).__setattr__``, but may also be a partial
            function.
        ''' ),
]
DeleterLigation: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[ [ str ], None ],
    __.typx.Doc(
        ''' Bound attribute deleter function.

            Usually from ``super( ).__delattr__``, but may also be a partial
            function.
        ''' ),
]
SurveyorLigation: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[ [ ], __.cabc.Iterable[ str ] ],
    __.typx.Doc(
        ''' Bound attribute surveyor function.

            Usually from ``super( ).__dir__``, but may also be a partial
            function.
        ''' ),
]
Decorator: __.typx.TypeAlias = __.cabc.Callable[ [ type ], type ]
Decorators: __.typx.TypeAlias = __.cabc.Sequence[ Decorator ]
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
            Decorators,
            Initializer,
            Assigner,
            Deleter,
            Surveyor,
        ],
        type
    ],
    __.typx.Doc( ''' Constructor to use with metaclass. ''' ),
]


ProduceCfcConstructorArgument: __.typx.TypeAlias = __.typx.Annotated[
    Constructor,
    __.typx.Doc( ''' Default constructor to use with metaclasses. ''' ),
]
ProduceCfcInitializerArgument: __.typx.TypeAlias = __.typx.Annotated[
    Initializer,
    __.typx.Doc( ''' Default initializer to use with metaclasses. ''' ),
]
ProduceCfcAssignerArgument: __.typx.TypeAlias = __.typx.Annotated[
    Assigner,
    __.typx.Doc(
        ''' Default attributes assigner to use with metaclasses. ''' ),
]
ProduceCfcDeleterArgument: __.typx.TypeAlias = __.typx.Annotated[
    Deleter,
    __.typx.Doc(
        ''' Default attributes deleter to use with metaclasses. ''' ),
]
ProduceCfcSurveyorArgument: __.typx.TypeAlias = __.typx.Annotated[
    Surveyor,
    __.typx.Doc(
        ''' Default attributes surveyor to use with metaclasses. ''' ),
]


decorators_name = '_class_decorators_'
initializer_name = '_class_initializer_'
assigner_name = '_class_attributes_assigner_'
deleter_name = '_class_attributes_deleter_'
surveyor_name = '_class_attributes_surveyor_'


def produce_constructor( ) -> Constructor:
    # TODO: Support hooks for additional class attributes.

    def construct( # noqa: PLR0913
        clscls: type[ _T ],
        superf: ConstructorLigation,
        name: str,
        bases: tuple[ type, ... ],
        namespace: dict[ str, __.typx.Any ],
        arguments: __.NominativeArguments,
        decorators: Decorators,
        initializer: Initializer,
        assigner: Assigner,
        deleter: Deleter,
        surveyor: Surveyor,
    ) -> type:
        ''' Constructs class, applying decorators and hooks. '''
        cls = superf( clscls, name, bases, namespace, **arguments )
        # Some decorators create new classes, which invokes this method again.
        # Short-circuit to prevent recursive decoration and other tangles.
        decorators_complete = getattr0( cls, decorators_name, [ ] )
        if decorators_complete: return cls
        setattr( cls, initializer_name, initializer )
        setattr( cls, assigner_name, assigner )
        setattr( cls, deleter_name, deleter )
        setattr( cls, surveyor_name, surveyor )
        # TODO: Run hooks for other class attributes.
        setattr( cls, decorators_name, decorators_complete )
        for decorator in decorators:
            decorators_complete.append( decorator )
            cls_ = decorator( cls )
            if cls is cls_: continue
            repair_class_reproduction( cls, cls_ )
            cls = cls_
        decorators_complete.clear( ) # Unblock top-level '__init__'.
        return cls

    return construct


def produce_initializer( ) -> Initializer:
    # TODO: Support hooks for additional class attributes.

    def initialize(
        cls: type,
        superf: InitializerLigation,
        posargs: __.PositionalArguments,
        nomargs: __.NominativeArguments,
    ) -> None:
        ''' Initializes class, applying hooks. '''
        # TODO? Separate pre-init and post-init hooks.
        superf( *posargs, **nomargs )
        # Some metaclasses add class attributes via '__init__' method.
        # So, we wait until last possible moment to complete initialization.
        decorators_complete = getattr0( cls, decorators_name, [ ] )
        if decorators_complete: return
        delattr( cls, decorators_name )
        # TODO: Run hooks for other class attributes.

    return initialize


def produce_assigner( ) -> Assigner:

    def assign(
        cls: type, superf: AssignerLigation, name: str, value: __.typx.Any
    ) -> None:
        ''' Assigns attribute to class. '''
        superf( name, value )

    return assign


def produce_deleter( ) -> Deleter:

    def delete(
        cls: type, superf: DeleterLigation, name: str
    ) -> None:
        ''' Deletes attribute from class. '''
        superf( name )

    return delete


def produce_surveyor( ) -> Surveyor:

    def survey(
        cls: type, superf: SurveyorLigation
    ) -> __.cabc.Iterable[ str ]:
        ''' Surveys attributes of class. '''
        return superf( )

    return survey


constructor_default_default = produce_constructor( )
initializer_default_default = produce_initializer( )
assigner_default_default = produce_assigner( )
deleter_default_default = produce_deleter( )
surveyor_default_default = produce_surveyor( )


def getattr0(
    cls: type, name: str, default: __.typx.Any
) -> __.typx.Any:
    # TODO: Support slotted classes.
    ''' Returns attribute from class without inheritance. '''
    return cls.__dict__.get( name, default )


def produce_class_factory_class( # noqa: PLR0913
    clscls_base: type[ _T ],
    # TODO: clscls_decorators (e.g., 'with_docstring')
    constructor_default: ProduceCfcConstructorArgument = (
        constructor_default_default ),
    initializer_default: ProduceCfcInitializerArgument = (
        initializer_default_default ),
    assigner_default: ProduceCfcAssignerArgument = (
        assigner_default_default ),
    deleter_default: ProduceCfcDeleterArgument = (
        deleter_default_default ),
    surveyor_default: ProduceCfcSurveyorArgument = (
        surveyor_default_default ),
) -> type:
    ''' Produces customized metaclasses from arbitrary base metaclasses. '''

    class Class( clscls_base ):

        def __new__( # noqa: PLR0913
            clscls: type[ Class ],
            name: str,
            bases: tuple[ type, ... ],
            namespace: dict[ str, __.typx.Any ], *,
            decorators: Decorators = ( ),
            constructor: Constructor = constructor_default,
            initializer: Initializer = initializer_default,
            assigner: Assigner = assigner_default,
            deleter: Deleter = deleter_default,
            surveyor: Surveyor = surveyor_default,
            **arguments: __.typx.Any,
        ) -> Class:
            return constructor(
                clscls, super( ).__new__,
                name, bases, namespace, arguments,
                decorators, initializer, assigner, deleter, surveyor )

        def __init__(
            cls: type,
            *posargs: __.typx.Any,
            **nomargs: __.typx.Any,
        ) -> None:
            init_base = super( ).__init__
            initializer = getattr0( cls, initializer_name, None )
            if initializer is None: init_base( *posargs, **nomargs )
            else: initializer( cls, init_base, posargs, nomargs )

        def __setattr__( cls: type, name: str, value: __.typx.Any ) -> None:
            setattr_base = super( ).__setattr__
            assigner = getattr0( cls, assigner_name, None )
            if assigner is None: setattr_base( name, value )
            else: assigner( cls, setattr_base, name, value )

        def __delattr__( cls: type, name: str ) -> None:
            delattr_base = super( ).__delattr__
            deleter = getattr0( cls, deleter_name, None )
            if deleter is None: delattr_base( name )
            else: deleter( cls, delattr_base, name )

        def __dir__( cls: type ) -> __.cabc.Iterable[ str ]:
            dir_base = super( ).__dir__
            surveyor = getattr0( cls, surveyor_name, None )
            if surveyor is None: return dir_base( )
            return surveyor( cls, dir_base )


    # TODO: Run decorators on metaclass.
    return Class


def repair_class_reproduction( original: type, reproduction: type ) -> None:
    ''' Repairs a class reproduction, if necessary. '''
    match __.platform.python_implementation( ):
        case 'CPython':  # pragma: no branch
            _repair_cpython_class_closures( original, reproduction )
        case _: pass  # pragma: no cover


def _repair_cpython_class_closures(
    original: type, reproduction: type
) -> None:
    # Adapted from https://github.com/python/cpython/pull/124455/files
    def try_repair_closure(
        function: __.cabc.Callable[ ..., __.typx.Any ]
    ) -> bool:
        try: index = function.__code__.co_freevars.index( '__class__' )
        except ValueError: return False
        if not function.__closure__: return False # pragma: no branch
        closure = function.__closure__[ index ]
        if original is closure.cell_contents: # pragma: no branch
            closure.cell_contents = reproduction
            return True
        return False # pragma: no cover

    for attribute in reproduction.__dict__.values( ):
        attribute_ = __.inspect.unwrap( attribute )
        if (    __.inspect.isfunction( attribute_ )
            and try_repair_closure( attribute_ )
        ): return
        if isinstance( attribute_, property ):
            for aname in ( 'fget', 'fset', 'fdel' ):
                accessor = getattr( attribute_, aname )
                if None is accessor: continue
                if try_repair_closure( accessor ): return # pragma: no branch
