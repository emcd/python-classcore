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


from __future__ import annotations

from . import __

Decorator: __.typx.TypeAlias = __.cabc.Callable[ [ type ], type ]
Decorators: __.typx.TypeAlias = __.cabc.Sequence[ Decorator ]
DecoratorsMutable: __.typx.TypeAlias = __.cabc.MutableSequence[ Decorator ]

# TODO: Rename to DecorationPreparer.
DecorationPreprocessor: __.typx.TypeAlias = (
    __.cabc.Callable[ [ type, DecoratorsMutable ], None ] )
DecorationPreprocessors: __.typx.TypeAlias = (
    __.cabc.Sequence[ DecorationPreprocessor ] )

InitializerLigation: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[ ..., None ],
    __.typx.Doc(
        ''' Bound initializer function.

            Usually from ``super( ).__init__`` or a partial function.
        ''' ),
]
AssignerLigation: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[ [ str, __.typx.Any ], None ],
    __.typx.Doc(
        ''' Bound attributes assigner function.

            Usually from ``super( ).__setattr__`` or a partial function.
        ''' ),
]
DeleterLigation: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[ [ str ], None ],
    __.typx.Doc(
        ''' Bound attributes deleter function.

            Usually from ``super( ).__delattr__`` or a partial function.
        ''' ),
]
SurveyorLigation: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[ [ ], __.cabc.Iterable[ str ] ],
    __.typx.Doc(
        ''' Bound attributes surveyor function.

            Usually from ``super( ).__dir__`` or a partial function.
        ''' ),
]
