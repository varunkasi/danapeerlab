#!/usr/bin/env python
import settings
import os
import pickle
from odict import OrderedDict
from scriptservices import CACHE
from scriptservices import make_unique_str
from widget import Widget
from view import View
from view import render
from view import convert_to_html
from biology.dataindex import DataIndex
from django.utils.html import linebreaks

def options_from_table(table):
    other_markers = table.get_markers('other')
    signal_markers = table.get_markers('signal')
    surface_markers = table.get_markers('surface')
    none_markers = table.get_markers_not_in_groups('other', 'signal', 'surface', 'surface_ignore', 'signal_ignore')
    return [
        ('t-SNE', sorted(other_markers)),
        ('Surface Markers', sorted(surface_markers)),
        ('Signal Markers', sorted(signal_markers)),
        ('', sorted(none_markers))]
    
class Select(Widget):
  def __init__(self, id, parent):
    Widget.__init__(self, id, parent)
    self.values.choices = None


  def guess_or_remember_choices(self, text, options, guess_hint=''):
    select_dict = CACHE.get('select_dict', none_if_not_found=True)
    key = make_unique_str((text, options, guess_hint))
    print key
    if not select_dict:
      select_dict = {}
    if self.values.choices == None:
      self.values.choices = select_dict.get(key, None)
    else:
      select_dict[key] = self.values.choices
      CACHE.put('select_dict', select_dict, 'select')
    print self.values.choices

    
  def view(self, text, save_button, options, multiple=True, group_buttons=[], choices=None):
    def add_titles_if_needed(items):
      if items and type(items[0]) != tuple:
        items = zip(items, items)
      return items
    
    def add_selected_state(items):
      return [(o[0], o[1], o[0] in choices) for o in items]
      
    if choices == None:
      choices = self.values.choices
    if choices == None:
      choices = []
      
    options = add_titles_if_needed(options)
    #print options
    # Now options is either a list of title,val or a list of (group_name, group_values)
    if not type(options[0][1]) in (tuple, list):
      options = [('None', options)]
    #print options
    # Now options is either a list of (group_name, list(titles)) or a list of (group_name, list(titles, vals))
    options = [(o[0], add_titles_if_needed(o[1])) for o in options]
    #print options
    # Now add selected state the list so that we have (group_name list(titles, vals, select))
    options = [(o[0], add_selected_state(o[1])) for o in options]
    #print options
    
    html = render('select.html', {
        'height' : 300,
        'groups' : group_buttons,
        'text' : text,
        'saver_id' : save_button.id,
        'id' : self._get_unique_id(),
        'multiple' : multiple,
        'items' : options,
        'widget_id' : self.id})
    v = View(
        self, 
        html, 
        ['jquery.multiselect.css'],
        ['jquery.multiselect.js'])
    return v
