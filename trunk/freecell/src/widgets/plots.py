#!/usr/bin/env python
import os
import time
import logging
import axes
import view
from timer import Timer
from widget import Widget
from view import View
from view import render
from biology.dataindex import DataIndex
from biology.datatable import DimRange
from django.utils.html import linebreaks
import settings
import StringIO
import matplotlib
from view import stack_lines
from select import Select
from select import options_from_table
from input import Input
from applybutton import ApplyButton
from figure import Figure
from leftpanel import LeftPanel
from areaselect import AreaSelect
from odict import OrderedDict
from table import Table
from scriptservices import cache

    
class AbstractPlot(Widget):
  def __init__(self, id, parent, enable_gating=False):
    Widget.__init__(self, id, parent)
    self._add_widget('dim_x', Select)
    self._add_widget('dim_y', Select)
#    self._add_widget('min_x', Input)
#    self._add_widget('min_y', Input)
#    self._add_widget('max_x', Input)
#    self._add_widget('max_y', Input)
    self._add_widget('gate_min_x', Input)
    self._add_widget('gate_min_y', Input)
    self._add_widget('gate_max_x', Input)
    self._add_widget('gate_max_y', Input)
    self._add_widget('apply', ApplyButton)
    self._add_widget('figure', Figure)
    self._add_widget('layout', LeftPanel)
    self._add_widget('area_select', AreaSelect)
    self._add_widget('input_table', Table)
    self.enable_gating = enable_gating

  def name(self):
    raise Exception('Not Implemented')

  def control_panel(self, table):
    return View(self, '')

  def draw_figures(self, fig, table, dim_x, dim_y, range):    
    raise Exception('Not Implemented')

  @cache('plots')
  def _draw_figures(self, table, dim_x_arr, dim_y_arr):
    ret = OrderedDict()
    for dim_x in dim_x_arr:
      for dim_y in dim_y_arr:
        range = (table.min(dim_x), table.min(dim_y), table.max(dim_x), table.max(dim_y))
        figures = self.draw_figures(table, dim_x, dim_y, range)
        for key, val in figures.iteritems():
          ret['%s_%s_%s' % (dim_x, dim_y, key)] = val
    return ret
          
  def _dims_ready(self, table=None):
    if not self.widgets.dim_x.values.choices:
      return False
    if not self.widgets.dim_y.values.choices:
      return False
    if table and not self.widgets.dim_y.values.choices[0] in table.dims:
      return False
    if table and not self.widgets.dim_x.values.choices[0] in table.dims:
      return False
    return True
  
  def title(self, short):
    name = self.name()
    if not self._dims_ready():
      return name
    else: 
      dim_x = self.widgets.dim_x.values.choices
      dim_y = self.widgets.dim_y.values.choices
      return '%s: %s X %s' % (name,
          ', '.join(dim_x),
          ', '.join(dim_y))
          
  def get_inputs(self):
    return ['table', 'table2', 'table3', 'table4']
    
  def get_outputs(self):
    if not self.enable_gating:
      return []
    else:
      return ['table']

  
  def run(self, **tables):
    if not self.enable_gating:
      return
    table = tables['table']
    if not self._dims_ready(table):
      return
    dim_x = self.widgets.dim_x.values.choices[0]
    dim_y = self.widgets.dim_y.values.choices[0]
    gate_min_x = self.widgets.gate_min_x.value_as_float()
    gate_max_x = self.widgets.gate_max_x.value_as_float()
    gate_min_y = self.widgets.gate_min_y.value_as_float()
    gate_max_y = self.widgets.gate_max_y.value_as_float()
    if gate_min_x > table.min(dim_x) or gate_max_x  < table.max(dim_x) or gate_min_y > table.min(dim_y) or gate_max_y  < table.max(dim_y):
      data = {}
      data['table'] = table.gate(
          DimRange(dim_x, gate_min_x, gate_max_x),
          DimRange(dim_y, gate_min_y, gate_max_y))
      data['view'] = View(self, 'Table gated, %d cells left' % data['table'].num_cells)
      return data
    
  
  def view(self, **tables):
    table = tables['table']
    self.widgets.dim_x.guess_or_remember_choices('X Axis', options_from_table(table), self.__class__.__name__)
    self.widgets.dim_y.guess_or_remember_choices('Y Axis', options_from_table(table), self.__class__.__name__)
    if not self._dims_ready(table):
      control_panel_view = stack_lines(
          self.widgets.dim_x.view('X Axis', self.widgets.apply, options_from_table(table), not self.enable_gating),
          self.widgets.dim_y.view('Y Axis', self.widgets.apply, options_from_table(table), not self.enable_gating),
          self.widgets.apply.view())
      return self.widgets.layout.view(View(None, 'Please select dimensions'), control_panel_view)
    dim_x = self.widgets.dim_x.values.choices
    dim_y = self.widgets.dim_y.values.choices
   
    def trim_to_range(num, min, max):
      if num < min: 
        return min
      if num > max:
        return max
      return num
    #self.widgets.min_x.set_value('value', table.min(dim_x))
    #self.widgets.min_y.set_value('value', table.min(dim_y))
    #self.widgets.max_x.set_value('value', table.max(dim_x))
    #self.widgets.max_y.set_value('value', table.max(dim_y))

    self.widgets.gate_min_x.set_default('value', '%.2f' % table.min(dim_x[0]))
    self.widgets.gate_min_y.set_default('value', '%.2f' % table.min(dim_y[0]))
    self.widgets.gate_max_x.set_default('value', '%.2f' % table.max(dim_x[0]))
    self.widgets.gate_max_y.set_default('value', '%.2f' % table.max(dim_y[0]))
    
    self.widgets.gate_min_x.values.value = '%.2f' % trim_to_range(self.widgets.gate_min_x.value_as_float(), table.min(dim_x[0]), table.max(dim_x[0]))
    self.widgets.gate_max_x.values.value = '%.2f' % trim_to_range(self.widgets.gate_max_x.value_as_float(), table.min(dim_x[0]), table.max(dim_x[0]))
    self.widgets.gate_min_y.values.value = '%.2f' % trim_to_range(self.widgets.gate_min_y.value_as_float(), table.min(dim_y[0]), table.max(dim_y[0]))
    self.widgets.gate_max_y.values.value = '%.2f' % trim_to_range(self.widgets.gate_max_y.value_as_float(), table.min(dim_y[0]), table.max(dim_y[0]))
    
    
    
    # We need to give custom ids for some of our controls, so we can reference them 
    # in area_select widget
    custom_figure_id = 'figure_%s'  % self._get_unique_id()
    custom_gate_min_x_id = 'min_x_%s'  % self._get_unique_id()
    custom_gate_max_x_id = 'max_x_%s'  % self._get_unique_id()
    custom_gate_min_y_id = 'min_y_%s'  % self._get_unique_id()
    custom_gate_max_y_id = 'max_y_%s'  % self._get_unique_id()

    if self.enable_gating:
      control_panel_view = stack_lines(
          self.widgets.dim_x.view('X Axis', self.widgets.apply, options_from_table(table), not self.enable_gating),
          self.widgets.dim_y.view('Y Axis', self.widgets.apply, options_from_table(table), not self.enable_gating),
          self.control_panel(table),
          #self.widgets.min_x.view('Min X',  self.widgets.apply, [('Default', table.min(dim_x))]),
          #self.widgets.min_y.view('Min Y',  self.widgets.apply, [('Default', table.min(dim_y))]),
          #self.widgets.max_x.view('Max X',  self.widgets.apply, [('Default', table.max(dim_x))]),
          #self.widgets.max_y.view('Max Y',  self.widgets.apply, [('Default', table.max(dim_y))]),
          self.widgets.gate_min_x.view('Gate Min X',  self.widgets.apply, [('Default', '%.2f' % table.min(dim_x[0]))], custom_gate_min_x_id),
          self.widgets.gate_min_y.view('Gate Min Y',  self.widgets.apply, [('Default', '%.2f' % table.min(dim_y[0]))], custom_gate_min_y_id),
          self.widgets.gate_max_x.view('Gate Max X',  self.widgets.apply, [('Default', '%.2f' % table.max(dim_x[0]))], custom_gate_max_x_id),
          self.widgets.gate_max_y.view('Gate Max Y',  self.widgets.apply, [('Default', '%.2f' % table.max(dim_y[0]))], custom_gate_max_y_id),
          self.widgets.area_select.view(
              custom_figure_id, custom_gate_min_x_id, custom_gate_max_x_id, custom_gate_min_y_id, custom_gate_max_y_id,
              table.min(dim_x[0]),
              table.max(dim_x[0]),
              table.min(dim_y[0]),
              table.max(dim_y[0])),
          self.widgets.apply.view())
    else:
      control_panel_view = stack_lines(
          self.widgets.dim_x.view('X Axis', self.widgets.apply, options_from_table(table), not self.enable_gating),
          self.widgets.dim_y.view('Y Axis', self.widgets.apply, options_from_table(table), not self.enable_gating),
          self.control_panel(table),
          self.widgets.apply.view())
    try:
      id_to_fig = []
      inputs = [input for input in self.get_inputs() if tables[input]]
      with Timer('draw figures'):
        for input in inputs:
          id_to_fig.append(self._draw_figures(tables[input], dim_x, dim_y))
      if self.enable_gating:
        assert len(id_to_fig[0]) == 1
        fig = id_to_fig[0].values()[0]
        main_view = self.widgets.figure.view(fig, id=custom_figure_id)
      else:
        lines = []
        for key in id_to_fig[0].iterkeys():
          line = []
          for i, input in enumerate(inputs):
            widget_key = self._normalize_id('%s_%s' % (input, key))
            if not widget_key in self.widgets:
              self._add_widget(widget_key, Figure)
            fig = id_to_fig[i][key]
            line.append(self.widgets[widget_key].view(fig))
          lines.append(line)
        #main_view = view.stack_left(*main_views)
        main_view = self.widgets.input_table.view(inputs, lines)
    except Exception as e:
      main_view = View(self, str(e))
      logging.exception('Exception while drawing %s' % self.name())
    return self.widgets.layout.view(main_view, control_panel_view)
    
FIG_SIZE_X = 500
FIG_SIZE_Y = 500

class DensityPlot(AbstractPlot):
  def __init__(self, id, parent):
    AbstractPlot.__init__(self, id, parent, False)
  
  def name(self):
    return 'Density Plot'
    
  def draw_figures(self, table, dim_x, dim_y, range):
    fig = axes.new_figure(FIG_SIZE_X, FIG_SIZE_Y)
    axes.kde2d_color_hist(fig, table, (dim_x, dim_y), range)
    return {'fig': fig}

class FunctionPlot(AbstractPlot):
  def __init__(self, id, parent, gate=False):
    AbstractPlot.__init__(self, id, parent, gate)
    self._add_widget('min_density_in_column', Input)  
  
  def name(self):
    return 'Function Plot'
    
  def control_panel(self, table): 
    if self.widgets.min_density_in_column.values.value == None:
      self.widgets.min_density_in_column.values.value = '0'
    return stack_lines(
        self.widgets.min_density_in_column.view('Minimal density in column', self.widgets.apply))

  def draw_figures(self, table, dim_x, dim_y, range):
    fig = axes.new_figure(FIG_SIZE_X, FIG_SIZE_Y)
    axes.kde2d_color_hist(fig, table, (dim_x, dim_y), range, 'y', self.widgets.min_density_in_column.value_as_float())
    return {'fig': fig}

class ScatterPlot(AbstractPlot):
  def __init__(self, id, parent, gate=False):
    AbstractPlot.__init__(self, id, parent, gate)
    self._add_widget('color', Select)  
    self._add_widget('num_bins', Select)  
    self._add_widget('min_cells_in_bin', Input)  
  
  def name(self):
    return 'Scatter Plot'
  
  def control_panel(self, table): 
    if not self.widgets.color.values.choices:
      self.widgets.color.values.choices = ['None']
    colors = [('None', ['None'])] + options_from_table(table)
    if not self.widgets.num_bins.values.choices:
      self.widgets.num_bins.values.choices = ['128']
    if self.widgets.min_cells_in_bin.values.value == None:
      self.widgets.min_cells_in_bin.values.value = 1
      
    return stack_lines(
        self.widgets.color.view('Color', self.widgets.apply, colors, not self.enable_gating),
        self.widgets.num_bins.view('Number of bins', self.widgets.apply, ['64', '128', '256', '512'], False),
        self.widgets.min_cells_in_bin.view('Minimum cells in a bin', self.widgets.apply))
  
  def draw_figures(self, table, dim_x, dim_y, range):
    colors = self.widgets.color.values.choices
    no_bins = int(self.widgets.num_bins.values.choices[0])*1j
    min_cells = int(self.widgets.min_cells_in_bin.values.value)-1
    ret = OrderedDict()
    for color in colors:
      if color == 'None':
        color = None
      fig = axes.new_figure(FIG_SIZE_X, FIG_SIZE_Y)
      ax = fig.add_subplot(111)
      axes.scatter2(ax, table, (dim_x, dim_y), range, color, min_cells_per_bin = min_cells, no_bins=no_bins)
      ret[str(color)] = fig
    return ret

class ScatterGater(ScatterPlot):
  def __init__(self, id, parent):
    ScatterPlot.__init__(self, id, parent, True)

  def name(self):
    return 'Scatter Gater'

class DensityGater(DensityPlot):
  def __init__(self, id, parent):
    AbstractPlot.__init__(self, id, parent, True)

  def name(self):
    return 'Density Gater'

class FunctionGater(FunctionPlot):
  def __init__(self, id, parent):
    FunctionPlot.__init__(self, id, parent, True)
    
  def name(self):
    return 'Function Gater'
