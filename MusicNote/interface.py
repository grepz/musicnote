#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

import urwid.raw_display
import urwid

# Just tests

class MNWindow(object):
    x0 = y0 = x1 = y1 = None
    
    def __init__ (self, x0, x1, y0, y1):
        self.x0, self.x1 = \
                 map(lambda x: ((x < 1 or x > cols) and [cols] or [x])[0],
                     (x0, x1))
        self.y0, self.y1 = \
                 map(lambda y: ((y < 1 or y > rows) and [rows] or [y])[0],
                     (y0, y1))
        

########################################################

cols = rows = None

pile = None
text = None

class MNGroupView:
    groups = None

    palette = [
		('body', 'black', 'light gray'),
		('selected', 'black', 'dark green', ('bold','underline')),
		('focus', 'light gray', 'dark blue', 'standout'),
		('selected focus', 'yellow', 'dark cyan', 
				('bold','standout','underline')),
		('head', 'yellow', 'black', 'standout'),
		('foot', 'light gray', 'black'),
		('key', 'light cyan', 'black','underline'),
		('title', 'white', 'black', 'bold'),
		('dirmark', 'black', 'dark cyan', 'bold'),
		('flag', 'dark gray', 'light gray'),
		('error', 'dark red', 'light gray'),
		]

    def run (self):
        self.ui.set_mouse_tracking()
        size = map (lambda x: x - 0, self.ui.get_cols_rows())
        while 1:
           focus, _ign = self.listbox.body.get_focus()
           canvas = self.view.render(size, focus=1 )
           self.ui.draw_screen(size, canvas )
            
    
    def main (self):
            self.ui = urwid.raw_display.Screen()
            self.ui.register_palette( self.palette )
            self.ui.run_wrapper( self.run )
    
    def __init__ (self, groups):
        if type(groups).__name__ != 'dict':
            raise Exception('MNInterface', 'Parameter is not a dict')
        self.groups = groups
        self.listbox = urwid.ListBox ([MNGroupElement(x) for x in groups])
        self.listbox.offset_rows = 1

        self.header = urwid.Text( "Header" )
        self.footer = urwid.AttrWrap (urwid.Text ("Footer"),
                                      'foot')
        self.view = urwid.Frame (urwid.AttrWrap( self.listbox, 'body' ), 
                                 header=urwid.AttrWrap(self.header, 'head' ), 
                                 footer=self.footer)

class Blob(urwid.WidgetWrap):
    def __init__(self, dw, attr, flow=True, thin=False):
        dw = urwid.Padding( dw, ('fixed left', 2), ('fixed right', 2))
        if flow:
            dw = urwid.Pile([urwid.Divider(), dw, urwid.Divider()])
        else:
            dw = urwid.Filler( dw, 'middle' )
        dw = urwid.AttrWrap( dw, attr )
        dw = urwid.Padding( dw, ('fixed left', 2), ('fixed right', 2))
        if flow and not thin:
            dw = urwid.Pile([urwid.Divider(), dw, urwid.Divider()])
        elif not thin:
            dw = urwid.Filler( dw, ('fixed top', 0),
                    ('fixed bottom', 1))
        urwid.WidgetWrap.__init__(self, dw)
        
#mn = MNGroupView({'q' : 1, 'w' : 2,
#                  'e' : 1, 'r' : 2,
#                  't' : 1, 'y' : 2,
#                  'u' : 1, 'i' : 2,
#                  'o' : 1, 'p' : 2,
#                  'a' : 1, 's' : 2,
#                  'd' : 1, 'f' : 2,
#                  'g' : 1, 'h' : 2})
#mn.main()

groups = { 'a' : 1, 'b' : 2, 'c' : 3}

class MNGroupElement (urwid.WidgetWrap):
    name = None
    selected = False

    def __init__ (self, name):
        self.name = name
        widget = urwid.Text(name)
        self.widget = widget
        self.__super.__init__(urwid.AttrWrap(widget, None))

    def selectable(self):
        return True


class MNGroupsView (urwid.Frame):
    def __init__ (self, groups, header):
        self.listbox = urwid.ListBox ([MNGroupElement(x) for x in groups])
        self.header = urwid.Text( "Header" )

        self.__super.__init__ (self.listbox, 
                               header=self.header)

class MNInterface:

    def main (self):
        self.ui = urwid.raw_display.Screen()
        self.ui.run_wrapper( self.run )

    def draw_screen(self, size):
        canvas = self.mn.render (size)
        self.ui.draw_screen (size, canvas)


    def run (self):
        cols,rows = self.ui.get_cols_rows()
        
        self.mn = MNGroupsView(groups, "Header")
        while True:
            self.draw_screen ((cols,rows))
            keys = self.ui.get_input()


def main():
    MNInterface().main()


if '__main__'==__name__:
    main()
