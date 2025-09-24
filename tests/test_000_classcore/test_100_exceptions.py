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

from .__ import PACKAGE_NAME, cache_import_module


CLASS_NAMES = (
    'Omniexception', 'Omnierror',
    'AttributeImmutability',
    'ErrorProvideFailure',
)
MODULE_QNAME = f"{PACKAGE_NAME}.exceptions"


@pytest.mark.parametrize( 'class_name', CLASS_NAMES )
def test_000_class_exists( class_name ):
    ''' Class exists in module. '''
    module = cache_import_module( MODULE_QNAME )
    assert hasattr( module, class_name )
    class_ = getattr( module, class_name )
    assert issubclass( class_, BaseException )


@pytest.mark.parametrize( 'class_name', CLASS_NAMES )
def test_001_omniexception_subclass( class_name ):
    ''' Class is subclass of family root. '''
    module = cache_import_module( MODULE_QNAME )
    omniclass = module.Omniexception
    class_ = getattr( module, class_name )
    assert issubclass( class_, omniclass )


@pytest.mark.parametrize( 'class_name', CLASS_NAMES )
def test_010_class_immutability( class_name ):
    ''' Class attributes are immutable. '''
    module = cache_import_module( MODULE_QNAME )
    class_ = getattr( module, class_name )
    error_class = module.AttributeImmutability
    with pytest.raises( error_class ):
        class_.__setattr__ = None
    with pytest.raises( error_class ):
        del class_.__delattr__


@pytest.mark.parametrize( 'class_name', CLASS_NAMES )
def test_020_class_concealment( class_name ):
    ''' Non-public class attributes are concealed. '''
    module = cache_import_module( MODULE_QNAME )
    class_ = getattr( module, class_name )
    for name in dir( class_ ): assert not name.startswith( '_' )


def test_100_omniexception_instantiation( ):
    ''' Omniexception can be instantiated. '''
    module = cache_import_module( MODULE_QNAME )
    class_ = module.Omniexception
    with pytest.raises( class_ ):
        raise class_
    with pytest.raises( class_ ) as excinfo:
        raise class_( "message" )
    assert "message" == str( excinfo.value )


def test_101_omniexception_instance_immutability( ):
    ''' Omniexception instance attributes are immutable. '''
    module = cache_import_module( MODULE_QNAME )
    class_ = module.Omniexception
    error_class = module.AttributeImmutability
    instance = class_( )
    with pytest.raises( error_class ):
        instance.extra_argument__ = None
    with pytest.raises( error_class ):
        del instance.extra_argument__


def test_102_omniexception_instance_concealment( ):
    ''' Only certain omniexception instance attributes are visible. '''
    module = cache_import_module( MODULE_QNAME )
    class_ = module.Omniexception
    instance = class_( )
    instance_dir = dir( instance )
    assert '__cause__' in instance_dir
    assert '__context__' in instance_dir
    assert 'args' in instance_dir
    assert '__init__' not in instance_dir


def test_110_omnierror_instantiation( ):
    ''' Omnierror can be instantiated. '''
    module = cache_import_module( MODULE_QNAME )
    class_ = module.Omnierror
    with pytest.raises( class_ ):
        raise class_
    with pytest.raises( class_ ) as excinfo:
        raise class_( "message" )
    assert "message" == str( excinfo.value )


def test_200_attribute_immutability_instantiation( ):
    ''' Attribute immutability error can be instantiated. '''
    module = cache_import_module( MODULE_QNAME )
    class_ = module.AttributeImmutability
    with pytest.raises( class_ ) as excinfo:
        raise class_( 'foo', "class 'bar'" )
    assert 'foo' in str( excinfo.value )
    assert "class 'bar'" in str( excinfo.value )


def test_300_error_provide_failure_instantiation( ):
    ''' Error provide failure can be instantiated. '''
    module = cache_import_module( MODULE_QNAME )
    class_ = module.ErrorProvideFailure
    with pytest.raises( class_ ) as excinfo:
        raise class_( 'FooFailure', 'does not exist' )
    assert 'FooFailure' in str( excinfo.value )
    assert 'does not exist' in str( excinfo.value )
