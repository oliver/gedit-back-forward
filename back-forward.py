#    Gedit back/forward buttons plugin
#    Copyright (C) 2008  Oliver Gerlich <oliver.gerlich@gmx.de>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


import os
import gedit


class BFWindowHelper:
    def __init__(self, plugin, window):
        print "back-forward: plugin created for", window
        self._window = window
        self._plugin = plugin

    def deactivate(self):
        print "back-forward: plugin stopped for", self._window

    def update_ui(self):
        print "back-forward: plugin update for", self._window


class BackForwardPlugin(gedit.Plugin):
    def __init__(self):
        gedit.Plugin.__init__(self)
        self._instances = {}

    def activate(self, window):
        self._instances[window] = BFWindowHelper(self, window)

    def deactivate(self, window):
        self._instances[window].deactivate()
        del self._instances[window]

    def update_ui(self, window):
        self._instances[window].update_ui()
