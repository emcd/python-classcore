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


''' Common constants, imports, and utilities. '''


from .doctab import *
from .imports import *
from .nomina import *


T = typx.TypeVar( 'T', bound = type )


dictproxy_empty: cabc.Mapping[ str, str ] = types.MappingProxyType( { } )


_context = dynadoc.produce_context( )
_introspection_cc = dynadoc.ClassIntrospectionControl(
    inheritance = True,
    introspectors = ( dynadoc.introspection.introspect_special_classes, ) )
_introspection = dynadoc.IntrospectionControl(
    class_control = _introspection_cc,
    targets = dynadoc.IntrospectionTargetsOmni )
assign_module_docstring = funct.partial(
    dynadoc.assign_module_docstring,
    context = _context,
    introspection = _introspection,
    table = fragments )
