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
#  under the License is distributed on an "AS IS" BASIS,                     #
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#  See the License for the specific language governing permissions and       #
#  limitations under the License.                                            #
#                                                                            #
#============================================================================#


''' Tests for attribute explanations (OpenSpec add-attribute-explanations). '''

import re

import pytest

from .__ import PACKAGE_NAME, cache_import_module


MODULE_QNAME = f"{PACKAGE_NAME}.standard.explanations"
DECORATORS_QNAME = f"{PACKAGE_NAME}.standard.decorators"
EXCEPTIONS_QNAME = f"{PACKAGE_NAME}.exceptions"


def _matches_alpha( name: str ) -> bool:
    return 'alpha' == name


def _produce_example( **verifiers ):
    decorators = cache_import_module( DECORATORS_QNAME )

    return decorators.with_standard_behaviors( **verifiers )


def test_400_explain_mutable_attribute( ):
    ''' Mutable attribute: assign and delete permitted, no decider. '''
    module = cache_import_module( MODULE_QNAME )

    @dataclass_free_decorator( )
    class MutableBase: pass

    explanation = module.explain_attribute( MutableBase, 'anything' )
    assign = explanation.operations[ 'assign' ]
    delete = explanation.operations[ 'delete' ]
    assert assign.permitted and assign.decider is None
    assert delete.permitted and delete.decider is None


def dataclass_free_decorator( ):
    ''' Produces decorator without standard behaviors. '''
    return _produce_no_behaviors( )


def _produce_no_behaviors( ):
    def decorate( cls ):
        return cls
    return decorate


def test_401_explain_excluded_by_name( ):
    ''' Name exclusion: permitted with kind 'names' and detail the name. '''
    module = cache_import_module( MODULE_QNAME )
    decorate = _produce_example( mutables = ( 'alpha', ) )

    @decorate
    class Example: pass

    explanation = module.explain_attribute( Example( ), 'alpha' )
    assign = explanation.operations[ 'assign' ]
    assert assign.permitted
    assert assign.decider is not None
    assert 'names' == assign.decider.kind
    assert 'alpha' == assign.decider.detail


def test_402_explain_excluded_by_regex( ):
    ''' Regex exclusion: permitted with kind 'regex' and pattern detail. '''
    module = cache_import_module( MODULE_QNAME )
    decorate = _produce_example( mutables = ( re.compile( 'al.*' ), ) )

    @decorate
    class Example: pass

    explanation = module.explain_attribute( Example( ), 'alpha' )
    assign = explanation.operations[ 'assign' ]
    assert assign.permitted
    assert 'regex' == assign.decider.kind
    assert 'al.*' == assign.decider.detail


def test_403_explain_excluded_by_predicate( ):
    ''' Predicate exclusion: permitted, kind 'predicate', qualified name. '''
    module = cache_import_module( MODULE_QNAME )
    decorate = _produce_example( mutables = ( _matches_alpha, ) )

    @decorate
    class Example: pass

    explanation = module.explain_attribute( Example( ), 'alpha' )
    assign = explanation.operations[ 'assign' ]
    assert assign.permitted
    assert 'predicate' == assign.decider.kind
    assert f"{__name__}._matches_alpha" == assign.decider.detail


def test_404_explain_wildcard_exclusion( ):
    ''' Wildcard exclusion for assign/delete: permitted, detail '*'.

        A wildcard never coexists with active immutability through the
        recording API (record_behavior skips the behavior label for
        wildcard verifiers), so this constructs the defensive state the
        cores are specified to handle: immutability active with the
        exclusion names configured as the wildcard.
    '''
    module = cache_import_module( MODULE_QNAME )
    base = cache_import_module( f"{PACKAGE_NAME}.__" )
    classes = cache_import_module( f"{PACKAGE_NAME}.standard.classes" )

    class Example( classes.Object ): pass

    type.__setattr__(
        Example, base.calculate_attrname( 'class', 'mutables_names' ), '*' )
    explanation = module.explain_attribute( Example, 'anything' )
    assign = explanation.operations[ 'assign' ]
    delete = explanation.operations[ 'delete' ]
    assert assign.permitted and 'wildcard' == assign.decider.kind
    assert '*' == assign.decider.detail
    assert delete.permitted and 'wildcard' == delete.decider.kind


def test_405_explain_immutable_attribute( ):
    ''' Immutability without permitting rule: not permitted, no decider. '''
    module = cache_import_module( MODULE_QNAME )
    decorate = _produce_example( )

    @decorate
    class Example: pass

    explanation = module.explain_attribute( Example( ), 'alpha' )
    assign = explanation.operations[ 'assign' ]
    assert not assign.permitted
    assert assign.decider is None


def test_406_explain_concealed_attribute( ):
    ''' Concealment without visibles rule: survey not permitted, empty. '''
    module = cache_import_module( MODULE_QNAME )
    decorate = _produce_example( visibles = ( ) )

    @decorate
    class Example: pass

    explanation = module.explain_attribute( Example( ), 'alpha' )
    survey = explanation.operations[ 'survey' ]
    assert not survey.permitted
    assert ( ) == survey.matched


def test_407_explain_survey_multi_match( ):
    ''' Survey union semantics: predicate and regex both in matched. '''
    module = cache_import_module( MODULE_QNAME )
    decorate = _produce_example(
        visibles = ( _matches_alpha, re.compile( 'al.*' ) ) )

    @decorate
    class Example: pass

    explanation = module.explain_attribute( Example( ), 'alpha' )
    survey = explanation.operations[ 'survey' ]
    assert survey.permitted
    kinds = tuple( rule.kind for rule in survey.matched )
    assert ( 'predicate', 'regex' ) == kinds


def test_408_explain_survey_wildcard( ):
    ''' Survey wildcard: single wildcard rule, no predicate/regex rules.

        As with the assign wildcard, a visibility wildcard suppresses the
        concealment label through the recording API, so this constructs
        the defensive state: concealment active with the visibles names
        configured as the wildcard.
    '''
    module = cache_import_module( MODULE_QNAME )
    base = cache_import_module( f"{PACKAGE_NAME}.__" )
    classes = cache_import_module( f"{PACKAGE_NAME}.standard.classes" )

    class Example( classes.Object ): pass

    type.__setattr__(
        Example, base.calculate_attrname( 'class', 'visibles_names' ), '*' )
    explanation = module.explain_attribute( Example, 'anything' )
    survey = explanation.operations[ 'survey' ]
    assert survey.permitted
    assert 1 == len( survey.matched )
    assert 'wildcard' == survey.matched[ 0 ].kind


def test_409_explain_survey_concealment_inactive( ):
    ''' Concealment inactive: survey permitted with empty matched. '''
    module = cache_import_module( MODULE_QNAME )

    class Plain: pass

    explanation = module.explain_attribute( Plain( ), 'alpha' )
    survey = explanation.operations[ 'survey' ]
    assert survey.permitted
    assert ( ) == survey.matched


def test_410_explanation_records_frozen( ):
    ''' Assigning a record field raises immutability error. '''
    module = cache_import_module( MODULE_QNAME )
    exceptions = cache_import_module( EXCEPTIONS_QNAME )
    decorate = _produce_example( mutables = ( 'alpha', ) )

    @decorate
    class Example: pass

    explanation = module.explain_attribute( Example( ), 'alpha' )
    with pytest.raises( exceptions.AttributeImmutability ):
        explanation.name = 'other'
    with pytest.raises( exceptions.AttributeImmutability ):
        explanation.operations[ 'assign' ].permitted = False
    with pytest.raises( exceptions.AttributeImmutability ):
        explanation.operations[ 'assign' ].decider.kind = 'names'


def test_411_explanation_collections_immutable( ):
    ''' Mutating nested collections raises. '''
    module = cache_import_module( MODULE_QNAME )
    decorate = _produce_example( )

    @decorate
    class Example: pass

    explanation = module.explain_attribute( Example( ), 'alpha' )
    with pytest.raises( TypeError ):
        explanation.operations[ 'survey' ] = None
    survey = explanation.operations[ 'survey' ]
    assert isinstance( survey.matched, tuple )
    behaviors = explanation.behaviors
    with pytest.raises( TypeError ):
        behaviors[ 'new' ] = frozenset( )


def test_412_explanation_internal_marking( ):
    ''' Framework and stdlib machinery names are marked internal. '''
    module = cache_import_module( MODULE_QNAME )
    decorate = _produce_example( )

    @decorate
    class Example: pass

    framework = module.explain_attribute(
        Example( ), '_classcore_class_in_progress_x' )
    stdlib = module.explain_attribute( Example( ), '_abc_cache' )
    user = module.explain_attribute( Example( ), 'alpha' )
    assert framework.internal
    assert stdlib.internal
    assert not user.internal


def test_413_explanation_level_semantics( ):
    ''' Class targets evaluate classes level; instances evaluate
        instances level. '''
    module = cache_import_module( MODULE_QNAME )
    classes = cache_import_module( f"{PACKAGE_NAME}.standard.classes" )

    explanation = module.explain_attribute( classes.Object, 'alpha' )
    assert 'class' in explanation.behaviors
    instance_explanation = (
        module.explain_attribute( classes.Object( ), 'alpha' ) )
    assert 'instance' in instance_explanation.behaviors


def test_414_explanation_observational( ):
    ''' Explanations do not bypass or alter behaviors. '''
    module = cache_import_module( MODULE_QNAME )
    exceptions = cache_import_module( EXCEPTIONS_QNAME )
    decorate = _produce_example( )

    @decorate
    class Example: pass

    instance = Example( )
    module.explain_attribute( instance, 'alpha' )
    with pytest.raises( exceptions.AttributeImmutability ):
        instance.alpha = 1


def test_415_explanation_repr_summary( ):
    ''' Repr summarizes target, behaviors, and verdict outcomes. '''
    module = cache_import_module( MODULE_QNAME )
    decorate = _produce_example(
        mutables = ( 'alpha', ), visibles = ( re.compile( 'pub.*' ), ) )

    @decorate
    class Example:
        alpha = 1
        public_total = 2

    permitted = repr( module.explain_attribute( Example( ), 'alpha' ) )
    assert "'alpha' on instance of class" in permitted
    assert 'behaviors: concealment, immutability (instance)' in permitted
    assert "assign: permitted via names 'alpha'" in permitted
    assert 'delete: permitted via names' in permitted
    assert 'survey: concealed (no matching rule)' in permitted

    visible = repr( module.explain_attribute( Example( ), 'public_total' ) )
    assert "survey: visible via regex 'pub.*'" in visible
    assert 'assign: forbidden (no permitting rule)' in visible

    class Plain: pass

    plain = repr( module.explain_attribute( Plain( ), 'x' ) )
    assert 'assign: permitted (behavior inactive)' in plain
    assert 'survey: visible' in plain
    assert '[internal]' not in plain

    internal = repr(
        module.explain_attribute( Plain( ), '_abc_cache' ) )
    assert '[internal]' in internal
