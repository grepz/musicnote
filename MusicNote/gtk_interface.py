#!/usr/bin/python
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk

# just tests

# So a typical drag-and-drop cycle would look as follows:
#     * Drag begins. Source can get "drag-begin" signal.
#       Can set up drag icon, etc.
#     * Drag moves over a drop area. Destination can get "drag-motion" signal.
#     * Drop occurs. Destination can get "drag-drop" signal.
#       Destination should ask for source data.
#     * Drag data request (when a drop occurs).
#       Source can get "drag-data-get" signal.
#     * Drop data received (may be on same or different application).
#       Destination can get "drag-data-received" signal.
#     * Drag data delete (if the drag was a move).
#       Source can get "drag-data-delete" signal
#     * Drag-and-drop procedure done. Source can receive "drag-end" signal.

drop_yes = ("drop_yes", gtk.TARGET_SAME_WIDGET, 0)
drop_no = ("drop_no", gtk.TARGET_SAME_WIDGET, 0)


class MNView(gtk.VBox):

    def __init__ (self):
        pass


class MNGtkMain:
    
    def destroy(self, widget, data=None):
        gtk.main_quit()

    def __init__ (self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)

        self.window.set_title("MusicNote")
        self.window.set_size_request(700, 500)

        self.window.connect("destroy", self.destroy)

        self.window.show()

    def checkSanity(self, model, source, target):
        source_path = model.get_path(source)
        target_path = model.get_path(target)
        print len(target_path)
        if target_path[0:len(source_path)] == source_path:
            return False
        else:
            return True

    def onDragDataReceived(self, treeview, drag_context, x, y,
                           selection_data, info, eventtime):
        res = treeview.get_dest_row_at_pos(x, y)
        if not res:
            return
        if len(res) > 1:
            drag_context.finish(False, False, eventtime)
        else:
            drag_context.finish(True, True, eventtime)

        
    def test(self):
        self.categories = gtk.TreeStore(str)

        for category in range (20):
            cat = self.categories.append(None, ['Row %d' % category])
            for element in range (5):
                self.categories.append(cat, ['Child row %d' % element])

        self.treeview = gtk.TreeView(self.categories)
#        self.treeview.connect('drag-data-received', self.__drag_control)
        self.treeview.connect("drag-data-received", self.onDragDataReceived)
        
        self.tvcolumn = gtk.TreeViewColumn('Names')
        self.treeview.append_column(self.tvcolumn)
        self.cell = gtk.CellRendererText()
        self.tvcolumn.pack_start(self.cell, True)
        self.tvcolumn.add_attribute(self.cell, 'text', 0)

        self.treeview.set_search_column(0)
        self.tvcolumn.set_sort_column_id(0)
        
        self.treeview.set_reorderable(True)
        
        self.window.add(self.treeview)
        self.window.show_all()
        

    def main(self):
        self.test()

        
        
        gtk.main()


if __name__ == "__main__":
    mnwin = MNGtkMain ()
    mnwin.main()
