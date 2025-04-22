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


_class_construction_arguments_name = '_class_construction_arguments_'

_cfc_behaviors_name = '_class_behaviors_'
_cfc_assigner_name = '_class_attributes_assigner_'
_cfc_deleter_name = '_class_attributes_deleter_'
_cfc_surveyor_name = '_class_attributes_surveyor_'
_class_behaviors_name = '_behaviors_'
_class_assigner_name = '_attributes_assigner_'
_class_deleter_name = '_attributes_deleter_'
_class_surveyor_name = '_attributes_surveyor_'
_cfc_mutables_names_name = '_class_mutable_attributes_names_'
_cfc_mutables_regexes_name = '_class_mutable_attributes_regexes_'
_cfc_mutables_predicates_name = '_class_mutable_attributes_predicates_'
_cfc_visibles_names_name = '_class_visible_attributes_names_'
_cfc_visibles_regexes_name = '_class_visible_attributes_regexes_'
_cfc_visibles_predicates_name = '_class_visible_attributes_predicates_'
_class_mutables_names_name = '_mutable_attributes_names_'
_class_mutables_regexes_name = '_mutable_attributes_regexes_'
_class_mutables_predicates_name = '_mutable_attributes_predicates_'
_class_visibles_names_name = '_visible_attributes_names_'
_class_visibles_regexes_name = '_visible_attributes_regexes_'
_class_visibles_predicates_name = '_visible_attributes_predicates_'
_dataclass_core = __.dcls.dataclass( kw_only = True, slots = True )
_concealment_label = 'concealment'
_immutability_label = 'immutability'
_instance_omnimutability_nomargs = (
    __.types.MappingProxyType( dict( instance_mutables = '*' ) ) )
_instance_omnivisibility_nomargs = (
    __.types.MappingProxyType( dict( instance_visibles = '*' ) ) )


def _calculate_attribute_name( level: str, core: str ) -> str:
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


def is_public_identifier( name: str ) -> bool:
    ''' Is Python identifier public? '''
    return not name.startswith( '_' )


_mutables_default = ( )
_visibles_default = ( is_public_identifier, )


def associate_delattr(
    cls: type[ _U ], error_provider: ErrorClassProvider
) -> None:
    extant = getattr( cls, _class_deleter_name, None )
    original = getattr( cls, '__delattr__' )
    if extant is original: return

    @__.funct.wraps( original )
    def deleter( self: object, name: str ) -> None:
        behaviors = (
            _utilities.getattr0( self, _class_behaviors_name, frozenset( ) ) )
        if _immutability_label not in behaviors:
            original( self, name )
            return
        mutables_names: MutablesNames = (
            getattr( self, _class_mutables_names_name, frozenset( ) ) )
        # mutables_predicates: AttributeMutabilityPredicates = (
        #     getattr( self, _class_mutables_predicates_name, ( ) ) )
        # mutables_regexes: AttributeMutabilityRegexes = (
        #     getattr( self, _class_mutables_regexes_name, ( ) ) )
        if name in mutables_names:
            original( self, name )
            return
        # TODO: Sweep predicates.
        # TODO: Sweep regexes.
        target = _utilities.qualify_object_name( self )
        raise error_provider( 'AttributeImmutability' )( name, target )

    setattr( cls, _class_deleter_name, deleter )
    cls.__delattr__ = deleter


def associate_setattr(
    cls: type[ _U ], error_provider: ErrorClassProvider
) -> None:
    extant = getattr( cls, _class_assigner_name, None )
    original = getattr( cls, '__setattr__' )
    if extant is original: return

    @__.funct.wraps( original )
    def assigner( self: object, name: str, value: __.typx.Any ) -> None:
        behaviors = (
            _utilities.getattr0( self, _class_behaviors_name, frozenset( ) ) )
        if _immutability_label not in behaviors:
            original( self, name, value )
            return
        mutables_names: MutablesNames = (
            getattr( self, _class_mutables_names_name, frozenset( ) ) )
        # mutables_predicates: AttributeMutabilityPredicates = (
        #     getattr( self, _class_mutables_predicates_name, ( ) ) )
        # mutables_regexes: AttributeMutabilityRegexes = (
        #     getattr( self, _class_mutables_regexes_name, ( ) ) )
        if name in mutables_names:
            original( self, name, value )
            return
        # TODO: Sweep predicates.
        # TODO: Sweep regexes.
        target = _utilities.qualify_object_name( self )
        raise error_provider( 'AttributeImmutability' )( name, target )

    setattr( cls, _class_assigner_name, assigner )
    cls.__setattr__ = assigner


def associate_dir( cls: type[ _U ] ) -> None:
    extant = getattr( cls, _class_surveyor_name, None )
    original = getattr( cls, '__dir__' )
    if extant is original: return

    @__.funct.wraps( original )
    def surveyor( self: object ) -> __.cabc.Iterable[ str ]:
        names = original( self )
        behaviors = (
            _utilities.getattr0( self, _class_behaviors_name, frozenset( ) ) )
        if _concealment_label not in behaviors: return names
        visibles_names: VisiblesNames = (
            getattr( self, _class_visibles_names_name, frozenset( ) ) )
        visibles_predicates: AttributeVisibilityPredicates = (
            getattr( self, _class_visibles_predicates_name, ( ) ) )
        # visibles_regexes: AttributeVisibilityRegexes = (
        #     getattr( self, _class_visibles_regexes_name, ( ) ) )
        names_: list[ str ] = [ ]
        for name in names:
            if visibles_names and name in visibles_names:
                names_.append( name )
                continue
            for predicate in visibles_predicates:
                if predicate( name ):
                    names_.append( name )
                    continue
            # TODO: Sweep regexes.
        return names_

    setattr( cls, _class_surveyor_name, surveyor )
    cls.__dir__ = surveyor


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
    behaviors: set[ str ] = set( )
    if mutables != '*': behaviors.add( _immutability_label )
    if visibles != '*': behaviors.add( _concealment_label )
    postproc_i = produce_initialization_postprocessor(
        behaviors = behaviors,
        nomargs_injection = { _class_behaviors_name: set( ) } )
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
    arguments = getattr( cls, _class_construction_arguments_name, { } )
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
    arguments: __.typx.Optional[ dict[ str, __.typx.Any ] ] = (
        getattr( cls, _class_construction_arguments_name, None ) )
    if arguments is not None:
        delattr( cls, _class_construction_arguments_name )
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
    setattr( cls, _cfc_behaviors_name, behaviors )


def produce_class_attributes_assigner(
    error_provider: ErrorClassProvider
) -> _factories.Assigner:

    def assign(
        cls: type,
        superf: _factories.AssignerLigation,
        name: str,
        value: __.typx.Any,
    ) -> None:
        behaviors = (
            _utilities.getattr0( cls, _cfc_behaviors_name, frozenset( ) ) )
        if _immutability_label not in behaviors:
            superf( name, value )
            return
        mutables_names: MutablesNames = (
            getattr( cls, _cfc_mutables_names_name, frozenset( ) ) )
        # mutables_predicates: AttributeMutabilityPredicates = (
        #     getattr( cls, _cfc_mutables_predicates_name, ( ) ) )
        # mutables_regexes: AttributeMutabilityRegexes = (
        #     getattr( cls, _cfc_mutables_regexes_name, ( ) ) )
        if name in mutables_names:
            superf( name, value )
            return
        # TODO: Sweep predicates.
        # TODO: Sweep regexes.
        target = _utilities.qualify_object_name( cls )
        raise error_provider( 'AttributeImmutability' )( name, target )

    return assign


def produce_class_attributes_deleter(
    error_provider: ErrorClassProvider
) -> _factories.Deleter:

    def delete(
        cls: type, superf: _factories.DeleterLigation, name: str
    ) -> None:
        behaviors = (
            _utilities.getattr0( cls, _cfc_behaviors_name, frozenset( ) ) )
        if _immutability_label not in behaviors:
            superf( name )
            return
        mutables_names: MutablesNames = (
            getattr( cls, _cfc_mutables_names_name, frozenset( ) ) )
        # mutables_predicates: AttributeMutabilityPredicates = (
        #     getattr( cls, _cfc_mutables_predicates_name, ( ) ) )
        # mutables_regexes: AttributeMutabilityRegexes = (
        #     getattr( cls, _cfc_mutables_regexes_name, ( ) ) )
        if name in mutables_names:
            superf( name )
            return
        # TODO: Sweep predicates.
        # TODO: Sweep regexes.
        target = _utilities.qualify_object_name( cls )
        raise error_provider( 'AttributeImmutability' )( name, target )

    return delete


def produce_class_attributes_surveyor( ) -> _factories.Surveyor:

    def survey(
        cls: type, superf: _factories.SurveyorLigation
    ) -> __.cabc.Iterable[ str ]:
        names = superf( )
        behaviors = (
            _utilities.getattr0( cls, _cfc_behaviors_name, frozenset( ) ) )
        if _concealment_label not in behaviors: return names
        visibles_names: VisiblesNames = (
            getattr( cls, _cfc_visibles_names_name, frozenset( ) ) )
        visibles_predicates: AttributeVisibilityPredicates = (
            getattr( cls, _cfc_visibles_predicates_name, ( ) ) )
        # visibles_regexes: AttributeVisibilityRegexes = (
        #     getattr( cls, _cfc_visibles_regexes_name, ( ) ) )
        names_: list[ str ] = [ ]
        for name in names:
            if visibles_names and name in visibles_names:
                names_.append( name )
                continue
            for predicate in visibles_predicates:
                if predicate( name ):
                    names_.append( name )
                    continue
            # TODO: Sweep regexes.
        return names_

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
        error_provider = _provide_error_class ) )
delete_class_attributes = (
    produce_class_attributes_deleter(
        error_provider = _provide_error_class ) )
survey_class_attributes = produce_class_attributes_surveyor( )


def produce_initialization_postprocessor(
    behaviors: __.cabc.Set[ str ] = frozenset( ),
    posargs_injection: __.PositionalArguments = ( ),
    nomargs_injection: __.NominativeArguments = __.dictproxy_empty,
) -> _nomina.DecorationPostprocessor:
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
            behaviors_ = _utilities.getattr0(
                self, _class_behaviors_name, set( ) )
            if not behaviors_:
                setattr( self, _class_behaviors_name, behaviors_ )
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

    def postprocess( cls: type ) -> None:
        mutables_names_: MutablesNames = frozenset( {
            *mutables_names,
            *getattr( cls, _class_mutables_names_name, frozenset( ) ) } )
        setattr( cls, _class_mutables_names_name, mutables_names_ )
        # TODO: Deduplicating, ordered merge for regexes and predicates.
        mutables_regexes_: AttributeMutabilityRegexes = (
            *mutables_regexes,
            *getattr( cls, _class_mutables_regexes_name, ( ) ) )
        setattr( cls, _class_mutables_regexes_name, mutables_regexes_ )
        mutables_predicates_: AttributeMutabilityPredicates = (
            *mutables_predicates,
            *getattr( cls, _class_mutables_predicates_name, ( ) ) )
        setattr( cls, _class_mutables_predicates_name, mutables_predicates_ )
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

    def postprocess( cls: type ) -> None:
        visibles_names_: VisiblesNames = frozenset( {
            *visibles_names,
            *getattr( cls, _class_visibles_names_name, frozenset( ) ) } )
        setattr( cls, _class_visibles_names_name, visibles_names_ )
        # TODO: Deduplicating, ordered merge for regexes and predicates.
        visibles_regexes_: AttributeVisibilityRegexes = (
            *visibles_regexes,
            *getattr( cls, _class_visibles_regexes_name, ( ) ) )
        setattr( cls, _class_visibles_regexes_name, visibles_regexes_ )
        visibles_predicates_: AttributeVisibilityPredicates = (
            *visibles_predicates,
            *getattr( cls, _class_visibles_predicates_name, ( ) ) )
        setattr( cls, _class_visibles_predicates_name, visibles_predicates_ )
        associate_dir( cls )

    return postprocess


Class = _factories.produce_class_factory(
    type,
    constructor = construct_class,
    initializer = initialize_class,
    assigner = assign_class_attributes,
    deleter = delete_class_attributes,
    surveyor = survey_class_attributes )
ProtocolClass = _factories.produce_class_factory(
    type( __.typx.Protocol ), # pyright: ignore[reportArgumentType]
    constructor = construct_class,
    initializer = initialize_class,
    assigner = assign_class_attributes,
    deleter = delete_class_attributes,
    surveyor = survey_class_attributes )


def _annotate_class(
    cls: type, decorators: _nomina.DecoratorsMutable
) -> None:
    ''' Annotates class in support of machinery. '''
    annotations = getattr( cls, '__annotations__' )
    # TODO: accretive set instead of set
    annotations[ _class_behaviors_name ] = set[ str ]


def _annotate_cfc(
    cls: type, decorators: _nomina.DecoratorsMutable
) -> None:
    ''' Annotates metaclass in support of machinery. '''
    annotations = getattr( cls, '__annotations__' )
    # TODO: accretive set instead of set
    annotations[ _cfc_behaviors_name ] = __.typx.ClassVar[ set[ str ] ]


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


def _probe_behavior( obj: object, collection_name: str, label: str ) -> bool:
    behaviors = _utilities.getattr0( obj, collection_name, frozenset( ) )
    return label in behaviors


def _record_class_mutables(
    cls: type, mutables: AttributeMutabilityVerifiers
) -> None:
    names, regexes, predicates = _classify_mutability_verifiers( mutables )
    setattr( cls, _cfc_mutables_names_name, names )
    setattr( cls, _cfc_mutables_regexes_name, regexes )
    setattr( cls, _cfc_mutables_predicates_name, predicates )


def _record_class_visibles(
    cls: type, mutables: AttributeVisibilityVerifiers
) -> None:
    names, regexes, predicates = _classify_visibility_verifiers( mutables )
    setattr( cls, _cfc_visibles_names_name, names )
    setattr( cls, _cfc_visibles_regexes_name, regexes )
    setattr( cls, _cfc_visibles_predicates_name, predicates )


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
    namespace[ _class_construction_arguments_name ] = arguments_


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
