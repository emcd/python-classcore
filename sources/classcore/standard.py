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


AttributeMutabilityPredicate: __.typx.TypeAlias = (
    __.cabc.Callable[ [ str, __.typx.Any ], bool ] )
AttributeMutabilityPredicates: __.typx.TypeAlias = (
    __.cabc.Sequence[ AttributeMutabilityPredicate ] )
AttributeMutabilityRegexes: __.typx.TypeAlias = (
    __.cabc.Sequence[ __.re.Pattern[ str ] ] )
AttributeMutabilityVerifier: __.typx.TypeAlias = (
    str | __.re.Pattern[ str ] | AttributeMutabilityPredicate )
AttributeMutabilityVerifiers: __.typx.TypeAlias = (
    __.cabc.Sequence[ AttributeMutabilityVerifier ] | __.typx.Literal[ '*' ] )
AttributeVisibilityPredicate: __.typx.TypeAlias = (
    __.cabc.Callable[ [ str ], bool ] )
AttributeVisibilityPredicates: __.typx.TypeAlias = (
    __.cabc.Sequence[ AttributeVisibilityPredicate ] )
AttributeVisibilityRegexes: __.typx.TypeAlias = (
    __.cabc.Sequence[ __.re.Pattern[ str ] ] )
AttributeVisibilityVerifier: __.typx.TypeAlias = (
    str | __.re.Pattern[ str ] | AttributeVisibilityPredicate )
AttributeVisibilityVerifiers: __.typx.TypeAlias = (
    __.cabc.Sequence[ AttributeVisibilityVerifier ] | __.typx.Literal[ '*' ] )
ErrorClassProvider: __.typx.TypeAlias = (
    __.cabc.Callable[ [ str ], type[ Exception ] ] )
MutablesNames: __.typx.TypeAlias = __.cabc.Set[ str ]
VisiblesNames: __.typx.TypeAlias = __.cabc.Set[ str ]


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


def associate_delattr(
    cls: type[ _U ], error_class_provider: ErrorClassProvider
) -> None:
    deleter_name = _calculate_attrname( 'instances', 'deleter' )
    extant = getattr( cls, deleter_name, None )
    original = getattr( cls, '__delattr__' )
    if extant is original: return
    behaviors_name = _calculate_attrname( 'instance', 'behaviors' )
    names_name = _calculate_attrname( 'instances', 'mutables_names' )
    regexes_name = _calculate_attrname( 'instances', 'mutables_regexes' )
    predicates_name = _calculate_attrname( 'instances', 'mutables_predicates' )

    @__.funct.wraps( original )
    def delete( self: object, name: str ) -> None:
        _delete_attribute_if_mutable(
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


def associate_setattr(
    cls: type[ _U ], error_class_provider: ErrorClassProvider
) -> None:
    assigner_name = _calculate_attrname( 'instances', 'assigner' )
    extant = getattr( cls, assigner_name, None )
    original = getattr( cls, '__setattr__' )
    if extant is original: return
    behaviors_name = _calculate_attrname( 'instance', 'behaviors' )
    names_name = _calculate_attrname( 'instances', 'mutables_names' )
    regexes_name = _calculate_attrname( 'instances', 'mutables_regexes' )
    predicates_name = _calculate_attrname( 'instances', 'mutables_predicates' )

    @__.funct.wraps( original )
    def assign( self: object, name: str, value: __.typx.Any ) -> None:
        _assign_attribute_if_mutable(
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


def associate_dir( cls: type[ _U ] ) -> None:
    surveyor_name = _calculate_attrname( 'instances', 'surveyor' )
    extant = getattr( cls, surveyor_name, None )
    original = getattr( cls, '__dir__' )
    if extant is original: return
    behaviors_name = _calculate_attrname( 'instance', 'behaviors' )
    names_name = _calculate_attrname( 'instances', 'visibles_names' )
    regexes_name = _calculate_attrname( 'instances', 'visibles_regexes' )
    predicates_name = _calculate_attrname( 'instances', 'visibles_predicates' )

    @__.funct.wraps( original )
    def survey( self: object ) -> __.cabc.Iterable[ str ]:
        return _survey_visible_attributes(
            self,
            ligation = __.funct.partial( original, self ),
            behaviors_name = behaviors_name,
            names_name = names_name,
            regexes_name = regexes_name,
            predicates_name = predicates_name )

    setattr( cls, surveyor_name, survey )
    cls.__dir__ = survey


@__.typx.dataclass_transform( frozen_default = True, kw_only_default = True )
def dataclass_standard(
    mutables: AttributeMutabilityVerifiers = ( ),
    visibles: AttributeVisibilityVerifiers = ( is_public_identifier, ),
    error_provider: ErrorClassProvider = _provide_error_class,
    # TODO? attribute value transformer
) -> _nomina.Decorator:
    # https://github.com/microsoft/pyright/discussions/10344
    ''' Dataclass decorator factory.

        Ensures instances have immutable attributes.
    '''
    behaviors_name = _calculate_attrname( 'instance', 'behaviors' )
    behaviors: set[ str ] = set( )
    if mutables != '*': behaviors.add( _immutability_label )
    if visibles != '*': behaviors.add( _concealment_label )
    postproc_i = produce_initialization_postprocessor(
        behaviors = behaviors,
        nomargs_injection = { behaviors_name: set( ) } )
    postproc_m = produce_mutables_postprocessor( error_provider, mutables )
    postproc_v = produce_visibles_postprocessor( visibles )
    return _factories.produce_decorator(
        decorators = ( _dataclass_core, ),
        preprocessors = ( _annotate_class, ),
        postprocessors = ( postproc_i, postproc_m, postproc_v ) )


def standard(
    mutables: AttributeMutabilityVerifiers = ( ),
    visibles: AttributeVisibilityVerifiers = ( is_public_identifier, ),
    error_provider: ErrorClassProvider = _provide_error_class,
    # TODO? attribute value transformer
) -> _nomina.Decorator:
    ''' Class decorator factory.

        Ensures instances have immutable attributes.
    '''
    behaviors: set[ str ] = set( )
    if mutables != '*': behaviors.add( _immutability_label )
    if visibles != '*': behaviors.add( _concealment_label )
    postproc_i = produce_initialization_postprocessor( behaviors = behaviors )
    postproc_m = produce_mutables_postprocessor( error_provider, mutables )
    postproc_v = produce_visibles_postprocessor( visibles )
    return _factories.produce_decorator(
        preprocessors = ( _annotate_class, ),
        postprocessors = ( postproc_i, postproc_m, postproc_v ) )


def class_construction_preprocessor( # noqa: PLR0913
    clscls: type,
    name: str,
    bases: list[ type ],
    namespace: dict[ str, __.typx.Any ],
    arguments: dict[ str, __.typx.Any ],
    decorators: _nomina.DecoratorsMutable,
) -> None:
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
    arguments_name = _calculate_attrname( 'class', 'construction_arguments' )
    arguments: __.typx.Optional[ dict[ str, __.typx.Any ] ] = (
        getattr( cls, arguments_name, None ) )
    if arguments is not None: delattr( cls, arguments_name )
    arguments = arguments or { }
    class_mutables = arguments.get( 'class_mutables', _mutables_default )
    class_visibles = arguments.get( 'class_visibles', _visibles_default )
    behaviors: set[ str ] = set( )
    if class_mutables != '*':
        _record_class_mutables( cls, class_mutables )
        behaviors.add( _immutability_label )
    if class_visibles != '*':
        _record_class_visibles( cls, class_visibles )
        behaviors.add( _concealment_label )
    # Set behaviors attribute last since it enables enforcement.
    setattr( cls, _calculate_attrname( 'class', 'behaviors' ), behaviors )


def produce_class_attributes_assigner(
    error_class_provider: ErrorClassProvider
) -> _factories.Assigner:
    behaviors_name = _calculate_attrname( 'class', 'behaviors' )
    names_name = _calculate_attrname( 'class', 'mutables_names' )
    regexes_name = _calculate_attrname( 'class', 'mutables_regexes' )
    predicates_name = _calculate_attrname( 'class', 'mutables_predicates' )

    def assign(
        cls: type,
        superf: _nomina.AssignerLigation,
        name: str,
        value: __.typx.Any,
    ) -> None:
        _assign_attribute_if_mutable(
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
    error_class_provider: ErrorClassProvider
) -> _factories.Deleter:
    behaviors_name = _calculate_attrname( 'class', 'behaviors' )
    names_name = _calculate_attrname( 'class', 'mutables_names' )
    regexes_name = _calculate_attrname( 'class', 'mutables_regexes' )
    predicates_name = _calculate_attrname( 'class', 'mutables_predicates' )

    def delete(
        cls: type, superf: _nomina.DeleterLigation, name: str
    ) -> None:
        _delete_attribute_if_mutable(
            cls,
            ligation = superf,
            error_class_provider = error_class_provider,
            behaviors_name = behaviors_name,
            names_name = names_name,
            regexes_name = regexes_name,
            predicates_name = predicates_name,
            name = name )

    return delete


def produce_class_attributes_surveyor( ) -> _factories.Surveyor:
    behaviors_name = _calculate_attrname( 'class', 'behaviors' )
    names_name = _calculate_attrname( 'class', 'visibles_names' )
    regexes_name = _calculate_attrname( 'class', 'visibles_regexes' )
    predicates_name = _calculate_attrname( 'class', 'visibles_predicates' )

    def survey(
        cls: type, superf: _nomina.SurveyorLigation
    ) -> __.cabc.Iterable[ str ]:
        return _survey_visible_attributes(
            cls,
            ligation = superf,
            behaviors_name = behaviors_name,
            names_name = names_name,
            regexes_name = regexes_name,
            predicates_name = predicates_name )

    return survey


construct_class = (
    _factories.produce_constructor(
        preprocessors = ( class_construction_preprocessor, ),
        postprocessors = ( class_construction_postprocessor, ) ) )
initialize_class = (
    _factories.produce_initializer(
        completers = ( class_initialization_completer, ) ) )
assign_class_attributes = (
    produce_class_attributes_assigner(
        error_class_provider = _provide_error_class ) )
delete_class_attributes = (
    produce_class_attributes_deleter(
        error_class_provider = _provide_error_class ) )
survey_class_attributes = produce_class_attributes_surveyor( )


def produce_initialization_postprocessor(
    behaviors: __.cabc.Set[ str ] = frozenset( ),
    posargs_injection: __.PositionalArguments = ( ),
    nomargs_injection: __.NominativeArguments = __.dictproxy_empty,
) -> _nomina.DecorationPostprocessor:
    behaviors_name = _calculate_attrname( 'instance', 'behaviors' )
    def postprocess( cls: type ) -> None:
        original_init = getattr( cls, '__init__' )

        @__.funct.wraps( original_init )
        def initialize(
            self: object, *posargs: __.typx.Any, **nomargs: __.typx.Any
        ) -> None:
            original_init(
                self,
                *( *posargs_injection, *posargs ),
                **{ **nomargs_injection, **nomargs } )
            behaviors_ = _utilities.getattr0( self, behaviors_name, set( ) )
            if not behaviors_:
                setattr( self, behaviors_name, behaviors_ )
            behaviors_.update( behaviors )

        cls.__init__ = initialize

    return postprocess


def produce_mutables_postprocessor(
    error_provider: ErrorClassProvider,
    mutables: AttributeMutabilityVerifiers = ( )
) -> _nomina.DecorationPostprocessor:
    if mutables == '*':
        def postprocess_null( cls: type ) -> None: pass
        return postprocess_null
    mutables_names, mutables_regexes, mutables_predicates = (
        _classify_mutability_verifiers( mutables ) )
    # TODO? Add regexes match cache.
    # TODO? Add predicates match cache.
    names_name = _calculate_attrname( 'instances', 'mutables_names' )
    regexes_name = _calculate_attrname( 'instances', 'mutables_regexes' )
    predicates_name = _calculate_attrname( 'instances', 'mutables_predicates' )

    def postprocess( cls: type ) -> None:
        mutables_names_: MutablesNames = frozenset( {
            *mutables_names, *getattr( cls, names_name, frozenset( ) ) } )
        setattr( cls, names_name, mutables_names_ )
        # TODO: Deduplicating, ordered merge for regexes and predicates.
        mutables_regexes_: AttributeMutabilityRegexes = (
            *mutables_regexes, *getattr( cls, regexes_name, ( ) ) )
        setattr( cls, regexes_name, mutables_regexes_ )
        mutables_predicates_: AttributeMutabilityPredicates = (
            *mutables_predicates, *getattr( cls, predicates_name, ( ) ) )
        setattr( cls, predicates_name, mutables_predicates_ )
        associate_delattr( cls, error_provider )
        associate_setattr( cls, error_provider )

    return postprocess


def produce_visibles_postprocessor(
    visibles: AttributeVisibilityVerifiers = ( )
) -> _nomina.DecorationPostprocessor:
    if visibles == '*':
        def postprocess_null( cls: type ) -> None: pass
        return postprocess_null
    visibles_names, visibles_regexes, visibles_predicates = (
        _classify_visibility_verifiers( visibles ) )
    # TODO? Add regexes match cache.
    # TODO? Add predicates match cache.
    names_name = _calculate_attrname( 'instances', 'visibles_names' )
    regexes_name = _calculate_attrname( 'instances', 'visibles_regexes' )
    predicates_name = _calculate_attrname( 'instances', 'visibles_predicates' )

    def postprocess( cls: type ) -> None:
        visibles_names_: VisiblesNames = frozenset( {
            *visibles_names, *getattr( cls, names_name, frozenset( ) ) } )
        setattr( cls, names_name, visibles_names_ )
        # TODO: Deduplicating, ordered merge for regexes and predicates.
        visibles_regexes_: AttributeVisibilityRegexes = (
            *visibles_regexes, *getattr( cls, regexes_name, ( ) ) )
        setattr( cls, regexes_name, visibles_regexes_ )
        visibles_predicates_: AttributeVisibilityPredicates = (
            *visibles_predicates, *getattr( cls, predicates_name, ( ) ) )
        setattr( cls, predicates_name, visibles_predicates_ )
        associate_dir( cls )

    return postprocess



class_construction_decorator = (
    _factories.produce_class_construction_decorator(
        constructor = construct_class ) )
class_initialization_decorator = (
    _factories.produce_class_initialization_decorator(
        initializer = initialize_class ) )
class_concealment_decorator = (
    _factories.produce_class_visibility_control_decorator(
        surveyor = survey_class_attributes ) )
class_immutability_decorator = (
    _factories.produce_class_mutation_control_decorator(
        assigner = assign_class_attributes,
        deleter = delete_class_attributes ) )


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


def _annotate_class(
    cls: type, decorators: _nomina.DecoratorsMutable
) -> None:
    ''' Annotates class in support of machinery. '''
    annotations = __.inspect.get_annotations( cls )
    # TODO: accretive set instead of set
    annotations[ _calculate_attrname( 'instance', 'behaviors' ) ] = set[ str ]


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
    ligation: SurveyorLigation,
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


def _classify_mutability_verifiers(
    mutables: AttributeMutabilityVerifiers
) -> tuple[
    MutablesNames,
    AttributeMutabilityRegexes,
    AttributeMutabilityPredicates,
]:
    names: set[ str ] = set( )
    regexes: list[ __.re.Pattern[ str ] ] = [ ]
    predicates: list[ AttributeMutabilityPredicate ] = [ ]
    for mutable in mutables:
        if isinstance( mutable, str ):
            names.add( mutable )
        elif isinstance( mutable, __.re.Pattern ):
            regexes.append( mutable )
        elif callable( mutable ):
            predicates.append( mutable )
    return frozenset( names ), tuple( regexes ), tuple( predicates )


def _classify_visibility_verifiers(
    visibles: AttributeVisibilityVerifiers
) -> tuple[
    VisiblesNames,
    AttributeVisibilityRegexes,
    AttributeVisibilityPredicates,
]:
    names: set[ str ] = set( )
    regexes: list[ __.re.Pattern[ str ] ] = [ ]
    predicates: list[ AttributeVisibilityPredicate ] = [ ]
    for visible in visibles:
        if isinstance( visible, str ):
            names.add( visible )
        elif isinstance( visible, __.re.Pattern ):
            regexes.append( visible )
        elif callable( visible ):
            predicates.append( visible )
    return frozenset( names ), tuple( regexes ), tuple( predicates )


def _record_class_mutables(
    cls: type, mutables: AttributeMutabilityVerifiers
) -> None:
    names, regexes, predicates = _classify_mutability_verifiers( mutables )
    names_name = _calculate_attrname( 'class', 'mutables_names' )
    regexes_name = _calculate_attrname( 'class', 'mutables_regexes' )
    predicates_name = _calculate_attrname( 'class', 'mutables_predicates' )
    setattr( cls, names_name, names )
    setattr( cls, regexes_name, regexes )
    setattr( cls, predicates_name, predicates )


def _record_class_visibles(
    cls: type, mutables: AttributeVisibilityVerifiers
) -> None:
    names, regexes, predicates = _classify_visibility_verifiers( mutables )
    names_name = _calculate_attrname( 'class', 'visibles_names' )
    regexes_name = _calculate_attrname( 'class', 'visibles_regexes' )
    predicates_name = _calculate_attrname( 'class', 'visibles_predicates' )
    setattr( cls, names_name, names )
    setattr( cls, regexes_name, regexes )
    setattr( cls, predicates_name, predicates )


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
