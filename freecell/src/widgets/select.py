#!/usr/bin/env python
from odict import OrderedDict
from widget import Widget
from view import View
from view import render
from view import convert_to_html
from biology.dataindex import DataIndex
from django.utils.html import linebreaks

class Select(Widget):
  def __init__(self, id, parent):
    Widget.__init__(self, id, parent)
    self.values.choices = []
    
   
  def view(self, text, save_button, options, multiple=True, choices=None):
    if choices==None:
      choices = self.values.choices
    if options and type(options[0]) != tuple:
      options = zip(options, options)
    options = [(o[0], o[1], o[1] in choices) for o in options]
    html = render('select.html', {
        'text' : text,
        'saver_id' : save_button.id,
        'id' : self._get_unique_id(),
        'multiple' : multiple,
        'items' : options,
        'widget_id' : self.id})
    v = View(
        self, 
        html, 
        ['ui.multiselect.css', 'ui-lightness/jquery-ui-1.8.11.custom.css'],
        ['jquery-ui-1.8.11.custom.min.js', 'ui.multiselect.js'])
    return v
