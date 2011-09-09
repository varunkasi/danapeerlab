#!/usr/bin/env python
import settings
import os
import pickle
from odict import OrderedDict
from cache import CACHE
from widget import Widget
from view import View
from view import render
from biology.dataindex import DataIndex
from biology.markers import GROUP_TO_TEXT
from biology.markers import HIDDEN_GROUPS
from django.utils.html import linebreaks

def options_from_table(table):
    ret = []
    for group_code, group_text in GROUP_TO_TEXT:
      if table.get_markers(group_code):
        ret.append((group_text, sorted(table.get_markers(group_code))))
    groups_to_ignore = HIDDEN_GROUPS + [g[0] for g in GROUP_TO_TEXT]
    if table.get_markers_not_in_groups(*groups_to_ignore):
      ret.append(('', sorted(table.get_markers_not_in_groups(*groups_to_ignore))))
    return ret
    
class Select(Widget):
  """ The select widget shows a combo box menu. 
  You can select one item or multiple items.
  When the user selects values, they are saved as a list in Select.values.choices.
  Note: The selected values are saved as a list thanks to the set_value method in main.py
  which supports lists.
  The widget can also offer a default value for choices based on previous selection
  of the user. This is done by the guess_or_remember method.
  """
  def __init__(self, id, parent):
    Widget.__init__(self, id, parent)
    self.values.choices = None

  def get_choices(self):
    if not self.values.choices:
      return []
    return self.values.choices
  
  def get_choice(self):
    if not self.values.choices:
      return None
    return self.values.choices[0]
    
  def guess_or_remember(self, key, default_value=None):
    return Widget._guess_or_remember(self, 'choices', key, default_value)

  def view(self, text, save_button, options, multiple=True, group_buttons=[], choices=None, comment=''):
    """ Returns a view of the select widget.
    text is a the title of the widget. 
    save_button is  an ApplyButton used to save the widget's state. 
    options describes the options in the select box. 
    options can be:
       1. a list of strings --> one selection group, titles and values are the same, none is selected
       2. a list of (value, title) tuples --> one selection group, titles and values are different, none is selected
       3. a list of (value, title, selected) tuples --> one selection group, titles and values are different, selection according to selected.
       3. a list of (group_name, 1/2/3 style list) --> multiple groups.
    groups is a list of tuples of (group_name, list of vals). If it is not None, then a button is added
    for every group. When the button is pressed, the relevant items are selected. 
    comment -- displays text next to the select box. 
    """
    def add_titles_if_needed(items):
      if items and type(items[0]) != tuple:
        items = zip(items, items)
      return items
    
    def add_selected_state(items):
      choices_as_str = [str(x) for x in choices]
      return [(o[0], o[1], str(o[0]) in choices_as_str) for o in items]
      
    if choices == None:
      choices = self.values.choices
    if choices == None:
      choices = []
    if not options:
      options = []
    else:  
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
        'comment' : comment,
        'widget_id' : self.id})
    v = View(
        self, 
        html, 
        ['jquery.multiselect.css'],
        ['jquery.multiselect.js'])
    return v
