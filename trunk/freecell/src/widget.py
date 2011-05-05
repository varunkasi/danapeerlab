#!/usr/bin/env python
from view import View
from view import render
from attrdict import AttrDict

ID_SEPERATOR = '-'

class Widget(object):
  def __init__(self, id, parent):
    self.id = id
    self.parent = parent
    self.unique_counter = 0
    self.widgets = AttrDict()
    self.values = AttrDict()
 
#  def __getstate__(self):
#    dict_copy = self.__dict__
#    return {
#        'unique_counter' : 0,
#        'on_set_values' : {},
#        'widgets': self.__dict__['widgets'],
#        'values' : self.__dict__['values']}
        
  def has_method(self, name):
    return name in dir(self) and callable(getattr(self, name))

  def set_default(self, name, val):
    if name in self.values and self.values[name] == None:
      self.set_value(name, val)
  def set_value(self, name, val):
    self.values[name] = val
#    if name in self.on_set_values:
#      self.on_set_values[name]()
      
  
#  def _register_on_set_value(self, name, func):
#    self.on_set_values[name] = func
         
  def _normalize_id(self, id):
    return id.replace(' ', '').replace('-','')

  def _add_widget(self, name, new_widget_type, *args, **kargs):
    name = self._normalize_id(name)
    if name in self.widgets:
      raise Exception('name %s is already in use')
    new_id = '%s%s%s' % (self.id, ID_SEPERATOR, name)
    new_widget = new_widget_type(new_id, self, *args, **kargs)   
    self.widgets[name] = new_widget
    return new_widget
  
  def run_on_load(self):
    for w in self.widgets.values():
      w.run_on_load()
    if 'on_load' in dir(self):
      self.on_load()
  
  def _get_unique_id(self):
    if not self.unique_counter:
      ret = self.id
    else:
      ret = '%s_%d' % (self.id, self.unique_counter)
    self.unique_counter += 1
    return ret
    
  def _view_from_template(
      self, template_file, context, css_files=[], js_files=[]):
    html = render(template_file, context)
    return View(self, html, css_files, js_files)

  def __str__(self):
    my_str = '%s' % '{%s}' % ','.join(['%s: %s' % (k,v) for k,v in self.values.items()])
    sub_widgets = '\n'.join('%s - %s' % (k,str(v)) for k,v in self.widgets.items())
    if sub_widgets:
      sub_widgets = '\n'.join(['  %s' % s for s in sub_widgets.split('\n')])
      return '%s\n%s' % (my_str, sub_widgets)
    else:
      return my_str