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


from dataclasses import dataclass
from platform import python_implementation

import pytest

from . import PACKAGE_NAME, cache_import_module


MODULE_QNAME = f"{PACKAGE_NAME}.utilities"

pyimpl = python_implementation( )


class Foo: x = 1
class Bar( Foo ): pass


class Baz:
    def __init__( self, value ):
        self.x = value


class FooSlotsBase: __slots__ = ( 'x', )


class FooSlots( FooSlotsBase ):
    def __init__( self, value ):
        self.x = value


foo = Foo( )
bar = Bar( )


def test_100_qualify_class_name( ):
    ''' Class name is correctly qualified. '''
    module = cache_import_module( MODULE_QNAME )
    assert f"{__name__}.Foo" == module.qualify_class_name( Foo )


def test_110_describe_object( ):
    ''' Object is correctly described. '''
    module = cache_import_module( MODULE_QNAME )
    assert 'class' in module.describe_object( Foo )
    assert 'instance of class' in module.describe_object( foo )


def test_200_getattr0_dict( ):
    ''' Attribute from object dictionary without inheritance. '''
    module = cache_import_module( MODULE_QNAME )
    function = module.getattr0
    sentinel = object( )
    assert 1 == function( Foo, 'x', sentinel )
    assert sentinel == function( Bar, 'x', sentinel )
    assert sentinel == function( foo, 'x', sentinel )
    assert sentinel == function( bar, 'x', sentinel )
    baz = Baz( 42 )
    assert 42 == function( baz, 'x', sentinel )


def test_205_getattr0_slots( ):
    ''' Attribute from object slots (empty and filled). '''
    module = cache_import_module( MODULE_QNAME )
    function = module.getattr0
    sentinel = object( )
    foono = FooSlotsBase( )
    assert sentinel == function( foono, 'x', sentinel )
    foo = FooSlots( 42 )
    assert 42 == function( foo, 'x', sentinel )


@pytest.mark.skipif(
    'CPython' != pyimpl, reason = 'Only relevant to CPython.' )
def test_300_cpython_class_repair_function_closure( ):
    ''' Reproduction has class cell repaired in function closure. '''
    class Wut:
        def __dir__( self ): return super( ).__dir__( )
    DataclassWut = dataclass( slots = True )( Wut )
    assert Wut is not DataclassWut
    module = cache_import_module( MODULE_QNAME )
    module.repair_class_reproduction( Wut, DataclassWut )
    cellidx = DataclassWut.__dir__.__code__.co_freevars.index( '__class__' )
    closure = DataclassWut.__dir__.__closure__[ cellidx ]
    assert closure.cell_contents is DataclassWut


@pytest.mark.skipif(
    'CPython' != pyimpl, reason = 'Only relevant to CPython.' )
def test_301_cpython_class_repair_property_closure( ):
    ''' Reproduction has class cell repaired in property closure. '''
    class Wut:
        @property
        def name( self ): return super( ).__str__( )
    DataclassWut = dataclass( slots = True )( Wut )
    assert Wut is not DataclassWut
    module = cache_import_module( MODULE_QNAME )
    module.repair_class_reproduction( Wut, DataclassWut )
    wut = DataclassWut( )
    assert wut.name == str( wut )


@pytest.mark.skipif(
    'CPython' != pyimpl, reason = 'Only relevant to CPython.' )
def test_302_cpython_class_repair_nothing( ):
    ''' Reproduction has no class cell to repair in anything. '''
    class Wut:
        @property
        def name( self ): return 'wut'
        @name.setter
        def setname( self, value ): pass
        @name.deleter
        def delname( self ): pass
    DataclassWut = dataclass( slots = True )( Wut )
    assert Wut is not DataclassWut
    module = cache_import_module( MODULE_QNAME )
    module.repair_class_reproduction( Wut, DataclassWut )
    wut = DataclassWut( )
    assert 'wut' == wut.name
