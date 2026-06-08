# classcore.standard

The `standard` subpackage provides pre-configured implementations of
classcore's behaviors for common use cases. It includes base classes,
metaclasses, decorators, and module utilities that combine immutability and
concealment with standard Python features like dataclasses and protocols.

## Base Classes

### `Object`

Standard class with full immutability and concealment behaviors. Instances
have immutable attributes and concealed internal attributes.

```python
from classcore.standard import Object

class Point(Object):
    x: float
    y: float
```

### `DataclassObject`

Automatic dataclass conversion with standard behaviors. Unlike
`dataclass(frozen=True)`, attributes can still be manipulated via
`__post_init__`.

```python
from dataclasses import field
from math import sqrt
from classcore.standard import DataclassObject

class Point2d(DataclassObject):
    x: float
    y: float
    hypotenuse: float = field(init=False)
    def __post_init__(self) -> None:
        x, y = self.x, self.y
        self.hypotenuse = sqrt(x*x + y*y)
```

### `ProtocolObject`

Protocol class with immutability and concealment. Combines `typing.Protocol`
with standard behaviors. Immutability and concealment are inherited by
subclassed implementations.

### Mutable Variants

- `ObjectMutable`: Object with concealment only (no immutability)
- `DataclassObjectMutable`: DataclassObject with concealment only
- `ProtocolObjectMutable`: ProtocolObject with concealment only

## Metaclasses

### `Class`

Metaclass for standard classes. Provides immutability and concealment to
any class that uses this metaclass.

### `Dataclass`

Metaclass that automatically applies `dataclasses.dataclass` during class
construction. Configurable for `frozen`, `slots`, etc.

### `Protocol`

Metaclass for protocol classes. Combines `typing.Protocol` with standard
behaviors.

### Mutable Variants

- `ClassMutable`: Metaclass with concealment only
- `DataclassMutable`: Dataclass metaclass with concealment only
- `ProtocolMutable`: Protocol metaclass with concealment only

## Decorators

### `class_with_standard_behaviors`

Apply standard behaviors to an existing class.

```python
from classcore.standard import class_with_standard_behaviors

@class_with_standard_behaviors()
class ExistingClass:
    x: int = 10
```

### `dataclass_with_standard_behaviors`

Create a dataclass with standard behaviors applied.

```python
from classcore.standard import dataclass_with_standard_behaviors

@dataclass_with_standard_behaviors()
class Point:
    x: float
    y: float
```

### `protocol_with_standard_behaviors`

Create a protocol with standard behaviors applied.

### `class_factory`

Generic factory for creating custom metaclasses with standard behaviors.

## Module Utilities

### `reclassify_module`

Apply immutability and concealment to a single module object.

```python
from classcore.standard import reclassify_module

reclassify_module(__name__)
```

### `finalize_module`

Complete module initialization with standard behaviors. Used internally by
the package to apply behaviors to all subpackage modules.

### `reclassify_modules` (deprecated)

Apply behaviors to entire packages recursively. Deprecated in favor of
`finalize_module` for individual module control.

## Behavior System

### Immutability

Attributes are immutable by default. Assignment attempts raise
`AttributeImmutability`. Deletion attempts raise
`AttributeDeletionImmutability`.

### Concealment

Internal attributes are concealed from `dir()` output. Only public
attributes and explicitly visible attributes are shown.

### Selective Mutability

Specify mutable attributes using verifiers:

- **Names**: Exact string matches
- **Regexes**: Regular expression patterns
- **Predicates**: Custom callable functions

```python
from classcore.standard import ObjectMutableByNames

class Config(ObjectMutableByNames, mutable_names=('debug', 'verbose')):
    debug: bool = False
    verbose: bool = False
    name: str = 'default'
```

### Verifier Interface

Behavior exclusions use a uniform verifier interface:

- Literal `'*'`: Allow all
- Sequence of strings: Exact name matches
- Sequence of `re.Pattern`: Regex matches
- Sequence of callables: Predicate functions

## Integration with Dataclasses

Standard metaclasses automatically apply `dataclasses.dataclass` during
class construction. The decorator application system ensures proper handling
of the class replacement that occurs with `slots=True`.

Key features:
- `__post_init__` can still modify attributes (unlike `frozen=True`)
- Slot classes are properly supported
- Type checkers recognize the dataclass transform

## Integration with Protocols

Standard protocol classes combine `typing.Protocol` with immutability and
concealment. Special handling for ABC-related mutable attributes
(`_abc_cache`, `_abc_registry`, etc.) ensures protocol functionality.

## Import Pattern

The standard subpackage uses the cascading import pattern:

```python
# sources/classcore/standard/__.py
from ..__ import *              # Inherit all parent imports
from ..exceptions import *      # Add package exceptions
```

Modules in `standard/` use the same `__` import pattern as the parent
package, gaining access to both parent and subpackage-specific imports.
