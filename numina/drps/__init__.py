#
# Copyright 2011-2018 Universidad Complutense de Madrid
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

"""DRP system wide initialization"""


from .drpsystem import DrpSystem

_system_drps = None


def get_system_drps():
    """Load all compatible DRPs in the system"""
    global _system_drps
    if _system_drps is None:
        _system_drps = DrpSystem()
        _system_drps.load()

    return _system_drps