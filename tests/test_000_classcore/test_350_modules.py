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

from . import PACKAGE_NAME, cache_import_module


MODULE_QNAME = f"{PACKAGE_NAME}.standard.modules"


def test_200_reclassification_of_package_module( ):
    ''' Reclassifies package module directly. '''
    module = cache_import_module( MODULE_QNAME )
    module_class = module.Module
    module_ = types.ModuleType( 'foobarnotreal' )
    module_.__package__ = None
    assert module_.__class__ is not module_class
    module.reclassify_modules( module_ )
    assert module_.__class__ is module_class
    module.reclassify_modules( module_ ) # idempotence
    assert module_.__class__ is module_class


def test_201_reclassification_of_normal_module( ):
    ''' Reclassifies normal module directly. '''
    module = cache_import_module( MODULE_QNAME )
    module_class = module.Module
    module_ = types.ModuleType( 'fakepackage.foobarnotreal' )
    module_.__package__ = 'fakepackage'
    assert module_.__class__ is not module_class
    module.reclassify_modules( module_ )
    assert module_.__class__ is module_class
    module.reclassify_modules( module_ ) # idempotence
    assert module_.__class__ is module_class


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
    module_class = module.Module
    module_ = types.ModuleType( 'fakepackage.foobarnotreal' )
    module_dict = { 'mod': module_, '__package__': 'fakepackage' }
    assert module_.__class__ is not module_class
    module.reclassify_modules( module_dict )
    assert module_.__class__ is module_class
    module.reclassify_modules( module_dict ) # idempotence
    assert module_.__class__ is module_class
