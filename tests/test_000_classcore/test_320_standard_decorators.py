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


from . import PACKAGE_NAME, cache_import_module


MODULE_QNAME = f"{PACKAGE_NAME}.standard.decorators"


def test_210_class_factory_decorator_idempotence( ):
    ''' Class factory decorators are idempotent. '''
    module = cache_import_module( MODULE_QNAME )
    @module.class_factory( )
    class Class: pass
    @module.class_factory( )
    class BetterClass( Class ): pass
    assert Class.__new__ is BetterClass.__new__
    assert Class.__init__ is BetterClass.__init__
    assert Class.__setattr__ is BetterClass.__setattr__
    assert Class.__delattr__ is BetterClass.__delattr__
    assert Class.__dir__ is BetterClass.__dir__
