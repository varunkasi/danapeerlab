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

class CorrelationMap(WidgetWithControlPanel):
  """ This module allows the user to compare multiple populations. The
  populations are overlayed over a 2d map.
  """
  def __init__(self, id, parent):
    WidgetWithControlPanel.__init__(self, id, parent)
    self._add_widget('motion_chart', MotionChart)
  
  def title(self, short):
    """Title for the module, the short version is displayed in menus, 
    the long version is displayed in the expander title.
    """
    return 'Correlation Map'
      
  def get_inputs(self):
    """ Returns the names input list.
    """
    return ['tables']
    
  def get_outputs(self):
    """ Returns the output list.
    """
    return ['tables']
    
  def control_panel(self, tables):

    
    self._add_select(
        'tables_to_show',
        'Tables to Show',
        options=[('all', 'All tables')] + [(t.name, t.name) for t in tables],
        is_multiple=True,
        cache_key=tables,
        default=['all'])
    
    self._add_select(
        'dims',
        'Dimensions to correlate', 
        options=options_from_table(tables[0]),
        is_multiple=True,
        cache_key=tables,
        default=[])

    self._add_select(
        'corr_method',
        'Correlation method',
        options=[('corr', 'Correlation'), ('mi', 'Mutual Information')],
        is_multiple=False,
        cache_key=tables,
        default=['corr'])
        
  
  @cache('correlationmap')
  def main_view(self, tables):
    dims = self.widgets.dims.get_choices()
    if 'all' in self.widgets.tables_to_show.get_choices():
      tables_to_show = tables
    else:
      tables_to_show = [t for t in tables if t.name in self.widgets.tables_to_show.get_choices()]
    if not tables_to_show:
      return
    # Assemble the figure to show
    figures_to_show = []
    multi_timer = MultiTimer(len(tables_to_show))
    for table in tables_to_show:
       
      comments = []
      col_names = []
      cols = []
    
      # Add id column
      col_names.append('id')
      cols.append(dims)

      # Add time column
      col_names.append('time')
      cols.append([0] * len(dims))
    
      # Add dim reduce columns
      col_names.append('dim_reduce1')
      col_names.append('dim_reduce2')
      corr = self.widgets.corr_method.get_choice() == 'corr'
      mutual_information_table = table.get_mutual_information_table(dims_to_use = dims, use_correlation=corr)      
      #assert np.all(mutual_information_table.data >= 0)
      distance = 1-np.abs(mutual_information_table.data)
      from mlabwrap import mlab
      Y, eig = mlab.cmdscale(distance, nout=2)
      cols.append(Y.T[0])
      cols.append(Y.T[1])
      comments.append(','.join(['%.3f' % val for val in eig[:4]]))
    
      # Add average columns:
      col_names.append('average')
      cols.append([table.get_average(dim) for dim in dims])

      # Add std columns:
      col_names.append('std')
      cols.append([table.get_std(dim) for dim in dims])
      
      motion_chart = self._add_widget_if_needed('motion_chart_%s' % table.name, MotionChart)
      motion_chart.guess_or_remember(('multicompare motionchart', tables), None)
      figures_to_show.append(motion_chart.view(col_names, zip(*cols), [''], '\n'.join(comments)))
    return stack_lines(*figures_to_show)