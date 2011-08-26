#!/usr/bin/env python
import settings
import os
import pickle
import numpy as np
import json
from odict import OrderedDict
from cache import CACHE
from cache import make_unique_str
from widget import Widget
from view import View
from view import render
from biology.dataindex import DataIndex
from biology.markers import GROUP_TO_TEXT
from biology.markers import HIDDEN_GROUPS
from django.utils.html import linebreaks

class MotionChart(Widget):
  """ Shows a Google Visualization API motion chart.
  """
  def __init__(self, id, parent):
    Widget.__init__(self, id, parent)
    self.values.state = None
    self.last_col_names = None
    self.id_map = None
    
  def guess_or_remember(self, key, default_value=None):
    return Widget._guess_or_remember(self, 'state', key, default_value)

  def modify_state(self, x_col, y_col, color_col, size_col):
    if not self.values.state:
      state_dict = {}
    else:
      state_dict = json.loads(self.values.state)
    state_dict['sizeOption'] = str(size_col)
    state_dict['xAxisOption'] = str(x_col)
    state_dict['yAxisOption'] = str(y_col)
    state_dict['colorOption'] = str(color_col)
    self.state = json.dumps(state_dict)
  
  def get_selected_ids(self):
    if not self.values.state:
      return []
    state = json.loads(self.values.state)
    selected_list = state['iconKeySettings']
    selected_list = [s['key']['dim0'] for s in selected_list]
    selected_list = [self.last_id_map[item] for item in selected_list]
    return selected_list
    #for key,val in state.iteritems():
    #  print '%s : %s' % (key, val)
   
  def get_current_time(self):
    if not self.values.state:
      return 0
    state = json.loads(self.values.state)
    return int(state['time']) - 1900

  def on_load(self):
    # save the id_map from the previous view, before view will change it
    self.last_id_map = self.id_map
    
  def view(self, col_names, data, time_strings, comment='', height=600, width=800):
    """Draws the motion chart. 
    col_names is a list of column names, data is a list of 
    rows (each row is a list of strings).
    The first column is the entity name (string).
    The second column is a time column, and should be a number.
    Other columns can be either numbers or strings.
    time_strings is a string representation for the timestamp number (time is the index).
    
    Note: This relies on the google api being loaded in the main 
    page, i.e that we have a script tag that loads https://www.google.com/jsapi
    in the head section.
    """
    col_types = []
    
    if (self.last_col_names and self.last_col_names != col_names):
      # If the columns were changed, we need to reset the state.
      self.values.state = None
    self.last_col_names = col_names
    
    # The motion chart flash can't handle characters like + in the id column.
    # We change those characters (only + for now) and save a map from the 
    # modified id to the original id.
    self.id_map = {}
    for i,row in enumerate(data):
      data[i] = list(row)
      old_id = data[i][0]
      new_id = old_id.replace('+', 'hi')
      data[i][0] = new_id
      self.id_map[new_id] = old_id

    first_row = data[0]
    for val in first_row:
      if type(val) in (str, unicode):
        col_types.append('string')
      elif type(val) in (int, float, np.float64):
        col_types.append('number')
      else:
        raise ValueError('Unsupported type %s' % str(type(val)))
    col_names_types = zip(col_names, col_types)
    json_data = json.dumps(data)
    print self.values.state
    html = render('motionchart.html', {
        'widget_id' : self.id,
        'id' : self._get_unique_id(),
        'comment' : comment,
        'height' : height,
        'width' : width,
        'json_data': json_data,
        'col_names_types': col_names_types, 
        'time_strings_json' : json.dumps(time_strings),
        'state': self.values.state})
    v = View(
        self, 
        html, 
        ['jquery.multiselect.css'],
        ['jquery.multiselect.js'])
    return v
    