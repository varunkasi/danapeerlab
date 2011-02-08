#!/usr/bin/env python
from view import View
from view import render
from attrdict import AttrDict

WIDGETS = {}

class Widget(object):
  def __init__(self):
    global WIDGETS
    list = WIDGETS.setdefault(self.__class__.__name__, [])
    list.append(self)
    self.id = '%s_%d' % (self.__class__.__name__, len(list) - 1)
    self.unique_counter = 0
    self.widgets = AttrDict()
  
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
    

    
