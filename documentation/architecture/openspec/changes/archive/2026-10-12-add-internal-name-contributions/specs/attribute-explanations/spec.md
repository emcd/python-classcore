## MODIFIED Requirements

### Requirement: Internal Attribute Marking

Explanations MUST mark attributes as internal according to
internal-name contributions carried by the machinery that constructed
the target: classcore's factory wiring contributes its framework-name
detector, the abstract-base wiring contributes the stdlib ABC machinery
set, and downstream factory-produced metaclasses contribute detectors
from their attribute namers. Contributions MUST be discovered by
consulting the target's metaclass method resolution order; a class
whose metaclass chain carries no matching contribution MUST NOT mark
the name, even when the name resembles a framework or machinery name.
The `_dynadoc_fragments_` attribute is a public declaration convention
and MUST NOT be marked internal.

#### Scenario: Framework-internal attribute
- **WHEN** the explained name matches the classcore detector carried by
  the target's metaclass chain
- **THEN** the explanation MUST be marked internal

#### Scenario: Downstream framework attribute
- **WHEN** the target's metaclass was produced by a downstream factory
  whose namer contributes a detector, and the explained name matches
  that detector
- **THEN** the explanation MUST be marked internal

#### Scenario: Machinery name without machinery
- **WHEN** a class whose metaclass chain lacks the abstract-base
  contribution defines an attribute named like stdlib ABC machinery
- **THEN** the explanation MUST NOT mark the name internal

#### Scenario: Inherited contribution across packages
- **WHEN** a class defined in one package derives from a base whose
  metaclass carries a framework contribution
- **THEN** the explanation MUST apply that contribution to the derived
  class

#### Scenario: Instance target consults metaclass chain
- **WHEN** an instance target is explained and a contribution is
  carried by the metaclass chain of the instance's type — discovered
  through the metaclass MRO, not the class MRO of the instance's type
- **THEN** the explanation MUST apply that contribution

#### Scenario: Shape-invalid lookalike
- **WHEN** an explained name shares a framework's prefix but fails the
  grammar the framework's detector requires — a core outside the
  framework's enumerated vocabulary (e.g.
  `_classcore_not_a_generated_core_`), or a mangled form with a
  malformed digest (wrong length, uppercase characters, or trailing
  underscore)
- **THEN** the explanation MUST NOT mark the name internal

#### Scenario: Declaration convention
- **WHEN** the explained name is `_dynadoc_fragments_`
- **THEN** the explanation MUST NOT mark the name internal

#### Scenario: User attribute
- **WHEN** the explained name matches no contribution in the target's
  metaclass chain
- **THEN** the explanation MUST NOT be marked internal
