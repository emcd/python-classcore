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


''' Explanations of attribute behavior decisions. '''


from .. import utilities as _utilities
from . import __
from . import behaviors as _behaviors
from . import classes as _classes
from . import decorators as _decorators
from . import nomina as _nomina


_framework_names_prefix = '_classcore_'


@_decorators.dataclass_with_standard_behaviors( )
class DecisionRule:
    ''' Rule which decided an attribute behavior outcome. '''
    kind: str
    detail: str
    level: str


@_decorators.dataclass_with_standard_behaviors( )
class AssignVerdict:
    ''' Verdict for attribute assignment under precedence semantics. '''
    operation: str
    permitted: bool
    decider: __.typx.Optional[ DecisionRule ]


@_decorators.dataclass_with_standard_behaviors( )
class DeleteVerdict:
    ''' Verdict for attribute deletion under precedence semantics. '''
    operation: str
    permitted: bool
    decider: __.typx.Optional[ DecisionRule ]


@_decorators.dataclass_with_standard_behaviors( )
class SurveyVerdict:
    ''' Verdict for attribute visibility under union semantics. '''
    operation: str
    permitted: bool
    matched: tuple[ DecisionRule, ... ]


@_decorators.dataclass_with_standard_behaviors( )
class AttributeExplanation:
    ''' Decision trace for one attribute of one target. '''
    target: str
    name: str
    behaviors: __.cabc.Mapping[ str, __.cabc.Set[ str ] ]
    operations: __.cabc.Mapping[ str, object ]
    internal: bool

    def __repr__( self ) -> str:
        ''' Returns summary of the decision trace. '''
        lines = [
            f"{self.name!r} on {self.target}"
            + ( ' [internal]' if self.internal else '' ) ]
        for level, labels in self.behaviors.items( ):
            lines.append(
                f"behaviors: {', '.join( sorted( labels ) )}"
                + f" ({level})" )
        for operation in ( 'assign', 'delete', 'survey' ):
            verdict = self.operations.get( operation )
            if verdict is None: continue # pragma: no cover
            lines.append( self._render_verdict( verdict ) )
        return '\n'.join( lines )

    def _render_verdict( self, verdict: object, / ) -> str:
        operation = getattr( verdict, 'operation', None )
        permitted = getattr( verdict, 'permitted', False )
        if operation == 'survey':
            matched = getattr( verdict, 'matched', ( ) )
            rules = ', '.join(
                f"{rule.kind} {rule.detail!r}" for rule in matched )
            outcome = (
                f"visible via {rules}" if permitted and rules
                else 'visible' if permitted
                else 'concealed (no matching rule)' )
        else:
            decider = getattr( verdict, 'decider', None )
            outcome = (
                f"permitted via {decider.kind} {decider.detail!r}"
                if decider is not None
                else 'permitted (behavior inactive)'
                if permitted else 'forbidden (no permitting rule)' )
        return f"{operation}: {outcome}"


def explain_attribute(
    target: object, name: str, /, *,
    attributes_namer: _nomina.AttributesNamer = __.calculate_attrname,
) -> AttributeExplanation:
    ''' Returns decision trace for attribute name on target.

        Assign and delete verdicts follow precedence semantics; the survey
        verdict follows union semantics. For class targets, the
        classes-level configuration is evaluated; for instance targets,
        the instances-level configuration is evaluated against the
        instance's class hierarchy — matching the levels the behavior
        cores evaluate. Records report the normalized level names
        ('class' and 'instance') at which behaviors and exclusion
        configuration were found. Explanations are observational: they
        neither bypass nor alter concealment or immutability.
    '''
    class_target = __.inspect.isclass( target )
    level = 'class' if class_target else 'instances'
    level_normalized = 'class' if class_target else 'instance'
    behaviors = _behaviors.survey_active_behaviors(
        target, attributes_namer = attributes_namer, level = level )
    immutability = _nomina.immutability_label in behaviors
    concealment = _nomina.concealment_label in behaviors
    operations: dict[ str, object ] = { }
    for operation in ( 'assign', 'delete' ):
        rule = (
            _behaviors.survey_first_permitting_rule(
                target, attributes_namer = attributes_namer,
                level = level, basename = 'mutables', name = name )
            if immutability else None )
        verdict_class = (
            AssignVerdict if operation == 'assign' else DeleteVerdict )
        operations[ operation ] = verdict_class(
            operation = operation,
            permitted = not immutability or rule is not None,
            decider = (
                DecisionRule(
                    kind = rule[ 0 ], detail = rule[ 1 ],
                    level = level_normalized )
                if rule is not None else None ) )
    if concealment:
        names_name = attributes_namer( level, 'visibles_names' )
        names: _nomina.BehaviorExclusionNamesOmni = (
            getattr( target, names_name, frozenset( ) ) )
        if names == '*':
            rule_wildcard = DecisionRule(
                kind = 'wildcard', detail = '*',
                level = level_normalized )
            matched = ( rule_wildcard, )
            survey_permitted = True
        else:
            matched = tuple(
                DecisionRule(
                    kind = kind, detail = detail, level = level_normalized )
                for kind, detail in _behaviors.survey_matched_rules(
                    target, attributes_namer = attributes_namer,
                    level = level, basename = 'visibles', name = name ) )
            survey_permitted = bool( matched )
    else:
        matched = ( )
        survey_permitted = True
    operations[ 'survey' ] = SurveyVerdict(
        operation = 'survey',
        permitted = survey_permitted, matched = matched )
    return AttributeExplanation(
        target = _utilities.describe_object( target ),
        name = name,
        behaviors = __.types.MappingProxyType(
            { level_normalized: frozenset( behaviors ) } ),
        operations = __.types.MappingProxyType( operations ),
        internal = survey_internal_name( name ) )


def survey_internal_name( name: str, / ) -> bool:
    ''' Returns whether name is framework-owned or stdlib machinery. '''
    return (
        name.startswith( _framework_names_prefix )
        or name in _classes.abc_class_mutables )
