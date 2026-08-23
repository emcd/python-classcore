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


''' Common constants, imports, and utilities. '''

# ruff: noqa: F403, F405


from ..__ import *
from ..nomina import is_public_identifier


def provide_error_class( name: str ) -> type[ Exception ]:
    ''' Produces error class for this package. '''
    match name:
        case 'AttributeImmutability':
            from ..exceptions import AttributeImmutability as error
        case _:
            from ..exceptions import ErrorProvideFailure
            raise ErrorProvideFailure( name, reason = 'Does not exist.' )
    return error


mutables_default = ( )
visibles_default = ( is_public_identifier, )

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


def is_same_detector(
    detector: cabc.Callable[ [ str ], bool ],
    other: cabc.Callable[ [ str ], bool ], /,
) -> bool:
    ''' Returns whether two detector references are the same detector.

        Bound methods are the same detector only when both the
        underlying function and the bound instance are identical, so
        distinct namer instances with distinct configured behavior keep
        separate contributions. Plain callables compare by identity.
    '''
    if detector is other: return True
    function = getattr( detector, '__func__', None )
    other_function = getattr( other, '__func__', None )
    if function is None or other_function is None: return False
    return (
        function is other_function
        and getattr( detector, '__self__', None )
            is getattr( other, '__self__', None ) )


def augment_internal_names(
    cls: type, /, detector: cabc.Callable[ [ str ], bool ]
) -> None:
    ''' Adds an internal-name detector to existing contributions.

        Private wiring point for machinery mixins: the abstract-base
        metaclass adds the stdlib machinery set after factory
        decoration, without expanding public factory arguments.
    '''
    detectors = getattr( cls, calculate_contribution_name( ), ( ) )
    if any( is_same_detector( detector, d ) for d in detectors ): return
    setattr(
        cls, calculate_contribution_name( ),
        ( *detectors, detector ) )
