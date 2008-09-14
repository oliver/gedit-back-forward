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
import gtk


ui_str = """<ui>
  <toolbar name="ToolBar">
    <separator />
      <toolitem name="BackButton" action="BackButton"/>
      <toolitem name="ForwardButton" action="ForwardButton"/>
  </toolbar>
</ui>
"""


class BFWindowHelper:
    def __init__(self, plugin, window):
        print "back-forward: plugin created for", window
        self._window = window
        self._plugin = plugin

        self._insert_toolbar_buttons()

    def deactivate(self):
        print "back-forward: plugin stopped for", self._window

    def update_ui(self):
        print "back-forward: plugin update for", self._window

    def _insert_toolbar_buttons (self):
        # Get the GtkUIManager
        manager = self._window.get_ui_manager()

        # Create a new action group
        self._action_group = gtk.ActionGroup("BFPluginActions")
        self._action_group.add_actions([
            ("BackButton", "gtk-go-back", _("Back"),
                "", _("Go to last edit position"),
                self.on_back_button_activate),
            ("ForwardButton", "gtk-go-forward", _("Forward"),
                "", _("Go to next edit position"),
                self.on_forward_button_activate)
        ])

        # Insert the action group
        manager.insert_action_group(self._action_group, -1)

        # Merge the UI
        self._ui_id = manager.add_ui_from_string(ui_str)

    def on_back_button_activate (self, action):
        print "(back)"
        pass

    def on_forward_button_activate (self, action):
        print "(forward)"
        pass

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
