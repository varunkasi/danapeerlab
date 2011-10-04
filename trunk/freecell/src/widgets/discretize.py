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

class Discretize(WidgetWithControlPanel):
  """ This modules discritizes the given dimensions according to boundries. 
  """
  def __init__(self, id, parent):
    WidgetWithControlPanel.__init__(self, id, parent)
    
  def title(self, short):
    """Title for the module, the short version is displayed in menus, 
    the long version is displayed in the expander title.
    """
    if not 'dims' in self.widgets:
      return 'Discretize'
    return 'Discretize: over %s' % (self.widgets.dims.get_choice()) 
  
  def run(self, tables):
    """ Does the clustering.
    """
    dims = self.widgets.dims.get_choices()
    if self.widgets.bin_type.get_choice() == 'divide':
      bins = self.widgets.bins.value_as_int()
    elif self.widgets.bin_type.get_choice() == 'explicit':
      bins = self.widgets.bins.value_as_float_list()
    else:
      raise Exception('unknown bin type')
      
    ret = []
    timer = MultiTimer(len(tables))
    for table in tables:
      new_table = table.discretize(dims, bins)
      new_table.tags = table.tags.copy()
      new_table.name = '%s discretized' % table.name
      ret.append(new_table)
      timer.complete_task(table.name)
    return {'tables':ret}
    
  def control_panel(self, tables):
    self._add_select(
        'dims',
        'Dimensions to discretize',
        options=options_from_table(tables[0]),
        is_multiple=True,
        cache_key=tables,
        default=[])
    
    self._add_select(
        'bin_type',
        'Bin Method',
        options=[('divide', 'Divide the range [min,max] equally to the spcified number of bins'), ('explicit', 'Use a comma separated list of bins')],
        is_multiple=False,
        cache_key=tables,
        default=['divide'])

    self._add_input(
        'bins', 
        'Bins',
        cache_key=tables,
        default='2',
        numeric_validation=False)
    
  def main_view(self, tables):
    pass
