.. vim: set fileencoding=utf-8:
.. -*- coding: utf-8 -*-
.. +--------------------------------------------------------------------------+
   |                                                                          |
   | Licensed under the Apache License, Version 2.0 (the "License");          |
   | you may not use this file except in compliance with the License.         |
   | You may obtain a copy of the License at                                  |
   |                                                                          |
   |     http://www.apache.org/licenses/LICENSE-2.0                           |
   |                                                                          |
   | Unless required by applicable law or agreed to in writing, software      |
   | distributed under the License is distributed on an "AS IS" BASIS,        |
   | WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. |
   | See the License for the specific language governing permissions and      |
   | limitations under the License.                                           |
   +--------------------------------------------------------------------------+


*******************************************************************************
Attribute Explanations
*******************************************************************************

The :py:func:`classcore.standard.explain_attribute` function explains why an
attribute of a class or an instance is mutable or immutable and visible or
concealed. It returns an explanation record which carries, for each operation
— assignment, deletion, and survey — a verdict with the rule which decided
the outcome. Explanations are observational: they neither bypass nor alter the
behaviors they describe.

.. doctest:: Standard.Explanations

    >>> import classcore.standard as ccstd


Explaining Immutability
===============================================================================

Consider a decorated class with selective mutability. Explaining an excluded
attribute name reports the permitting rule with its kind and detail text.

.. doctest:: Standard.Explanations

    >>> @ccstd.with_standard_behaviors( mutables = ( 'count', ) )
    ... class Counter:
    ...     count: int = 0
    ...
    >>> explanation = ccstd.explain_attribute( Counter( ), 'count' )
    >>> assign = explanation.operations[ 'assign' ]
    >>> assign.permitted
    True
    >>> assign.decider.kind
    'names'
    >>> assign.decider.detail
    'count'

Explaining a non-excluded attribute reports that immutability forbids the
operation and no rule decided otherwise.

.. doctest:: Standard.Explanations

    >>> explanation = ccstd.explain_attribute( Counter( ), 'total' )
    >>> assign = explanation.operations[ 'assign' ]
    >>> assign.permitted
    False
    >>> assign.decider is None
    True


Explaining Concealment
===============================================================================

Concealment verdicts follow union semantics: every matching visibility rule
appears in the survey verdict, in evaluation order.

.. doctest:: Standard.Explanations

    >>> import re
    >>> @ccstd.with_standard_behaviors(
    ...     visibles = ( re.compile( 'pub.*' ), ) )
    ... class Ledger:
    ...     public_total = 1
    ...     _secret = 2
    ...
    >>> explanation = ccstd.explain_attribute( Ledger( ), 'public_total' )
    >>> survey = explanation.operations[ 'survey' ]
    >>> survey.permitted
    True
    >>> [ rule.kind for rule in survey.matched ]
    ['regex']
    >>> survey.matched[ 0 ].detail
    'pub.*'

    >>> explanation = ccstd.explain_attribute( Ledger( ), '_secret' )
    >>> explanation.operations[ 'survey' ].permitted
    False


Internal Attributes
===============================================================================

Framework-owned attribute names and standard library machinery names are
marked as internal.

.. doctest:: Standard.Explanations

    >>> explanation = ccstd.explain_attribute( Ledger( ), '_abc_cache' )
    >>> explanation.internal
    True
    >>> explanation = ccstd.explain_attribute( Ledger( ), 'public_total' )
    >>> explanation.internal
    False


Record Immutability
===============================================================================

Explanation records are themselves immutable, including every nested
collection.

.. doctest:: Standard.Explanations

    >>> explanation = ccstd.explain_attribute( Ledger( ), 'public_total' )
    >>> explanation.name = 'other'
    Traceback (most recent call last):
        ...
    classcore.exceptions.AttributeImmutability: Could not assign or delete attribute 'name' on instance of class 'classcore.standard.explanations.AttributeExplanation'.


Summaries
===============================================================================

The explanation record renders a human-readable summary of the whole
decision trace, so digging through attributes and mappings is only
necessary for programmatic use.

.. doctest:: Standard.Explanations

    >>> print( ccstd.explain_attribute( Ledger( ), 'public_total' ) )
    'public_total' on instance of class '...Ledger'
    behaviors: concealment, immutability (instance)
    assign: forbidden (no permitting rule)
    delete: forbidden (no permitting rule)
    survey: visible via regex 'pub.*'
