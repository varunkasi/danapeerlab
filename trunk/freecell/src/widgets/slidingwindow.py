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
from widgetwithcontrolopanel import WidgetWithControlPanel
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
    self._add_widget('window_dim', Select)
    self._add_widget('agg_method', Select)
    self._add_widget('size', Input)
    self._add_widget('overlap', Input)
    self._add_widget('apply', ApplyButton)
    
  def title(self, short):
    """Title for the module, the short version is displayed in menus, 
    the long version is displayed in the expander title.
    """
    
    return 'Windows: %s over %s' % (self.widgets.agg_method.get_choice(), self.widgets.window_dim.get_choice()) 
      
  def get_inputs(self):
    """ Returns the names input list.
    """
    return ['tables']
    
  def get_outputs(self):
    """ Returns the output list.
    """
    return ['tables']
  
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
    self.widgets.window_dim.guess_or_remember(('sliding window dims', tables), ['Time'])
    self.widgets.agg_method.guess_or_remember(('sliding window agg', tables), ['median'])
    self.widgets.size.guess_or_remember(('window size', tables), 1000)
    self.widgets.overlap.guess_or_remember(('window overlap', tables), 500)
    # Create the control panel view. This will enable users to choose the dimensions. 
    control_panel_view = stack_lines(
        self.widgets.window_dim.view('Sliding window dimension', self.widgets.apply, options_from_table(tables[0]), multiple=False), 
        self.widgets.size.view('Sliding window size', self.widgets.apply),
        self.widgets.overlap.view('Sliding window overlap', self.widgets.apply),        
        self.widgets.agg_method.view('From every window take', self.widgets.apply, [('avg', 'Average'), ('median', 'Median')], multiple=False),
        self.widgets.apply.view())
    return control_panel_view
    
  def main_view(self, tables):
    pass
