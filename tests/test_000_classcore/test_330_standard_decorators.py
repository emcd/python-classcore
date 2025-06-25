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


import pytest

from . import PACKAGE_NAME, cache_import_module


MODULE_QNAME = f"{PACKAGE_NAME}.standard.decorators"


def simple_assigner_core(
    objct,
    ligation,
    attributes_namer,
    error_class_provider,
    level, name, value
):
    object.__setattr__( objct, name, value )


def simple_deleter_core(
    objct,
    ligation,
    attributes_namer,
    error_class_provider,
    level, name
):
    object.__delattr__( objct, name )


def simple_surveyor_core( objct, ligation, attributes_namer, level ):
    return object.__dir__( objct )


def test_120_core_function_inheritance( ):
    ''' Core functions inherited. '''
    module = cache_import_module( MODULE_QNAME )
    exceptions = cache_import_module( f"{PACKAGE_NAME}.exceptions" )

    @module.with_standard_behaviors( )
    class Base: pass

    b = Base( )
    with pytest.raises( exceptions.AttributeImmutability ):
        b.bar = 6
    assert not hasattr( b, 'bar' )
    assert 'bar' not in dir( b )
    with pytest.raises( exceptions.AttributeImmutability ):
        del b.bar

    @module.with_standard_behaviors( )
    class Derivation( Base ): pass

    d = Derivation( )
    with pytest.raises( exceptions.AttributeImmutability ):
        d.foo = 2
    assert not hasattr( d, 'foo' )
    assert 'foo' not in dir( d )
    with pytest.raises( exceptions.AttributeImmutability ):
        del d.foo


def test_121_core_function_replacements_inheritance( ):
    ''' Replacement core functions inherited. '''
    module = cache_import_module( MODULE_QNAME )

    @module.with_standard_behaviors(
        assigner_core = simple_assigner_core,
        deleter_core = simple_deleter_core,
        surveyor_core = simple_surveyor_core,
    )
    class Base: pass

    b = Base( )
    b.bar = 6
    assert b.bar == 6
    assert 'bar' in dir( b )
    del b.bar
    assert not hasattr( b, 'bar' )

    @module.with_standard_behaviors( )
    class Derivation( Base ): pass

    d = Derivation( )
    d.foo = 2
    assert d.foo == 2
    assert 'foo' in dir( d )
    del d.foo
    assert not hasattr( d, 'foo' )
