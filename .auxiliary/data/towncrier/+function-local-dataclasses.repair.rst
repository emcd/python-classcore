Fix construction of function-local dataclass classes. Classes derived
from the dataclass base classes (``DataclassObject``,
``DataclassObjectMutable``, ``DataclassProtocol``, and
``DataclassProtocolMutable``) failed with ``TypeError`` when defined
inside a function body, because the construction marker could not be
recognized during dataclass slot reproduction.
