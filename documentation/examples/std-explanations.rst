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

The :py:func:`classcore.standard.explanations.explain_attribute` function explains why an
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
attribute name reports the decision which permitted the operation, with its
payload carried by a typed record.

.. doctest:: Standard.Explanations

    >>> @ccstd.with_standard_behaviors( mutables = ( 'count', ) )
    ... class Counter:
    ...     count: int = 0
    ...
    >>> explanation = ccstd.explain_attribute( Counter( ), 'count' )
    >>> assign = explanation.operations[ 'assign' ]
    >>> assign.permissible
    True
    >>> assign.decision.name
    'count'

Explaining a non-excluded attribute reports that the operation is
prohibited.

.. doctest:: Standard.Explanations

    >>> explanation = ccstd.explain_attribute( Counter( ), 'total' )
    >>> assign = explanation.operations[ 'assign' ]
    >>> assign.permissible
    False
    >>> type( assign.decision ).__name__
    'Prohibit'


Explaining Concealment
===============================================================================

Concealment verdicts follow precedence semantics, like every operation: the
first matching visibility rule decides the survey verdict.

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
    >>> survey.permissible
    True
    >>> survey.decision.pattern
    'pub.*'

    >>> explanation = ccstd.explain_attribute( Ledger( ), '_secret' )
    >>> explanation.operations[ 'survey' ].permissible
    False


Internal Attributes
===============================================================================

Framework attribute names mark as internal wherever the framework's
machinery built the class. Standard library machinery names, like the
ABC caches, mark only where that machinery actually operates — a class
without ABC machinery keeps such a name unmarked.

.. doctest:: Standard.Explanations

    >>> import hashlib
    >>> digest = hashlib.sha256( b'x' ).hexdigest( )
    >>> explanation = ccstd.explain_attribute(
    ...     Ledger( ), f"_classcore_class_in_progress_{digest}" )
    >>> explanation.internal
    True
    >>> explanation = ccstd.explain_attribute( Ledger( ), '_abc_cache' )
    >>> explanation.internal
    False

    >>> class Registry( ccstd.AbstractObject ):
    ...     pass
    ...
    >>> explanation = ccstd.explain_attribute( Registry( ), '_abc_cache' )
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
    'public_total' on instance of class 'builtins.Ledger'
    behaviors: concealment, immutability (instance)
    assign: prohibited (no permitting rule)
    delete: prohibited (no permitting rule)
    survey: permitted by regex 'pub.*'
