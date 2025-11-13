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
   |                                                                          |
   +--------------------------------------------------------------------------+


*******************************************************************************
System Overview
*******************************************************************************

Classcore is a foundational library for creating classes with customized
behaviors, particularly immutability and concealment. The library operates at
the metaclass level to provide composable, inheritable behaviors while
maintaining compatibility with standard Python features like dataclasses and
protocols.

Architectural Goals
===============================================================================

**Composability**
   Enable incremental addition of class behaviors through decorators,
   metaclasses, and inheritance without conflicts or unexpected interactions.

**Transparency**
   Work seamlessly with existing Python features (dataclasses, protocols,
   ABCs) and tools (type checkers, IDEs).

**Customizability**
   Provide extension points at every layer for users to adapt behaviors to
   specific needs through verifiers, hooks, and core function replacements.

**Performance**
   Minimize runtime overhead through strategic caching and lazy evaluation
   while centralizing import costs at package initialization.

High-Level Architecture
===============================================================================

The system follows a layered architecture with clear separation of concerns:

Core Factory Layer
-------------------------------------------------------------------------------

Location: ``sources/classcore/factories.py``

Produces metaclass components with customizable hooks:

- ``produce_class_constructor``: Creates ``__new__`` implementations with
  preprocessor and postprocessor hooks
- ``produce_class_initializer``: Creates ``__init__`` implementations with
  completer hooks

These factories enable the construction of metaclasses that can intercept and
augment class creation at multiple lifecycle points.

Decorator Layer
-------------------------------------------------------------------------------

Location: ``sources/classcore/decorators.py``

Manages class decoration and replacement:

- ``apply_decorators``: Applies decorator sequences while handling class
  replacements
- ``decoration_by``: Composes multiple decorators with preparation hooks
- ``produce_class_construction_decorator``: Wraps constructor logic into
  metaclass ``__new__``
- ``produce_class_initialization_decorator``: Wraps initializer logic into
  metaclass ``__init__``

Critical feature: Repairs class closures when decorators replace classes
(e.g., ``dataclass(slots=True)``), ensuring ``super()`` continues to function
correctly.

Behavior Layer
-------------------------------------------------------------------------------

Location: ``sources/classcore/standard/behaviors.py``

Implements immutability and concealment enforcement:

- Attribute assignment control with selective mutability
- Attribute deletion control
- Attribute visibility filtering for ``dir()``
- Verifier system supporting names, regexes, and predicates

The verifier system allows fine-grained control: specify mutable attributes by
name, pattern, or custom predicate functions.

Standard Layer
-------------------------------------------------------------------------------

Location: ``sources/classcore/standard/``

Pre-configured implementations for common use cases:

**Base Classes:**
- ``Object``: Standard class with immutability and concealment
- ``DataclassObject``: Automatic dataclass conversion with standard behaviors
- ``ProtocolObject``: Protocol class with immutability and concealment
- Variants for selective mutability (``ObjectMutable``, etc.)

**Metaclasses:**
- ``Class``: Metaclass for standard classes
- ``Dataclass``: Metaclass that auto-applies dataclass decorator
- ``Protocol``: Metaclass for protocol classes
- Mutable variants of each

**Decorators:**
- ``class_with_standard_behaviors``: Add behaviors to existing classes
- ``dataclass_with_standard_behaviors``: Dataclass creation with behaviors
- ``protocol_with_standard_behaviors``: Protocol creation with behaviors

**Module Utilities:**
- ``reclassify_module``: Apply immutability and concealment to module objects
- ``finalize_module``: Complete module initialization with standard behaviors

Utility Layer
-------------------------------------------------------------------------------

Location: ``sources/classcore/utilities.py``

Provides essential operations for metaclass machinery:

- ``mangle_name``: Creates unique attribute names using SHA-256 hashing to
  avoid inheritance collisions
- ``getattr0/setattr0/delattr0``: Access mangled attributes while respecting
  ``__slots__``
- ``repair_class_reproduction``: Fixes closure cells when decorators replace
  classes (CPython/PyPy-specific)
- ``describe_object``: Generates human-readable object descriptions for error
  messages

Data Flow
===============================================================================

Class Creation Flow
-------------------------------------------------------------------------------

1. User defines class with standard metaclass or inherits from standard base
2. Metaclass ``__new__`` invoked via ``produce_class_constructor``
3. Preprocessors modify bases, namespace, arguments, decorators
4. Superclass ``__new__`` creates initial class object
5. Progress flag prevents recursive processing
6. Postprocessors execute (e.g., adding behavior configurations)
7. Decorators applied via ``apply_decorators``
8. If decorator replaces class, closures repaired
9. Metaclass ``__init__`` invoked via ``produce_class_initializer``
10. Completers execute (e.g., freezing behaviors)
11. Progress flag cleared
12. Fully initialized class returned

Attribute Access Flow (Instances)
-------------------------------------------------------------------------------

**Assignment (``obj.attr = value``):**
1. ``__setattr__`` intercepted by assigner core function
2. Check for immutability behavior flag
3. If immutable, verify against mutables (names, regexes, predicates)
4. If allowed, delegate to ligation (super or core override)
5. If denied, raise ``AttributeImmutability`` error

**Visibility (``dir(obj)``):**
1. ``__dir__`` intercepted by surveyor core function
2. Collect all attributes from object and class hierarchy
3. Check visibility verifiers (names, regexes, predicates)
4. Filter attributes based on verifiers
5. Return filtered set

Key Architectural Patterns
===============================================================================

Factory Pattern
-------------------------------------------------------------------------------

Metaclass components are produced by factory functions rather than fixed
inheritance hierarchies. This enables composition of behaviors and runtime
customization of class creation logic.

Decorator Composition
-------------------------------------------------------------------------------

Multiple decorators can be applied in sequence, with automatic handling of
class replacements. The ``decoration_by`` function enables declarative
composition of decorator stacks.

Hook-Based Extension
-------------------------------------------------------------------------------

Every critical point in the class lifecycle offers hooks:

- Preprocessors: Modify class construction inputs
- Postprocessors: Augment constructed classes
- Completers: Finalize initialized classes
- Preparers: Adjust decorator lists before application

Verifier Pattern
-------------------------------------------------------------------------------

Behavior exclusions (mutability, visibility) use a uniform verifier interface:

- Literal ``'*'``: Allow all
- Sequence of strings: Exact name matches
- Sequence of ``re.Pattern``: Regex matches
- Sequence of callables: Predicate functions

This provides flexible, user-customizable behavior rules.

Core Function Replacement
-------------------------------------------------------------------------------

Critical behaviors (assignment, deletion, visibility) can be replaced entirely
by providing alternative "core" functions. This enables deep customization
without subclassing.

Integration Points
===============================================================================

Dataclasses
-------------------------------------------------------------------------------

Standard metaclasses automatically apply ``dataclasses.dataclass`` during
class construction, with configurability for ``frozen``, ``slots``, etc. The
decorator application system ensures proper handling of the class replacement
that occurs with ``slots=True``.

Protocols
-------------------------------------------------------------------------------

Standard protocol classes combine ``typing.Protocol`` with immutability and
concealment. Special handling for ABC-related mutable attributes
(``_abc_cache``, ``_abc_registry``, etc.) ensures protocol functionality.

Type Checkers
-------------------------------------------------------------------------------

Metaclasses use ``@dataclass_transform`` decorator to signal dataclass
behavior to type checkers. This enables proper type inference and checking
for classes produced by standard metaclasses.

Module Objects
-------------------------------------------------------------------------------

Module reclassification applies class-level behaviors to module objects,
enabling immutable, concealed module namespaces for API control.

Dependencies
===============================================================================

External Dependencies
-------------------------------------------------------------------------------

The library depends on standard library modules only:

- ``dataclasses``: Automatic dataclass generation
- ``functools``: Decorator utilities and partials
- ``hashlib``: Attribute name mangling (SHA-256)
- ``inspect``: Class and function introspection
- ``platform``: Python implementation detection for platform-specific repairs
- ``re``: Regular expression support for verifiers
- ``typing``: Type hints and protocol support
- ``collections.abc``: Abstract base classes

Internal Dependencies
-------------------------------------------------------------------------------

- ``dynadoc``: Documentation generation with fragment interpolation
- ``frigid``: Immutable data structures for internal use
- ``falsifier``: Base classes for falsey objects

Extension Points
===============================================================================

Users can extend the library at multiple levels:

**Decorator Level**
   Create custom class decorators and compose with ``decoration_by``.

**Metaclass Level**
   Build custom metaclasses using factory functions with custom hooks.

**Behavior Level**
   Replace core functions for assignment, deletion, visibility, or error
   provision.

**Verifier Level**
   Implement custom predicate functions for mutability/visibility rules.

**Hook Level**
   Provide preprocessors, postprocessors, completers, or preparers for
   lifecycle customization.