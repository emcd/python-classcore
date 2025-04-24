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


''' Decorators and metaclasses with concealment and immutability. '''
# TODO: Support introspection of PEP 593 annotations for markers.
#       Behaviors enum for mutability and visibility.


from __future__ import annotations

from . import __
from . import bases as _bases
from . import factories as _factories
from . import nomina as _nomina
from . import utilities as _utilities


_T = __.typx.TypeVar( '_T', bound = type )
_U = __.typx.TypeVar( '_U' )


BehaviorExclusionNames: __.typx.TypeAlias = __.cabc.Set[ str ]
BehaviorExclusionPredicate: __.typx.TypeAlias = __.cabc.Callable[ ..., bool ]
BehaviorExclusionPredicates: __.typx.TypeAlias = (
    __.cabc.Sequence[ BehaviorExclusionPredicate ] )
BehaviorExclusionRegex: __.typx.TypeAlias = __.re.Pattern[ str ]
BehaviorExclusionRegexes: __.typx.TypeAlias = (
    __.cabc.Sequence[ BehaviorExclusionRegex ] )
BehaviorExclusionVerifier: __.typx.TypeAlias = (
    str | BehaviorExclusionRegex | BehaviorExclusionPredicate )
BehaviorExclusionVerifiers: __.typx.TypeAlias = (
    __.cabc.Sequence[ BehaviorExclusionVerifier ] )
MutablesNames: __.typx.TypeAlias = __.cabc.Set[ str ]
AttributeMutabilityPredicate: __.typx.TypeAlias = (
    __.cabc.Callable[ [ str, __.typx.Any ], bool ] )
AttributeMutabilityPredicates: __.typx.TypeAlias = (
    __.cabc.Sequence[ AttributeMutabilityPredicate ] )
AttributeMutabilityRegexes: __.typx.TypeAlias = (
    __.cabc.Sequence[ __.re.Pattern[ str ] ] )
AttributeMutabilityVerifier: __.typx.TypeAlias = (
    str | BehaviorExclusionRegex | AttributeMutabilityPredicate )
AttributeMutabilityVerifiers: __.typx.TypeAlias = (
    __.cabc.Sequence[ AttributeMutabilityVerifier ] | __.typx.Literal[ '*' ] )
VisiblesNames: __.typx.TypeAlias = __.cabc.Set[ str ]
AttributeVisibilityPredicate: __.typx.TypeAlias = (
    __.cabc.Callable[ [ str ], bool ] )
AttributeVisibilityPredicates: __.typx.TypeAlias = (
    __.cabc.Sequence[ AttributeVisibilityPredicate ] )
AttributeVisibilityRegexes: __.typx.TypeAlias = (
    __.cabc.Sequence[ __.re.Pattern[ str ] ] )
AttributeVisibilityVerifier: __.typx.TypeAlias = (
    str | BehaviorExclusionRegex | AttributeVisibilityPredicate )
AttributeVisibilityVerifiers: __.typx.TypeAlias = (
    __.cabc.Sequence[ AttributeVisibilityVerifier ] | __.typx.Literal[ '*' ] )
AttributesNamer: __.typx.TypeAlias = (
    __.cabc.Callable[ [ str, str ], str ] )
ErrorClassProvider: __.typx.TypeAlias = (
    __.cabc.Callable[ [ str ], type[ Exception ] ] )


class AssignerCore( __.typx.Protocol ):
    ''' Core implementation of attributes assigner. '''

    @staticmethod
    def __call__( # noqa: PLR0913
        obj: object, /, *,
        ligation: _nomina.AssignerLigation,
        error_class_provider: ErrorClassProvider,
        behaviors_name: str,
        names_name: str,
        regexes_name: str,
        predicates_name: str,
        name: str,
        value: __.typx.Any,
    ) -> None: raise NotImplementedError


class DeleterCore( __.typx.Protocol ):
    ''' Core implementation of attributes deleter. '''

    @staticmethod
    def __call__( # noqa: PLR0913
        obj: object, /, *,
        ligation: _nomina.DeleterLigation,
        error_class_provider: ErrorClassProvider,
        behaviors_name: str,
        names_name: str,
        regexes_name: str,
        predicates_name: str,
        name: str,
    ) -> None: raise NotImplementedError


class SurveyorCore( __.typx.Protocol ):
    ''' Core implementation of attributes surveyor. '''

    @staticmethod
    def __call__( # noqa: PLR0913
        obj: object, /, *,
        ligation: _nomina.SurveyorLigation,
        behaviors_name: str,
        names_name: str,
        regexes_name: str,
        predicates_name: str,
    ) -> __.cabc.Iterable[ str ]: raise NotImplementedError


def is_public_identifier( name: str ) -> bool:
    ''' Is Python identifier public? '''
    return not name.startswith( '_' )


_dataclass_core = __.dcls.dataclass( kw_only = True, slots = True )
_concealment_label = 'concealment'
_immutability_label = 'immutability'
_mutables_default = ( )
_visibles_default = ( is_public_identifier, )


def _calculate_attrname( level: str, core: str ) -> str:
    return f"_{__.package_name}_{level}_{core}_"


def _provide_error_class( name: str ) -> type[ Exception ]:
    ''' Produces error class for this package. '''
    match name:
        case 'AttributeImmutability':
            from .exceptions import AttributeImmutability as error
        case _:
            from .exceptions import ErrorProductionFailure
            raise ErrorProductionFailure( name, reason = 'Does not exist.' )
    return error


@__.typx.dataclass_transform( frozen_default = True, kw_only_default = True )
def dataclass_standard(
    mutables: AttributeMutabilityVerifiers = _mutables_default,
    visibles: AttributeVisibilityVerifiers = _visibles_default,
    # TODO? attribute value transformer
) -> _nomina.Decorator:
    # https://github.com/microsoft/pyright/discussions/10344
    ''' Dataclass decorator factory. '''
    preprocessors, postprocessors = (
        _produce_decoration_processors( mutables, visibles ) )
    return _factories.produce_decorator(
        decorators = ( _dataclass_core, ),
        preprocessors = preprocessors,
        postprocessors = postprocessors )


def standard(
    mutables: AttributeMutabilityVerifiers = _mutables_default,
    visibles: AttributeVisibilityVerifiers = _visibles_default,
    # TODO? attribute value transformer
) -> _nomina.Decorator:
    ''' Class decorator factory. '''
    preprocessors, postprocessors = (
        _produce_decoration_processors( mutables, visibles ) )
    return _factories.produce_decorator(
        preprocessors = preprocessors,
        postprocessors = postprocessors )


def class_construction_preprocessor( # noqa: PLR0913
    clscls: type,
    name: str,
    bases: list[ type ],
    namespace: dict[ str, __.typx.Any ],
    arguments: dict[ str, __.typx.Any ],
    decorators: _nomina.DecoratorsMutable,
) -> None:
    # TODO: Produce function via factory to customize attributes namer.
    _record_class_construction_arguments( namespace, arguments )
    annotations = namespace.get( '__annotations__', { } )
    # annotations[ _cfc_behaviors_name ] = __.typx.ClassVar[ set[ str ] ]
    namespace[ '__annotations__' ] = annotations
    if '__slots__' in namespace:
        slots = list( namespace[ '__slots__' ] )
        # slots.append( _cfc_behaviors_name )
        namespace[ '__slots__' ] = slots


def class_construction_postprocessor(
    cls: type, decorators: _nomina.DecoratorsMutable
) -> None:
    # TODO: Produce function via factory to customize attributes namer.
    arguments_name = _calculate_attrname( 'class', 'construction_arguments' )
    arguments = getattr( cls, arguments_name, { } )
    dcls_spec = getattr( cls, '__dataclass_transform__', None )
    instance_mutables = arguments.get( 'instance_mutables', _mutables_default )
    instance_visibles = arguments.get( 'instance_visibles', _visibles_default )
    if dcls_spec and dcls_spec.get( 'kw_only_default', False ):
        decorator_factory = dataclass_standard
        if not dcls_spec.get( 'frozen_default', True ):
            instance_mutables = instance_mutables or '*'
    else: decorator_factory = standard
    decorator = decorator_factory(
        mutables = instance_mutables, visibles = instance_visibles )
    decorators.append( decorator )


def class_initialization_completer( cls: type ) -> None:
    # TODO: Produce function via factory to customize attributes namer.
    attributes_namer = _calculate_attrname
    arguments_name = attributes_namer( 'class', 'construction_arguments' )
    arguments: __.typx.Optional[ dict[ str, __.typx.Any ] ] = (
        getattr( cls, arguments_name, None ) )
    if arguments is not None: delattr( cls, arguments_name )
    arguments = arguments or { }
    class_mutables = arguments.get( 'class_mutables', _mutables_default )
    class_visibles = arguments.get( 'class_visibles', _visibles_default )
    behaviors: set[ str ] = set( )
    if class_mutables != '*':
        _record_behavior_exclusions(
            cls, attributes_namer, 'mutables', 'class', class_mutables )
        behaviors.add( _immutability_label )
    if class_visibles != '*':
        _record_behavior_exclusions(
            cls, attributes_namer, 'visibles', 'class', class_visibles )
        behaviors.add( _concealment_label )
    # Set behaviors attribute last since it enables enforcement.
    setattr( cls, attributes_namer( 'class', 'behaviors' ), behaviors )


def produce_class_attributes_assigner(
    attributes_namer: AttributesNamer,
    error_class_provider: ErrorClassProvider,
    implementation_core: AssignerCore,
) -> _factories.Assigner:
    behaviors_name = attributes_namer( 'class', 'behaviors' )
    names_name = attributes_namer( 'class', 'mutables_names' )
    regexes_name = attributes_namer( 'class', 'mutables_regexes' )
    predicates_name = attributes_namer( 'class', 'mutables_predicates' )

    def assign(
        cls: type,
        superf: _nomina.AssignerLigation,
        name: str,
        value: __.typx.Any,
    ) -> None:
        implementation_core(
            cls,
            ligation = superf,
            error_class_provider = error_class_provider,
            behaviors_name = behaviors_name,
            names_name = names_name,
            regexes_name = regexes_name,
            predicates_name = predicates_name,
            name = name,
            value = value )

    return assign


def produce_class_attributes_deleter(
    attributes_namer: AttributesNamer,
    error_class_provider: ErrorClassProvider,
    implementation_core: DeleterCore,
) -> _factories.Deleter:
    behaviors_name = attributes_namer( 'class', 'behaviors' )
    names_name = attributes_namer( 'class', 'mutables_names' )
    regexes_name = attributes_namer( 'class', 'mutables_regexes' )
    predicates_name = attributes_namer( 'class', 'mutables_predicates' )

    def delete(
        cls: type, superf: _nomina.DeleterLigation, name: str
    ) -> None:
        implementation_core(
            cls,
            ligation = superf,
            error_class_provider = error_class_provider,
            behaviors_name = behaviors_name,
            names_name = names_name,
            regexes_name = regexes_name,
            predicates_name = predicates_name,
            name = name )

    return delete


def produce_class_attributes_surveyor(
    attributes_namer: AttributesNamer,
    implementation_core: SurveyorCore,
) -> _factories.Surveyor:
    behaviors_name = attributes_namer( 'class', 'behaviors' )
    names_name = attributes_namer( 'class', 'visibles_names' )
    regexes_name = attributes_namer( 'class', 'visibles_regexes' )
    predicates_name = attributes_namer( 'class', 'visibles_predicates' )

    def survey(
        cls: type, superf: _nomina.SurveyorLigation
    ) -> __.cabc.Iterable[ str ]:
        return implementation_core(
            cls,
            ligation = superf,
            behaviors_name = behaviors_name,
            names_name = names_name,
            regexes_name = regexes_name,
            predicates_name = predicates_name )

    return survey


def _annotate_class_for_instances(
    cls: type, decorators: _nomina.DecoratorsMutable
) -> None:
    ''' Annotates class in support of instantiation machinery. '''
    annotations = __.inspect.get_annotations( cls )
    # TODO: accretive set instead of set
    annotations[ _calculate_attrname( 'instance', 'behaviors' ) ] = set[ str ]


def _associate_instances_attributes_assigner(
    cls: type[ _U ], /, *,
    attributes_namer: AttributesNamer,
    error_class_provider: ErrorClassProvider,
    implementation_core: AssignerCore,
) -> None:
    assigner_name = attributes_namer( 'instances', 'assigner' )
    extant = getattr( cls, assigner_name, None )
    original = getattr( cls, '__setattr__' )
    if extant is original: return
    behaviors_name = attributes_namer( 'instance', 'behaviors' )
    names_name = attributes_namer( 'instances', 'mutables_names' )
    regexes_name = attributes_namer( 'instances', 'mutables_regexes' )
    predicates_name = attributes_namer( 'instances', 'mutables_predicates' )

    @__.funct.wraps( original )
    def assign( self: object, name: str, value: __.typx.Any ) -> None:
        implementation_core(
            self,
            ligation = __.funct.partial( original, self ),
            error_class_provider = error_class_provider,
            behaviors_name = behaviors_name,
            names_name = names_name,
            regexes_name = regexes_name,
            predicates_name = predicates_name,
            name = name,
            value = value )

    setattr( cls, assigner_name, assign )
    cls.__setattr__ = assign


def _associate_instances_attributes_deleter(
    cls: type[ _U ],
    attributes_namer: AttributesNamer,
    error_class_provider: ErrorClassProvider,
    implementation_core: DeleterCore,
) -> None:
    deleter_name = attributes_namer( 'instances', 'deleter' )
    extant = getattr( cls, deleter_name, None )
    original = getattr( cls, '__delattr__' )
    if extant is original: return
    behaviors_name = attributes_namer( 'instance', 'behaviors' )
    names_name = attributes_namer( 'instances', 'mutables_names' )
    regexes_name = attributes_namer( 'instances', 'mutables_regexes' )
    predicates_name = attributes_namer( 'instances', 'mutables_predicates' )

    @__.funct.wraps( original )
    def delete( self: object, name: str ) -> None:
        implementation_core(
            self,
            ligation = __.funct.partial( original, self ),
            error_class_provider = error_class_provider,
            behaviors_name = behaviors_name,
            names_name = names_name,
            regexes_name = regexes_name,
            predicates_name = predicates_name,
            name = name )

    setattr( cls, deleter_name, delete )
    cls.__delattr__ = delete


def _associate_instances_attributes_surveyor(
    cls: type[ _U ],
    attributes_namer: AttributesNamer,
    implementation_core: SurveyorCore,
) -> None:
    surveyor_name = attributes_namer( 'instances', 'surveyor' )
    extant = getattr( cls, surveyor_name, None )
    original = getattr( cls, '__dir__' )
    if extant is original: return
    behaviors_name = attributes_namer( 'instance', 'behaviors' )
    names_name = attributes_namer( 'instances', 'visibles_names' )
    regexes_name = attributes_namer( 'instances', 'visibles_regexes' )
    predicates_name = attributes_namer( 'instances', 'visibles_predicates' )

    @__.funct.wraps( original )
    def survey( self: object ) -> __.cabc.Iterable[ str ]:
        return implementation_core(
            self,
            ligation = __.funct.partial( original, self ),
            behaviors_name = behaviors_name,
            names_name = names_name,
            regexes_name = regexes_name,
            predicates_name = predicates_name )

    setattr( cls, surveyor_name, survey )
    cls.__dir__ = survey


def _assign_attribute_if_mutable( # noqa: PLR0913
    obj: object, /, *,
    ligation: _nomina.AssignerLigation,
    error_class_provider: ErrorClassProvider,
    behaviors_name: str,
    names_name: str,
    regexes_name: str,
    predicates_name: str,
    name: str,
    value: __.typx.Any,
) -> None:
    behaviors = _utilities.getattr0( obj, behaviors_name, frozenset( ) )
    if _immutability_label not in behaviors:
        ligation( name, value )
        return
    names: MutablesNames = getattr( obj, names_name, frozenset( ) )
    # regexes: AttributeMutabilityRegexes = (
    #     getattr( self, regexes_name, ( ) ) )
    # predicates: AttributeMutabilityPredicates = (
    #     getattr( self, predicates_name, ( ) ) )
    if name in names:
        ligation( name, value )
        return
    # TODO: Sweep predicates.
    # TODO: Sweep regexes.
    target = _utilities.qualify_object_name( obj )
    raise error_class_provider( 'AttributeImmutability' )( name, target )


def _delete_attribute_if_mutable( # noqa: PLR0913
    obj: object, /, *,
    ligation: _nomina.DeleterLigation,
    error_class_provider: ErrorClassProvider,
    behaviors_name: str,
    names_name: str,
    regexes_name: str,
    predicates_name: str,
    name: str,
) -> None:
    behaviors = _utilities.getattr0( obj, behaviors_name, frozenset( ) )
    if _immutability_label not in behaviors:
        ligation( name )
        return
    names: MutablesNames = getattr( obj, names_name, frozenset( ) )
    # regexes: AttributeMutabilityRegexes = (
    #     getattr( self, regexes_name, ( ) ) )
    # predicates: AttributeMutabilityPredicates = (
    #     getattr( self, predicates_name, ( ) ) )
    if name in names:
        ligation( name )
        return
    # TODO: Sweep predicates.
    # TODO: Sweep regexes.
    target = _utilities.qualify_object_name( obj )
    raise error_class_provider( 'AttributeImmutability' )( name, target )


def _survey_visible_attributes( # noqa: PLR0913
    obj: object, /, *,
    ligation: _nomina.SurveyorLigation,
    behaviors_name: str,
    names_name: str,
    regexes_name: str,
    predicates_name: str,
) -> __.cabc.Iterable[ str ]:
    names_base = ligation( )
    behaviors = _utilities.getattr0( obj, behaviors_name, frozenset( ) )
    if _concealment_label not in behaviors: return names_base
    names: VisiblesNames = getattr( obj, names_name, frozenset( ) )
    predicates: AttributeVisibilityPredicates = (
        getattr( obj, predicates_name, ( ) ) )
    # regexes: AttributeVisibilityRegexes = (
    #     getattr( obj, regexes_name, ( ) ) )
    names_: list[ str ] = [ ]
    for name in names_base:
        if name in names:
            names_.append( name )
            continue
        for predicate in predicates:
            if predicate( name ):
                names_.append( name )
                continue
        # TODO: Sweep regexes.
    return names_


def _classify_behavior_exclusion_verifiers(
    verifiers: BehaviorExclusionVerifiers
) -> tuple[
    BehaviorExclusionNames,
    BehaviorExclusionRegexes,
    BehaviorExclusionPredicates,
]:
    names: set[ str ] = set( )
    regexes: list[ __.re.Pattern[ str ] ] = [ ]
    predicates: list[ __.cabc.Callable[ ..., bool ] ] = [ ]
    for verifier in verifiers:
        if isinstance( verifier, str ):
            names.add( verifier )
        elif isinstance( verifier, __.re.Pattern ):
            regexes.append( verifier )
        elif callable( verifier ):
            predicates.append( verifier )
    return frozenset( names ), tuple( regexes ), tuple( predicates )


def _produce_decoration_processors(
    mutables: AttributeMutabilityVerifiers,
    visibles: AttributeVisibilityVerifiers,
) -> tuple[
    _nomina.DecorationPreprocessors, _nomina.DecorationPostprocessors
]:
    # TODO: Wrap in factory which accepts attributes namer, error class
    #       provider, and core implementations.
    ''' Produces processors for standard decorators. '''
    attributes_namer = _calculate_attrname
    error_class_provider = _provide_error_class
    preprocessors: list[ _nomina.DecorationPreprocessor ] = [ ]
    postprocessors: list[ _nomina.DecorationPostprocessor ] = [ ]
    preprocessors.append( _annotate_class_for_instances )
    postprocessors.append(
        _produce_initialization_postprocessor(
            attributes_namer = attributes_namer,
            mutables = mutables, visibles = visibles ) )
    if mutables != '*':
        postprocessors.append(
            __.funct.partial(
                _associate_instances_attributes_assigner,
                attributes_namer = attributes_namer,
                error_class_provider = error_class_provider,
                implementation_core = _assign_attribute_if_mutable ) )
        postprocessors.append(
            __.funct.partial(
                _associate_instances_attributes_deleter,
                attributes_namer = attributes_namer,
                error_class_provider = error_class_provider,
                implementation_core = _delete_attribute_if_mutable ) )
    if visibles != '*':
        postprocessors.append(
            __.funct.partial(
                _associate_instances_attributes_surveyor,
                attributes_namer = attributes_namer,
                implementation_core = _survey_visible_attributes ) )
    return tuple( preprocessors ), tuple( postprocessors )


def _produce_initialization_postprocessor(
    attributes_namer: AttributesNamer,
    mutables: AttributeMutabilityVerifiers,
    visibles: AttributeVisibilityVerifiers,
) -> _nomina.DecorationPostprocessor:
    behaviors_name = attributes_namer( 'instance', 'behaviors' )
    behaviors: set[ str ] = set( )

    def postprocess( cls: type ) -> None:
        original_init = getattr( cls, '__init__' )
        nomargs_injection = { }
        posargs_injection = [ ]
        if mutables != '*':
            _record_behavior_exclusions(
                cls, attributes_namer, 'mutables', 'instances', mutables )
            behaviors.add( _immutability_label )
        if visibles != '*':
            _record_behavior_exclusions(
                cls, attributes_namer, 'visibles', 'instances', visibles )
            behaviors.add( _concealment_label )
        if __.dcls.is_dataclass( cls ):
            # Pass instance variables.
            nomargs_injection[ behaviors_name ] = set( )

        @__.funct.wraps( original_init )
        def initialize(
            self: object, *posargs: __.typx.Any, **nomargs: __.typx.Any
        ) -> None:
            original_init(
                self,
                *( *posargs_injection, *posargs ),
                **{ **nomargs_injection, **nomargs } )
            behaviors_ = _utilities.getattr0( self, behaviors_name, set( ) )
            if not behaviors_: setattr( self, behaviors_name, behaviors_ )
            behaviors_.update( behaviors )

        cls.__init__ = initialize

    return postprocess


def _record_behavior_exclusions(
    cls: type,
    attributes_namer: AttributesNamer,
    basename: str,
    level: str,
    verifiers: BehaviorExclusionVerifiers,
) -> None:
    names, regexes, predicates = (
        _classify_behavior_exclusion_verifiers( verifiers ) )
    names_name = attributes_namer( level, f"{basename}_names" )
    regexes_name = attributes_namer( level, f"{basename}_regexes" )
    predicates_name = attributes_namer( level, f"{basename}_predicates" )
    names_: BehaviorExclusionNames = frozenset( {
        *names, *getattr( cls, names_name, frozenset( ) ) } )
    # TODO: Deduplicating, ordered merge for regexes and predicates.
    regexes_: BehaviorExclusionRegexes = (
        *regexes, *getattr( cls, regexes_name, ( ) ) )
    predicates_: BehaviorExclusionPredicates = (
        *predicates, *getattr( cls, predicates_name, ( ) ) )
    setattr( cls, names_name, names_ )
    setattr( cls, regexes_name, regexes_ )
    setattr( cls, predicates_name, predicates_ )
    # TODO? Add regexes match cache.
    # TODO? Add predicates match cache.


def _record_class_construction_arguments(
    namespace: dict[ str, __.typx.Any ],
    arguments: dict[ str, __.typx.Any ],
) -> None:
    arguments_ = { }
    for name in (
        'class_mutables', 'class_visibles',
        'instance_mutables', 'instance_visibles',
    ):
        if name not in arguments: continue
        arguments_[ name ] = arguments.pop( name )
    arguments_name = _calculate_attrname( 'class', 'construction_arguments' )
    namespace[ arguments_name ] = arguments_


construct_class = (
    _factories.produce_constructor(
        preprocessors = ( class_construction_preprocessor, ),
        postprocessors = ( class_construction_postprocessor, ) ) )
initialize_class = (
    _factories.produce_initializer(
        completers = ( class_initialization_completer, ) ) )
assign_class_attributes = (
    produce_class_attributes_assigner(
        attributes_namer = _calculate_attrname,
        error_class_provider = _provide_error_class,
        implementation_core = _assign_attribute_if_mutable ) )
delete_class_attributes = (
    produce_class_attributes_deleter(
        attributes_namer = _calculate_attrname,
        error_class_provider = _provide_error_class,
        implementation_core = _delete_attribute_if_mutable ) )
survey_class_attributes = (
    produce_class_attributes_surveyor(
        attributes_namer = _calculate_attrname,
        implementation_core = _survey_visible_attributes ) )


class_construction_decorator = (
    _factories.produce_class_construction_decorator(
        constructor = construct_class ) )
class_initialization_decorator = (
    _factories.produce_class_initialization_decorator(
        initializer = initialize_class ) )
class_immutability_decorator = (
    _factories.produce_class_mutation_control_decorator(
        assigner = assign_class_attributes,
        deleter = delete_class_attributes ) )
class_concealment_decorator = (
    _factories.produce_class_visibility_control_decorator(
        surveyor = survey_class_attributes ) )


decorators_standard = (
    class_construction_decorator,
    class_initialization_decorator,
    class_concealment_decorator,
    class_immutability_decorator,
)


@_factories.decoration_by( decorators_standard )
class Class( type ): pass


@_factories.decoration_by( decorators_standard )
class ProtocolClass( type( __.typx.Protocol ) ): pass


class Object( metaclass = Class ): pass


class DataclassObject(
    _bases.DataclassObjectBase, metaclass = Class
): pass


class DataclassObjectMutable(
    _bases.DataclassObjectMutableBase, metaclass = Class
): pass


class Protocol( __.typx.Protocol, metaclass = ProtocolClass ): pass


class DataclassProtocol(
    _bases.DataclassProtocolBase, __.typx.Protocol,
    metaclass = ProtocolClass,
): pass


class DataclassProtocolMutable(
    _bases.DataclassProtocolMutableBase, __.typx.Protocol,
    metaclass = ProtocolClass,
): pass
