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


# import pytest

from .__ import PACKAGE_NAME, cache_import_module


MODULE_QNAME = f"{PACKAGE_NAME}.decorators"


def test_111_produce_class_initialization_decorator_original( ):
    module = cache_import_module( MODULE_QNAME )
    base_module = cache_import_module( f"{PACKAGE_NAME}.__" )
    factories_module = cache_import_module( f"{PACKAGE_NAME}.factories" )
    constructor = factories_module.produce_class_constructor(
        attributes_namer = base_module.calculate_attrname )
    cdecorator = module.produce_class_construction_decorator(
        attributes_namer = base_module.calculate_attrname,
        constructor = constructor )
    initializer = factories_module.produce_class_initializer(
        attributes_namer = base_module.calculate_attrname )
    idecorator = module.produce_class_initialization_decorator(
        attributes_namer = base_module.calculate_attrname,
        initializer = initializer )
    @idecorator
    @cdecorator
    class Class( type ):
        def __init__( self, *posargs, **nomargs ):
            self._hello = 'Hi'
    class Object( metaclass = Class ): pass
    assert Object._hello == 'Hi'
