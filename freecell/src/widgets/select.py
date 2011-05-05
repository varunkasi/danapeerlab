#!/usr/bin/env python
from odict import OrderedDict
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
    self.values.choices = []
    
   
  def view(self, text, save_button, options, multiple=True, group_buttons=[], choices=None):
    def add_titles_if_needed(items):
      if items and type(items[0]) != tuple:
        print 'yo'
        print items
        print 'yi'
        items = zip(items, items)
      return items
    
    def add_selected_state(items):
      return [(o[0], o[1], o[1] in choices) for o in items]
      
    if choices==None:
      choices = self.values.choices    
    
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
