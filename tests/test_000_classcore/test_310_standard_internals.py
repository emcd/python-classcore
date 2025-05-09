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


MODULE_QNAME = f"{PACKAGE_NAME}.standard.__"


def test_200_provide_error_class( ):
    module = cache_import_module( MODULE_QNAME )
    exceptions = cache_import_module( f"{PACKAGE_NAME}.exceptions" )
    error_class = module.provide_error_class( 'AttributeImmutability' )
    assert exceptions.AttributeImmutability is error_class
    with pytest.raises( exceptions.ErrorProvideFailure ):
        module.provide_error_class( 'DoesNotExist' )
