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


Decorator: __.typx.TypeAlias = __.cabc.Callable[ [ type ], type ]
Decorators: __.typx.TypeAlias = __.cabc.Sequence[ Decorator ]


_decorators_name = '_class_decorators_'
_initializer_name = '_class_initializer_'


BaseConstructorLigation: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[ ..., type ],
    __.typx.Doc( ''' Constructor method from base metaclass. ''' ),
]
BaseInitializerLigation: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[ ..., None ],
    __.typx.Doc( ''' Initializer method from base metaclass. ''' ),
]

Initializer: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[
        [
            type,
            BaseInitializerLigation,
            __.PositionalArguments,
            __.NominativeArguments,
        ],
        None
    ],
    __.typx.Doc( ''' Initializer to use with metaclass. ''' ),
]


Constructor: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[
        [
            type,
            BaseConstructorLigation,
            str,
            tuple[ type, ... ],
            dict[ str, __.typx.Any ],
            __.NominativeArguments,
            Decorators,
            Initializer,
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


def produce_constructor( ) -> Constructor:
    # TODO: Support hooks for additional class attributes.

    def construct( # noqa: PLR0913
        clscls: type[ _T ],
        superf: BaseConstructorLigation,
        name: str,
        bases: tuple[ type, ... ],
        namespace: dict[ str, __.typx.Any ],
        arguments: __.NominativeArguments,
        decorators: Decorators,
        initializer: Initializer,
    ) -> type:
        ''' Constructs class, applying decorators and hooks. '''
        cls = superf( clscls, name, bases, namespace, **arguments )
        # Some decorators create new classes, which invokes this method again.
        # Short-circuit to prevent recursive decoration and other tangles.
        decorators_complete = getattr0( cls, _decorators_name, [ ] )
        if decorators_complete: return cls
        setattr( cls, _initializer_name, initializer )
        # TODO: Assign assigner, deleter, surveyor.
        # TODO: Run hooks for other class attributes.
        setattr( cls, _decorators_name, decorators_complete )
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
        superf: BaseInitializerLigation,
        posargs: __.PositionalArguments,
        nomargs: __.NominativeArguments,
    ) -> None:
        ''' Initializes class, applying hooks. '''
        # TODO? Separate pre-init and post-init hooks.
        superf( *posargs, **nomargs )
        # Some metaclasses add class attributes via '__init__' method.
        # So, we wait until last possible moment to complete initialization.
        decorators_complete = getattr0( cls, _decorators_name, [ ] )
        if decorators_complete: return
        delattr( cls, _decorators_name )
        # TODO: Run hooks for other class attributes.

    return initialize


construct_core = produce_constructor( )
initialize_core = produce_initializer( )


def getattr0(
    cls: type, name: str, default: __.typx.Any
) -> __.typx.Any:
    # TODO: Support slotted classes.
    ''' Returns attribute from class without inheritance. '''
    return cls.__dict__.get( name, default )


def produce_class_factory_class(
    clscls_base: type[ _T ],
    # TODO: clscls_decorators (e.g., 'with_docstring')
    constructor_default: ProduceCfcConstructorArgument = construct_core,
    initializer_default: ProduceCfcInitializerArgument = initialize_core,
    # TODO: assigner_default
    # TODO: deleter_default
    # TODO: surveyor_default
) -> type:
    ''' Produces hooked metaclasses from arbitrary base metaclasses. '''

    class Class( clscls_base ):

        def __new__( # noqa: PLR0913
            clscls: type[ Class ],
            name: str,
            bases: tuple[ type, ... ],
            namespace: dict[ str, __.typx.Any ], *,
            decorators: Decorators = ( ),
            constructor: Constructor = constructor_default,
            initializer: Initializer = initializer_default,
            # TODO: assigner
            # TODO: deleter
            # TODO: surveyor
            **arguments: __.typx.Any,
        ) -> Class:
            return constructor(
                clscls, super( ).__new__,
                name, bases, namespace, arguments,
                decorators, initializer )

        def __init__(
            cls: type,
            *posargs: __.typx.Any,
            **nomargs: __.typx.Any,
        ) -> None:
            # TODO? Default to None and raise exception if default.
            initializer = getattr0(
                cls, _initializer_name, initializer_default )
            initializer( cls, super( ).__init__, posargs, nomargs )

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
