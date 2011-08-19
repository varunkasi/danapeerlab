#!/usr/bin/env python
import axes
import numpy as np
import view
import logging
import biology.datatable as datatable
from multitimer import MultiTimer
from operator import itemgetter
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
from cache import cache

def greedy_distance_sort(distance_table, items_to_sort):
  """Accepts a list of items and a rectangular distance DataTable.
  The item indexes match those of the distance_table dims.
  We will sort the items s.t. for each item the next one is the nearest
  one not already chosen.
  """
  ret = [items_to_sort[0]]
  while len(ret) < len(distance_table.dims):
    # find item nearest to the last one in the list
    last_item_index = items_to_sort.index(ret[-1])
    distances = distance_table.get_points(distance_table.dims[last_item_index])
    min_value = np.inf
    min_index = None
    for i,distance in enumerate(distances):
      if items_to_sort[i] in ret:
        continue
      if distance < min_value:
        min_value = distance
        min_index = i
    ret += [items_to_sort[min_index]]
  return ret

class HistogramPlot(Widget):
  """ This is a module that displays multiple histogram plots for some selected
  dimensions.
  The module has one input which can contain multiple tables for comparison.
  The module has no outputs, as it doesn't change the data it receives.
  """
  def __init__(self, id, parent):
    Widget.__init__(self, id, parent)
    self._add_widget('dims', Select)
    self._add_widget('color', Select)
    self._add_widget('text', Select)
    self._add_widget('sort_inside', Select)
    self._add_widget('sort_outside', Select)
    self._add_widget('layout', LeftPanel)
    self._add_widget('apply', ApplyButton)
    self._add_widget('shift', Input)
    self._add_widget('legend_figure', Figure)
  
  def on_load(self):
    if not 'text' in self.widgets:
      self._add_widget('text', Select)
    
  def title(self, short):
    """Title for the module, the short version is displayed in menus, 
    the long version is displayed in the expander title.
    """
    if not self.widgets.dims.values.choices:
      return 'Histogram'
    else:
      return 'Histogram %s' % ', '.join(self.widgets.dims.values.choices)
      
  def get_inputs(self):
    """ Returns the names input list.
    """
    return ['tables']
    
  def get_outputs(self):
    """ Returns the empty list of outputs for this module.
    """
    return []
  
  def run(self, **tables):
    """ The run method for this module doesn't do anything.
    """
    pass
  
  def create_and_adjust_figure(self, tables):
    X_SIZE_FOR_HISTOGRAMS = 300
    X_SIZE_PER_NAME_LETTER = 6
    Y_SIZE_PER_CURVE = 35
    MIN_Y = 300
  
    # first let's calculate the width.
    texts = [str(t.get_tags(self.widgets.text.values.choices)) for t in tables]
    max_text_length = max([len(t) for t in texts])
    x_size_for_text = X_SIZE_PER_NAME_LETTER * max_text_length
    x_size = x_size_for_text + X_SIZE_FOR_HISTOGRAMS
    y_size = len(tables) * Y_SIZE_PER_CURVE
    y_size = max(MIN_Y, y_size)
    fig = axes.new_figure(x_size, y_size)
    fig.subplots_adjust(left=x_size_for_text / float(x_size))
    return fig
    
    
  @cache('histograms')
  def view(self, tables):
    """ The view method of this module draws the control panel and the histograms. 
    We need at least one input to be able to draw something.
    """
    if not tables:
      return View(self, 'No tables to show.')
    self.widgets.color.guess_or_remember(('histogram text', tables), 'name')
    self.widgets.text.guess_or_remember(('histogram colors', tables), 'name')
    self.widgets.shift.guess_or_remember(('histogram shift', tables), '0.2')
    self.widgets.shift.guess_or_remember(('histogram sort inside', tables), 'similarity')
    self.widgets.shift.guess_or_remember(('histogram sort outside', tables), 'sort')
    
    sort_inside_options = [('unsort', 'Keep original order'), ('similarity', 'Put similar curves together')]
    sort_inside_options += [(x, 'Sort by %s' % x) for x in tables[0].tags.keys()]
    
    # Create the control panel view. This will enable users to choose the dimensions. 
    control_panel_view = stack_lines(
        self.widgets.dims.view('Dimension', self.widgets.apply, options_from_table(tables[0])),
        self.widgets.text.view('Text by', self.widgets.apply, tables[0].tags.keys()),
        self.widgets.color.view('Color by', self.widgets.apply, tables[0].tags.keys()),
        self.widgets.shift.view('Shift for multiple curves', self.widgets.apply),
        self.widgets.sort_inside.view('Curve sorting', self.widgets.apply, 
                                      sort_inside_options,
                                      multiple=False),
        self.widgets.sort_outside.view('Plot sorting', self.widgets.apply, 
                                      [('sort', 'Put plots with many differences first'), ('unsort', 'Keep original order')],
                                      multiple=False),
        self.widgets.apply.view())
    main_views = []
    shift = self.widgets.shift.value_as_float()
    plots_for_legend = OrderedDict()
    # Check that the user has already chosen dimensions. Otherwise, ask him 
    # to do so.
    if self.widgets.dims.values.choices:
      timer = MultiTimer(len(self.widgets.dims.values.choices))
      for i, dim in enumerate(self.widgets.dims.values.choices):
        try:
          # Go over every dimension and create the histogram:
          # First create a new figure:
          fig = self.create_and_adjust_figure(tables)
          ax = fig.add_subplot(111)
          
          # Draw the histogram for every input
          plots = []
          colorer = axes.Colorer()
          sorted_tables = tables
          sort_method = self.widgets.sort_inside.values.choices[0]
          if sort_method == 'unsort':
            sorted_tables = tables
          elif sort_method == 'similarity':
            # get distances table:
            distances = datatable.ks_distances(tables, dim)
            # sort by distance
            sorted_tables = greedy_distance_sort(distances, tables)
          else:
            # we need to sort by tags:
            tag_for_sort = self.widgets.sort_inside.values.choices[0]
            sorted_tables = sorted(tables, key=lambda table: table.tags[tag_for_sort])
          for i, table in enumerate(sorted_tables):
            color_tags = self.widgets.color.values.choices
            color_key = tuple([table.tags[c] for c in color_tags])
            plot = axes.kde1d(ax, table, dim,
                              color=colorer.get_color(color_key),
                              shift=shift*i)
            plots_for_legend[color_key] = plot
          # Add ticks with table names:
          if self.widgets.shift.value_as_float() > 0:
            ax.set_yticks(np.arange(0, len(tables)*shift, shift))
            ax.set_yticklabels([t.get_tags(self.widgets.text.values.choices) for t in sorted_tables], size='xx-small')
          # set axes y range:
          ax.set_ylim(bottom = -0.1, top=0.8+shift*(len(sorted_tables)-1))
          # Make sure we don't create the same widget twice. We create a new widget
          # for every dimension asked. 
          widget_key = self._normalize_id(dim)
          if not widget_key in self.widgets:
            self._add_widget(widget_key, Figure)
          figure_widget = self.widgets[widget_key]
        
          if len(tables) > 1:
            from scipy.stats import ks_2samp
            ks, p_ks = ks_2samp(tables[0].get_cols(dim)[0], tables[1].get_cols(dim)[0])
            ks_view = View(self, 'ks: %.3f, p_ks: %.10f' % (ks, p_ks))
            final_view = stack_lines(ks_view, figure_widget.view(fig))
          else:
            ks, p_ks = 0, 0
            final_view = figure_widget.view(fig)
          # Add the new widget's view
          main_views.append((ks, p_ks, final_view))
        except Exception as e:
          logging.exception('Exception when drawing histogram')
          main_views.append((0, 0, View(self, str(e))))
                  
        timer.complete_task(dim)
      
      # sort by the ks test:
      main_views = sorted(main_views, key=itemgetter(0), reverse=True)
      main_views = [v[2] for v in main_views]
      
      
      
      
      # create legend:
      legened_titles = plots_for_legend.keys()
      print len(legened_titles)
      max_title_len = max([len(str(t)) for t in legened_titles])
      print max_title_len
      WIDTH_PER_LETTER = 7
      EXTRA_WIDTH = 60
      HEIGHT_PER_LINE = 30
      EXTRA_HEIGHT = 50
      MIN_X = 300
      MIN_Y = 100
      legend_x = max(MIN_X, EXTRA_WIDTH + WIDTH_PER_LETTER * max_title_len)
      legend_y = max(MIN_Y, EXTRA_HEIGHT + HEIGHT_PER_LINE * len(legened_titles))
      fig = axes.new_figure(legend_x, legend_y)
      ax = fig.add_subplot(111)
      ax.get_xaxis().set_visible(False)
      ax.get_yaxis().set_visible(False)
      ax.legend(plots_for_legend.values(),
                plots_for_legend.keys(),
                loc='center',
                mode='expand',
                frameon=False,
                prop={'size' : 'xx-small'})
      main_views = [self.widgets.legend_figure.view(fig)] + main_views
      main_view = view.stack_left(*main_views)
      
      
    else:
      main_view = View(None, 'Please select dimensions')    
    # combine the control panel and the main view togeteher:
    return self.widgets.layout.view(main_view, control_panel_view)
