# vim: set filetype=python fileencoding=utf-8:
# -*- coding: utf-8 -*-

#============================================================================#
#                                                                            #
#  Licensed under the Apache License, Version 2.0 (the "License");           #
#  you may not use this file except in compliance with the License.          #
#  You may obtain a copy of the License at                                   #
#                                                                            #
#      http://www.apache.org/licenses/LICENSE-2.0                            #
#                                                                            #
#  Unless required by applicable law or agreed to in writing, software       #
#  distributed under the License is distributed on an "AS IS" BASIS,         #
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#  See the License for the specific language governing permissions and       #
#  limitations under the License.                                            #
#                                                                            #
#============================================================================#


''' Standard module classes and reclassifers. '''


from .. import utilities as _utilities
from . import __
from . import behaviors as _behaviors
from . import classes as _classes
from . import nomina as _nomina


_dynadoc_context = __.dynadoc.produce_context( )
_dynadoc_introspection_cc = __.dynadoc.ClassIntrospectionControl(
    inheritance = True,
    introspectors = ( __.dynadoc.introspection.introspect_special_classes, ) )
_dynadoc_introspection = __.dynadoc.IntrospectionControl(
    class_control = _dynadoc_introspection_cc,
    limiters = (
        __.funct.partial(
            _behaviors.dynadoc_avoid_immutables,
            attributes_namer = __.calculate_attrname ), ),
    targets = __.dynadoc.IntrospectionTargetsOmni )
# TODO: Convert into proper function with attributes namer argument.
assign_module_docstring = __.funct.partial(
    __.dynadoc.assign_module_docstring,
    context = _dynadoc_context,
    introspection = _dynadoc_introspection,
    table = __.fragments )


class Module( __.types.ModuleType, _classes.Object ):
    ''' Modules with attributes immutability and concealment. '''


def reclassify_modules(
    attributes: __.typx.Annotated[
        __.cabc.Mapping[ str, __.typx.Any ] | __.types.ModuleType | str,
        __.dynadoc.Doc(
            'Module, module name, or dictionary of object attributes.' ),
    ], /, *,
    attributes_namer: __.typx.Annotated[
        _nomina.AttributesNamer,
        __.dynadoc.Doc(
            ''' Attributes namer function with which to seal class. ''' ),
    ] = __.calculate_attrname,
    recursive: __.typx.Annotated[
        bool, __.dynadoc.Doc( 'Recursively reclassify package modules?' )
    ] = False,
) -> None:
    # TODO? Ensure correct operation with namespace packages.
    ''' Reclassifies modules to have attributes concealment and immutability.

        Can operate on individual modules or entire package hierarchies.

        Only converts modules within the same package to prevent unintended
        modifications to external modules.

        When used with a dictionary, converts any module objects found as
        values if they belong to the same package.

        Has no effect on already-reclassified modules.
    '''
    if isinstance( attributes, str ):
        attributes = __.sys.modules[ attributes ]
    if isinstance( attributes, __.types.ModuleType ):
        module = attributes
        attributes = attributes.__dict__
    else: module = None
    package_name = (
        attributes.get( '__package__' ) or attributes.get( '__name__' ) )
    if not package_name: return
    for value in attributes.values( ):
        if not __.inspect.ismodule( value ): continue
        if not value.__name__.startswith( f"{package_name}." ): continue
        if recursive: reclassify_modules( value, recursive = True )
        if isinstance( value, Module ): continue
        _seal_module( value, attributes_namer )
    if module and not isinstance( module, Module ):
        _seal_module( module, attributes_namer )


def _seal_module(
     module: __.types.ModuleType, attributes_namer: _nomina.AttributesNamer
) -> None:
    behaviors = { _behaviors.concealment_label, _behaviors.immutability_label }
    behaviors_name = attributes_namer( 'instance', 'behaviors' )
    _utilities.setattr0( module, behaviors_name, behaviors )
    module.__class__ = Module
