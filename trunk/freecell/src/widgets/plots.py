﻿#!/usr/bin/env python
import os
import time
import logging
import axes
import view
import numpy as np
from timer import Timer
from widget import Widget
from view import View
from view import render
from biology.dataindex import DataIndex
from biology.datatable import DimRange
from biology.datatable import dim_range_to_str
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
from cache import cache

    
class AbstractPlot(Widget):
  def __init__(self, id, parent, enable_gating=False):
    Widget.__init__(self, id, parent)
    self._add_widget('dim_x', Select)
    self._add_widget('dim_y', Select)
    self._add_widget('negative_values', Select)
    self._add_widget('tables_to_show', Select)
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

  def on_load(self):
    if not 'negative_values' in self.widgets:
      self._add_widget('negative_values', Select)
  
  def name(self):
    raise Exception('Not Implemented')

  def control_panel(self, table):
    return View(self, '')

  def draw_figures(self, fig, table, dim_x, dim_y, range):    
    raise Exception('Not Implemented')

  @cache('plots')
  def _draw_figures(self, table, dim_x_arr, dim_y_arr, table_for_range, min_val):
    ret = OrderedDict()
    for dim_x in dim_x_arr:
      for dim_y in dim_y_arr:
        fixed_table = table.gate(DimRange(dim_x, min_val, np.inf), DimRange(dim_y, min_val, np.inf))
        fixed_range = table_for_range.gate(DimRange(dim_x, min_val, np.inf), DimRange(dim_y, min_val, np.inf))
        range = (fixed_range.min(dim_x), fixed_range.min(dim_y), fixed_range.max(dim_x), fixed_range.max(dim_y))
        figures = self.draw_figures(fixed_table, dim_x, dim_y, range)
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
    return ['tables']
    
  def get_outputs(self):
    if not self.enable_gating:
      return []
    else:
      return ['tables', 'tables_out_of_gate']

  
  def run(self, tables):
    if not self.enable_gating:
      return
    dim_x = self.widgets.dim_x.values.choices[0]
    dim_y = self.widgets.dim_y.values.choices[0]
    gate_min_x = self.widgets.gate_min_x.value_as_float()
    gate_max_x = self.widgets.gate_max_x.value_as_float()
    gate_min_y = self.widgets.gate_min_y.value_as_float()
    gate_max_y = self.widgets.gate_max_y.value_as_float()
    range_x = DimRange(dim_x, gate_min_x, gate_max_x)
    range_y = DimRange(dim_y, gate_min_y, gate_max_y)
    ret_tables = []
    ret_tables_out = []
    texts = []
    for table in tables:
      if not self._dims_ready(table):
        raise Exception("The tables don't have the same dims")
      if gate_min_x > table.min(dim_x) or gate_max_x  < table.max(dim_x) or gate_min_y > table.min(dim_y) or gate_max_y  < table.max(dim_y):
        gated_in = table.gate(range_x, range_y)
        gated_in.tags = table.tags.copy()
        gated_in.name = '%s | %s, %s' % (table.name, dim_range_to_str(range_x), dim_range_to_str(range_y))
        gated_in.tags['gate_type'] = 'in'
        gated_out = table.gate_out(range_x, range_y)
        gated_out.tags = table.tags.copy()
        gated_out.name = '%s |NOT: %s, %s' % (table.name, dim_range_to_str(range_x), dim_range_to_str(range_y))
        gated_out.tags['gate_type'] = 'out'
        ret_tables.append(gated_in)
        ret_tables_out.append(gated_out)
        #texts.append('Table %s gated, %d cells left' % (gated_in.name, gated_in.num_cells))
        
    ret = {}
    ret['tables'] = ret_tables
    ret['tables_out_of_gate'] = ret_tables_out
    #ret['view'] = '\n'.join(texts)
    return ret
    
  
  def view(self, tables):
    if not tables:
      return View(self, "No tables to show")
    table = tables[0]
    if self.enable_gating:
      self.widgets.tables_to_show.guess_or_remember(('plot tables to show gating', tables), ['0'])
    else:
      self.widgets.tables_to_show.values.choices = [str(i) for i,t in enumerate(tables)]
    self.widgets.dim_x.guess_or_remember(('X Axis', options_from_table(table), self.__class__.__name__))
    self.widgets.dim_y.guess_or_remember(('Y Axis', options_from_table(table), self.__class__.__name__))
    self.widgets.negative_values.guess_or_remember(('Remove Values', ['Keep Everything', 'Remove Negative', 'Remove > 2'], self.__class__.__name__))
    if not self.widgets.negative_values.values.choices:
      self.widgets.negative_values.values.choices = ['Keep Everything']
    #if self.enable_gating:
    #  self.widgets.negative_values.values.choices = ['Keep Everything']
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
    
    if 'Remove Negative' in self.widgets.negative_values.values.choices:
      min_val = 0
      min_val_for_area_select_x = 0
      min_val_for_area_select_y = 0
    elif 'Keep Everything' in self.widgets.negative_values.values.choices:
      min_val = -np.inf
      min_val_for_area_select_x = table.min(dim_x[0])
      min_val_for_area_select_y = table.min(dim_y[0])
    elif 'Remove > 2' in self.widgets.negative_values.values.choices:
      min_val = 2
      min_val_for_area_select_x = 2
      min_val_for_area_select_y = 2    
    
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
          self.widgets.tables_to_show.view('Table to show', self.widgets.apply, [(i, t.name) for i,t in enumerate(tables)], False),
          self.widgets.negative_values.view('Remove Values', self.widgets.apply, ['Keep Everything', 'Remove Negative', 'Remove > 2'], False),
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
              min_val_for_area_select_x,
              table.max(dim_x[0]),
              min_val_for_area_select_y,
              table.max(dim_y[0])),
          self.widgets.apply.view())
    else:
      control_panel_view = stack_lines(
          self.widgets.dim_x.view('X Axis', self.widgets.apply, options_from_table(table), not self.enable_gating),
          self.widgets.dim_y.view('Y Axis', self.widgets.apply, options_from_table(table), not self.enable_gating),
          #self.widgets.tables_to_show.view('Tables to show', self.widgets.apply, [(i, t.name) for i,t in enumerate(tables)], True),
          self.widgets.negative_values.view('Remove Values', self.widgets.apply, ['Keep Everything', 'Remove Negative', 'Remove > 2'], False),
          self.control_panel(table),
          self.widgets.apply.view())
    tables_to_show = [t for i,t in enumerate(tables) if str(i) in [str(s) for s in self.widgets.tables_to_show.values.choices]]
    try:
      id_to_fig = []
      with Timer('draw figures'):
        for table_input in tables_to_show:
          id_to_fig.append(self._draw_figures(table_input, dim_x, dim_y, tables[0], min_val))
      if self.enable_gating:
        assert len(id_to_fig[0]) == 1
        fig = id_to_fig[0].values()[0]
        # Other than figure, the sub functions can also send an extra view. In this case
        # fig will be tuple. 
        if type(fig) == tuple:
          main_view = stack_lines(self.widgets.figure.view(fig[0], id=custom_figure_id), fig[1])
        else:
          main_view = self.widgets.figure.view(fig, id=custom_figure_id)
      else:
        lines = []
        for key in id_to_fig[0].iterkeys():
          line = []
          for i in xrange(len(id_to_fig)):
            widget_key = self._normalize_id('%d_%s' % (i, key))
            if not widget_key in self.widgets:
              self._add_widget(widget_key, Figure)
            fig = id_to_fig[i][key]
            # Other than figure, the sub functions can also send an extra view. In this case
            # fig will be tuple. 
            if type(fig) == tuple:
              box_view = stack_lines(
                  self.widgets[widget_key].view(fig[0]), fig[1])
            else:
              box_view = self.widgets[widget_key].view(fig)
            line.append(box_view)
            
          lines.append(line)
        if len(tables) == 1:
          main_view = view.stack_left(*[l[0] for l in lines])
        else:
          main_view = self.widgets.input_table.view([table_input.name for table_input in tables_to_show], lines)
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
      self.widgets.min_density_in_column.values.value = '0.005'
    return stack_lines(
        self.widgets.min_density_in_column.view('Minimal density in column', self.widgets.apply))

  def draw_figures(self, table, dim_x, dim_y, range):
    fig = axes.new_figure(FIG_SIZE_X, FIG_SIZE_Y)
    axes.kde2d_color_hist(fig, table, (dim_x, dim_y), range, 'y', self.widgets.min_density_in_column.value_as_float())    
    corr_view = View(None, 'corr: %.2f; mi: %.2f' % (table.get_correlation(dim_x, dim_y), table.get_mutual_information(dim_x, dim_y)))
    return {'fig': (fig, corr_view)}

class ScatterPlot(AbstractPlot):
  def __init__(self, id, parent, gate=False):
    AbstractPlot.__init__(self, id, parent, gate)
    self._add_widget('color', Select)  
    self._add_widget('resolution', Select)  
    self._add_widget('min_cells_in_bin', Input)  
    self._add_widget('contour', Select)  
  
  def name(self):
    return 'Scatter Plot'
  
  def control_panel(self, table): 
    self.widgets.contour.guess_or_remember(('scatter plot contour', table), ['none'])
    self.widgets.resolution.guess_or_remember(('scatter plot resolution', table), ['1'])
    if not self.widgets.color.values.choices:
      self.widgets.color.values.choices = ['None']
    colors = [('None', ['None'])] + options_from_table(table)
    if self.widgets.min_cells_in_bin.values.value == None:
      self.widgets.min_cells_in_bin.values.value = 1
      
    return stack_lines(
        self.widgets.contour.view('Draw Contour Lines', self.widgets.apply,
            [('none', 'None'), ('regular', 'Regular Contour'), ('smooth', 'Smooth Contour')], multiple=False),
        self.widgets.color.view('Color', self.widgets.apply, colors, not self.enable_gating),
        self.widgets.resolution.view('resolution', self.widgets.apply, ['1', '1.25', '1.5', '2', '3', '4'], False),
        self.widgets.min_cells_in_bin.view('Minimum cells in a bin', self.widgets.apply))
  
  def get_planned_axes_width(self):
    # We need to calculate the pixel size for the figure
    # so we create a fake figure and add to it a colorbar
    # and axes the same way the scatter function sdoes:
    fig = axes.new_figure(FIG_SIZE_X, FIG_SIZE_Y)
    ax = fig.add_subplot(111)
    ax.set_xlabel('temp', size='x-small')
    ax.set_ylabel('temp', size='x-small')
    ax.figure.subplots_adjust(bottom=0.15)
    cbar = ax.figure.colorbar(ax.imshow([[0]]))
    # Now we know the future width, height.
    return axes.ax_size_pixels(ax)
  
  def draw_figures(self, table, dim_x, dim_y, range):
    res = float(self.widgets.resolution.get_choice())
    ax_width, ax_height = self.get_planned_axes_width()
    ax_width /= res
    ax_height /= res
    if res == 1:
      interpolation = 'nearest'
    else:
      interpolation = 'blackman'

    colors = self.widgets.color.values.choices
    min_cells = int(self.widgets.min_cells_in_bin.values.value)-1
    ret = OrderedDict()
    for color in colors:
      if color == 'None':
        color = None
      fig = axes.new_figure(FIG_SIZE_X, FIG_SIZE_Y)
      ax = fig.add_subplot(111)
      
      hist, extent = axes.histogram_scatter(ax, table, (dim_x, dim_y), range, color, min_cells_per_bin = min_cells, no_bins_x=ax_width*1j, no_bins_y=ax_height*1j, interpolation=interpolation)
      if self.widgets.contour.get_choices()[0] == 'regular':
        cs = ax.contour(hist, extent=extent, origin='lower')
        #ax.clabel(cs, inline=1, fontsize=10)
        
      elif self.widgets.contour.get_choices()[0] == 'smooth':
        display_data, extent, density, X, Y = axes.kde2d_data(table, (dim_x, dim_y), range, res=ax_width)
        #np.r_[0:np.max(display_data):10j][1:]
        levels = np.array([0.1, 0.2, 0.3, 0.35, 0.4, 0.5, 0.6, 0.8, 1]) * np.max(display_data)
        if color!=None:
          cs = ax.contour(display_data, extent=extent, origin='lower', levels=levels, colors='black')
        else:
          cs = ax.contour(display_data, extent=extent, origin='lower', levels=levels)
        #ax.clabel(cs, inline=1, fontsize=10)
      ret[str(color)] = fig
    print axes.ax_size_pixels(ax)
    return ret


class TrueScatterPlot(AbstractPlot):
  """TrueScatterPlot. A scatter plot where each point is a single cell.
  """
  def __init__(self, id, parent, gate=False):
    AbstractPlot.__init__(self, id, parent, gate)
    
  def name(self):
    return 'True Scatter Plot'
  
  def control_panel(self, table): 
    return View(self, '')

  def draw_figures(self, table, dim_x, dim_y, range):
    ret = OrderedDict();
    fig = axes.new_figure(FIG_SIZE_X, FIG_SIZE_Y)
    ax = fig.add_subplot(111)
    axes.points(ax, table, (dim_x, dim_y))
    ret[0] = fig;
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
