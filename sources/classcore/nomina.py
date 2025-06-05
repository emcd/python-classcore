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


''' Catalog of common type aliases. '''


from . import __


AttributesNamer: __.typx.TypeAlias = __.cabc.Callable[ [ str, str ], str ]

Decorator: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[ [ type[ __.U ] ], type[ __.U ] ],
    __.dynadoc.Doc(
        ''' Class decorator.

            Takes class argument and returns class.
        ''' ),
]
Decorators: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Sequence[ Decorator[ __.U ] ], __.dynadoc.Fname( 'decorators' )
]
DecoratorsMutable: __.typx.TypeAlias = __.typx.Annotated[
   __.cabc.MutableSequence[ Decorator[ __.U ] ],
   __.dynadoc.Fname( 'decorators' ),
   __.dynadoc.Doc(
       ''' Decorators may be inserted or removed from sequence. ''' ),
]

DecorationPreparer: __.typx.TypeAlias = (
    __.cabc.Callable[ [ type[ __.U ], DecoratorsMutable[ __.U ] ], None ] )
DecorationPreparers: __.typx.TypeAlias = (
    __.cabc.Sequence[ DecorationPreparer[ __.U ] ] )
DecorationPreparersFactory: __.typx.TypeAlias = (
    __.cabc.Callable[ [ ], DecorationPreparers[ __.U ] ] )

ClassConstructorLigation: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[ ..., type ],
    __.dynadoc.Doc(
        ''' Bound class constructor function.

            Usually from ``super( ).__new__`` or a partial function.
        ''' ),
]
InitializerLigation: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[ ..., None ],
    __.dynadoc.Doc(
        ''' Bound initializer function.

            Usually from ``super( ).__init__`` or a partial function.
        ''' ),
]
AssignerLigation: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[ [ str, __.typx.Any ], None ],
    __.dynadoc.Doc(
        ''' Bound attributes assigner function.

            Usually from ``super( ).__setattr__`` or a partial function.
        ''' ),
]
DeleterLigation: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[ [ str ], None ],
    __.dynadoc.Doc(
        ''' Bound attributes deleter function.

            Usually from ``super( ).__delattr__`` or a partial function.
        ''' ),
]
SurveyorLigation: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[ [ ], __.cabc.Iterable[ str ] ],
    __.dynadoc.Doc(
        ''' Bound attributes surveyor function.

            Usually from ``super( ).__dir__`` or a partial function.
        ''' ),
]


ClassConstructionPreprocessor: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[
        [
            type[ type ],               # metaclass
            str,                        # class name
            list[ type ],               # bases (mutable)
            dict[ str, __.typx.Any ],   # namespace (mutable)
            dict[ str, __.typx.Any ],   # arguments (mutable)
            DecoratorsMutable[ __.U ],  # decorators (mutable)
        ],
        None
    ],
    __.dynadoc.Doc(
        ''' Processes class data before construction.

            For use cases, such as argument conversion.
        ''' ),
]
ClassConstructionPostprocessor: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[ [ type, DecoratorsMutable[ __.U ] ], None ],
    __.dynadoc.Doc(
        ''' Processes class before decoration.

            For use cases, such as decorator list manipulation.
        ''' ),
]
# TODO: ClassInitializationPreparer (arguments mutation)
ClassInitializationCompleter: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[ [ type ], None ],
    __.dynadoc.Doc(
        ''' Completes initialization of class.

            For use cases, such as enabling immutability once all other
            initialization has occurred.
        ''' ),
]


ClassConstructor: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[
        [
            type,
            ClassConstructorLigation,
            str,
            tuple[ type, ... ],
            dict[ str, __.typx.Any ],
            __.NominativeArguments,
            Decorators[ __.U ],
        ],
        type
    ],
    __.dynadoc.Doc( ''' Constructor to use with metaclass. ''' ),
]
ClassInitializer: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[
        [
            type,
            InitializerLigation,
            __.PositionalArguments,
            __.NominativeArguments,
        ],
        None
    ],
    __.dynadoc.Doc( ''' Initializer to use with metaclass. ''' ),
]


ProduceConstructorPreprocsArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Sequence[ ClassConstructionPreprocessor[ __.U ] ],
    __.dynadoc.Doc(
        ''' Processors to apply before construction of class. ''' ),
]
ProduceConstructorPostprocsArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Sequence[ ClassConstructionPostprocessor[ __.U ] ],
    __.dynadoc.Doc(
        ''' Processors to apply before decoration of class. ''' ),
]
ProduceInitializerCompletersArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Sequence[ ClassInitializationCompleter ],
    __.dynadoc.Doc(
        ''' Processors to apply at final stage of class initialization. ''' ),
]
