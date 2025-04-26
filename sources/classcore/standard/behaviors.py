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


''' Implementations for standard behaviors. '''
# TODO? Support introspection of PEP 593 annotations for behavior exclusions.
#       Maybe enum for mutability and visibility.


from __future__ import annotations

from .. import factories as _factories
from .. import utilities as _utilities
from . import __
from . import nomina as _nomina


concealment_label = 'concealment'
immutability_label = 'immutability'


def assign_attribute_if_mutable( # noqa: PLR0913
    obj: object, /, *,
    ligation: _nomina.AssignerLigation,
    error_class_provider: _nomina.ErrorClassProvider,
    behaviors_name: str,
    names_name: str,
    regexes_name: str,
    predicates_name: str,
    name: str,
    value: __.typx.Any,
) -> None:
    behaviors = _utilities.getattr0( obj, behaviors_name, frozenset( ) )
    if immutability_label not in behaviors:
        ligation( name, value )
        return
    names: _nomina.BehaviorExclusionNames = (
        getattr( obj, names_name, frozenset( ) ) )
    regexes: _nomina.BehaviorExclusionRegexes = (
        getattr( obj, regexes_name, ( ) ) )
    predicates: _nomina.BehaviorExclusionPredicates = (
        getattr( obj, predicates_name, ( ) ) )
    if name in names:
        ligation( name, value )
        return
    for predicate in predicates:
        if predicate( name ):
            # TODO? Cache predicate hit.
            ligation( name, value )
            return
    for regex in regexes:
        if regex.fullmatch( name ):
            # TODO? Cache regex hit.
            ligation( name, value )
            return
    target = _utilities.describe_object( obj )
    raise error_class_provider( 'AttributeImmutability' )( name, target )


def delete_attribute_if_mutable( # noqa: PLR0913
    obj: object, /, *,
    ligation: _nomina.DeleterLigation,
    error_class_provider: _nomina.ErrorClassProvider,
    behaviors_name: str,
    names_name: str,
    regexes_name: str,
    predicates_name: str,
    name: str,
) -> None:
    behaviors = _utilities.getattr0( obj, behaviors_name, frozenset( ) )
    if immutability_label not in behaviors:
        ligation( name )
        return
    names: _nomina.BehaviorExclusionNames = (
        getattr( obj, names_name, frozenset( ) ) )
    regexes: _nomina.BehaviorExclusionRegexes = (
        getattr( obj, regexes_name, ( ) ) )
    predicates: _nomina.BehaviorExclusionPredicates = (
        getattr( obj, predicates_name, ( ) ) )
    if name in names:
        ligation( name )
        return
    for predicate in predicates:
        if predicate( name ):
            # TODO? Cache predicate hit.
            ligation( name )
            return
    for regex in regexes:
        if regex.fullmatch( name ):
            # TODO? Cache regex hit.
            ligation( name )
            return
    target = _utilities.describe_object( obj )
    raise error_class_provider( 'AttributeImmutability' )( name, target )


def survey_visible_attributes( # noqa: PLR0913
    obj: object, /, *,
    ligation: _nomina.SurveyorLigation,
    behaviors_name: str,
    names_name: str,
    regexes_name: str,
    predicates_name: str,
) -> __.cabc.Iterable[ str ]:
    names_base = ligation( )
    behaviors = _utilities.getattr0( obj, behaviors_name, frozenset( ) )
    if concealment_label not in behaviors: return names_base
    names: _nomina.BehaviorExclusionNames = (
        getattr( obj, names_name, frozenset( ) ) )
    regexes: _nomina.BehaviorExclusionRegexes = (
        getattr( obj, regexes_name, ( ) ) )
    predicates: _nomina.BehaviorExclusionPredicates = (
        getattr( obj, predicates_name, ( ) ) )
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


def classify_behavior_exclusion_verifiers(
    verifiers: _nomina.BehaviorExclusionVerifiers
) -> tuple[
    _nomina.BehaviorExclusionNames,
    _nomina.BehaviorExclusionRegexes,
    _nomina.BehaviorExclusionPredicates,
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


def produce_class_construction_preprocessor(
    attributes_namer: _nomina.AttributesNamer
) -> _factories.ConstructionPreprocessor:

    def preprocess( # noqa: PLR0913
        clscls: type,
        name: str,
        bases: list[ type ],
        namespace: dict[ str, __.typx.Any ],
        arguments: dict[ str, __.typx.Any ],
        decorators: _nomina.DecoratorsMutable,
    ) -> None:
        record_class_construction_arguments(
            attributes_namer, namespace, arguments )

    return preprocess


def produce_class_construction_postprocessor(
    attributes_namer: _nomina.AttributesNamer
) -> _factories.ConstructionPostprocessor:
    arguments_name = attributes_namer( 'class', 'construction_arguments' )

    def postprocess(
        cls: type, decorators: _nomina.DecoratorsMutable
    ) -> None:
        arguments = getattr( cls, arguments_name, { } )
        dcls_spec = getattr( cls, '__dataclass_transform__', None )
        if not dcls_spec: # either base class or metaclass may be marked
            clscls = type( cls )
            dcls_spec = getattr( clscls, '__dataclass_transform__', None )
        instances_mutables = arguments.get(
            'instances_mutables', __.mutables_default )
        instances_visibles = arguments.get(
            'instances_visibles', __.visibles_default )
        if dcls_spec and dcls_spec.get( 'kw_only_default', False ):
            from .decorators import dataclass_with_standard_behaviors
            decorator_factory = dataclass_with_standard_behaviors
            if not dcls_spec.get( 'frozen_default', True ):
                instances_mutables = instances_mutables or '*'
        else:
            from .decorators import with_standard_behaviors
            decorator_factory = with_standard_behaviors
        decorator = decorator_factory(
            mutables = instances_mutables, visibles = instances_visibles )
        decorators.append( decorator )

    return postprocess


def produce_class_initialization_completer(
    attributes_namer: _nomina.AttributesNamer
) -> _factories.InitializationCompleter:
    arguments_name = attributes_namer( 'class', 'construction_arguments' )

    def complete( cls: type ) -> None:
        arguments: __.typx.Optional[ dict[ str, __.typx.Any ] ] = (
            getattr( cls, arguments_name, None ) )
        if arguments is not None: delattr( cls, arguments_name )
        arguments = arguments or { }
        class_mutables = arguments.get( 'class_mutables', __.mutables_default )
        class_visibles = arguments.get( 'class_visibles', __.visibles_default )
        behaviors: set[ str ] = set( )
        if class_mutables != '*':
            record_behavior_exclusions(
                cls, attributes_namer, 'mutables', 'class', class_mutables )
            behaviors.add( immutability_label )
        if class_visibles != '*':
            record_behavior_exclusions(
                cls, attributes_namer, 'visibles', 'class', class_visibles )
            behaviors.add( concealment_label )
        # Set behaviors attribute last since it enables enforcement.
        setattr( cls, attributes_namer( 'class', 'behaviors' ), behaviors )

    return complete


def record_behavior_exclusions(
    cls: type,
    attributes_namer: _nomina.AttributesNamer,
    basename: str,
    level: str,
    verifiers: _nomina.BehaviorExclusionVerifiers,
) -> None:
    names, regexes, predicates = (
        classify_behavior_exclusion_verifiers( verifiers ) )
    names_name = attributes_namer( level, f"{basename}_names" )
    regexes_name = attributes_namer( level, f"{basename}_regexes" )
    predicates_name = attributes_namer( level, f"{basename}_predicates" )
    names_: _nomina.BehaviorExclusionNames = frozenset( {
        *names, *getattr( cls, names_name, frozenset( ) ) } )
    regexes_: _nomina.BehaviorExclusionRegexes = (
        _deduplicate_merge_sequences(
            regexes, getattr( cls, regexes_name, ( ) ) ) )
    predicates_: _nomina.BehaviorExclusionPredicates = (
        _deduplicate_merge_sequences(
            predicates, getattr( cls, predicates_name, ( ) ) ) )
    setattr( cls, names_name, names_ )
    setattr( cls, regexes_name, regexes_ )
    setattr( cls, predicates_name, predicates_ )
    # TODO? Add regexes match cache.
    # TODO? Add predicates match cache.


def record_class_construction_arguments(
    attributes_namer: _nomina.AttributesNamer,
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
