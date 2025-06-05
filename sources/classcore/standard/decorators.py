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


''' Standard decorators. '''
# TODO? Add attribute value transformer as standard decorator argument.

# ruff: noqa: F401


from .. import factories as _factories
from .. import utilities as _utilities
from ..decorators import (
    decoration_by,
    produce_class_construction_decorator,
    produce_class_initialization_decorator,
)
from . import __
from . import behaviors as _behaviors
from . import dynadoc as _dynadoc
from . import nomina as _nomina


_dataclass_core = __.dcls.dataclass( kw_only = True, slots = True )
_dynadoc_configuration = _dynadoc.produce_dynadoc_configuration( )


def prepare_dataclass_for_instances(
    cls: type,
    decorators: _nomina.DecoratorsMutable[ __.U ], /, *,
    attributes_namer: _nomina.AttributesNamer,
) -> None:
    ''' Annotates dataclass in support of instantiation machinery. '''
    annotations = __.inspect.get_annotations( cls )
    behaviors_name = attributes_namer( 'instance', 'behaviors' )
    behaviors_name_m = _utilities.mangle_name( cls, behaviors_name )
    annotations[ behaviors_name_m ] = set[ str ]
    setattr( cls, '__annotations__', annotations ) # in case of absence
    setattr( cls, behaviors_name_m, __.dcls.field( init = False ) )


def apply_cfc_dynadoc_configuration(
    clscls: type[ __.T ], /,
    attributes_namer: _nomina.AttributesNamer,
    configuration: _nomina.DynadocConfiguration,
) -> None:
    ''' Stores Dynadoc configuration on metaclass. '''
    configuration_name = attributes_namer( 'classes', 'dynadoc_configuration' )
    setattr( clscls, configuration_name, configuration )


def apply_cfc_constructor(
    clscls: type[ __.T ], /, attributes_namer: _nomina.AttributesNamer
) -> None:
    ''' Injects '__new__' method into metaclass. '''
    preprocessors = (
        _behaviors.produce_class_construction_preprocessor(
            attributes_namer = attributes_namer ), )
    postprocessors = (
        _behaviors.produce_class_construction_postprocessor(
            attributes_namer = attributes_namer ), )
    constructor: _nomina.ClassConstructor[ __.T ] = (
        _factories.produce_class_constructor(
            attributes_namer = attributes_namer,
            preprocessors = preprocessors,
            postprocessors = postprocessors ) )
    decorator = produce_class_construction_decorator(
        attributes_namer = attributes_namer, constructor = constructor )
    decorator( clscls )


def apply_cfc_initializer(
    clscls: type[ __.T ], attributes_namer: _nomina.AttributesNamer
) -> None:
    ''' Injects '__init__' method into metaclass. '''
    completers = (
        _behaviors.produce_class_initialization_completer(
            attributes_namer = attributes_namer ), )
    initializer = (
        _factories.produce_class_initializer(
            attributes_namer = attributes_namer,
            completers = completers ) )
    decorator = produce_class_initialization_decorator(
        attributes_namer = attributes_namer, initializer = initializer )
    decorator( clscls )


def apply_cfc_attributes_assigner(
    clscls: type[ __.T ], /,
    attributes_namer: _nomina.AttributesNamer,
    error_class_provider: _nomina.ErrorClassProvider,
    implementation_core: _nomina.AssignerCore,
) -> None:
    ''' Injects '__setattr__' method into metaclass. '''
    decorator = produce_attributes_assignment_decorator(
        level = 'class',
        attributes_namer = attributes_namer,
        error_class_provider = error_class_provider,
        implementation_core = implementation_core )
    decorator( clscls )


def apply_cfc_attributes_deleter(
    clscls: type[ __.T ], /,
    attributes_namer: _nomina.AttributesNamer,
    error_class_provider: _nomina.ErrorClassProvider,
    implementation_core: _nomina.DeleterCore,
) -> None:
    ''' Injects '__delattr__' method into metaclass. '''
    decorator = produce_attributes_deletion_decorator(
        level = 'class',
        attributes_namer = attributes_namer,
        error_class_provider = error_class_provider,
        implementation_core = implementation_core )
    decorator( clscls )


def apply_cfc_attributes_surveyor(
    clscls: type[ __.T ],
    attributes_namer: _nomina.AttributesNamer,
    implementation_core: _nomina.SurveyorCore,
) -> None:
    ''' Injects '__dir__' method into metaclass. '''
    decorator = produce_attributes_surveillance_decorator(
        level = 'class',
        attributes_namer = attributes_namer,
        implementation_core = implementation_core )
    decorator( clscls )


def class_factory( # noqa: PLR0913
    attributes_namer: _nomina.AttributesNamer = __.calculate_attrname,
    error_class_provider: _nomina.ErrorClassProvider = __.provide_error_class,
    assigner_core: _nomina.AssignerCore = (
        _behaviors.assign_attribute_if_mutable ),
    deleter_core: _nomina.DeleterCore = (
        _behaviors.delete_attribute_if_mutable ),
    surveyor_core: _nomina.SurveyorCore = (
        _behaviors.survey_visible_attributes ),
    dynadoc_configuration: __.cabc.Mapping[ str, __.typx.Any ] = (
        _dynadoc_configuration ),
) -> _nomina.Decorator[ __.T ]:
    ''' Produces decorator to apply standard behaviors to metaclass. '''
    def decorate( clscls: type[ __.T ] ) -> type[ __.T ]:
        apply_cfc_dynadoc_configuration(
            clscls,
            attributes_namer = attributes_namer,
            configuration = dynadoc_configuration )
        apply_cfc_constructor( clscls, attributes_namer = attributes_namer )
        apply_cfc_initializer( clscls, attributes_namer = attributes_namer )
        apply_cfc_attributes_assigner(
            clscls,
            attributes_namer = attributes_namer,
            error_class_provider = error_class_provider,
            implementation_core = assigner_core )
        apply_cfc_attributes_deleter(
            clscls,
            attributes_namer = attributes_namer,
            error_class_provider = error_class_provider,
            implementation_core = deleter_core )
        apply_cfc_attributes_surveyor(
            clscls,
            attributes_namer = attributes_namer,
            implementation_core = surveyor_core )
        return clscls

    return decorate


def produce_instances_initialization_decorator(
    attributes_namer: _nomina.AttributesNamer,
    mutables: _nomina.BehaviorExclusionVerifiersOmni,
    visibles: _nomina.BehaviorExclusionVerifiersOmni,
) -> _nomina.Decorator[ __.U ]:
    ''' Produces decorator to inject '__init__' method into class. '''
    def decorate( cls: type[ __.U ] ) -> type[ __.U ]:
        initializer_name = attributes_namer( 'instances', 'initializer' )
        extant = getattr( cls, initializer_name, None )
        original = getattr( cls, '__init__' )
        if extant is original: return cls
        behaviors: set[ str ] = set( )
        behaviors_name = attributes_namer( 'instance', 'behaviors' )
        behaviors_name_m = _utilities.mangle_name( cls, behaviors_name )
        _behaviors.record_behavior(
            cls, attributes_namer = attributes_namer,
            level = 'instances', basename = 'mutables',
            label = _nomina.immutability_label, behaviors = behaviors,
            verifiers = mutables )
        _behaviors.record_behavior(
            cls, attributes_namer = attributes_namer,
            level = 'instances', basename = 'visibles',
            label = _nomina.concealment_label, behaviors = behaviors,
            verifiers = visibles )

        @__.funct.wraps( original )
        def initialize(
            self: object, *posargs: __.typx.Any, **nomargs: __.typx.Any
        ) -> None:
            original( self, *posargs, **nomargs )
            behaviors_: set[ str ] = getattr( self, behaviors_name_m, set( ) )
            behaviors_.update( behaviors )
            setattr( self, behaviors_name_m, frozenset( behaviors_ ) )

        setattr( cls, initializer_name, initialize )
        cls.__init__ = initialize
        return cls

    return decorate


def produce_attributes_assignment_decorator(
    level: str,
    attributes_namer: _nomina.AttributesNamer,
    error_class_provider: _nomina.ErrorClassProvider,
    implementation_core: _nomina.AssignerCore,
) -> _nomina.Decorator[ __.U ]:
    ''' Produces decorator to inject '__setattr__' method into class. '''
    def decorate( cls: type[ __.U ] ) -> type[ __.U ]:
        assigner_name = attributes_namer( level, 'assigner' )
        extant = getattr( cls, assigner_name, None )
        original = getattr( cls, '__setattr__' )
        if extant is original: return cls

        @__.funct.wraps( original )
        def assign( self: object, name: str, value: __.typx.Any ) -> None:
            implementation_core(
                self,
                ligation = __.funct.partial( original, self ),
                attributes_namer = attributes_namer,
                error_class_provider = error_class_provider,
                level = level,
                name = name, value = value )

        setattr( cls, assigner_name, assign )
        cls.__setattr__ = assign
        return cls

    return decorate


def produce_attributes_deletion_decorator(
    level: str,
    attributes_namer: _nomina.AttributesNamer,
    error_class_provider: _nomina.ErrorClassProvider,
    implementation_core: _nomina.DeleterCore,
) -> _nomina.Decorator[ __.U ]:
    ''' Produces decorator to inject '__delattr__' method into class. '''
    def decorate( cls: type[ __.U ] ) -> type[ __.U ]:
        deleter_name = attributes_namer( level, 'deleter' )
        extant = getattr( cls, deleter_name, None )
        original = getattr( cls, '__delattr__' )
        if extant is original: return cls

        @__.funct.wraps( original )
        def delete( self: object, name: str ) -> None:
            implementation_core(
                self,
                ligation = __.funct.partial( original, self ),
                attributes_namer = attributes_namer,
                error_class_provider = error_class_provider,
                level = level,
                name = name )

        setattr( cls, deleter_name, delete )
        cls.__delattr__ = delete
        return cls

    return decorate


def produce_attributes_surveillance_decorator(
    level: str,
    attributes_namer: _nomina.AttributesNamer,
    implementation_core: _nomina.SurveyorCore,
) -> _nomina.Decorator[ __.U ]:
    ''' Produces decorator to inject '__dir__' method into class. '''
    def decorate( cls: type[ __.U ] ) -> type[ __.U ]:
        surveyor_name = attributes_namer( level, 'surveyor' )
        extant = getattr( cls, surveyor_name, None )
        original = getattr( cls, '__dir__' )
        if extant is original: return cls

        @__.funct.wraps( original )
        def survey( self: object ) -> __.cabc.Iterable[ str ]:
            return implementation_core(
                self,
                ligation = __.funct.partial( original, self ),
                attributes_namer = attributes_namer,
                level = level )

        setattr( cls, surveyor_name, survey )
        cls.__dir__ = survey
        return cls

    return decorate


def produce_decorators_factory( # noqa: PLR0913
    level: str,
    attributes_namer: _nomina.AttributesNamer = __.calculate_attrname,
    error_class_provider: _nomina.ErrorClassProvider = __.provide_error_class,
    assigner_core: _nomina.AssignerCore = (
        _behaviors.assign_attribute_if_mutable ),
    deleter_core: _nomina.DeleterCore = (
        _behaviors.delete_attribute_if_mutable ),
    surveyor_core: _nomina.SurveyorCore = (
        _behaviors.survey_visible_attributes ),
) -> __.cabc.Callable[
    [
        _nomina.BehaviorExclusionVerifiersOmni,
        _nomina.BehaviorExclusionVerifiersOmni
    ],
    _nomina.Decorators[ __.U ]
]:
    ''' Produces decorators to imbue class with standard behaviors. '''
    def produce(
        mutables: _nomina.BehaviorExclusionVerifiersOmni,
        visibles: _nomina.BehaviorExclusionVerifiersOmni,
    ) -> _nomina.Decorators[ __.U ]:
        ''' Produces standard decorators. '''
        decorators: list[ _nomina.Decorator[ __.U ] ] = [ ]
        decorators.append(
            produce_instances_initialization_decorator(
                attributes_namer = attributes_namer,
                mutables = mutables, visibles = visibles ) )
        if mutables != '*':
            decorators.append(
                produce_attributes_assignment_decorator(
                    level = level,
                    attributes_namer = attributes_namer,
                    error_class_provider = error_class_provider,
                    implementation_core = assigner_core ) )
            decorators.append(
                produce_attributes_deletion_decorator(
                    level = level,
                    attributes_namer = attributes_namer,
                    error_class_provider = error_class_provider,
                    implementation_core = deleter_core ) )
        if visibles != '*':
            decorators.append(
                produce_attributes_surveillance_decorator(
                    level = level,
                    attributes_namer = attributes_namer,
                    implementation_core = surveyor_core ) )
        return decorators

    return produce


def produce_decoration_preparers_factory(
    attributes_namer: _nomina.AttributesNamer = __.calculate_attrname,
    error_class_provider: _nomina.ErrorClassProvider = __.provide_error_class,
    class_preparer: __.typx.Optional[ _nomina.ClassPreparer ] = None,
) -> _nomina.DecorationPreparersFactory[ __.U ]:
    ''' Produces factory to produce class decoration preparers.

        E.g., a preparer needs to inject special annotations to ensure
        compatibility with standard behaviors before
        :py:func:`dataclasses.dataclass` decorates a class.
    '''
    def produce( ) -> _nomina.DecorationPreparers[ __.U ]:
        ''' Produces processors for standard decorators. '''
        preprocessors: list[ _nomina.DecorationPreparer[ __.U ] ] = [ ]
        if class_preparer is not None:
            preprocessors.append(
                __.funct.partial(
                    class_preparer,
                    attributes_namer = attributes_namer  ) )
        return tuple( preprocessors )

    return produce


@__.typx.dataclass_transform( frozen_default = True, kw_only_default = True )
def dataclass_with_standard_behaviors(
    decorators: _nomina.Decorators[ __.U ] = ( ),
    mutables: _nomina.BehaviorExclusionVerifiersOmni = __.mutables_default,
    visibles: _nomina.BehaviorExclusionVerifiersOmni = __.visibles_default,
) -> _nomina.Decorator[ __.U ]:
    # https://github.com/microsoft/pyright/discussions/10344
    ''' Dataclass decorator factory. '''
    decorators_factory = produce_decorators_factory( level = 'instances' )
    decorators_: _nomina.Decorators[ __.U ] = (
        decorators_factory( mutables, visibles ) )
    preparers_factory = produce_decoration_preparers_factory(
        class_preparer = prepare_dataclass_for_instances )
    preparers: _nomina.DecorationPreparers[ __.U ] = preparers_factory( )
    return decoration_by(
        *decorators, _dataclass_core, *decorators_, preparers = preparers )


def with_standard_behaviors(
    decorators: _nomina.Decorators[ __.U ] = ( ),
    mutables: _nomina.BehaviorExclusionVerifiersOmni = __.mutables_default,
    visibles: _nomina.BehaviorExclusionVerifiersOmni = __.visibles_default,
) -> _nomina.Decorator[ __.U ]:
    ''' Class decorator factory. '''
    decorators_factory = produce_decorators_factory( level = 'instances' )
    decorators_: _nomina.Decorators[ __.U ] = (
        decorators_factory( mutables, visibles ) )
    preparers_factory = produce_decoration_preparers_factory( )
    preparers: _nomina.DecorationPreparers[ __.U ] = preparers_factory( )
    return decoration_by( *decorators, *decorators_, preparers = preparers )
