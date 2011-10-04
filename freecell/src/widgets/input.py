#!/usr/bin/env python
from odict import OrderedDict
from widget import Widget
from view import View
from view import render
from cache import CACHE
from cache import make_unique_str
from biology.dataindex import DataIndex
from django.utils.html import linebreaks

class Input(Widget):
  def __init__(self, id, parent):
    Widget.__init__(self, id, parent)
    self.values.value = None

  def guess_or_remember(self, key, default_value=None):
    return Widget._guess_or_remember(self, 'value', key, default_value)
      
  def value_as_str(self):
    return self.values.value

  def value_as_int(self):
    return int(self.values.value)

  def value_as_float(self):
    return float(self.values.value)
    
  def value_as_float_list(self):
    splitted = self.values.value.split(',')
    return [float(val) for val in splitted]

  def view(self, text, apply, predefined_values=[], id=None, numeric_validation=True, comment='', non_empty_validation=True, size=20):
    if not id:
      id = self._get_unique_id()
    val = ''   
    if self.values.value:
      val = self.values.value
    html = render('input.html', {
        'size' : size,
        'id' : id,
        'value' : str(val),
        'saver_id' : apply.id,
        'text' : text, 
        'predefined_values' : predefined_values,
        'numeric_validation' : numeric_validation,
        'non_empty_validation' : non_empty_validation,
        'comment' : comment,
        'widget_id' : self.id})
    v = View(
        self, 
        html, 
        [],
        [])
    return v
