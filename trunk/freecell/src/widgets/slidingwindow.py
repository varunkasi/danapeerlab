#!/usr/bin/env python
import axes
import numpy as np
import view
import logging
import biology.datatable as datatable
from biology.tagorder import multiple_tag_sort_key
from multitimer import MultiTimer
from operator import itemgetter
from widget import Widget
from widgetwithcontrolpanel import WidgetWithControlPanel
from view import View
from view import render
from view import stack_lines
from select import options_from_table
from input import Input
from applybutton import ApplyButton
from figure import Figure
from areaselect import AreaSelect
from odict import OrderedDict
from table import Table
from select import Select
from cache import cache
from motionchart import MotionChart

class SlidingWindow(WidgetWithControlPanel):
  """ This module creates a new table from every inputted table. For every table
  we take a sliding window along a certain dimension, and from every window 
  create a row (by taking averages, medians, etc)
  """
  def __init__(self, id, parent):
    WidgetWithControlPanel.__init__(self, id, parent)
    
  def title(self, short):
    """Title for the module, the short version is displayed in menus, 
    the long version is displayed in the expander title.
    """
    if not 'agg_method' in self.widgets:
      return 'Sliding Window'
    return 'Windows: %s over %s' % (self.widgets.agg_method.get_choice(), self.widgets.window_dim.get_choice()) 
  
  @cache('sliding')
  def run(self, tables):
    """ Does the clustering.
    """
    ret = []
    timer = MultiTimer(len(tables))
    for table in tables:
      new_table = table.window_agg(
          self.widgets.window_dim.get_choice(),
          self.widgets.size.value_as_float(),
          self.widgets.overlap.value_as_float(),
          self.widgets.agg_method.get_choice())
      new_table.tags = table.tags.copy()
      new_table.name = '%s %s over %s' % (table.name, self.widgets.agg_method.get_choice(), self.widgets.window_dim.get_choice())
      ret.append(new_table)
      timer.complete_task(table.name)  
    return {'tables':ret}
    
  def control_panel(self, tables):
    self._add_select(
        'window_dim',
        'Sliding window dimension',
        options=options_from_table(tables[0]),
        is_multiple=False,
        cache_key=tables,
        default=['Time'])
    
    self._add_input(
        'size', 
        'Sliding window size',
        cache_key=tables,
        default=1000)

    self._add_input(
        'overlap', 
        'Sliding window overlap',
        cache_key=tables,
        default=500)
    
    self._add_select(
        'agg_method',
        'From every window take',
        options=[('average', 'Average'), ('median', 'Median')],
        is_multiple=False)
    
    
  def main_view(self, tables):
    pass
