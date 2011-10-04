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
from view import stack_left
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

class BoxPlot(WidgetWithControlPanel):
  """ Shoes a box plot for the selected dimensions.
  """
  def __init__(self, id, parent):
    WidgetWithControlPanel.__init__(self, id, parent)
    
  def title(self, short):
    """Title for the module, the short version is displayed in menus, 
    the long version is displayed in the expander title.
    """
    
    return 'BoxPlot: over %s' % (self.widgets.dims.get_choices()) 
  
  def run(self, tables):
    return {'tables':tables}
    
  def control_panel(self, tables):
    self._add_select(
        'dims',
        'Dimensions for box plot',
        options=options_from_table(tables[0]),
        is_multiple=True,
        cache_key=tables,
        default=[])
  
  @cache('boxplots')      
  def main_view(self, tables):
    dims = self.widgets.dims.get_choices()
    views = []
    for table in tables:
      fig_widget = self._add_widget_if_needed('figure_%s' % table.name, Figure)
      ax = axes.new_axes(60 * len(dims), 500)
      axes.boxplot(ax, table, dims)
      views.append(fig_widget.view(ax.figure))
    return stack_left(*views)
      
    
