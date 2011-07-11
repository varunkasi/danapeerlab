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
from cache import cache


FIG_SIZE_X = 500
FIG_SIZE_Y = 500


class HistogramPlot(Widget):
  """ This is a module that displays multiple histogram plots for some selected
  dimensions.
  The module has 4 inputs, each input is drawn in a different color.
  The module has no outputs, as it doesn't change the data it receives.
  """
  def __init__(self, id, parent):
    Widget.__init__(self, id, parent)
    self._add_widget('dims', Select)
    self._add_widget('layout', LeftPanel)
    self._add_widget('apply', ApplyButton)
    
  def title(self, short):
    """Title for the module, the short version is displayed in menus, 
    the long version is displayed in the expander title.
    """
    if not self.widgets.dims.values.choices:
      return 'Histogram'
    else:
      return 'Histogram %s' % ', '.join(self.widgets.dims.values.choices)
      
  def get_inputs(self):
    """ Returns the names of the 4 inputs. The first input is called
    table and not talbe1, so that outputs with the name table will be
    connected to it by default.
    """
    return ['table', 'table2', 'table3', 'table4']
    
  def get_outputs(self):
    """ Returns the empty list of outputs for this module.
    """
    return []
  
  def run(self, **tables):
    """ The run method for this module doesn't do anything.
    """
    pass
    
  @cache('histograms')
  def view(self, **tables):
    """ The view method of this module draws the control panel and the histograms. 
    We need at least one input to be able to draw something.
    """
    
    # Create the control panel view. This will enable users to choose the dimensions. 
    control_panel_view = stack_lines(
        self.widgets.dims.view('Dimension', self.widgets.apply, options_from_table(tables['table'])),
        self.widgets.apply.view())
    # These are the inputs which contain data:
    inputs = [input for input in self.get_inputs() if tables[input]]
    main_views = []
    # Check that the user has already chosen dimensions. Otherwise, ask him 
    # to do so.
    if self.widgets.dims.values.choices:
      for dim in self.widgets.dims.values.choices:
        # Go over every dimension and create the histogram:
        # First create a new figure:
        fig = axes.new_figure(FIG_SIZE_X, FIG_SIZE_Y)
        ax = fig.add_subplot(111)
        # Draw the histogram for every input (matplotlib will know to switch colors)
        for input in inputs:
          axes.kde1d(ax, tables[input], dim)
        # Make sure we don't create the same widget twice. We create a new widget
        # for every dimension asked. 
        widget_key = self._normalize_id(dim)
        if not widget_key in self.widgets:
          self._add_widget(widget_key, Figure)
        figure_widget = self.widgets[widget_key]
        # Add the new widget's view
        main_views.append(figure_widget.view(fig))
      main_view = view.stack_left(*main_views)
    else:
      main_view = View(None, 'Please select dimensions')    
    # combine the control panel and the main view togeteher:
    return self.widgets.layout.view(main_view, control_panel_view)
