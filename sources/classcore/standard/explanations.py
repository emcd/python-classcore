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
from . import decorators as _decorators
from . import nomina as _nomina


_framework_names_prefix = '_classcore_'


@_decorators.dataclass_with_standard_behaviors( )
class Decision:
    ''' Decision which one operation reached for one attribute.

        The decision subclasses form a closed hierarchy; the decision
        type is the discriminant. Verdict permissibility is derived
        from the decision type.
    '''


@_decorators.dataclass_with_standard_behaviors( )
class PermitByInapplicability( Decision ):
    ''' Permission because the governing behavior is inactive. '''


@_decorators.dataclass_with_standard_behaviors( )
class PermitByOmni( Decision ):
    ''' Permission by the omni marker, which permits every name. '''


@_decorators.dataclass_with_standard_behaviors( )
class PermitByNames( Decision ):
    ''' Permission by exclusion names membership. '''
    name: str


@_decorators.dataclass_with_standard_behaviors( )
class PermitByPredicate( Decision ):
    ''' Permission by an exclusion predicate. '''
    predicate: str


@_decorators.dataclass_with_standard_behaviors( )
class PermitByRegex( Decision ):
    ''' Permission by an exclusion regex. '''
    pattern: str


@_decorators.dataclass_with_standard_behaviors( )
class Prohibit( Decision ):
    ''' Prohibition: the behavior is active and no rule permits. '''


@_decorators.dataclass_with_standard_behaviors( )
class Verdict:
    ''' Verdict for one operation on one attribute. '''
    operation: str
    decision: Decision

    @property
    def permissible( self ) -> bool:
        ''' Returns whether the operation is permissible. '''
        return not isinstance( self.decision, Prohibit )


@_decorators.dataclass_with_standard_behaviors( )
class AssignVerdict( Verdict ):
    ''' Verdict for attribute assignment. '''


@_decorators.dataclass_with_standard_behaviors( )
class DeleteVerdict( Verdict ):
    ''' Verdict for attribute deletion. '''


@_decorators.dataclass_with_standard_behaviors( )
class SurveyVerdict( Verdict ):
    ''' Verdict for attribute visibility in survey results. '''


@_decorators.dataclass_with_standard_behaviors( )
class AttributeExplanation:
    ''' Decision trace for one attribute of one target. '''
    target: str
    name: str
    behaviors: __.cabc.Mapping[ str, __.cabc.Set[ str ] ]
    operations: __.cabc.Mapping[ str, Verdict ]
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
            lines.append( f"{operation}: {self._render( verdict.decision )}" )
        return '\n'.join( lines )

    def _render( self, decision: Decision, / ) -> str:
        if isinstance( decision, PermitByInapplicability ):
            return 'permitted (behavior inapplicable)'
        if isinstance( decision, PermitByOmni ):
            return "permitted by omni '*'"
        if isinstance( decision, PermitByNames ):
            return f"permitted by names {decision.name!r}"
        if isinstance( decision, PermitByPredicate ):
            return f"permitted by predicate {decision.predicate!r}"
        if isinstance( decision, PermitByRegex ):
            return f"permitted by regex {decision.pattern!r}"
        if isinstance( decision, Prohibit ):
            return 'prohibited (no permitting rule)'
        raise ValueError( type( decision ) )


def explain_attribute(
    target: object, name: str, /, *,
    attributes_namer: _nomina.AttributesNamer = __.calculate_attrname,
) -> AttributeExplanation:
    ''' Returns decision trace for attribute name on target.

        All operations follow precedence semantics: omni, then names
        membership, then the first matching predicate, then the first
        matching regex; prohibition when the governing behavior is
        active and nothing permits; permission by inapplicability when
        the behavior is inactive. For class targets, the classes-level
        configuration is evaluated; for instance targets, the
        instances-level configuration is evaluated against the
        instance's class hierarchy — matching the levels the behavior
        cores evaluate. Records report the normalized level names
        ('class' and 'instance') at which behaviors and exclusion
        configuration were found. Explanations are observational: they
        neither bypass nor alter concealment or immutability.

        Survey explanations describe normalized first-match semantics;
        the survey core's current once-per-matching-rule duplication is
        characterized as a defect whose repair is deferred separately.
    '''
    class_target = __.inspect.isclass( target )
    level = 'class' if class_target else 'instances'
    level_normalized = 'class' if class_target else 'instance'
    behaviors = _behaviors.survey_active_behaviors(
        target, attributes_namer = attributes_namer, level = level )
    immutability = _nomina.immutability_label in behaviors
    concealment = _nomina.concealment_label in behaviors
    operations: dict[ str, Verdict ] = { }
    for operation, verdict_class, basename, active in (
        ( 'assign', AssignVerdict, 'mutables', immutability ),
        ( 'delete', DeleteVerdict, 'mutables', immutability ),
        ( 'survey', SurveyVerdict, 'visibles', concealment ),
    ):
        rule = (
            _behaviors.survey_first_permitting_rule(
                target, attributes_namer = attributes_namer,
                level = level, basename = basename, name = name )
            if active else None )
        operations[ operation ] = verdict_class(
            operation = operation,
            decision = produce_decision( rule, active ) )
    return AttributeExplanation(
        target = _utilities.describe_object( target ),
        name = name,
        behaviors = __.types.MappingProxyType(
            { level_normalized: frozenset( behaviors ) } ),
        operations = __.types.MappingProxyType( operations ),
        internal = survey_internal_name( name ) )


def produce_decision(
    rule: __.typx.Optional[ tuple[ str, str ] ], active: bool, /
) -> Decision:
    ''' Returns decision for governing-behavior activity and first rule.

        Rules are the (kind, detail) pairs produced by
        survey_first_permitting_rule; the kind vocabulary matches the
        omni/names/predicate/regex precedence stages.
    '''
    if not active: return PermitByInapplicability( )
    if rule is None: return Prohibit( )
    kind, detail = rule
    if kind == 'omni': return PermitByOmni( )
    if kind == 'names': return PermitByNames( name = detail )
    if kind == 'predicate': return PermitByPredicate( predicate = detail )
    if kind == 'regex': return PermitByRegex( pattern = detail )
    raise ValueError( kind )


def survey_internal_name( name: str, / ) -> bool:
    ''' Returns whether name is framework-owned or stdlib machinery. '''
    return (
        name.startswith( _framework_names_prefix )
        or name in __.abc_class_mutables )
