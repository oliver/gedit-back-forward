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


class History:
    lastSteps = []
    nextSteps = []

    def addNewStep (self, step):
        print "addNewStep"
        self.lastSteps.append(step)
        self.nextSteps = []

    def goBack (self):
        if not(self.canGoBack()):
            return None
        self.nextSteps.insert(0, self.lastSteps[-1])
        return self.lastSteps.pop()

    def goForward (self):
        if not(self.canGoForward()):
            return None
        self.lastSteps.append(self.nextSteps[0])
        return self.nextSteps.pop(0)

    def canGoBack (self):
        if len(self.lastSteps) == 0:
            return False
        else:
            return True

    def canGoForward (self):
        if len(self.nextSteps) == 0:
            return False
        else:
            return True


class Step:
    doc = None
    textIter = None


class BFWindowHelper:
    def __init__(self, plugin, window):
        print "back-forward: plugin created for", window
        self._window = window
        self._plugin = plugin

        self._history = History()
        #self._recordNextMovement = False

        self._lastCursorPos = None

        self._insert_toolbar_buttons()

        self._window.connect_object("tab-added", BFWindowHelper.onTabAdded, self)

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

        self._btnBack = manager.get_action("/ToolBar/BackButton")
        self._btnForward = manager.get_action("/ToolBar/ForwardButton")

        # disable toolbar buttons
        self._btnBack.set_sensitive(False)
        self._btnForward.set_sensitive(False)

    def onTabAdded (self, tab):
        tab.get_view().connect_object("button-press-event", BFWindowHelper.onButtonPress, self, tab)
        tab.get_document().connect_object("cursor-moved", BFWindowHelper.onCursorMoved, self, tab)
        return False
        pass

    def onButtonPress (self, event, tab):
        print "onButtonPress"
        self._addNewStep(tab)
        #self._recordNextMovement = True
        return False
        pass

    def onCursorMoved (self, tab):
        print "cursor moved"

        insertMark = tab.get_document().get_insert()
        self._lastCursorPos = tab.get_document().get_iter_at_mark(insertMark)

        #if self._recordNextMovement:
            #self._addNewStep(tab)
            #self._recordNextMovement = False
        return False

    def _addNewStep (self, tab):
        print "adding new step"

        if self._lastCursorPos == None:
            print "ignoring last step (None)"
            return

        #insertMark = tab.get_document().get_insert()
        #insertIter = tab.get_document().get_iter_at_mark(insertMark)

        step = Step()
        step.doc = tab.get_document()
        #step.textIter = insertIter
        step.textIter = self._lastCursorPos

        self._history.addNewStep(step)
        self._btnBack.set_sensitive(True)
        self._btnForward.set_sensitive( self._history.canGoForward() )


    def on_back_button_activate (self, action):
        print "(back)"
        step = self._history.goBack()
        print "step: line %d col %d" % (step.textIter.get_line(), step.textIter.get_line_offset())
        self._btnBack.set_sensitive( self._history.canGoBack() )
        self._btnForward.set_sensitive( self._history.canGoForward() )

        step.doc.place_cursor(step.textIter)

    def on_forward_button_activate (self, action):
        print "(forward)"
        step = self._history.goForward()
        print "step: line %d col %d" % (step.textIter.get_line(), step.textIter.get_line_offset())
        self._btnBack.set_sensitive( self._history.canGoBack() )
        self._btnForward.set_sensitive( self._history.canGoForward() )

        step.doc.place_cursor(step.textIter)


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
