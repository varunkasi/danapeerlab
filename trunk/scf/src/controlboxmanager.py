#!/usr/bin/env python
from collections import namedtuple
import logging
import threading
import pygtk
import gtk
import gobject  
from autoreloader import AutoReloader

    
class ControlBoxManager(object):
  def __init__(self, table):
    self.table = table
    self.table.set_col_spacing(0, 50)
    self.widgets = []
    
  def __init__vbox(self, vbox):
    self.vbox = vbox
    self.widgets = []
    
  def add_widget(self, title, widget):
    self.table.set_row_spacing(0, 5) 
    label = gtk.Label(title)
    label.set_alignment(0,0)
    label.show()
    widget.show()
    if self.widgets:
      n_rows = self.table.get_property('n-rows')
      self.table.resize(n_rows + 1, 2)
    
    n_rows = self.table.get_property('n-rows')
    label_align = gtk.Alignment(xalign = 0, yalign=0.5, xscale=0, yscale=0)
    label_align.add(label)
    label_align.show()

    widget_align = gtk.Alignment(xalign = 0, yalign=0.5, xscale=0, yscale=0)
    widget_align.add(widget)
    widget_align.show()

    
    self.table.attach(label_align, 0, 1, n_rows-1, n_rows,
        xoptions=gtk.FILL|gtk.EXPAND, yoptions=0, xpadding=5, ypadding=5)
    self.table.attach(widget_align, 1, 2, n_rows-1, n_rows,
        xoptions=gtk.FILL|gtk.EXPAND, yoptions=0, xpadding=5, ypadding=5)
    self.widgets.append(widget_align)
    self.widgets.append(label_align)

  def add_widget_vbox(self, title, widget):
    label = gtk.Label(title)
    
    label.show()
    widget.show()
    table = gtk.Table(1, 1, True)
    table.show()
    table.attach(label, 0, 1, 0, 1,
        xoptions=gtk.EXPAND, yoptions=gtk.EXPAND)
    table.attach(widget, 1, 2, 0, 1,
        xoptions=gtk.EXPAND, yoptions=gtk.EXPAND)
    self.vbox.pack_start(table, False, False)
    self.widgets.append(table)

  def clear(self):
    for w in self.widgets:
      self.table.remove(w)
    self.widgets = []
    self.table.resize(1,1)
    
    
  def clear_vbox(self):
    for w in self.widgets:
      self.vbox.remove(w)
    self.widgets = []
    
    
