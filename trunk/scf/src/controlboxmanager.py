#!/usr/bin/env python
from collections import namedtuple
import logging
import threading
import pygtk
import gtk
import gobject  
from autoreloader import AutoReloader



class ControlBoxManager(object):
  def __init__table(self, table):
    self.table = table
    #self.table.set_col_spacing(0, 0)
    self.widgets = []
    
  def __init__(self, scrolled_win_control_box):
    self.vbox = gtk.VBox()
    self.vbox.show()
    align = gtk.Alignment(0,0,1,1)
    align.show()
    align.add(self.vbox)
    align.set_padding(3,3,3,3)
    scrolled_win_control_box.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    scrolled_win_control_box.add_with_viewport(align)
    self.widgets = []
      
  def add_widget_table(self, title, widget):
    self.table.set_row_spacing(0, 5) 
    label = gtk.Label(title)
    label.set_alignment(0,0)
    label.set_size_request(65,-1)
    label.set_line_wrap(True)
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
    self.table.show_all()
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
  
  def add_widget(self, title, widget):
    label = gtk.Label()
    label.set_use_markup(True)   
    label.set_alignment(0, 0)
    label.set_line_wrap(True)    
    label.set_markup('<b>%s</b>' % title)
    label.show()
    #expander = gtk.Expander('<b>%s</b>' % title)
    #expander.set_use_markup(True)   
    #expander.set_expanded(True)
    #expander.show()
    widget_align = gtk.Alignment(0,0,1,1)
    widget_align.set_padding(3,13,0,0)
    widget_align.show()
    widget_align.add(widget)
    #expander.add(widget_align)
    widget.show()
    #self.vbox.pack_start(expander, False, False, padding=5)
    self.vbox.pack_start(label, False, False, padding=0)
    self.vbox.pack_start(widget_align, False, False, padding=0)
    self.widgets.append(label)
    self.widgets.append(widget_align)
    #self.widgets.append(widget)
    return label

  def clear_table(self):
    for w in self.widgets:
      self.table.remove(w)
    self.widgets = []
    self.table.resize(1,1)
    
    
  def clear(self):
    for w in self.widgets:
      self.vbox.remove(w)
    self.widgets = []
    
    
