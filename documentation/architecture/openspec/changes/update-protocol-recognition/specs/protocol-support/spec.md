## MODIFIED Requirements

### Requirement: Protocol Metaclass

The protocol metaclasses MUST combine `typing.Protocol` with standard
behaviors and MUST form a proper inheritance hierarchy.

#### Scenario: Protocol class creation
- **WHEN** a class uses a protocol metaclass
- **THEN** the resulting class MUST support structural subtyping with
  immutability and concealment

#### Scenario: Metaclass hierarchy
- **WHEN** `ProtocolDataclass` and `ProtocolDataclassMutable` are inspected
- **THEN** `ProtocolDataclass` MUST be a subclass of `ProtocolClass`
- **AND** `ProtocolDataclassMutable` MUST be a subclass of `ProtocolDataclass`

#### Scenario: Cross-metaclass inheritance
- **WHEN** a class inherits from bases backed by different protocol
  metaclasses (e.g., `Protocol` and `DataclassProtocol`)
- **THEN** class creation MUST succeed without `TypeError: metaclass conflict`

#### Scenario: Dataclass transform preservation
- **WHEN** `ProtocolDataclassMutable` inherits from `ProtocolDataclass`
- **THEN** `ProtocolDataclassMutable.__dataclass_transform__` MUST have
  `frozen_default = False`
- **AND** the value MUST be in `ProtocolDataclassMutable.__dict__`, not
  inherited from `ProtocolDataclass`

## ADDED Requirements

### Requirement: Runtime Protocol Recognition

Direct subclasses of classcore protocol base classes MUST be recognized as
protocols at runtime. The `_is_protocol` attribute MUST be set to `True` on
classes that directly inherit from a classcore protocol base class
(`Protocol`, `ProtocolMutable`, `DataclassProtocol`,
`DataclassProtocolMutable`). Concrete implementation subclasses (subclasses
of a protocol that do not include a protocol base class in their own
`__bases__`) MUST have `_is_protocol` set to `False`, matching standard
`typing.Protocol` semantics.

#### Scenario: Direct subclass recognized as protocol
- **WHEN** a class directly inherits from a classcore protocol base class
- **THEN** `cls._is_protocol` MUST be `True`

#### Scenario: Concrete implementation not recognized as protocol
- **WHEN** a class inherits from a protocol subclass without including a
  protocol base class in its own `__bases__`
- **THEN** `cls._is_protocol` MUST be `False`

#### Scenario: Runtime checkable application
- **WHEN** `typing.runtime_checkable` is applied to a classcore protocol
  subclass via the `decorators=` metaclass argument
- **THEN** the application MUST succeed without `TypeError`
- **AND** `cls._is_runtime_protocol` MUST be `True`

#### Scenario: Runtime structural subtyping
- **WHEN** a classcore protocol is decorated with `@runtime_checkable`
- **AND** a candidate object implements all protocol methods
- **THEN** `isinstance(candidate, protocol)` MUST return `True`

#### Scenario: Protocol attributes collection
- **WHEN** a classcore protocol subclass is created
- **THEN** `cls.__protocol_attrs__` MUST contain the protocol's attribute names
