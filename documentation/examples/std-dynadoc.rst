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
Dynadoc Integration
*******************************************************************************


Introduction
===============================================================================

Seamless integration with Dynadoc is provided to automate documentation of
classes and their members. This integration allows you to configure Dynadoc
behavior at both the metaclass and individual class levels, ensuring that your
classes receive appropriate documentation based on their structure and
annotations.

.. doctest:: Dynadoc.Integration

    >>> from typing import Annotated
    >>> import classcore.standard as ccstd
    >>> import dynadoc


Basic Configuration
===============================================================================

Dynadoc configuration can be applied to classes through the standard Classcore
metaclasses. The configuration controls how documentation is generated,
including which objects to introspect and how to render the results.

.. doctest:: Dynadoc.Integration

    >>> class Person( ccstd.DataclassObject ):
    ...     ''' A person with basic information. '''
    ...     name: Annotated[ str, dynadoc.Doc( "Full name of the person" ) ]
    ...     age: Annotated[ int, dynadoc.Doc( "Age in years" ) ]
    ...     email: Annotated[ str | None, dynadoc.Doc( "Email address if available" ) ] = None
    ...
    >>> print( Person.__doc__ )
    A person with basic information.
    <BLANKLINE>
    :ivar name: Full name of the person
    :vartype name: str
    :ivar age: Age in years
    :vartype age: int
    :ivar email: Email address if available
    :vartype email: str | None

The documentation is automatically enhanced with parameter information derived
from the dataclass fields and their type annotations.


Metaclass-Level Configuration
===============================================================================

You can configure Dynadoc behavior for all classes created with a particular
metaclass by setting configuration attributes directly on the metaclass:

.. doctest:: Dynadoc.Integration

    >>> # Create a custom metaclass with specific Dynadoc settings
    >>> @ccstd.class_factory(
    ...     dynadoc_configuration = ccstd.dynadoc.produce_dynadoc_configuration(
    ...         preserve = False  # Don't preserve existing docstrings
    ...     )
    ... )
    ... class CustomClass( type ): pass
    ...
    >>> class Calculator( metaclass = CustomClass ):
    ...     ''' Original calculator docstring. '''
    ...     def add(
    ...         self,
    ...         x: Annotated[ float, dynadoc.Doc( "First number" ) ],
    ...         y: Annotated[ float, dynadoc.Doc( "Second number" ) ]
    ...     ) -> Annotated[ float, dynadoc.Doc( "Sum of x and y" ) ]:
    ...         ''' Add two numbers. '''
    ...         return x + y
    ...     def multiply(
    ...         self,
    ...         x: Annotated[ float, dynadoc.Doc( "First number" ) ],
    ...         y: Annotated[ float, dynadoc.Doc( "Second number" ) ]
    ...     ) -> Annotated[ float, dynadoc.Doc( "Product of x and y" ) ]:
    ...         ''' Multiply two numbers. '''
    ...         return x * y
    ...
    >>> print( Calculator.__doc__ )
    None

.. code-block:: text

    >>> print( Calculator.add.__doc__ )
    Add two numbers.

    :argument self:
    :argument x: First number
    :type x: float
    :argument y: Second number
    :type y: float
    :returns: Sum of x and y
    :rtype: float

.. code-block:: text

    >>> print( Calculator.multiply.__doc__ )
    Multiply two numbers.

    :argument self:
    :argument x: First number
    :type x: float
    :argument y: Second number
    :type y: float
    :returns: Product of x and y
    :rtype: float

Notice how the original class docstring was completely replaced (due to
``preserve: False``) and is now ``None``, while the individual method
docstrings were enhanced with parameter and return type documentation from
their annotations.


Class-Level Configuration
===============================================================================

Individual classes can override metaclass defaults by providing their own
Dynadoc configuration as a ``class`` statement argument:

.. doctest:: Dynadoc.Integration

    >>> class Vehicle(
    ...     ccstd.DataclassObject,
    ...     dynadoc_configuration = {
    ...         'preserve': True,
    ...         'introspection': ccstd.dynadoc.produce_dynadoc_introspection_control(
    ...             enable = False  # Disable automatic introspection
    ...         )
    ...     }
    ... ):
    ...     ''' A vehicle with make and model information.
    ...
    ...         This class represents various types of vehicles.
    ...     '''
    ...     make: Annotated[ str, dynadoc.Doc( "Vehicle manufacturer" ) ]
    ...     model: Annotated[ str, dynadoc.Doc( "Vehicle model name" ) ]
    ...     year: Annotated[ int, dynadoc.Doc( "Year of manufacture" ) ]
    ...
    >>> print( Vehicle.__doc__ )
    A vehicle with make and model information.
    <BLANKLINE>
    This class represents various types of vehicles.

Since introspection was disabled, only the original docstring is preserved
without any automatic parameter documentation.


Documentation of Modules
===============================================================================

A variation of ``assign_module_docstring`` is provided, which respects
immutable classes. This function is used by this package, itself, to
automatically generate documentation for its own modules:

.. code-block:: python

    from . import standard

    # ... other imports and definitions ...

    standard.dynadoc.assign_module_docstring( __name__, table = __.fragments )
    standard.reclassify_modules( __name__, recursive = True )

This automatically generates comprehensive documentation for the entire
package, including all submodules. The key benefits of this variation include:

* **Automatic immutable class avoidance**: By default, immutable classes are not
  introspected during documentation generation to prevent potential issues.

* **Recursive package documentation**: When applied to a package, it can
  recursively document all submodules.

* **Fragment table integration**: Supports reusable documentation fragments
  for consistent terminology across the package.

You can apply this to your own modules and packages:

.. code-block:: python

    import classcore.standard as ccstd

    # At the end of your module's __init__.py
    ccstd.dynadoc.assign_module_docstring( __name__ )

    # Optionally make the entire package immutable
    ccstd.reclassify_modules( __name__, recursive = True )
