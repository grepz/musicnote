# -*- coding: utf-8 -*-

#  gtk_interface.py -- ondisk Music data crawler with a number of features
#
#  Copyright 2009 Stanislav M. Ivankin <stas@concat.info>
#
#  This file is part of musicnote.
#
#  musicnote is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  musicnote is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with musicnote.  If not, see <http://www.gnu.org/licenses/>.

import gobject
import gtk
import pygtk

pygtk.require('2.0')

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

class MNTreeView:
    drop_yes = ('drop_yes', gtk.TARGET_SAME_WIDGET, 0)
    drop_no = ('drop_no', gtk.TARGET_SAME_WIDGET, 0)

    def checkDNDSanity (self, model, source, dest, drop_pos):
        source_path = model.get_path(source)
        dest_path = model.get_path(dest)
        target_len, source_len = len(dest_path), len(source_path)

        # If i am trying to drop element to the child node with the
        # same parent
        if dest_path[0] == source_path[0]:
            return False
        # We can't drop elements into child nodes
        if target_len > 1 and \
               (drop_pos == gtk.TREE_VIEW_DROP_INTO_OR_BEFORE or \
                drop_pos == gtk.TREE_VIEW_DROP_INTO_OR_AFTER):
            return False
        # Root nodes can't be simply reordered
        if (target_len == 1 and source_len == 1) and \
               drop_pos == gtk.TREE_VIEW_DROP_BEFORE or \
               drop_pos == gtk.TREE_VIEW_DROP_AFTER:
            return False
        
        return True

    def __iter_is_child (self, model, iter):
        if len (model.get_path (iter)) > 1:
            return True
        else:
            return False

    def __copy_data (self, treeview, model,
                     source, dest, drop_pos):
        # source is child
        if self.__iter_is_child (model, source):
            # in children list
            if self.__iter_is_child (model, dest):
                append_dest = model.iter_parent (dest)
            # to root node
            else:
                # into root node
                if drop_pos == gtk.TREE_VIEW_DROP_INTO_OR_BEFORE or \
                   drop_pos == gtk.TREE_VIEW_DROP_INTO_OR_AFTER:
                    append_dest = dest
                # next to root node
                else:
                    append_dest = None        
            model.append (append_dest, model[source])
        # source is root
        else:
            if self.__iter_is_child (model, dest):
                append_dest = model.iter_parent (dest)
            else:
                append_dest = dest
            iter = model.iter_children(source)
            while iter:
                model.append (append_dest, model[iter])
                model.remove(iter)
                iter = model.iter_children(source)
            model.append ((self.__iter_is_child (model, dest) and \
                           [model.iter_parent (dest)] or \
                           [dest])[0], model[source])
                
    def __drag_motion_cb (self, treeview, drag_context,
                        x, y, evtime):
        try:
            dest_path, drop_pos = treeview.get_dest_row_at_pos(x, y)
            model, source = treeview.get_selection().get_selected()
            dest = model.get_iter(dest_path)
        except:
            return
        
        if self.checkDNDSanity(model, source, dest, drop_pos):
            treeview.enable_model_drag_dest (
                [self.drop_yes], gtk.gdk.ACTION_MOVE)
        else:
            treeview.enable_model_drag_dest (
                [self.drop_no], gtk.gdk.ACTION_MOVE)
    
    def __drag_data_received_cb (self, treeview, drag_context, x, y,
                              selection_data, info, evtime):
        dest_path, drop_pos = treeview.get_dest_row_at_pos(x, y)
        model, source = treeview.get_selection().get_selected()
        dest = model.get_iter(dest_path)
        
        if self.checkDNDSanity (model, source, dest, drop_pos):
            self.__copy_data (treeview, model,
                              source, dest, drop_pos)
            drag_context.finish(True, True, evtime)
        else:
            drag_context.finish(False, False, evtime)

    def __setup_dnd_rules (self, treeview):
        treeview.enable_model_drag_source (
            gtk.gdk.BUTTON1_MASK, [self.drop_yes],
            gtk.gdk.ACTION_MOVE)
        treeview.enable_model_drag_dest (
            [self.drop_yes], gtk.gdk.ACTION_MOVE)

        # Connect drag signal, they will check if we may put dragged
        # widget, or not
        treeview.connect ('drag-data-received',
                          self.__drag_data_received_cb)
        treeview.connect ('drag-motion',
                          self.__drag_motion_cb)

    def __init__ (self, treeview):
        self.__setup_dnd_rules(treeview)

class MNGtkMain:
    
    def destroy(self, widget, data=None):
        gtk.main_quit()

    def __init__ (self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)

        self.window.set_title("MusicNote")
        self.window.set_size_request(700, 500)

        self.window.connect("destroy", self.destroy)

        self.window.show()

        
    def test(self):
        self.categories = gtk.TreeStore(str)

        for category in range (5):
            cat = self.categories.append(None, ['Row %d' % category])
            for element in range (5):
                self.categories.append(cat, ['Child row %d' % element])
        self.treeview = gtk.TreeView(self.categories)
        
        self.tvcolumn = gtk.TreeViewColumn('Names')
        self.treeview.append_column(self.tvcolumn)
        self.cell = gtk.CellRendererText()
        self.tvcolumn.pack_start(self.cell, True)
        self.tvcolumn.add_attribute(self.cell, 'text', 0)

#        self.treeview.set_search_column(0)
#        self.tvcolumn.set_sort_column_id(0)
#        self.treeview.set_reorderable(True)
        
        self.window.add(self.treeview)

        self.mntv = MNTreeView (self.treeview)
        
        self.window.show_all()
        

    def main(self):
        self.test()
        gtk.main()


if __name__ == "__main__":
    mnwin = MNGtkMain ()
    mnwin.main()
