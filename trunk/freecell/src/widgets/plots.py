#!/usr/bin/env python
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
from multitimer import MultiTimer
from widgetwithcontrolpanel import WidgetWithControlPanel
    
class AbstractPlot(WidgetWithControlPanel):
  """An abstract class for plot modules. 
  Every sub class must implement: _name, _draw_figures_internal and control_panel.
  """
  def __init__(self, id, parent, enable_gating):
    WidgetWithControlPanel.__init__(self, id, parent)
    self.enable_gating = enable_gating
    
  def title(self, short):
    name = self._name()
    if 'dim_x' in self.widgets and 'dim_y' in self.widgets:
      dim_x = self.widgets.dim_x.values.choices
      dim_y = self.widgets.dim_y.values.choices
    else:
      dim_x = ''
      dim_y = ''
    return '%s: %s X %s' % (name,
        ', '.join(dim_x),
        ', '.join(dim_y))
        
  def get_outputs(self):
    if not self.enable_gating:
      return []
    else:
      return ['tables', 'tables_out_of_gate']

        
  def control_panel(self, tables):
    self._add_select(
        'dim_x',
        'X Axis',
        options=options_from_table(tables[0]),
        is_multiple=not self.enable_gating,
        cache_key=tables,
        default=[tables[0].dims[0]])
    
    self._add_select(
        'dim_y',
        'Y Axis',
        options=options_from_table(tables[0]),
        is_multiple=not self.enable_gating,
        cache_key=tables,
        default=[tables[0].dims[1]])
      
    self._add_select(
        'tables_to_show',
        'Tables to Show',
        options=[('all', 'All tables')] + [(t.name, t.name) for t in tables],
        is_multiple=True,
        cache_key=tables,
        default=['all'])
        
    self._begin_section('View Area')
        
    self._add_input(
        'min_x',
        'Min X',
        cache_key=tables,
        default='common',
        numeric_validation=False,
        non_empty_validation=False,
        size=8,
        predefined_values=[('Fit per plot', 'auto'), ('Fit for row plots', 'common')])

    self._add_input(
        'min_y',
        'Min Y',
        cache_key=tables,
        default='common',
        numeric_validation=False,
        non_empty_validation=False,
        size=8,
        predefined_values=[('Fit per plot', 'auto'), ('Fit for row plots', 'common')])
    
    self._add_input(
        'max_x',
        'Max X',
        cache_key=tables,
        default='common',
        numeric_validation=False,
        non_empty_validation=False,
        size=8,
        predefined_values=[('Fit per plot', 'auto'), ('Fit for row plots', 'common')])

    self._add_input(
        'max_y',
        'Max Y',
        cache_key=tables,
        default='common',
        numeric_validation=False,
        non_empty_validation=False,
        size=8,
        predefined_values=[('Fit per plot', 'auto'), ('Fit for row plots', 'common')])
    
    self._end_section('View Area', False)
    
    if self.enable_gating:  
      # we need to save ids for the gate inputs, so that the areaselect in the view function 
      # can reference them.
      self.gate_min_x_id = 'min_x_%s'  % self._get_unique_id()
      self.gate_max_x_id = 'max_x_%s'  % self._get_unique_id()
      self.gate_min_y_id = 'min_y_%s'  % self._get_unique_id()
      self.gate_max_y_id = 'max_y_%s'  % self._get_unique_id()
      
      
      # we need the max/min values for the predefined values on the gate input.
      dim_x = self.widgets.dim_x.get_choice()
      dim_y = self.widgets.dim_y.get_choice()
      min_x=0; min_y=0; max_x=0; max_y=0;
      if dim_x:
        min_x = tables[0].min(dim_x)
        max_x = tables[0].max(dim_x)
      if dim_y:
        min_y = tables[0].min(dim_y)
        max_y = tables[0].max(dim_y)        
      
      
      self._begin_section('Gate')      
        
      self._add_input(
          'gate_min_x',
          'Gate Min X',
          id=self.gate_min_x_id,
          cache_key=tables,
          default='%.2f' % min_x,
          numeric_validation=False,
          non_empty_validation=False,
          predefined_values=[('Minimum', '%.2f' % min_x)])

      self._add_input(
          'gate_min_y',
          'Gate Min Y',
          id=self.gate_min_y_id,
          cache_key=tables,
          default='%.2f' % min_y,
          numeric_validation=False,
          non_empty_validation=False,
          predefined_values=[('Minimum', '%.2f' % min_y)])
    
      self._add_input(
          'gate_max_x',
          'Gate Max X',
          id=self.gate_max_x_id,
          cache_key=tables,
          default='%.2f' % max_x,
          numeric_validation=False,
          non_empty_validation=False,
          predefined_values=[('Maximum', '%.2f' % max_x)])

      self._add_input(
          'gate_max_y',
          'Gate Max Y',
          id=self.gate_max_y_id,
          cache_key=tables,
          default='%.2f' % max_y,
          numeric_validation=False,
          non_empty_validation=False,
          predefined_values=[('Maximum', '%.2f' % max_y)])
    
      self._end_section('Gate', False)


  def _get_range(self, table, dim_x, dim_y, all_tables):
    """Returns the [min_x, min_y, max_x, max_y] range according to the relevant
    control panel inputs. If 'auto' is in one of the inputs we will use the
    relevant min/max value.
    """
    def convert_to_number(val, val_if_auto, val_if_common):
      try:
        return float(val)
      except ValueError:
        if val == 'auto':
          return val_if_auto
        else:
          return val_if_common
    return [
        convert_to_number(self.widgets.min_x.value_as_str(), table.min(dim_x), min([t.min(dim_x) for t in all_tables])),
        convert_to_number(self.widgets.min_y.value_as_str(), table.min(dim_y), min([t.min(dim_y) for t in all_tables])),
        convert_to_number(self.widgets.max_x.value_as_str(), table.max(dim_x), max([t.max(dim_x) for t in all_tables])),
        convert_to_number(self.widgets.max_y.value_as_str(), table.max(dim_y), max([t.max(dim_y) for t in all_tables]))]

  @cache('plots')
  def _draw_figures(self, table, dim_x_arr, dim_y_arr, all_tables):
    """Returns a dictionary of id->(figure, extra_view, range). figure is a matplotlib figure.
    extra_view is a view. range is the range for the data in the figure.
    Id is composed of the image dimensions, and the id it received in the
    _draw_figures_internal function. We will create a Figure widget for each 
    unique id.
    """
    ret = OrderedDict()
    multi_timer = MultiTimer(len(dim_x_arr) * len(dim_y_arr))
    for dim_x in dim_x_arr:
      for dim_y in dim_y_arr:
        fig_range = self._get_range(table, dim_x, dim_y, all_tables)
        figures = self._draw_figures_internal(table, dim_x, dim_y, fig_range)        
        for key, val in figures.iteritems():
          # Other than figure, the sub _draw_figures_internal can also send an extra view. In this case
          # fig will be tuple. 
          if type(val) == tuple:
            fig = val[0]
            extra_view = val[1]
          else:
            fig = val
            extra_view = View(self, '')            
          ret['%s_%s_%s' % (dim_x, dim_y, key)] = (fig, extra_view, fig_range)
        multi_timer.complete_task('%s %s' % (dim_x, dim_y))
    return ret

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

  @cache('plots_main_view')
  def main_view(self, tables):
    if 'all' in self.widgets.tables_to_show.get_choices():
      tables_to_show = tables
    else:
      tables_to_show = [t for t in tables if t.name in self.widgets.tables_to_show.get_choices()]
    if not tables_to_show:
      return
    # Assemble the figure to show
    figures_to_show = []
    multi_timer = MultiTimer(len(tables_to_show))
    for table_input in tables_to_show:
      figures_to_show.append(self._draw_figures(table_input, self.widgets.dim_x.get_choices(), self.widgets.dim_y.get_choices(), tables_to_show))
      multi_timer.complete_task(table_input.name)

    # Draw the figures in a table
    lines = []
    for key in figures_to_show[0].iterkeys():
      line = []
      for i in xrange(len(tables_to_show)):
        fig_widget = self._add_widget_if_needed('%d_%s' % (i, key), Figure)
        fig, extra_view, fig_range = figures_to_show[i][key]      
        # We give the view function a predefined id so that we can reference this viewed instance from
        # the areaselect widget in gating mode.  
        widget_id = self._get_unique_id()
        if fig:
          fig_view = fig_widget.view(fig, id=widget_id)
          if self.enable_gating:
            area_select_widget = self._add_widget_if_needed('area_select_%s' % widget_id, AreaSelect)
            area_select_view = area_select_widget.view(
                widget_id, self.gate_min_x_id, self.gate_max_x_id, self.gate_min_y_id, self.gate_max_y_id, fig_range)
            fig_view = stack_lines(fig_view, area_select_view)          
        else:
          fig_view = View(self, '')
        # On gating mode we want to add areaselect.
        line.append(stack_lines(fig_view, extra_view))
      lines.append(line)  
    if len(tables_to_show) == 1:
      return view.stack_left(*[l[0] for l in lines])
    else:
      self._add_widget_if_needed('input_table', Table)
      return self.widgets.input_table.view([table_input.name for table_input in tables_to_show], lines)
    
FIG_SIZE_X = 500
FIG_SIZE_Y = 500

class DensityPlot(AbstractPlot):
  def __init__(self, id, parent):
    AbstractPlot.__init__(self, id, parent, False)
  
  def _name(self):
    return 'Density Plot'
    
  def _draw_figures_internal(self, table, dim_x, dim_y, range):
    fig = axes.new_figure(FIG_SIZE_X, FIG_SIZE_Y)
    try:
      axes.kde2d_color_hist(fig, table, (dim_x, dim_y), range)
      return {'fig': fig}
    except Exception as e:
      logging.exception('Exception in DensityPlot')
      return {'fig': (None, View(self, str(e)))}
    

class FunctionPlot(AbstractPlot):
  def __init__(self, id, parent, enable_gating=False):
    AbstractPlot.__init__(self, id, parent, enable_gating)
    self._add_widget('min_density_in_column', Input)  
  
  def _name(self):
    return 'Function Plot'
    
  def control_panel(self, tables):
    AbstractPlot.control_panel(self, tables)
    self._add_input(
        'min_density_in_column',
        'Minimal density in column',
        cache_key=tables,
        default='0.005')

  def _draw_figures_internal(self, table, dim_x, dim_y, range):
    fig = axes.new_figure(FIG_SIZE_X, FIG_SIZE_Y)
    try:
      axes.kde2d_color_hist(fig, table, (dim_x, dim_y), range, 'y', self.widgets.min_density_in_column.value_as_float())
      corr_view = View(None, 'corr: %.2f; mi: %.2f' % (table.get_correlation(dim_x, dim_y), table.get_mutual_information(dim_x, dim_y)))
      return {'fig': (fig, corr_view)}
    except Exception as e:
      logging.exception('Exception in DensityPlot')
      return {'fig': (None, View(self, str(e)))}
    

class ScatterPlot(AbstractPlot):
  def __init__(self, id, parent, enable_gating=False):
    AbstractPlot.__init__(self, id, parent, enable_gating)
    self._add_widget('color', Select)
    self._add_widget('resolution', Select)
    self._add_widget('min_cells_in_bin', Input)
    self._add_widget('contour', Select)
  
  def _name(self):
    return 'Scatter Plot'
  
  def control_panel(self, tables):
    AbstractPlot.control_panel(self, tables)
    self._add_select(
        'contour',
        'Draw Contour Lines',
        options=[('none', 'None'), ('regular', 'Regular Contour'), ('smooth', 'Smooth Contour')],
        is_multiple=False,
        cache_key=tables,
        default=['none'])

    self._add_select(
        'color',
        'Color',
        options=[('None', [('none', 'No Color')])] +  options_from_table(tables[0]),
        is_multiple=True,
        cache_key=tables,
        default=['none'])

    if not self.widgets.color.values.choices:
      self.widgets.color.values.choices = ['None']

    self._add_select(
        'resolution',
        'Resolution',
        options=['1', '1.25', '1.5', '2', '3', '4'],
        is_multiple=False,
        cache_key=tables,
        default=['1'])
    
    self._add_input(
        'min_cells_in_bin',
        'Minimum cells in a bin',
        cache_key=tables,
        default='1')
    
    if self.widgets.min_cells_in_bin.values.value == None:
      self.widgets.min_cells_in_bin.values.value = 1

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
  
  def _draw_figures_internal(self, table, dim_x, dim_y, range):
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
      try:
        if color == 'none':
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
      except Exception as e:
        logging.exception('Exception in ScatterPlot')
        ret[str(color)] = (None, View(self, str(e)))
    return ret


class TrueScatterPlot(AbstractPlot):
  """TrueScatterPlot. A scatter plot where each point is a single cell.
  """
  def __init__(self, id, parent, enable_gating=False):
    AbstractPlot.__init__(self, id, parent, enable_gating)
    
  def _name(self):
    return 'True Scatter Plot'
  

  def _draw_figures_internal(self, table, dim_x, dim_y, range):
    ret = OrderedDict();
    try:
      if table.num_cells > 10000:
        raise Exception('table is too big')  
      fig = axes.new_figure(FIG_SIZE_X, FIG_SIZE_Y)
      ax = fig.add_subplot(111)
      axes.points(ax, table, (dim_x, dim_y), range)
      ret[0] = fig;
    except Exception as e:
      logging.exception('Exception in ScatterPlot')
      ret[0] = (None, View(self, str(e)))  
    return ret


class ScatterGater(ScatterPlot):
  def __init__(self, id, parent):
    ScatterPlot.__init__(self, id, parent, True)

  def _name(self):
    return 'Scatter Gater'

class DensityGater(DensityPlot):
  def __init__(self, id, parent):
    AbstractPlot.__init__(self, id, parent, True)

  def _name(self):
    return 'Density Gater'

class FunctionGater(FunctionPlot):
  def __init__(self, id, parent):
    FunctionPlot.__init__(self, id, parent, True)
    
  def _name(self):
    return 'Function Gater'
