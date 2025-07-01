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
Standard Modules
*******************************************************************************


Introduction
===============================================================================

The ``standard.modules`` submodule provides functionality to enhance Python
modules with immutability, concealment, and automatic documentation generation.
This is particularly useful for package authors who want to prevent accidental
modification of their module's public API while providing rich documentation.

The module provides two main approaches:

1. **Module reclassification** - converts standard modules to have immutable 
   and concealed attributes
2. **Module finalization** - combines documentation generation with
   reclassification in a single convenient function


Module Reclassification
===============================================================================

The ``reclassify_modules`` function converts modules to use a custom module
class that provides immutability and concealment behaviors. Here's how you
might use it in a hypothetical package:

.. code-block:: python

    # mypackage/__init__.py
    import classcore.standard as _ccstd
    
    # Import your submodules
    from . import core
    from . import utils
    from . import exceptions
    
    # Apply module reclassification
    _ccstd.reclassify_modules( __name__, recursive = True )

After reclassification, the modules become immutable:

.. code-block:: python

    # This would raise AttributeImmutability exception
    # mypackage.core = "something else"
    
    # Non-public attributes are concealed from dir()
    # dir( mypackage )  # Only shows public attributes

The ``recursive = True`` parameter ensures that all submodules within the
package hierarchy are also reclassified, providing consistent behavior
throughout your package.


Individual Module Reclassification
-------------------------------------------------------------------------------

You can also reclassify individual modules without affecting the entire
package hierarchy:

.. code-block:: python

    # mypackage/core.py
    import classcore.standard as _ccstd
    
    def important_function():
        ''' This function should not be accidentally modified. '''
        return "Important result"
    
    # Reclassify only this module
    _ccstd.reclassify_modules( __name__ )

This approach is useful when you want fine-grained control over which modules
in your package receive the enhanced behaviors.


Module Finalization with Documentation
===============================================================================

The ``finalize_module`` function provides a convenient way to combine automatic
documentation generation (via Dynadoc integration) with module reclassification.
This is the recommended approach for most packages.

Basic Usage
-------------------------------------------------------------------------------

.. code-block:: python

    # mypackage/__init__.py
    import classcore.standard as _ccstd
    
    from . import core
    from . import utils
    from . import exceptions
    
    # Define documentation fragments
    _fragments = {
        'version': '1.0.0',
        'author': 'Your Name',
        'description': 'A utility package for data processing'
    }
    
    # Finalize the module with documentation and reclassification
    _ccstd.finalize_module(
        __name__,
        dynadoc_table = _fragments,
        recursive = True
    )

The ``finalize_module`` function will:

1. Generate comprehensive documentation for the module and its members using
   Dynadoc introspection
2. Apply the documentation fragments you provide
3. Reclassify the module and its submodules for immutability and concealment

Advanced Configuration
-------------------------------------------------------------------------------

For complex packages, you might want to configure different parts differently:

.. code-block:: python

    # mypackage/__init__.py
    import classcore.standard as _ccstd
    
    # Configure main package with full documentation
    _ccstd.finalize_module(
        __name__,
        dynadoc_table = main_fragments,
        recursive = False  # Handle submodules individually
    )
    
    # Configure submodules with different settings
    _ccstd.finalize_module(
        f"{__name__}.core",
        dynadoc_table = core_fragments,
        recursive = True
    )
    
    _ccstd.finalize_module(
        f"{__name__}.utils",
        dynadoc_table = utils_fragments,
        recursive = True
    )

This approach allows you to provide different documentation fragments and
introspection settings for different parts of your package.


Best Practices
===============================================================================

Package-Level Application
-------------------------------------------------------------------------------

For most packages, apply ``finalize_module`` at the package level in your
``__init__.py`` file:

.. code-block:: python

    # mypackage/__init__.py
    import classcore.standard as _ccstd
    
    # Package metadata and documentation fragments
    __version__ = '1.0.0'
    _fragments = {
        'version': __version__,
        'maintainer': 'Package Team',
        'license': 'Apache 2.0'
    }
    
    # Import public API
    from .core import PublicClass, public_function
    from .utils import helper_function
    
    # Finalize the entire package
    _ccstd.finalize_module(
        __name__,
        dynadoc_table = _fragments,
        recursive = True
    )

This pattern ensures that:

- Your package's public API is documented
- All modules in the package are immutable and concealed
- Documentation fragments are applied consistently
- The entire package hierarchy is protected from accidental modification

Documentation Fragments
-------------------------------------------------------------------------------

Use documentation fragments to provide consistent metadata across your package:

.. code-block:: python

    # mypackage/_metadata.py
    fragments = {
        'version': '1.0.0',
        'author': 'Your Name <your.email@example.com>',
        'license': 'Apache License 2.0',
        'homepage': 'https://github.com/yourname/mypackage',
        'description': 'A comprehensive data processing library',
        'examples_url': 'https://mypackage.readthedocs.io/examples',
        'api_url': 'https://mypackage.readthedocs.io/api'
    }
    
    # mypackage/__init__.py
    from ._metadata import fragments
    import classcore.standard as _ccstd
    
    _ccstd.finalize_module( __name__, dynadoc_table = fragments, recursive = True )

This approach centralizes your package metadata and makes it easy to maintain
consistency across documentation.

Error Handling
-------------------------------------------------------------------------------

When using module finalization, be aware that the resulting modules will raise
``AttributeImmutability`` exceptions if code attempts to modify them:

.. code-block:: python

    import classcore.exceptions
    
    # After finalization, this will raise an exception
    try:
        mypackage.core.some_function = lambda: "modified"
    except classcore.exceptions.AttributeImmutability as e:
        print( f"Cannot modify module: {e}" )

Design your package APIs to avoid dynamic modification after finalization.
If you need dynamic behavior, consider using configuration objects or factory
functions instead of direct module attribute modification.


Integration with Build Systems
===============================================================================

Module finalization integrates well with modern Python build systems. The
immutability ensures that your package's API surface is clearly defined and
cannot be accidentally modified at runtime.

For packages that use entry points or plugin systems, apply finalization after
all dynamic setup is complete:

.. code-block:: python

    # mypackage/__init__.py
    import classcore.standard as _ccstd
    
    # Dynamic setup (plugin registration, etc.)
    _setup_plugins()
    _register_entry_points()
    
    # Final API definition
    from .api import *
    
    # Lock down the package
    _ccstd.finalize_module( __name__, dynadoc_table = _fragments, recursive = True )

This ensures that your package initialization is complete before the
immutability protections are applied.