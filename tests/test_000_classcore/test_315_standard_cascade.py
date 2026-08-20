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


''' Characterizing tests for the attribute behavior decision cascade.

    These tests pin the current behavior of the cores in
    standard/behaviors.py — active-behavior sets, exclusion names,
    wildcard, predicates, regexes, and the survey matching loops —
    before the cascade is extracted into pure helpers shared with the
    explanations module (OpenSpec add-attribute-explanations, task 1.1).
'''


import re

import pytest

from .__ import PACKAGE_NAME, cache_import_module


MODULE_QNAME = f"{PACKAGE_NAME}.standard.behaviors"
DECORATORS_QNAME = f"{PACKAGE_NAME}.standard.decorators"
EXCEPTIONS_QNAME = f"{PACKAGE_NAME}.exceptions"


def _predicate_matches_alpha( name: str ) -> bool:
    return 'alpha' == name


def test_300_immutable_without_exclusions( ):
    ''' Immutability active and no rule permits: assignment raises. '''
    decorators = cache_import_module( DECORATORS_QNAME )
    exceptions = cache_import_module( EXCEPTIONS_QNAME )

    @decorators.with_standard_behaviors( )
    class Example: pass

    instance = Example( )
    with pytest.raises( exceptions.AttributeImmutability ):
        instance.alpha = 1
    with pytest.raises( exceptions.AttributeImmutability ):
        del instance.alpha


def test_301_immutable_excluded_by_name( ):
    ''' Name exclusion permits assignment and deletion. '''
    decorators = cache_import_module( DECORATORS_QNAME )

    @decorators.with_standard_behaviors( mutables = ( 'alpha', ) )
    class Example: pass

    instance = Example( )
    instance.alpha = 1
    assert 1 == instance.alpha
    del instance.alpha
    assert not hasattr( instance, 'alpha' )


def test_302_immutable_excluded_by_regex( ):
    ''' Regex exclusion permits assignment. '''
    decorators = cache_import_module( DECORATORS_QNAME )

    @decorators.with_standard_behaviors(
        mutables = ( re.compile( 'al.*' ), ) )
    class Example: pass

    instance = Example( )
    instance.alpha = 1
    assert 1 == instance.alpha


def test_303_immutable_excluded_by_predicate( ):
    ''' Predicate exclusion permits assignment. '''
    decorators = cache_import_module( DECORATORS_QNAME )

    @decorators.with_standard_behaviors(
        mutables = ( _predicate_matches_alpha, ) )
    class Example: pass

    instance = Example( )
    instance.alpha = 1
    assert 1 == instance.alpha


def test_304_immutable_wildcard( ):
    ''' Wildcard exclusion permits any assignment. '''
    decorators = cache_import_module( DECORATORS_QNAME )

    @decorators.with_standard_behaviors( mutables = '*' )
    class Example: pass

    instance = Example( )
    instance.anything = 1
    assert 1 == instance.anything


def test_310_concealment_without_visibles( ):
    ''' Concealment hides non-public names; public names stay visible
        via the default public-identifier predicate. '''
    decorators = cache_import_module( DECORATORS_QNAME )

    @decorators.with_standard_behaviors( )
    class Example:
        _private = 1
        public = 2

    instance = Example( )
    assert '_private' not in dir( instance )
    assert 'public' in dir( instance )


def test_310a_concealment_no_visibles_rules( ):
    ''' Concealment with empty visibles hides every name. '''
    decorators = cache_import_module( DECORATORS_QNAME )

    @decorators.with_standard_behaviors( visibles = ( ) )
    class Example:
        alpha = 1

    instance = Example( )
    assert 'alpha' not in dir( instance )


def test_311_concealment_visibles_by_name( ):
    ''' Visibles name rule reveals the name in dir. '''
    decorators = cache_import_module( DECORATORS_QNAME )

    @decorators.with_standard_behaviors( visibles = ( 'alpha', ) )
    class Example:
        alpha = 1

    instance = Example( )
    assert 'alpha' in dir( instance )


def test_312_concealment_visibles_wildcard( ):
    ''' Visibles wildcard reveals all names. '''
    decorators = cache_import_module( DECORATORS_QNAME )

    @decorators.with_standard_behaviors( visibles = '*' )
    class Example:
        alpha = 1

    instance = Example( )
    assert 'alpha' in dir( instance )


def test_313_concealment_visibles_by_regex( ):
    ''' Visibles regex rule reveals matching names. '''
    decorators = cache_import_module( DECORATORS_QNAME )

    @decorators.with_standard_behaviors(
        visibles = ( re.compile( 'al.*' ), ) )
    class Example:
        alpha = 1
        beta = 2

    instance = Example( )
    assert 'alpha' in dir( instance )
    assert 'beta' not in dir( instance )


def test_314_survey_multi_match_yields_duplicates( ):
    ''' Survey yields a name multiple times when multiple rules match.

        Characterizes the current control flow: the per-name matching
        loops continue the inner loop only, so a name matching one
        predicate and one regex is appended twice. Preserved deliberately
        by the extraction; normalization is a separate repair.

        Note the lookup asymmetry: the core reads the active-behaviors
        set through the mangling accessors, but exclusion configuration
        through plain attribute access under raw level names.
    '''
    module = cache_import_module( MODULE_QNAME )
    base = cache_import_module( f"{PACKAGE_NAME}.__" )
    utilities = cache_import_module( f"{PACKAGE_NAME}.utilities" )

    class Example: pass
    example = Example( )
    utilities.setattr0(
        example, base.calculate_attrname( 'instance', 'behaviors' ),
        frozenset( ( 'concealment', ) ) )
    setattr( example,
        base.calculate_attrname( 'instances', 'visibles_names' ),
        frozenset( ) )
    setattr( example,
        base.calculate_attrname( 'instances', 'visibles_predicates' ),
        ( _predicate_matches_alpha, ) )
    setattr( example,
        base.calculate_attrname( 'instances', 'visibles_regexes' ),
        ( re.compile( 'al.*' ), ) )

    visible = list( module.survey_visible_attributes(
        example, ligation = lambda: [ 'alpha', 'beta' ],
        attributes_namer = base.calculate_attrname,
        level = 'instances' ) )
    assert [ 'alpha', 'alpha' ] == visible


def test_315_survey_wildcard_short_circuits( ):
    ''' Survey wildcard returns all names before rule evaluation. '''
    module = cache_import_module( MODULE_QNAME )
    base = cache_import_module( f"{PACKAGE_NAME}.__" )
    utilities = cache_import_module( f"{PACKAGE_NAME}.utilities" )

    calls: list[ str ] = [ ]

    def recording_predicate( name: str ) -> bool:
        calls.append( name )
        return True

    class Example: pass
    example = Example( )
    utilities.setattr0(
        example, base.calculate_attrname( 'instance', 'behaviors' ),
        frozenset( ( 'concealment', ) ) )
    setattr( example,
        base.calculate_attrname( 'instances', 'visibles_names' ), '*' )
    setattr( example,
        base.calculate_attrname( 'instances', 'visibles_predicates' ),
        ( recording_predicate, ) )

    visible = list( module.survey_visible_attributes(
        example, ligation = lambda: [ 'alpha' ],
        attributes_namer = base.calculate_attrname,
        level = 'instances' ) )
    assert [ 'alpha' ] == visible
    assert [ ] == calls


def test_316_survey_names_match_skips_rules( ):
    ''' A names match short-circuits predicate and regex evaluation.

        Characterizes the original control flow, where a names match
        continued the outer per-name loop: with a name rule overlapping
        predicate and regex rules, the name is yielded once and no
        predicate or regex runs for it.
    '''
    module = cache_import_module( MODULE_QNAME )
    base = cache_import_module( f"{PACKAGE_NAME}.__" )
    utilities = cache_import_module( f"{PACKAGE_NAME}.utilities" )

    calls: list[ str ] = [ ]

    def recording_predicate( name: str ) -> bool:
        calls.append( name )
        return True

    class Example: pass
    example = Example( )
    utilities.setattr0(
        example, base.calculate_attrname( 'instance', 'behaviors' ),
        frozenset( ( 'concealment', ) ) )
    setattr( example,
        base.calculate_attrname( 'instances', 'visibles_names' ),
        frozenset( ( 'alpha', ) ) )
    setattr( example,
        base.calculate_attrname( 'instances', 'visibles_predicates' ),
        ( recording_predicate, ) )
    setattr( example,
        base.calculate_attrname( 'instances', 'visibles_regexes' ),
        ( re.compile( 'al.*' ), ) )

    visible = list( module.survey_visible_attributes(
        example, ligation = lambda: [ 'alpha' ],
        attributes_namer = base.calculate_attrname,
        level = 'instances' ) )
    assert [ 'alpha' ] == visible
    assert [ ] == calls


def test_320_render_verifier_text( ):
    ''' Verifier rendering: pattern text, qualified names, fallbacks. '''
    module = cache_import_module( MODULE_QNAME )

    assert 'al.*' == module.render_verifier_text( re.compile( 'al.*' ) )
    assert (
        f"{__name__}._predicate_matches_alpha"
        == module.render_verifier_text( _predicate_matches_alpha ) )
    assert '<anonymous>' == module.render_verifier_text( object( ) )

    def local_predicate( name: str ) -> bool: return True

    assert (
        'test_320_render_verifier_text.<locals>.local_predicate'
        == module.render_verifier_text( local_predicate ) )


def test_321_first_permitting_rule_precedence( ):
    ''' First permitting rule follows wildcard/names/predicate/regex
        precedence and reports kind with detail text. '''
    module = cache_import_module( MODULE_QNAME )
    base = cache_import_module( f"{PACKAGE_NAME}.__" )
    namer = base.calculate_attrname

    class Stub: pass
    stub = Stub( )

    setattr( stub, namer( 'instances', 'mutables_names' ), '*' )
    assert ( 'wildcard', '*' ) == module.survey_first_permitting_rule(
        stub, attributes_namer = namer, level = 'instances',
        basename = 'mutables', name = 'anything' )

    setattr( stub, namer( 'instances', 'mutables_names' ),
        frozenset( ( 'alpha', ) ) )
    assert ( 'names', 'alpha' ) == module.survey_first_permitting_rule(
        stub, attributes_namer = namer, level = 'instances',
        basename = 'mutables', name = 'alpha' )

    setattr( stub, namer( 'instances', 'mutables_names' ), frozenset( ) )
    setattr( stub, namer( 'instances', 'mutables_predicates' ),
        ( _predicate_matches_alpha, ) )
    setattr( stub, namer( 'instances', 'mutables_regexes' ),
        ( re.compile( 'al.*' ), ) )
    assert ( 'predicate', f"{__name__}._predicate_matches_alpha"
        ) == module.survey_first_permitting_rule(
        stub, attributes_namer = namer, level = 'instances',
        basename = 'mutables', name = 'alpha' )

    setattr( stub, namer( 'instances', 'mutables_predicates' ), ( ) )
    assert ( 'regex', 'al.*' ) == module.survey_first_permitting_rule(
        stub, attributes_namer = namer, level = 'instances',
        basename = 'mutables', name = 'alpha' )

    setattr( stub, namer( 'instances', 'mutables_regexes' ), ( ) )
    assert None is module.survey_first_permitting_rule(
        stub, attributes_namer = namer, level = 'instances',
        basename = 'mutables', name = 'alpha' )


def test_322_matched_rules_union( ):
    ''' Matched rules report predicate/regex matches in evaluation order;
        a names match short-circuits to the single names rule. '''
    module = cache_import_module( MODULE_QNAME )
    base = cache_import_module( f"{PACKAGE_NAME}.__" )
    namer = base.calculate_attrname

    class Stub: pass
    stub = Stub( )
    setattr( stub, namer( 'instances', 'visibles_names' ),
        frozenset( ( 'alpha', ) ) )
    assert ( ( 'names', 'alpha' ), ) == module.survey_matched_rules(
        stub, attributes_namer = namer, level = 'instances',
        basename = 'visibles', name = 'alpha' )

    setattr( stub, namer( 'instances', 'visibles_names' ), frozenset( ) )
    setattr( stub, namer( 'instances', 'visibles_predicates' ),
        ( _predicate_matches_alpha, ) )
    setattr( stub, namer( 'instances', 'visibles_regexes' ),
        ( re.compile( 'al.*' ), ) )

    assert (
        ( 'predicate', f"{__name__}._predicate_matches_alpha" ),
        ( 'regex', 'al.*' ) ) == module.survey_matched_rules(
        stub, attributes_namer = namer, level = 'instances',
        basename = 'visibles', name = 'alpha' )
    assert ( ) == module.survey_matched_rules(
        stub, attributes_namer = namer, level = 'instances',
        basename = 'visibles', name = 'beta' )
