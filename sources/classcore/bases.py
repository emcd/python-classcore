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


''' Special base classes.

    The dataclass bases provide a means of marking a derived class as a
    dataclass without directly decorating the derived class. This allows us to
    provide a single metaclass factory without needing variants of the factory
    to support production of dataclasses.
'''


from __future__ import annotations

from . import __


@__.typx.dataclass_transform( frozen_default = True, kw_only_default = True )
class DataclassObjectBase:
    ''' Dataclass base with immutability.

        Metaclasses can look for ``__dataclass_transform__`` field to trigger
        application of appropriate dataclass decorator.
    '''


@__.typx.dataclass_transform( kw_only_default = True )
class DataclassObjectMutableBase:
    ''' Dataclass base.

        Metaclasses can look for ``__dataclass_transform__`` field to trigger
        application of appropriate dataclass decorator.
    '''


@__.typx.dataclass_transform( frozen_default = True, kw_only_default = True )
class DataclassProtocolBase( __.typx.Protocol ):
    ''' Protocol dataclass base with immutability.

        Metaclasses can look for ``__dataclass_transform__`` field to trigger
        application of appropriate dataclass decorator.
    '''


@__.typx.dataclass_transform( kw_only_default = True )
class DataclassProtocolMutableBase( __.typx.Protocol ):
    ''' Protocol dataclass base.

        Metaclasses can look for ``__dataclass_transform__`` field to trigger
        application of appropriate dataclass decorator.
    '''
