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
    """ Used to suggest a default value for the widget, or record the selected 
    value. 
    If there is no value in values.value:
      The method will look for a value under 'key', and set values.value
      to that value. If there is no value, values.value is set to default_value.
    If there is a value in values.value:
      The value is saved under 'key'.
    """
    input_dicr = CACHE.get('input_dict', none_if_not_found=True)
    key = make_unique_str(key)
    if not input_dicr:
      input_dicr = {}
    if self.values.value == None:
      self.values.value = input_dicr.get(key, default_value)
    else:
      input_dicr[key] = self.values.value
      CACHE.put('input_dict', input_dicr, 'input')
      
  def value_as_str(self):
    return self.values.value

  def value_as_float(self):
    return float(self.values.value)

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
