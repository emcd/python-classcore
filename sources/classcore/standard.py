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
#       Maybe behaviors enum for mutability and visibility.
# TODO? Add attribute value transformer as standard decorator argument.
# TODO: Convert instances association functions from postproceesors to
#       decorators and append to end of decorators list.
#       Then, generalize and collapse metaclass and class decorators
#       for operations.
#       Drop notion of postprocessors for creation of instances decorators.


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


class ClassPreparer( __.typx.Protocol ):
    ''' Prepares class for decorator application. '''

    @staticmethod
    def __call__(
        class_: type,
        decorators: _nomina.DecoratorsMutable, /, *,
        attributes_namer: AttributesNamer,
    ) -> None: raise NotImplementedError


def is_public_identifier( name: str ) -> bool:
    ''' Is Python identifier public? '''
    return not name.startswith( '_' )


_dataclass_core = __.dcls.dataclass( kw_only = True, slots = True )
_concealment_label = 'concealment'
_immutability_label = 'immutability'
_mutables_default = ( )
_visibles_default = ( is_public_identifier, )


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
    regexes: AttributeMutabilityRegexes = (
        getattr( obj, regexes_name, ( ) ) )
    # predicates: AttributeMutabilityPredicates = (
    #     getattr( obj, predicates_name, ( ) ) )
    if name in names:
        ligation( name, value )
        return
    # TODO: Sweep predicates.
    for regex in regexes:
        if regex.fullmatch( name ):
            # TODO? Cache regex hit.
            ligation( name, value )
            return
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
    regexes: AttributeMutabilityRegexes = (
        getattr( obj, regexes_name, ( ) ) )
    # predicates: AttributeMutabilityPredicates = (
    #     getattr( obj, predicates_name, ( ) ) )
    if name in names:
        ligation( name )
        return
    # TODO: Sweep predicates.
    for regex in regexes:
        if regex.fullmatch( name ):
            # TODO? Cache regex hit.
            ligation( name )
            return
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
    regexes: AttributeVisibilityRegexes = (
        getattr( obj, regexes_name, ( ) ) )
    names_: list[ str ] = [ ]
    for name in names_base:
        if name in names:
            names_.append( name )
            continue
        for predicate in predicates:
            if predicate( name ):
                # TODO? Cache predicate hit.
                names_.append( name )
                continue
        for regex in regexes:
            if regex.fullmatch( name ):
                # TODO? Cache regex hit.
                names_.append( name )
                continue
    return names_


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


def prepare_dataclass_for_instances(
    cls: type,
    decorators: _nomina.DecoratorsMutable, /, *,
    attributes_namer: AttributesNamer,
) -> None:
    ''' Annotates dataclass in support of instantiation machinery. '''
    annotations = __.inspect.get_annotations( cls )
    behaviors_name = attributes_namer( 'instance', 'behaviors' )
    annotations[ behaviors_name ] = set[ str ]
    setattr( cls, '__annotations__', annotations ) # in case of absence
    setattr( cls, behaviors_name, __.dcls.field( init = False ) )


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


def _deduplicate_merge_sequences(
    addends: __.cabc.Sequence[ __.typx.Any ],
    augends: __.cabc.Sequence[ __.typx.Any ],
) -> __.cabc.Sequence[ __.typx.Any ]:
    result = list( augends )
    augends_ = set( augends )
    for addend in addends:
        if addend in augends_: continue
        result.append( addend )
    return tuple( result )


def _produce_class_construction_preprocessor(
    attributes_namer: AttributesNamer
) -> _factories.ConstructionPreprocessor:

    def preprocess( # noqa: PLR0913
        clscls: type,
        name: str,
        bases: list[ type ],
        namespace: dict[ str, __.typx.Any ],
        arguments: dict[ str, __.typx.Any ],
        decorators: _nomina.DecoratorsMutable,
    ) -> None:
        _record_class_construction_arguments(
            attributes_namer, namespace, arguments )

    return preprocess


def _produce_class_construction_postprocessor(
    attributes_namer: AttributesNamer
) -> _factories.ConstructionPostprocessor:
    arguments_name = attributes_namer( 'class', 'construction_arguments' )

    def postprocess(
        cls: type, decorators: _nomina.DecoratorsMutable
    ) -> None:
        arguments = getattr( cls, arguments_name, { } )
        dcls_spec = getattr( cls, '__dataclass_transform__', None )
        instances_mutables = arguments.get(
            'instances_mutables', _mutables_default )
        instances_visibles = arguments.get(
            'instances_visibles', _visibles_default )
        if dcls_spec and dcls_spec.get( 'kw_only_default', False ):
            decorator_factory = dataclass_standard
            if not dcls_spec.get( 'frozen_default', True ):
                instances_mutables = instances_mutables or '*'
        else: decorator_factory = standard
        decorator = decorator_factory(
            mutables = instances_mutables, visibles = instances_visibles )
        decorators.append( decorator )

    return postprocess


def _produce_class_initialization_completer(
    attributes_namer: AttributesNamer
) -> _factories.InitializationCompleter:
    arguments_name = attributes_namer( 'class', 'construction_arguments' )

    def complete( cls: type ) -> None:
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

    return complete


def _produce_class_attributes_assigner(
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


def _produce_class_attributes_deleter(
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


def _produce_class_attributes_surveyor(
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


def _produce_class_operations(
    attributes_namer: AttributesNamer,
    error_class_provider: ErrorClassProvider,
    assigner_core: AssignerCore,
    deleter_core: DeleterCore,
    surveyor_core: SurveyorCore,
) -> tuple[
    _factories.Constructor,
    _factories.Initializer,
    _factories.Assigner,
    _factories.Deleter,
    _factories.Surveyor,
]:
    constructor = (
        _factories.produce_constructor(
            preprocessors = (
                _produce_class_construction_preprocessor(
                    attributes_namer = attributes_namer ), ),
            postprocessors = (
                _produce_class_construction_postprocessor(
                    attributes_namer = attributes_namer ), ) ) )
    initializer = (
        _factories.produce_initializer(
            completers = (
                _produce_class_initialization_completer(
                    attributes_namer = attributes_namer ), ) ) )
    assigner = (
        _produce_class_attributes_assigner(
            attributes_namer = attributes_namer,
            error_class_provider = error_class_provider,
            implementation_core = assigner_core ) )
    deleter = (
        _produce_class_attributes_deleter(
            attributes_namer = attributes_namer,
            error_class_provider = error_class_provider,
            implementation_core = deleter_core ) )
    surveyor = (
        _produce_class_attributes_surveyor(
            attributes_namer = attributes_namer,
            implementation_core = surveyor_core ) )
    return constructor, initializer, assigner, deleter, surveyor


def _produce_instances_initialization_postprocessor(
    attributes_namer: AttributesNamer,
    mutables: AttributeMutabilityVerifiers,
    visibles: AttributeVisibilityVerifiers,
) -> _nomina.DecorationPostprocessor:
    # TODO: Replace with associater.
    behaviors_name = attributes_namer( 'instance', 'behaviors' )
    behaviors: set[ str ] = set( )

    def postprocess( cls: type ) -> None:
        original_init = getattr( cls, '__init__' )
        if mutables != '*':
            _record_behavior_exclusions(
                cls, attributes_namer, 'mutables', 'instances', mutables )
            behaviors.add( _immutability_label )
        if visibles != '*':
            _record_behavior_exclusions(
                cls, attributes_namer, 'visibles', 'instances', visibles )
            behaviors.add( _concealment_label )

        @__.funct.wraps( original_init )
        def initialize(
            self: object, *posargs: __.typx.Any, **nomargs: __.typx.Any
        ) -> None:
            original_init( self, *posargs, **nomargs )
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
    regexes_: BehaviorExclusionRegexes = (
        _deduplicate_merge_sequences(
            regexes, getattr( cls, regexes_name, ( ) ) ) )
    predicates_: BehaviorExclusionPredicates = (
        _deduplicate_merge_sequences(
            predicates, getattr( cls, predicates_name, ( ) ) ) )
    setattr( cls, names_name, names_ )
    setattr( cls, regexes_name, regexes_ )
    setattr( cls, predicates_name, predicates_ )
    # TODO? Add regexes match cache.
    # TODO? Add predicates match cache.


def _record_class_construction_arguments(
    attributes_namer: AttributesNamer,
    namespace: dict[ str, __.typx.Any ],
    arguments: dict[ str, __.typx.Any ],
) -> None:
    arguments_ = { }
    for name in (
        'class_mutables', 'class_visibles',
        'instances_mutables', 'instances_visibles',
    ):
        if name not in arguments: continue
        arguments_[ name ] = arguments.pop( name )
    arguments_name = attributes_namer( 'class', 'construction_arguments' )
    namespace[ arguments_name ] = arguments_


def produce_decoration_processors_factory( # noqa: PLR0913
    attributes_namer: AttributesNamer = _calculate_attrname,
    error_class_provider: ErrorClassProvider = _provide_error_class,
    class_preparer: __.typx.Optional[ ClassPreparer ] = None,
    assigner_core: AssignerCore = _assign_attribute_if_mutable,
    deleter_core: DeleterCore = _delete_attribute_if_mutable,
    surveyor_core: SurveyorCore = _survey_visible_attributes,
) -> __.cabc.Callable[
    [ AttributeMutabilityVerifiers, AttributeVisibilityVerifiers ],
    tuple[ _nomina.DecorationPreprocessors, _nomina.DecorationPostprocessors ]
]:
    def produce(
        mutables: AttributeMutabilityVerifiers,
        visibles: AttributeVisibilityVerifiers,
    ) -> tuple[
        _nomina.DecorationPreprocessors, _nomina.DecorationPostprocessors
    ]:
        ''' Produces processors for standard decorators. '''
        preprocessors: list[ _nomina.DecorationPreprocessor ] = [ ]
        postprocessors: list[ _nomina.DecorationPostprocessor ] = [ ]
        if class_preparer is not None:
            preprocessors.append(
                __.funct.partial(
                    class_preparer,
                    attributes_namer = attributes_namer  ) )
        postprocessors.append(
            _produce_instances_initialization_postprocessor(
                attributes_namer = attributes_namer,
                mutables = mutables, visibles = visibles ) )
        if mutables != '*':
            postprocessors.append(
                __.funct.partial(
                    _associate_instances_attributes_assigner,
                    attributes_namer = attributes_namer,
                    error_class_provider = error_class_provider,
                    implementation_core = assigner_core ) )
            postprocessors.append(
                __.funct.partial(
                    _associate_instances_attributes_deleter,
                    attributes_namer = attributes_namer,
                    error_class_provider = error_class_provider,
                    implementation_core = deleter_core ) )
        if visibles != '*':
            postprocessors.append(
                __.funct.partial(
                    _associate_instances_attributes_surveyor,
                    attributes_namer = attributes_namer,
                    implementation_core = surveyor_core ) )
        return tuple( preprocessors ), tuple( postprocessors )

    return produce


@__.typx.dataclass_transform( frozen_default = True, kw_only_default = True )
def dataclass_standard(
    mutables: AttributeMutabilityVerifiers = _mutables_default,
    visibles: AttributeVisibilityVerifiers = _visibles_default,
) -> _nomina.Decorator:
    # https://github.com/microsoft/pyright/discussions/10344
    ''' Dataclass decorator factory. '''
    processors_factory = produce_decoration_processors_factory(
        class_preparer = prepare_dataclass_for_instances )
    preprocessors, postprocessors = processors_factory( mutables, visibles )
    return _factories.produce_decorator(
        decorators = ( _dataclass_core, ),
        preprocessors = preprocessors,
        postprocessors = postprocessors )


def standard(
    mutables: AttributeMutabilityVerifiers = _mutables_default,
    visibles: AttributeVisibilityVerifiers = _visibles_default,
) -> _nomina.Decorator:
    ''' Class decorator factory. '''
    processors_factory = produce_decoration_processors_factory( )
    preprocessors, postprocessors = processors_factory( mutables, visibles )
    return _factories.produce_decorator(
        preprocessors = preprocessors,
        postprocessors = postprocessors )


def produce_class_factory_decorators(
    attributes_namer: AttributesNamer = _calculate_attrname,
    error_class_provider: ErrorClassProvider = _provide_error_class,
    assigner_core: AssignerCore = _assign_attribute_if_mutable,
    deleter_core: DeleterCore = _delete_attribute_if_mutable,
    surveyor_core: SurveyorCore = _survey_visible_attributes,
) -> _nomina.Decorators:
    constructor, initializer, assigner, deleter, surveyor = (
        _produce_class_operations(
            attributes_namer = attributes_namer,
            error_class_provider = error_class_provider,
            assigner_core = assigner_core,
            deleter_core = deleter_core,
            surveyor_core = surveyor_core ) )
    class_construction_decorator = (
        _factories.produce_class_construction_decorator(
            constructor = constructor ) )
    class_initialization_decorator = (
        _factories.produce_class_initialization_decorator(
            initializer = initializer ) )
    class_immutability_decorator = (
        _factories.produce_class_mutation_control_decorator(
            assigner = assigner, deleter = deleter ) )
    class_concealment_decorator = (
        _factories.produce_class_visibility_control_decorator(
            surveyor = surveyor ) )
    return (
        class_construction_decorator,
        class_initialization_decorator,
        class_concealment_decorator,
        class_immutability_decorator,
    )


class_factory_decorators = produce_class_factory_decorators( )


@_factories.decoration_by( class_factory_decorators )
class Class( type ): pass


@_factories.decoration_by( class_factory_decorators )
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
