#
# Copyright 2008-2012 Universidad Complutense de Madrid
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

from .base import BaseConectable

class Shutter(BaseConectable):
    def __init__(self):
        self.closed = True 
    
    def open(self):
        self.closed = False
    
    def close(self):
        self.closed = True
        
    def emit(self):
        if self.closed:
            return 0.0
        else:
            return self.source.emit()
        
