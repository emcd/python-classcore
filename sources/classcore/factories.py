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
NominativeArguments: __.typx.TypeAlias = __.cabc.Mapping[ str, __.typx.Any ]


_decorators_name: str = '_class_decorators_'


BaseConstructor: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[ ..., type ],
    __.typx.Doc( ''' Constructor from base class. ''' ),
]
Constructor: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[
        [
            type,
            BaseConstructor,
            str,
            tuple[ type, ... ],
            dict[ str, __.typx.Any ],
            NominativeArguments,
            Decorators,
        ],
        type
    ],
    __.typx.Doc( ''' Constructor called by ``__new__``. ''' ),
]

ProduceCfcConstructorArgument: __.typx.TypeAlias = __.typx.Annotated[
    Constructor,
    __.typx.Doc( ''' Default constructor for classes. ''' ),
]


def produce_constructor( ) -> Constructor:
    # TODO: Support hooks for additional class attributes.

    def construct( # noqa: PLR0913
        clscls: type[ _T ],
        superf: BaseConstructor,
        name: str,
        bases: tuple[ type, ... ],
        namespace: dict[ str, __.typx.Any ],
        arguments: __.cabc.Mapping[ str, __.typx.Any ],
        decorators: Decorators,
    ) -> type:
        ''' Constructs class, applying decorators. '''
        cls = superf( clscls, name, bases, namespace, **arguments )
        # Some decorators create new classes, which invokes this method again.
        # Short-circuit to prevent recursive decoration and other tangles.
        decorators_complete = getattr0( cls, _decorators_name, [ ] )
        if decorators_complete: return cls
        # TODO: Assign initializer, assigner, deleter, surveyor.
        # TODO: Run closure hooks for other class attributes.
        setattr( cls, _decorators_name, decorators_complete )
        for decorator in decorators:
            decorators_complete.append( decorator )
            cls_ = decorator( cls )
            if cls is cls_: continue
            # TODO: __.repair_class_reproduction( cls, cls_ )
            cls = cls_
        decorators_complete.clear( ) # Unblock top-level '__init__'.
        return cls

    return construct


construct_core = produce_constructor( )


def getattr0(
    cls: type, name: str, default: __.typx.Any
) -> __.typx.Any:
    # TODO: Support slotted classes.
    ''' Returns attribute from class without inheritance. '''
    return cls.__dict__.get( name, default )


def produce_class_factory_class(
    clscls_base: type[ _T ],
    constructor_default: ProduceCfcConstructorArgument = construct_core,
    # TODO: initializer_default
    # TODO: assigner_default
    # TODO: deleter_default
    # TODO: surveyor_default
) -> type:

    class Class( clscls_base ):

        def __new__(
            clscls: type[ Class ],
            name: str,
            bases: tuple[ type, ... ],
            namespace: dict[ str, __.typx.Any ], *,
            decorators: Decorators = ( ),
            constructor: Constructor = constructor_default,
            # TODO: initializer
            # TODO: assigner
            # TODO: deleter
            # TODO: surveyor
            **arguments: __.typx.Any,
        ) -> Class:
            return constructor(
                clscls, super( ).__new__,
                name, bases, namespace, arguments,
                decorators )

    return Class
