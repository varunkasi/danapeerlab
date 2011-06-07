#!/usr/bin/env python
import axes
import view
from widget import Widget
from view import View
from view import render
from view import stack_lines
from select import options_from_table
from input import Input
from applybutton import ApplyButton
from figure import Figure
from leftpanel import LeftPanel
from areaselect import AreaSelect
from odict import OrderedDict
from table import Table
from select import Select
from scriptservices import cache


FIG_SIZE_X = 500
FIG_SIZE_Y = 500


class HistogramPlot(Widget):
  def __init__(self, id, parent):
    Widget.__init__(self, id, parent)
    self._add_widget('dims', Select)
    self._add_widget('layout', LeftPanel)
    self._add_widget('apply', ApplyButton)
    
  def title(self, short):
    if not self.widgets.dims.values.choices:
      return 'Histogram'
    else:
      return 'Histogram %s' % ', '.join(self.widgets.dims.values.choices)
      
  def get_inputs(self):
    return ['table', 'table2', 'table3', 'table4']
    
  def get_outputs(self):
    return []
  
  def run(self, **tables):
    pass
    
  @cache('histograms')
  def view(self, **tables):
    control_panel_view = stack_lines(
        self.widgets.dims.view('Dimension', self.widgets.apply, options_from_table(tables['table'])),
        self.widgets.apply.view())
    inputs = [input for input in self.get_inputs() if tables[input]]
    main_views = []
    if self.widgets.dims.values.choices:
      for dim in self.widgets.dims.values.choices:
        fig = axes.new_figure(FIG_SIZE_X, FIG_SIZE_Y)
        ax = fig.add_subplot(111)        
        for input in inputs:
          axes.kde1d(ax, tables[input], dim)
        widget_key = self._normalize_id(dim)
        if not widget_key in self.widgets:
          self._add_widget(widget_key, Figure)
        figure_widget = self.widgets[widget_key]
        main_views.append(figure_widget.view(fig))
      main_view = view.stack_left(*main_views)
    else:
      main_view = View(None, 'Please select dimensions')    
    return self.widgets.layout.view(main_view, control_panel_view)
