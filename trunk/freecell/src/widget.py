#!/usr/bin/env python
from view import View
from view import render
from attrdict import AttrDict

ID_SEPERATOR = '-'

class Widget(object):
  """ A widget is an object that can generate HTML (in a View instance) and 
  maintain state. 
  
  Each widget has sub widgets, and a dictionary of values.
  Sub widgets are saved in the 'widgets' dictionary.
  Values are saved in the 'valeus' dictionary.
  Values can be changed through an http request. The request will contain the
  id of the widget (in the format: preant1_id-parent2_id-widget_id) along with
  a key and value. This is managed by 'set_value' in report.py. The javascript
  command is in src/static/js/freecell.js/freecell.
  
  How to implement a widget
  -------------------------
  1. Inherit from Widget. 
  2. Add an __init__ like this:
     def __init__(self, id, parent, arg1, arg2, arg3, arg4):
       Widget.__init__(self, id, parent)
  3. Add a view method that returns a View object.
  4. If you want, add a on_load method. 
  
  
  How to change the state of a widget
  -----------------------------------
  Create HTML/JS in a view that will call the set_value
  function defined in static/js/freecell.js. This function 
  requires the widget id, which you can access using the 'id' 
  member. 
  Usually you will want to set state using an ApplyButton. 
  See ApplyButton.py for details.
  
  """
  
  def __init__(self, id, parent):
    """ Inits a new widget.
    The constructor should never be called directly. To add a sub-widgegt use
    _add_widget. To create a root widget see report.py
    """
    self.id = id
    self.parent = parent
    self.unique_counter = 0
    self.widgets = AttrDict()
    self.values = AttrDict()
         
  def has_method(self, name):
    """ Tests is the widget has a method with the given name.
    """
    return name in dir(self) and callable(getattr(self, name))

  def set_value(self, name, val):
    self.values[name] = val
    if self.has_method('on_set_value'):
      self.on_set_value(name, val)

  def set_default(self, name, val):
    """ Sets a value if no value was defined. """
    if name in self.values and self.values[name] == None:
      self.set_value(name, val)
        
  def _normalize_id(self, id):
    """ Removes illegal characters from the widget id. The id can appear in HTML, 
    as file name, as part of css. """
    return id.replace(' ', '').replace('-','').replace('/','_').replace('\\', '_')

  def _add_widget(self, name, new_widget_type, *args, **kargs):
    """ Adds a sub widget. """
    name = self._normalize_id(name)
    if name in self.widgets:
      raise Exception('name %s is already in use' % name)
    new_id = '%s%s%s' % (self.id, ID_SEPERATOR, name)
    new_widget = new_widget_type(new_id, self, *args, **kargs)   
    self.widgets[name] = new_widget
    return new_widget
  
  def _remove_widget(self, widget):
    """ Removes a sub widget. """
    widget_name = widget.id.split(ID_SEPERATOR)[-1]
    del self.widgets[widget_name]
  
  def run_on_load(self):
    """ Called by a Report when a widget is reloaded. """
    for w in self.widgets.values():
      w.run_on_load()
    if 'on_load' in dir(self):
      self.on_load()
  
  def _get_unique_id(self):
    """ Returns a unique id. Multiple calls to this function 
    will no generate the same id.
    """
    if not self.unique_counter:
      ret = self.id
    else:
      ret = '%s_%d' % (self.id, self.unique_counter)
    self.unique_counter += 1
    return ret

  def __str__(self):
    my_str = '%s' % '{%s}' % ','.join(['%s: %s' % (k,v) for k,v in self.values.items()])
    sub_widgets = '\n'.join('%s - %s' % (k,str(v)) for k,v in self.widgets.items())
    if sub_widgets:
      sub_widgets = '\n'.join(['  %s' % s for s in sub_widgets.split('\n')])
      return '%s\n%s' % (my_str, sub_widgets)
    else:
      return my_str
