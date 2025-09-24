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

import pytest

from .__ import PACKAGE_NAME, cache_import_module


MODULE_QNAME = f"{PACKAGE_NAME}.utilities"


class Foo: x = 1
foo = Foo( )


def test_100_qualify_class_name( ):
    ''' Class name is correctly qualified. '''
    module = cache_import_module( MODULE_QNAME )
    assert f"{__name__}.Foo" == module.qualify_class_name( Foo )


def test_110_describe_object( ):
    ''' Object is correctly described. '''
    module = cache_import_module( MODULE_QNAME )
    assert 'class' in module.describe_object( Foo )
    assert 'instance of class' in module.describe_object( foo )


def test_200_attr0( ):
    ''' Can access and mutate special private attribute. '''
    module = cache_import_module( MODULE_QNAME )
    sentinel = object( )
    class C: pass
    module.setattr0( C, 'x', 1 )
    assert 1 == module.getattr0( C, 'x', sentinel )
    assert sentinel == module.getattr0( C, 'y', sentinel )
    class D( C ): pass
    module.setattr0( D, 'y', 2 )
    assert sentinel == module.getattr0( D, 'x', sentinel )
    assert 2 == module.getattr0( D, 'y', sentinel )
    module.delattr0( C, 'x' )
    assert sentinel == module.getattr0( C, 'x', sentinel )
    class CS: __slots__ = ( 'z', )
    cs = CS( )
    assert sentinel == module.getattr0( cs, 'z', sentinel )
    module.setattr0( cs, 'z', 3 )
    assert 3 == module.getattr0( cs, 'z', sentinel )
    module.delattr0( cs, 'z' )
    assert sentinel == module.getattr0( cs, 'z', sentinel )
    with pytest.raises( AttributeError ):
        module.delattr0( cs, 'missing' )


def test_300_class_repair_function_closure( ):
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


def test_301_class_repair_property_closure( ):
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


def test_302_class_repair_nothing( ):
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
