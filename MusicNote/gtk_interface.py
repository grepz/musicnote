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

try:
    import pygtk
    pygtk.require('2.0')
except:
    pass

# TODO: Handle what wasn't found
try:
    import gobject
    import gtk
    import gtk.glade
except:
    print 'Can\'t find python gtk bindings.'
    exit(1)

###############################################################################

class MNError:
    def __init__ (self, msg):
        print msg
        
class MNListStore (gtk.ListStore):
    names_list = None
    
    def __init__ (self, names_list=None):
        # Chain costructor
        gtk.ListStore.__init__(self, str)
        self.names_list = names_list
        
        if names_list:    
            for name in names_list:
                self.append([name])

    def get_raw_list (self):
        return self.names_list

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
    
class DNDRules:
    drop_yes = ('drop_yes', gtk.TARGET_SAME_APP, 0)
    drop_no = ('drop_no', gtk.TARGET_SAME_APP, 0)
    target = None

    # Callbacks
    def __drag_motion_cb (self, treeview, drag_context,
                          x, y, evtime):
        try:
            dest_path, drop_pos = treeview.get_dest_row_at_pos(x, y)
        except:
            return

        model, source = treeview.get_selection().get_selected()
        dest = model.get_iter(dest_path)
        
        if self.checkDNDSanity(model, source, dest, drop_pos):
            treeview.enable_model_drag_dest (
                [self.drop_yes], gtk.gdk.ACTION_MOVE)
        else:
            treeview.enable_model_drag_dest (
                [self.drop_no], gtk.gdk.ACTION_MOVE)

    def __drag_data_received_cb (self, treeview, drag_context, x, y,
                                 selection_data, info, evtime):
        try:
            dest_path, drop_pos = treeview.get_dest_row_at_pos(x, y)
            model, source = treeview.get_selection().get_selected()
            dest = model.get_iter(dest_path)
        except:
            return
        
        if self.checkDNDSanity (model, source, dest, drop_pos):
            self.__copy_data (treeview, model,
                              source, dest, drop_pos)
            drag_context.finish(True, True, evtime)
        else:
            drag_context.finish(False, False, evtime)


    ## ---------------------------------------
    
    def __iter_is_child (self, model, iter):
        if len (model.get_path (iter)) > 1:
            return True
        else:
            return False

    def __copy_data (self, treeview, model,
                     source, dest, drop_pos):
        pass

    def __setup_dnd_rules (self, treeview):
        treeview.enable_model_drag_source (gtk.gdk.BUTTON1_MASK,
                                           [self.target],
                                           gtk.gdk.ACTION_DEFAULT|
                                           gtk.gdk.ACTION_MOVE)
        treeview.enable_model_drag_dest ([self.target],
                                         gtk.gdk.ACTION_DEFAULT)

        # Connect drag signal, they will check if we may put dragged
        # widget, or not
        treeview.connect ('drag-data-received',
                          self.__drag_data_received_cb)
        treeview.connect ('drag-motion',
                          self.__drag_motion_cb)
        
    def checkDNDSanity (self, model, source, dest, drop_pos):
        try:
            source_path = model.get_path(source)
            dest_path = model.get_path(dest)
            target_len, source_len = len(dest_path), len(source_path)
        except:
            return False
        
        return False
#         # If i am trying to drop element to the child node with the
#         # same parent
#         if dest_path[0] == source_path[0]:
#             return False
#         # We can't drop elements into child nodes
#         if target_len > 1 and \
#                (drop_pos == gtk.TREE_VIEW_DROP_INTO_OR_BEFORE or \
#                 drop_pos == gtk.TREE_VIEW_DROP_INTO_OR_AFTER):
#             return False
#         # Root nodes can't be simply reordered
#         if (target_len == 1 and source_len == 1) and \
#                drop_pos == gtk.TREE_VIEW_DROP_BEFORE or \
#                drop_pos == gtk.TREE_VIEW_DROP_AFTER:
#             return False
        
#        return True

    
    def __init__ (self, treeview):
        self.__setup_dnd_rules (treeview)

#class MNEditorElements (DNDRules):
class MNEditorElements ():
    data = None
    
    def __set_columns (self):
            tvcolumn = gtk.TreeViewColumn(self.name)
            self.treeview.append_column(tvcolumn)
            cell = gtk.CellRendererText()
            tvcolumn.pack_start(cell, True)
            tvcolumn.add_attribute(cell, 'text', 0)

    def fill_view (self):
        self.liststore = MNListStore (self.data)
        self.treeview.set_model (self.liststore)
    
    def __init__ (self, treeview, name):
#        DNDRules.__init__ (self, treeview)
        self.name = name
        self.treeview = treeview
        self.__set_columns()
        
    def set_data (self, data):
        pass

class MNGroupLeads (MNEditorElements):
#    target = ('MY_TREE_MODEL_ROW', gtk.TARGET_SAME_WIDGET, 0)
    def set_data (self, data):
        self.data = [x[0] for x in data]
        self.fill_view ()

    def change_element (self, old, new):
        self.data = map (lambda x: (x == old and [new] or [x])[0], self.data)


class MNLeadSubs (MNEditorElements):
    group_lead = None

    def set_data (self, data):
        self.data = filter (lambda x: x[0] == self.group_lead, data)[0][1]
        self.fill_view ()
    
    def set_group_lead (self, lead):
        self.group_lead = lead
    

class GroupsEditor:
    group_leads = None
    lead_subs   = None

    data = None

    def __init_views (self):
        self.choosen_view = MNChoosenView (
            self.wTree.get_widget (self.choosen_names_name),
            'Categories names')
        self.sub_view = MNSubView (
            self.wTree.get_widget (self.sub_names_name),
            'Sub elements names')
    
    def fill_with_data (self, data):
        self.data = data
        self.group_leads.set_data (data)
        
    
    def __init__ (self, group_leads_view, lead_subs_view,
                  data=None):
        self.group_leads = MNGroupLeads (
            group_leads_view, 'Group leaders')
        self.lead_subs = MNLeadSubs (
            lead_subs_view, 'Group sub names')
        
    # Callbacks
    # TODO: Here we have some ugliness, optimize, maybe using hash, but then I
    # will need to convert hash to list and sort it
    def group_leads_activated_cb (self, treeview, path,
                                  view_column, *data):
        model, source = treeview.get_selection().get_selected()
        value = model.get_value (source, 0)
        
        self.lead_subs.set_group_lead (value)
        self.lead_subs.set_data (self.data)

    def lead_subs_activated_cb (self, treeview, path,
                                view_column, *data):
        model, source = treeview.get_selection().get_selected()
        value = model.get_value (source, 0)

        self.data = map (lambda x: (x[0] == self.lead_subs.group_lead and \
                                    [value, x[1]] or x),
                         self.data)
        self.lead_subs.set_group_lead (value)
        self.group_leads.set_data(self.data)
        self.group_leads.fill_view ()

class MNGUI:
    glade_file            = 'mn_main.glade'
    main_window_gladename = 'MNMainWindow'
    toolbar_gladename     = 'MNMainToolBar'
    group_leads_gladename = 'MNGroupLeadsView'
    lead_subs_gladename   = 'MNLeadSubsView'

    main_window = None
    groups_editor = None

    def destroy (self, widget, data=None):
        gtk.main_quit()
        
    def __init__ (self):
        # Widget tree from glade resource file
        self.wTree = gtk.glade.XML (self.glade_file)
        
        self.main_window = self.wTree.get_widget (
            self.main_window_gladename)
        
        self.groups_editor = GroupsEditor (
            self.wTree.get_widget (self.group_leads_gladename),
            self.wTree.get_widget (self.lead_subs_gladename))
        
        self.cb = {
            'handle_win_destroy'   : self.destroy,
            'handle_toolbar_quit'  : self.destroy,
            'group_lead_activated' : \
                  self.groups_editor.group_leads_activated_cb,
            'lead_subs_activated'  : \
            self.groups_editor.lead_subs_activated_cb
        }
        self.wTree.signal_autoconnect (self.cb)
        
        self.main_window.show_all ()

    def connect_data (self, data):
        '''Put data to GUI through this function'''
        self.groups_editor.fill_with_data(data)

if __name__ == '__main__':
    mn= MNGUI()
    mn.connect_data ([ ['Therion', ['Therrion', 'Tharion', 'Therion']],
                       ['Зимовьё зверей', ['ЗЗ', 'Зимовьё', 'Зимовьё зверей',
                                           'Зимовьё Зверей']],
                       ['Дудук', ['Дудук_', 'Дудук', '_Дудук']],
                       ['IN_FLAMES', ['In Flames', 'In_Flames', 'IN_FLAMES']]
                      ])
    gtk.main()
