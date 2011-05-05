#!/usr/bin/env python
from odict import OrderedDict
from widget import Widget
from view import View
from view import render
from view import convert_to_html
from biology.dataindex import DataIndex
from django.utils.html import linebreaks

class Input(Widget):
  def __init__(self, id, parent):
    Widget.__init__(self, id, parent)
    self.values.value = None
    
  def value_as_float(self):
    return float(self.values.value)

  def view(self, text, apply, predefined_values=[], id=None, numeric_validation=True):
    if not id:
      id = self._get_unique_id()
    val = ''   
    if self.values.value:
      val = self.values.value
    html = render('input.html', {
        'id' : id,
        'value' : str(val),
        'saver_id' : apply.id,
        'text' : text, 
        'predefined_values' : predefined_values,
        'numeric_validation' : numeric_validation,
        'widget_id' : self.id})
    v = View(
        self, 
        html, 
        [],
        [])
    return v
