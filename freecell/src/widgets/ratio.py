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

class Ratio(WidgetWithControlPanel):
  """ This divides all dimension by the value of another dimension.
  """
  def __init__(self, id, parent):
    WidgetWithControlPanel.__init__(self, id, parent)
    
  def title(self, short):
    """Title for the module, the short version is displayed in menus, 
    the long version is displayed in the expander title.
    """
    if not 'dims' in self.widgets:
      return 'Ratio'
    return 'Ratio: of %s / %s' % (self.widgets.dims.get_choices(), self.widgets.ratio_dim.get_choice()) 
  
  def run(self, tables):
    """ Does the clustering.
    """
    dims = self.widgets.dims.get_choices()
    ratio_dim = self.widgets.ratio_dim.get_choice()  
    ret = []
    timer = MultiTimer(len(tables))
    for table in tables:
      new_table = table.ratio(dims, ratio_dim)
      new_table.tags = table.tags.copy()
      new_table.name = '%s ratio %s' % (table.name, ratio_dim)
      ret.append(new_table)
      timer.complete_task(table.name)
    return {'tables':ret}
    
  def control_panel(self, tables):
    self._add_select(
        'dims',
        'Dimensions to divide',
        options=options_from_table(tables[0]),
        is_multiple=True,
        cache_key=tables,
        default=[])
    
    self._add_select(
        'ratio_dim',
        'Divider dimension',
        options=options_from_table(tables[0]),
        is_multiple=False,
        cache_key=tables,
        default=[])
    
  def main_view(self, tables):
    pass
