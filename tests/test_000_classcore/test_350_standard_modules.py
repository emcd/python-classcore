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


import types

import pytest

from . import PACKAGE_NAME, cache_import_module


MODULE_QNAME = f"{PACKAGE_NAME}.standard.modules"


def test_200_reclassification_of_package_module( ):
    ''' Reclassifies package module directly. '''
    module = cache_import_module( MODULE_QNAME )
    exceptions_module = cache_import_module( f"{PACKAGE_NAME}.exceptions" )
    module_class = module.Module
    module_ = types.ModuleType( 'foobarnotreal' )
    module_.__package__ = None
    assert module_.__class__ is not module_class
    module.reclassify_modules( module_ )
    assert module_.__class__ is module_class
    module.reclassify_modules( module_ ) # idempotence
    assert module_.__class__ is module_class
    with pytest.raises( exceptions_module.AttributeImmutability ):
        module.foo = 1


def test_201_reclassification_of_normal_module( ):
    ''' Reclassifies normal module directly. '''
    module = cache_import_module( MODULE_QNAME )
    exceptions_module = cache_import_module( f"{PACKAGE_NAME}.exceptions" )
    module_class = module.Module
    module_ = types.ModuleType( 'fakepackage.foobarnotreal' )
    module_.__package__ = 'fakepackage'
    assert module_.__class__ is not module_class
    module.reclassify_modules( module_ )
    assert module_.__class__ is module_class
    module.reclassify_modules( module_ ) # idempotence
    assert module_.__class__ is module_class
    with pytest.raises( exceptions_module.AttributeImmutability ):
        module.foo = 1


def test_202_reclassification_of_incomplete_module( ):
    ''' Reclassification ignores incomplete module. '''
    module = cache_import_module( MODULE_QNAME )
    module_class = module.Module
    module_ = types.ModuleType( 'foobarnotreal' )
    module_.__package__ = None
    del module_.__name__
    assert module_.__class__ is not module_class
    module.reclassify_modules( module_ )
    assert module_.__class__ is not module_class


def test_205_reclassification_via_module_globals( ):
    ''' Reclassifies via module globals dictionary. '''
    module = cache_import_module( MODULE_QNAME )
    exceptions_module = cache_import_module( f"{PACKAGE_NAME}.exceptions" )
    module_class = module.Module
    module_ = types.ModuleType( 'fakepackage.foobarnotreal' )
    module_dict = { 'mod': module_, '__package__': 'fakepackage' }
    assert module_.__class__ is not module_class
    module.reclassify_modules( module_dict )
    assert module_.__class__ is module_class
    module.reclassify_modules( module_dict ) # idempotence
    assert module_.__class__ is module_class
    with pytest.raises( exceptions_module.AttributeImmutability ):
        module.foo = 1


def test_210_finalize_module_basic( ):
    ''' Finalizes module with default parameters. '''
    module = cache_import_module( MODULE_QNAME )
    exceptions_module = cache_import_module( f"{PACKAGE_NAME}.exceptions" )
    module_class = module.Module
    module_ = types.ModuleType( 'fakepackage.foobarnotreal' )
    module_.__package__ = 'fakepackage'
    assert module_.__class__ is not module_class
    module.finalize_module( module_ )
    assert module_.__class__ is module_class
    with pytest.raises( exceptions_module.AttributeImmutability ):
        module_.foo = 1


def test_211_finalize_module_recursive_with_module_targets( ):
    ''' Finalizes module recursively when introspection has Module targets. '''
    module = cache_import_module( MODULE_QNAME )
    dynadoc_module = cache_import_module( f"{PACKAGE_NAME}.standard.dynadoc" )
    exceptions_module = cache_import_module( f"{PACKAGE_NAME}.exceptions" )
    module_class = module.Module
    module_ = types.ModuleType( 'fakepackage.foobarnotreal' )
    module_.__package__ = 'fakepackage'
    introspection_with_module = dynadoc_module.dynadoc_introspection_on_package
    assert module_.__class__ is not module_class
    module.finalize_module(
        module_,
        dynadoc_introspection = introspection_with_module,
        recursive = True )
    assert module_.__class__ is module_class
    with pytest.raises( exceptions_module.AttributeImmutability ):
        module_.foo = 1


def test_212_finalize_module_recursive_without_module_targets( ):
    ''' Finalizes module recursively when introspection lacks targets. '''
    module = cache_import_module( MODULE_QNAME )
    dynadoc_module = cache_import_module( f"{PACKAGE_NAME}.standard.dynadoc" )
    exceptions_module = cache_import_module( f"{PACKAGE_NAME}.exceptions" )
    module_class = module.Module
    module_ = types.ModuleType( 'fakepackage.foobarnotreal' )
    module_.__package__ = 'fakepackage'
    introspection_without_module = (
        dynadoc_module.dynadoc_introspection_on_class )
    assert module_.__class__ is not module_class
    module.finalize_module(
        module_,
        dynadoc_introspection = introspection_without_module,
        recursive = True )
    assert module_.__class__ is module_class
    with pytest.raises( exceptions_module.AttributeImmutability ):
        module_.foo = 1


def test_213_finalize_module_nonrecursive_with_module_targets( ):
    ''' Finalizes module non-recursively when introspection has targets. '''
    module = cache_import_module( MODULE_QNAME )
    dynadoc_module = cache_import_module( f"{PACKAGE_NAME}.standard.dynadoc" )
    exceptions_module = cache_import_module( f"{PACKAGE_NAME}.exceptions" )
    module_class = module.Module
    module_ = types.ModuleType( 'fakepackage.foobarnotreal' )
    module_.__package__ = 'fakepackage'
    introspection_with_module = dynadoc_module.dynadoc_introspection_on_package
    assert module_.__class__ is not module_class
    module.finalize_module(
        module_,
        dynadoc_introspection = introspection_with_module,
        recursive = False )
    assert module_.__class__ is module_class
    with pytest.raises( exceptions_module.AttributeImmutability ):
        module_.foo = 1


def test_214_finalize_module_nonrecursive_without_module_targets( ):
    ''' Finalizes module non-recursively when introspection lacks targets. '''
    module = cache_import_module( MODULE_QNAME )
    dynadoc_module = cache_import_module( f"{PACKAGE_NAME}.standard.dynadoc" )
    exceptions_module = cache_import_module( f"{PACKAGE_NAME}.exceptions" )
    module_class = module.Module
    module_ = types.ModuleType( 'fakepackage.foobarnotreal' )
    module_.__package__ = 'fakepackage'
    introspection_without_module = (
        dynadoc_module.dynadoc_introspection_on_class )
    assert module_.__class__ is not module_class
    module.finalize_module(
        module_,
        dynadoc_introspection = introspection_without_module,
        recursive = False )
    assert module_.__class__ is module_class
    with pytest.raises( exceptions_module.AttributeImmutability ):
        module_.foo = 1
