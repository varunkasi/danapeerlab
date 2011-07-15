#!/usr/bin/env python
import os
from odict import OrderedDict
from widget import Widget
from view import View
from view import render
from view import stack_left
from view import stack_lines
from biology.dataindex import DataIndex
from widgets.expander import Expander
from widgets.select import Select
from input import Input
from biology.loaddatatable import load_data_table
from widgets.applybutton import ApplyButton
import settings


class LoadFcs(Widget):
  """ This module loads a single FCS file from a path the user enters. 
  The module has no inputs, and only one output -- a datatable with the loaded
  FCS file.
  """
  
  def __init__(self, id, parent):
    Widget.__init__(self, id, parent)
    self._add_widget('fcs_location', Input)
    self._add_widget('arcsin_factor', Input)
    self._add_widget('apply', ApplyButton)

  def get_inputs(self):
    return []

  def get_outputs(self):
    return ['table']
  
  def title(self, short):
    if not self.widgets.fcs_location.value_as_str():
      return 'Please pick a path for FCS file'
    if short:           
      return os.path.split(self.widgets.fcs_location.value_as_str())[1]
    else:
      return self.widgets.fcs_location.value_as_str()


  def run(self):
    """ The run method loads the datatable.
    """
    # Raise an exception if no path is given or if the path does not exist. This will
    # stop the chain, but the user will be able to pick a new path as the view method
    # is called before the run method. 
    if not self.widgets.fcs_location.value_as_str() or not os.path.exists(self.widgets.fcs_location.value_as_str()):
      raise Exception('Could not find %s' % self.widgets.fcs_location.value_as_str())

    ret = {}
    # This is the only output -- the loaded datatable. 
    ret['table'] = load_data_table(self.widgets.fcs_location.value_as_str(), arcsin_factor=self.widgets.arcsin_factor.value_as_float())
    ret['table'].name = os.path.split(self.widgets.fcs_location.value_as_str())[1]
    # We want to display a little log message after the module's box:
    ret['view'] = 'Loaded %d cells' % ret['table'].num_cells
    return ret

  def view(self):
    """ The view method will display the control panel to select the FCS path
    and the arcsin factor.
    """
    # Set a default value for the arcsin widget:
    if not self.widgets.arcsin_factor.values.value:
      self.widgets.arcsin_factor.values.value = '1'
    # display the control panel:
    return stack_lines(
        self.widgets.fcs_location.view('FCS Path', self.widgets.apply, numeric_validation=False),
        self.widgets.arcsin_factor.view('Arcsinh Factor', self.widgets.apply, numeric_validation=True, comment='Transformation: arcsinh(value * factor)'),
        self.widgets.apply.view())