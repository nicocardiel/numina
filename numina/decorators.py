#
# Copyright 2008-2011 Sergio Pascual
# 
# This file is part of Numina
# 
# Numina is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Numina is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Numina.  If not, see <http://www.gnu.org/licenses/>.
# 

'''Decorators for the numina package.'''

import time
import logging

_logger = logging.getLogger("numina")

def print_timing(func):
    '''Print timing decorator.'''
    def wrapper(*arg, **keywords):
        t1 = time.time()
        res = func(*arg, **keywords)
        t2 = time.time()
        print '%s took %0.3f s' % (func.func_name, (t2 - t1))
        return res
    return wrapper

def log_timing(func):
    '''Log timing decorator.'''
    def wrapper(*arg, **keywords):
        t1 = time.time()
        res = func(*arg, **keywords)
        t2 = time.time()
        _logger.debug('%s took %0.3f s' % (func.func_name, (t2 - t1)))
        return res
    return wrapper