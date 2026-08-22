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


def test_400_explain_inapplicable_behavior( ):
    ''' Inactive behavior: permitted by inapplicability. '''
    module = cache_import_module( MODULE_QNAME )

    class Plain: pass

    explanation = module.explain_attribute( Plain( ), 'anything' )
    assign = explanation.operations[ 'assign' ]
    survey = explanation.operations[ 'survey' ]
    assert isinstance( assign.decision, module.PermitByInapplicability )
    assert assign.permissible
    assert isinstance( survey.decision, module.PermitByInapplicability )
    assert survey.permissible


def test_401_explain_permit_by_names( ):
    ''' Names exclusion: permitted by names carrying the matched name. '''
    module = cache_import_module( MODULE_QNAME )
    decorate = _produce_example( mutables = ( 'alpha', ) )

    @decorate
    class Example: pass

    explanation = module.explain_attribute( Example( ), 'alpha' )
    assign = explanation.operations[ 'assign' ]
    assert isinstance( assign.decision, module.PermitByNames )
    assert 'alpha' == assign.decision.name
    assert assign.permissible


def test_402_explain_permit_by_regex( ):
    ''' Regex exclusion: permitted by regex carrying pattern text. '''
    module = cache_import_module( MODULE_QNAME )
    decorate = _produce_example( mutables = ( re.compile( 'al.*' ), ) )

    @decorate
    class Example: pass

    explanation = module.explain_attribute( Example( ), 'alpha' )
    assign = explanation.operations[ 'assign' ]
    assert isinstance( assign.decision, module.PermitByRegex )
    assert 'al.*' == assign.decision.pattern


def test_403_explain_permit_by_predicate( ):
    ''' Predicate exclusion: permitted by predicate carrying the
        qualified name text. '''
    module = cache_import_module( MODULE_QNAME )
    decorate = _produce_example( mutables = ( _matches_alpha, ) )

    @decorate
    class Example: pass

    explanation = module.explain_attribute( Example( ), 'alpha' )
    assign = explanation.operations[ 'assign' ]
    assert isinstance( assign.decision, module.PermitByPredicate )
    assert f"{__name__}._matches_alpha" == assign.decision.predicate


def test_404_explain_permit_by_omni( ):
    ''' Omni exclusion for assign/delete: permitted by omni.

        An omni marker never coexists with an active behavior through
        the recording API (record_behavior skips the behavior label for
        omni verifiers), so this constructs the defensive state the
        cores are specified to handle: immutability active with the
        exclusion names configured as the omni marker.
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
    assert isinstance( assign.decision, module.PermitByOmni )
    assert assign.permissible
    assert isinstance( delete.decision, module.PermitByOmni )


def test_405_explain_prohibit( ):
    ''' Active behavior without permitting rule: prohibited. '''
    module = cache_import_module( MODULE_QNAME )
    decorate = _produce_example( )

    @decorate
    class Example: pass

    explanation = module.explain_attribute( Example( ), 'alpha' )
    assign = explanation.operations[ 'assign' ]
    assert isinstance( assign.decision, module.Prohibit )
    assert not assign.permissible


def test_406_explain_concealed_attribute( ):
    ''' Concealment without visibles rule: survey prohibited. '''
    module = cache_import_module( MODULE_QNAME )
    decorate = _produce_example( visibles = ( ) )

    @decorate
    class Example: pass

    explanation = module.explain_attribute( Example( ), 'alpha' )
    survey = explanation.operations[ 'survey' ]
    assert isinstance( survey.decision, module.Prohibit )
    assert not survey.permissible


def test_407_explain_survey_precedence( ):
    ''' Survey follows precedence: the first matching rule decides. '''
    module = cache_import_module( MODULE_QNAME )
    decorate = _produce_example(
        visibles = ( _matches_alpha, re.compile( 'al.*' ) ) )

    @decorate
    class Example: pass

    explanation = module.explain_attribute( Example( ), 'alpha' )
    survey = explanation.operations[ 'survey' ]
    assert isinstance( survey.decision, module.PermitByPredicate )
    assert not isinstance( survey.decision, module.PermitByRegex )


def test_407a_explain_survey_names_precedence( ):
    ''' Survey names match short-circuits predicate and regex rules. '''
    module = cache_import_module( MODULE_QNAME )
    base = cache_import_module( f"{PACKAGE_NAME}.__" )
    classes = cache_import_module( f"{PACKAGE_NAME}.standard.classes" )

    calls: list[ str ] = [ ]

    def recording_predicate( name: str ) -> bool:
        calls.append( name )
        return True

    class Example( classes.Object ): pass

    type.__setattr__(
        Example, base.calculate_attrname( 'class', 'visibles_names' ),
        frozenset( ( 'alpha', ) ) )
    type.__setattr__(
        Example, base.calculate_attrname( 'class', 'visibles_predicates' ),
        ( recording_predicate, ) )
    explanation = module.explain_attribute( Example, 'alpha' )
    survey = explanation.operations[ 'survey' ]
    assert isinstance( survey.decision, module.PermitByNames )
    assert [ ] == calls


def test_408_explain_survey_omni( ):
    ''' Survey omni: permitted by omni, no predicate/regex evaluation. '''
    module = cache_import_module( MODULE_QNAME )
    base = cache_import_module( f"{PACKAGE_NAME}.__" )
    classes = cache_import_module( f"{PACKAGE_NAME}.standard.classes" )

    calls: list[ str ] = [ ]

    def recording_predicate( name: str ) -> bool:
        calls.append( name )
        return True

    class Example( classes.Object ): pass

    type.__setattr__(
        Example, base.calculate_attrname( 'class', 'visibles_names' ), '*' )
    type.__setattr__(
        Example, base.calculate_attrname( 'class', 'visibles_predicates' ),
        ( recording_predicate, ) )
    explanation = module.explain_attribute( Example, 'anything' )
    survey = explanation.operations[ 'survey' ]
    assert isinstance( survey.decision, module.PermitByOmni )
    assert [ ] == calls


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
        explanation.operations[ 'assign' ].decision = module.Prohibit( )
    with pytest.raises( exceptions.AttributeImmutability ):
        explanation.operations[ 'assign' ].decision.name = 'other'


def test_411_explanation_collections_immutable( ):
    ''' Mutating nested collections raises. '''
    module = cache_import_module( MODULE_QNAME )
    decorate = _produce_example( )

    @decorate
    class Example: pass

    explanation = module.explain_attribute( Example( ), 'alpha' )
    with pytest.raises( TypeError ):
        explanation.operations[ 'survey' ] = None
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
    ''' Repr summarizes target, behaviors, and decision outcomes. '''
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
    assert "assign: permitted by names 'alpha'" in permitted
    assert "delete: permitted by names 'alpha'" in permitted

    visible = repr( module.explain_attribute( Example( ), 'public_total' ) )
    assert "survey: permitted by regex 'pub.*'" in visible
    assert 'assign: prohibited (no permitting rule)' in visible

    class Plain: pass

    plain = repr( module.explain_attribute( Plain( ), 'x' ) )
    assert 'permitted (behavior inapplicable)' in plain
    assert '[internal]' not in plain

    internal = repr(
        module.explain_attribute( Plain( ), '_abc_cache' ) )
    assert '[internal]' in internal


def test_416_names_payload_collision( ):
    ''' A name literally 'regex' permitted by names stays distinct from
        a regex decision. '''
    module = cache_import_module( MODULE_QNAME )
    decorate = _produce_example( mutables = ( 'regex', ) )

    @decorate
    class Example: pass

    explanation = module.explain_attribute( Example( ), 'regex' )
    decision = explanation.operations[ 'assign' ].decision
    assert isinstance( decision, module.PermitByNames )
    assert 'regex' == decision.name
    assert not isinstance( decision, module.PermitByRegex )


def test_417_permissible_derivation( ):
    ''' Permissibility derives from the decision type. '''
    module = cache_import_module( MODULE_QNAME )
    decorate = _produce_example( mutables = ( 'alpha', ) )

    @decorate
    class Example: pass

    permitted = module.explain_attribute( Example( ), 'alpha' )
    prohibited = module.explain_attribute( Example( ), 'beta' )
    assert permitted.operations[ 'assign' ].permissible
    assert not prohibited.operations[ 'assign' ].permissible
    assert prohibited.operations[ 'assign' ].permissible is (
        not isinstance(
            prohibited.operations[ 'assign' ].decision, module.Prohibit ) )


def test_418_render_covers_decisions( ):
    """ Repr renders every decision branch. """
    module = cache_import_module( MODULE_QNAME )
    base = cache_import_module( f"{PACKAGE_NAME}.__" )
    classes = cache_import_module( f"{PACKAGE_NAME}.standard.classes" )

    class Example( classes.Object ): pass

    type.__setattr__(
        Example, base.calculate_attrname( 'class', 'visibles_names' ), '*' )
    type.__setattr__(
        Example, base.calculate_attrname( 'class', 'mutables_predicates' ),
        ( _matches_alpha, ) )
    omni = repr( module.explain_attribute( Example, 'anything' ) )
    assert "survey: permitted by omni '*'" in omni
    predicated = repr( module.explain_attribute( Example, 'alpha' ) )
    assert (
        f"assign: permitted by predicate '{__name__}._matches_alpha'"
        in predicated )


def test_419_produce_decision_rejects_unknown_kinds( ):
    ''' Unknown rule kinds raise instead of misclassifying. '''
    module = cache_import_module( MODULE_QNAME )

    with pytest.raises( ValueError, match = 'unknown' ):
        module.produce_decision( ( 'unknown', 'x' ), True )
    inapplicable = module.produce_decision( None, False )
    assert isinstance( inapplicable, module.PermitByInapplicability )
    prohibited = module.produce_decision( None, True )
    assert isinstance( prohibited, module.Prohibit )
    omni = module.produce_decision( ( 'omni', '*' ), True )
    assert isinstance( omni, module.PermitByOmni )


def test_420_render_rejects_unknown_decisions( ):
    ''' Rendering an unknown decision raises instead of reporting
        prohibited. '''
    module = cache_import_module( MODULE_QNAME )
    decorate = _produce_example( )

    @decorate
    class Example: pass

    explanation = module.explain_attribute( Example( ), 'alpha' )
    with pytest.raises( ValueError, match = 'object' ):
        explanation._render( object( ) )
