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
from . import bases as _bases
from . import factories as _factories
from . import nomina as _nomina


# TODO: Custom implementations.
#       Concealment and immutability.
#       Dataclass detection.
#       Slots detection.


Class = _factories.produce_factory_class( type )
ProtocolClass = (
    _factories.produce_factory_class(
        type( __.typx.Protocol ) ) ) # pyright: ignore[reportArgumentType]


def immutable(
    # TODO: mutables
    # TODO? mutables_regexes
    # TODO? mutables_predicates
    # TODO: visibles
    # TODO? visibles_regexes
    # TODO? visibles_predicates (default: public members only)
) -> _nomina.Decorator:
    # TODO: Pass appropriate postprocessors to decorator factory.
    return _factories.produce_decorator( )


# TODO: Object (with 'immutable' decorator)


class ObjectMutable( metaclass = Class ): pass


class DataclassObject(
    _bases.DataclassObjectBase, metaclass = Class
): pass


class DataclassObjectMutable(
    _bases.DataclassObjectMutableBase, metaclass = Class
): pass


# TODO: Protocol (with 'immutable' decorator)


class ProtocolMutable( __.typx.Protocol, metaclass = ProtocolClass ): pass


class DataclassProtocol(
    _bases.DataclassProtocolBase, __.typx.Protocol,
    metaclass = ProtocolClass,
): pass


class DataclassProtocolMutable(
    _bases.DataclassProtocolMutableBase, __.typx.Protocol,
    metaclass = ProtocolClass,
): pass
