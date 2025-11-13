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
Product Requirements Document
*******************************************************************************

Product Vision
===============================================================================

Classcore provides foundational class factories and decorators for Python
developers who need to create classes with immutable and concealed attributes.
The library enables safer, more maintainable code by making immutability and
API control first-class features that integrate seamlessly with standard Python
constructs like dataclasses and protocols.

Target Audience
===============================================================================

Primary Users
-------------------------------------------------------------------------------

**Library Authors**
   Developers creating reusable packages who want to provide stable APIs with
   controlled modification and clear public interfaces.

**Application Developers**
   Engineers building systems that benefit from immutable data structures and
   controlled state management (configuration objects, DTOs, domain models).

**Framework Developers**
   Authors of frameworks and plugin systems who need controlled extension
   points and stable interfaces.

Secondary Users
-------------------------------------------------------------------------------

**Data Scientists**
   Practitioners working with immutable data pipelines and reproducible
   analysis workflows.

**API Designers**
   Architects defining service interfaces and contracts with strict stability
   guarantees.

Core Requirements
===============================================================================

FR-1: Attribute Immutability
-------------------------------------------------------------------------------

**Requirement**
   Provide mechanisms to make class and instance attributes immutable after
   initialization.

**Rationale**
   Immutability prevents accidental state modification, reduces bugs, and
   enables safer concurrent access.

**Acceptance Criteria**

- Classes produced by standard metaclasses have immutable attributes
- Instances of standard classes have immutable attributes
- Immutability applies after ``__init__`` and ``__post_init__`` complete
- Attempting to modify immutable attributes raises ``AttributeImmutability``
- Attempting to delete immutable attributes raises ``AttributeImmutability``

FR-2: Selective Mutability
-------------------------------------------------------------------------------

**Requirement**
   Allow users to specify exceptions to immutability rules using names,
   regexes, or custom predicates.

**Rationale**
   Some attributes (cache values, internal state) need mutability while
   maintaining immutability for public API attributes.

**Acceptance Criteria**

- Support ``class_mutables`` argument for class-level selective mutability
- Support ``instances_mutables`` argument for instance-level selective
  mutability
- Accept attribute names as strings for exact matches
- Accept compiled regex patterns for pattern-based matching
- Accept predicate functions for custom matching logic
- Support literal ``'*'`` to disable immutability entirely
- Mutability verifiers are inherited and composable

FR-3: Attribute Concealment
-------------------------------------------------------------------------------

**Requirement**
   Provide mechanisms to conceal non-public attributes from ``dir()`` output.

**Rationale**
   Reduces API noise, makes documentation cleaner, and clearly communicates
   public interfaces.

**Acceptance Criteria**

- By default, only public attributes (not starting with ``_``) visible in
  ``dir()``
- Non-public attributes remain accessible but concealed from introspection
- Concealment applies to both classes and instances
- Users can customize visibility via ``class_visibles`` and
  ``instances_visibles``
- Visibility verifiers support names, regexes, and predicates
- Literal ``'*'`` provides full visibility (Python default)

FR-4: Dataclass Integration
-------------------------------------------------------------------------------

**Requirement**
   Automatically convert classes to dataclasses while applying immutability and
   concealment.

**Rationale**
   Dataclasses are widely used for data containers. Integration should be
   seamless and preserve all dataclass functionality.

**Acceptance Criteria**

- ``Dataclass`` metaclass auto-applies ``@dataclass`` decorator
- ``DataclassObject`` base class produces dataclass with standard behaviors
- ``dataclass_with_standard_behaviors`` decorator creates dataclass with
  behaviors
- ``__post_init__`` can modify attributes before immutability enforced
- Compatible with ``dataclass`` arguments (``frozen``, ``slots``, ``kw_only``,
  etc.)
- Proper handling of class replacement when ``slots=True``
- Type checkers recognize classes as dataclasses via ``@dataclass_transform``

FR-5: Protocol Support
-------------------------------------------------------------------------------

**Requirement**
   Provide protocol classes with immutability and concealment that work with
   structural subtyping.

**Rationale**
   Protocols enable structural typing. Immutable protocols provide type-safe
   interfaces with guaranteed stability.

**Acceptance Criteria**

- ``Protocol`` metaclass combines ``typing.Protocol`` with standard behaviors
- ``ProtocolObject`` base class for protocol definitions
- ``protocol_with_standard_behaviors`` decorator for existing protocols
- Protocol functionality preserved (structural subtyping, runtime checks)
- ABC-related mutable attributes (``_abc_cache``, ``_abc_registry``) allowed
  by default
- Immutability and concealment inherited by protocol implementations

FR-6: Module Reclassification
-------------------------------------------------------------------------------

**Requirement**
   Apply immutability and concealment to module objects to protect module
   namespaces.

**Rationale**
   Module attributes can be accidentally modified. Reclassification provides
   package-level API control.

**Acceptance Criteria**

- ``reclassify_module`` function applies behaviors to single module
- ``finalize_module`` applies behaviors and dynadoc configuration
- Support for recursive application to submodules
- Module attributes become immutable after reclassification
- Non-public module attributes concealed from ``dir()``
- Public module API clearly defined through visibility

FR-7: Extensibility
-------------------------------------------------------------------------------

**Requirement**
   Provide hooks and factory functions for users to create custom behaviors and
   metaclasses.

**Rationale**
   Different use cases require different behaviors. Core machinery should be
   reusable for custom implementations.

**Acceptance Criteria**

- Factory functions for creating custom metaclasses
- Hook system for class construction (preprocessors, postprocessors)
- Hook system for class initialization (completers)
- Hook system for decoration (preparers)
- Core function replacement (assigner, deleter, surveyor)
- Custom error class provider support
- Composition of decorators via ``decoration_by``

FR-8: Type Checker Compatibility
-------------------------------------------------------------------------------

**Requirement**
   Ensure classes produced by classcore are fully compatible with static type
   checkers.

**Rationale**
   Type checking is essential for modern Python development. Library must not
   interfere with type inference.

**Acceptance Criteria**

- All public APIs have complete type annotations
- Metaclasses use ``@dataclass_transform`` for dataclass type checking
- Generic type variables properly constrained
- ``py.typed`` marker included in package
- Pyright strict mode compliance
- No type checker warnings for standard usage patterns

FR-9: Python Implementation Compatibility
-------------------------------------------------------------------------------

**Requirement**
   Support multiple Python implementations with graceful degradation for
   implementation-specific features.

**Rationale**
   Users may deploy on CPython, PyPy, or other implementations. Core
   functionality should work everywhere.

**Acceptance Criteria**

- Core functionality works on CPython 3.10+
- Core functionality works on PyPy 3.10+
- Platform-specific optimizations (closure repair) detected and applied
- No ``exec``, ``eval``, or ``ctypes`` usage
- Rely only on documented Python data model
- Comprehensive test coverage across implementations

Non-Functional Requirements
===============================================================================

Performance
-------------------------------------------------------------------------------

- Metaclass overhead should be negligible for typical use cases
- Import costs centralized to package initialization
- Attribute access overhead minimal (single method call)
- No unnecessary object allocations in hot paths

Compatibility
-------------------------------------------------------------------------------

- Support Python 3.10+ on CPython
- Support Python 3.10+ on PyPy
- Compatible with major type checkers (Pyright, mypy)
- No breaking changes within major version

Maintainability
-------------------------------------------------------------------------------

- Comprehensive test coverage (>95%)
- Clear documentation for all public APIs
- Examples for common use cases
- Architecture documentation for contributors

Usability
-------------------------------------------------------------------------------

- Clear error messages with actionable information
- Consistent API across classes, decorators, and metaclasses
- Minimal boilerplate for common cases
- Type hints for IDE autocompletion