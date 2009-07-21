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

    def addNewStep (self, lastStep):
        print "addNewStep (row: %d; col: %d)" % (lastStep.textIter.get_line(), lastStep.textIter.get_line_offset())
        print lastStep.doc.get_uri()
        self.lastSteps.append(lastStep)
        self.nextSteps = []

    def goBack (self, currStep):
        if not(self.canGoBack()):
            return None
        self.nextSteps.insert(0, currStep)
        return self.lastSteps.pop()

    def goForward (self, currStep):
        if not(self.canGoForward()):
            return None
        self.lastSteps.append(currStep)
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
    lineNo = None
    colNo = None


class BFWindowHelper:
    def __init__(self, plugin, window):
        print "back-forward: plugin created for", window
        self._window = window
        self._plugin = plugin
        self.handlers = [] # list of (object, handlerId) tuples, for deactivate() method

        self._history = History()

        self._insert_toolbar_buttons()

        # register button-press handlers for all existing tabs
        for doc in self._window.get_documents():
            tab = gedit.tab_get_from_document(doc)
            self.onTabAdded(tab)

        handler = self._window.connect_object("tab-added", BFWindowHelper.onTabAdded, self)
        self.handlers.append( (self._window, handler) )


    def deactivate(self):
        print "back-forward: plugin stopped for", self._window
        self._remove_menu()

        # unregister all of our GTK handlers:
        for (obj, handler) in self.handlers:
            obj.disconnect(handler)
        self.handlers = []

        self._history = None

        self._window = None
        self._plugin = None

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

    def _remove_menu(self):
        # remove toolbar buttons
        manager = self._window.get_ui_manager()
        manager.remove_ui(self._ui_id)
        manager.remove_action_group(self._action_group)
        manager.ensure_update()

        self._btnBack = None
        self._btnForward = None
        self._ui_id = None

    def onTabAdded (self, tab):
        print "onTabAdded"
        handler = tab.get_view().connect_object("button-press-event", BFWindowHelper.onButtonPress, self, tab)
        self.handlers.append( (tab.get_view(), handler) )
        self._addNewStep()
        return False

    def onButtonPress (self, event, tab):
        print "onButtonPress"
        self._addNewStep()
        return False

    def _getCurrentStep (self):
        tab = self._window.get_active_tab()

        insertMark = tab.get_document().get_insert()
        insertIter = tab.get_document().get_iter_at_mark(insertMark)

        step = Step()
        step.doc = tab.get_document()
        step.textIter = insertIter
        step.lineNo = insertIter.get_line()
        step.colNo = insertIter.get_line_offset()
        return step

    def _addNewStep (self):
        print "adding new step"

        step = self._getCurrentStep()

        self._history.addNewStep(step)
        self._btnBack.set_sensitive(True)
        self._btnForward.set_sensitive( self._history.canGoForward() )


    def _restoreStep (self, step):
        print "step: line %d col %d" % (step.lineNo, step.colNo)
        self._btnBack.set_sensitive( self._history.canGoBack() )
        self._btnForward.set_sensitive( self._history.canGoForward() )

        newIter = step.doc.get_iter_at_line_offset(step.lineNo, step.colNo)
        step.doc.place_cursor(newIter)

        self._window.set_active_tab(gedit.tab_get_from_document(step.doc))
        view = gedit.tab_get_from_document(step.doc).get_view()
        view.scroll_to_cursor()

    def on_back_button_activate (self, action):
        print "(back)"
        step = self._history.goBack( self._getCurrentStep() )
        self._restoreStep(step)

    def on_forward_button_activate (self, action):
        print "(forward)"
        step = self._history.goForward( self._getCurrentStep() )
        self._restoreStep(step)


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
