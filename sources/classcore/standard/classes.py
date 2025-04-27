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


''' Standard classes and class factories. '''


from __future__ import annotations

from .. import factories as _factories
from . import __
from . import behaviors as _behaviors
from . import decorators as _decorators
from . import nomina as _nomina


def _produce_class_factory_core(
    attributes_namer: _nomina.AttributesNamer,
    error_class_provider: _nomina.ErrorClassProvider,
) -> tuple[ _nomina.ClassConstructor, _nomina.ClassInitializer ]:
    preprocessors = (
        _behaviors.produce_class_construction_preprocessor(
            attributes_namer = attributes_namer ), )
    postprocessors = (
        _behaviors.produce_class_construction_postprocessor(
            attributes_namer = attributes_namer ), )
    completers = (
        _behaviors.produce_class_initialization_completer(
            attributes_namer = attributes_namer ), )
    constructor = (
        _factories.produce_class_constructor(
            attributes_namer = attributes_namer,
            preprocessors = preprocessors,
            postprocessors = postprocessors ) )
    initializer = (
        _factories.produce_class_initializer(
            attributes_namer = attributes_namer,
            completers = completers ) )
    return constructor, initializer


def produce_class_factory_decorators(
    attributes_namer: _nomina.AttributesNamer = __.calculate_attrname,
    error_class_provider: _nomina.ErrorClassProvider = __.provide_error_class,
    assigner_core: _nomina.AssignerCore = (
        _behaviors.assign_attribute_if_mutable ),
    deleter_core: _nomina.DeleterCore = (
        _behaviors.delete_attribute_if_mutable ),
    surveyor_core: _nomina.SurveyorCore = (
        _behaviors.survey_visible_attributes ),
) -> _nomina.Decorators:
    decorators: list[ _nomina.Decorator ] = [ ]
    constructor, initializer = (
        _produce_class_factory_core(
            attributes_namer = attributes_namer,
            error_class_provider = error_class_provider ) )
    decorators.append(
        _factories.produce_class_construction_decorator(
            attributes_namer = attributes_namer,
            constructor = constructor ) )
    decorators.append(
        _factories.produce_class_initialization_decorator(
            attributes_namer = attributes_namer,
            initializer = initializer ) )
    decorators.append(
        _decorators.produce_attributes_assignment_decorator(
            level = 'class',
            attributes_namer = attributes_namer,
            error_class_provider = error_class_provider,
            implementation_core = assigner_core ) )
    decorators.append(
        _decorators.produce_attributes_deletion_decorator(
            level = 'class',
            attributes_namer = attributes_namer,
            error_class_provider = error_class_provider,
            implementation_core = deleter_core ) )
    decorators.append(
        _decorators.produce_attributes_surveillance_decorator(
            level = 'class',
            attributes_namer = attributes_namer,
            implementation_core = surveyor_core ) )
    return decorators


class_factory_decorators = produce_class_factory_decorators( )


@_factories.decoration_by( *class_factory_decorators )
class Class( type ): pass


@_factories.decoration_by( *class_factory_decorators )
@__.typx.dataclass_transform( frozen_default = True, kw_only_default = True )
class Dataclass( type ): pass


@_factories.decoration_by( *class_factory_decorators )
@__.typx.dataclass_transform( kw_only_default = True )
class DataclassMutable( type ): pass


@_factories.decoration_by( *class_factory_decorators )
class ProtocolClass( type( __.typx.Protocol ) ): pass


@_factories.decoration_by( *class_factory_decorators )
@__.typx.dataclass_transform( frozen_default = True, kw_only_default = True )
class ProtocolDataclass( type( __.typx.Protocol ) ): pass


@_factories.decoration_by( *class_factory_decorators )
@__.typx.dataclass_transform( kw_only_default = True )
class ProtocolDataclassMutable( type( __.typx.Protocol ) ): pass


class Object( metaclass = Class ): pass


class DataclassObject( metaclass = Dataclass ): pass


class DataclassObjectMutable( metaclass = DataclassMutable ): pass


class Protocol( __.typx.Protocol, metaclass = ProtocolClass ): pass


class DataclassProtocol(
    __.typx.Protocol, metaclass = ProtocolDataclass,
): pass


class DataclassProtocolMutable(
    __.typx.Protocol, metaclass = ProtocolDataclassMutable,
): pass
