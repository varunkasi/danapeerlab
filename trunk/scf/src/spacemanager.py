#!/usr/bin/env python
from collections import namedtuple
import logging
import threading
import pygtk
import gtk
import gobject  
from autoreloader import AutoReloader

WidgetLocation = namedtuple('WidgetLocation',
    ['space_name','col', 'row', 'end_col', 'end_row'])

WidgetEntry = namedtuple('WidgetEntry',
    ['widget', 'location', 'data'])
    
class SpaceEntry(object):
  def __init__(self, name, table, scrolled, screen_rows, screen_cols, rows, cols):
    self.name = name
    self.table = table
    self.scrolled = scrolled
    self.screen_rows = screen_rows
    self.screen_cols = screen_cols
    self.rows = rows
    self.cols = cols

class SpaceManager(AutoReloader):
  """Manages the spaces on the screen where scripts can put
  widgets/visualizations. The spaces are made of tables."""
  def __init__(self, notebook):
    self.space_name_to_entry = {} # saves the tables of all spaces.
    self.space_name_to_window = {} # saves the windows for windowed spaces.
    
    self.location_to_widget = {} #links a widget location to a widget entry.     
    self.notebook = notebook
    self.lock = threading.RLock()

  def space_exists(self, name):
    with self.lock:
      return name in self.space_name_to_entry
  
  def viewport_size_allocate(self, widget, allocation, space_name):
    entry = self.space_name_to_entry[space_name]
    vertical_ratio = float(entry.rows) / float(entry.screen_rows)
    horizontal_ratio = float(entry.cols) / float(entry.screen_cols)
    entry.table.set_size_request(
        int(allocation.width * horizontal_ratio * 0.9),
        int(allocation.height * vertical_ratio * 0.9))
    print allocation
    
  def add_space(self, name, is_tabbed=True, rows=3, columns=3, title = None):
    """Creates a new widget space.

    A space is a table tha can contain widgets. The table can appear in a
    floating window or in a tab (if is_tabbed is true). The name parameter is
    used to reference the space.
    
    This function must run in the GUI thread.
    """
    with self.lock:
      if not title:
        title = name
      if name in self.space_name_to_entry:
        raise Exception('Space name %s is already used' % name)
      new_table = gtk.Table(rows, columns, True)
      new_scrolled = gtk.ScrolledWindow()
      new_scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
      new_scrolled.add_with_viewport(new_table)
      new_table.show()
      new_scrolled.show()
      self.space_name_to_entry[name] = SpaceEntry(
          name, new_table, new_scrolled, rows, columns, rows, columns)
      new_table.get_parent().connect(
          'size-allocate', self.viewport_size_allocate, name)
      if is_tabbed:
        self.notebook.append_page(new_scrolled, gtk.Label(title))
      else:
        new_window = gtk.Window()
        new_window.add(new_table)
        new_window.set_title(title)
        new_window.connect("destroy", self.on_windowed_space_destroyed, name)
        self.space_name_to_window[name] = new_window
        new_window.show()

  def on_windowed_space_destroyed(self, widget, space_name):
    logging.debug('on_windowed_space_destroyed for %s ' % space_name)
    self.remove_space(space_name)

  def clear_spaces(self):
    """Removes all spaces"""
    with self.lock:
      names_to_delete = self.space_name_to_entry.keys()
      for name in names_to_delete:
        self.remove_space(name)
        
  def remove_space(self, name):
    """Removes the specified space.
    
    This must run in the GUI thread.
    """
    with self.lock:
      if not name in self.space_name_to_entry:
        raise Exception('No space with the name %s')
      # first we remove all the widgets in the space.
      entries_to_remove = self._widgets_in_space(name)
      for entry in entries_to_remove:
        self.remove_widget(entry)
      # now remove the space
      if name in self.space_name_to_window:
        #it's a windowed space.
        self.space_name_to_window[name].destroy()
        del self.space_name_to_window[name]
      else:
        #It's a tabbed space
        self.notebook.remove_page(
            self.notebook.page_num(self.space_name_to_entry[name].scrolled))
            # add disconnect here
      del self.space_name_to_entry[name]

  def add_widget(self, widget, location, data=None):
    """Puts the given widget in the given location (WidgetLocation).
    
    Custom data can be attached to the widget.
    A WidgetEntry used for referencing the widget is returned.
    This must run in the GUI thread.
    """
    # TODO(daniv): add a verify location function that also checks for the space
    # boundries
    with self.lock:
      if not location.space_name in self.space_name_to_entry:
        self.add_space(
            location.space_name, True, location.end_col * 2, location.end_row * 2)
      if location in self.location_to_widget:
        self.remove_widget(self.location_to_widget[location])
        #raise Exception('The location %s is already in use' % str(location))
      entry = WidgetEntry(widget, location, data)
      self.location_to_widget[location] = entry
      widget.show()
      table_entry = self.space_name_to_entry[location.space_name]
      if location.end_col > table_entry.cols or location.end_row > table_entry.rows:
        table_entry.cols = max(table_entry.cols, location.end_col)
        table_entry.rows = max(table_entry.rows, location.end_row)
        table_entry.table.resize(table_entry.rows, table_entry.cols)
      table_entry.table.attach(
          widget, location.col, location.end_col, location.row, location.end_row)
      return entry

  def remove_widget(self, widget_entry):
    """Removes the specified widget. Must run in the GUI thread"""
    with self.lock:
      del self.location_to_widget[widget_entry.location]
      table = self.space_name_to_entry[widget_entry.location.space_name].table
      table.remove(widget_entry.widget)

  def get_widget(self, location, deprecated=None):
    """Returns the widget in the given location."""
    with self.lock:
      if not location in self.location_to_widget:
        return None
      #if self.location_to_widget[location].data != data_test:
      #  return None
      return self.location_to_widget[location].widget

  def _widgets_in_space(self, space_name):
    """Returns a list of all the widget entries in the given space."""
    with self.lock:
      return [
          v 
          for k,v
          in self.location_to_widget.iteritems() 
          if k.space_name == space_name]
