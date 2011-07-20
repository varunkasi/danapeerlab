#!/usr/bin/env python
import os
from odict import OrderedDict
from widget import Widget
from view import View
from view import render
from view import stack_left
from view import stack_lines
from biology.dataindex import DataIndex
from biology.datatable import combine_tables
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
    self._add_widget('fcs_dir', Input)
    self._add_widget('fcs_files', Select)
    self._add_widget('combine_select', Select)
    self._add_widget('arcsin_factor', Input)
    self._add_widget('apply', ApplyButton)
    self.last_selected_dir = None

  def get_inputs(self):
    return []

  def get_outputs(self):
    if not self.widgets.combine_select.values.choices or 'combine' in self.widgets.combine_select.values.choices:
      return ['table']
    else:
      return ['table'] + ['table%d' % i for i in xrange(1, len(self.widgets.fcs_files.values.choices))]

  def title(self, short):
   dirname = self.widgets.fcs_dir.value_as_str()
   if not dirname or not os.path.exists(dirname):
      return 'Please enter a valid path for a directory with FCS files'
   return os.path.split(dirname)[-1]

  def run(self):
    """ The run method loads the datatable.
    """
    # Raise an exception if no path is given or if the path does not exist. This will
    # stop the chain, but the user will be able to pick a new path as the view method
    # is called before the run method. 
    dirname = self.widgets.fcs_dir.value_as_str()
    if not os.path.exists(dirname):
      raise Exception('Could not find %s' % dirname)

    loaded_tables = []
    log_text = []
    for filename in self.widgets.fcs_files.values.choices:
      filepath = os.path.join(dirname, filename)
      table = load_data_table(filepath, arcsin_factor=self.widgets.arcsin_factor.value_as_float())
      table.name = filename
      loaded_tables.append(table)
      log_text.append('Loaeded %s: %d cells' % (filename, table.num_cells))
    
    if not loaded_tables:
      raise Exception('No files were chosen')
    
    ret = {}  
    ret['view'] = '\n'.join(log_text)
    if 'combine' in self.widgets.combine_select.values.choices:
      ret['table'] = combine_tables(loaded_tables)
      ret['table'].name = os.path.split(dirname)[-1]
    else:
      ret['table'] = loaded_tables[0]
      for i in xrange(1, len(loaded_tables)):
        ret['table%d' % i] = loaded_tables[i]
    return ret

  def view(self):
    """ The view method will display the control panel to select the FCS path
    and the arcsin factor.
    """
    self.widgets.fcs_dir.guess_or_remember('load_fcs fcs_dir', '')
    dirname = self.widgets.fcs_dir.value_as_str()
    if os.path.exists(dirname):
      files = [f for f in os.listdir(dirname) if os.path.isfile(os.path.join(dirname, f))]
    else:
      return stack_lines(
          View(self, 'Please select a valid directory'),
          self.widgets.fcs_dir.view('FCS Directory', self.widgets.apply, numeric_validation=False, size=100),
          self.widgets.apply.view())

    # Clear file list if we switched directory:
    if dirname != self.last_selected_dir:
      self.widgets.fcs_files.values.choices = None
      self.last_selected_dir = dirname

    self.widgets.fcs_files.guess_or_remember(('load_fcs fcs_files', files, dirname), [])
    self.widgets.combine_select.guess_or_remember(('load_fcs combine_select', dirname), ['combine'])
    self.widgets.arcsin_factor.guess_or_remember(('load_fcs arcsin_factor', dirname), 1)

    # display the control panel:
    return stack_lines(
        self.widgets.fcs_dir.view('FCS Directory', self.widgets.apply, numeric_validation=False, size=100),
        self.widgets.fcs_files.view('FCS Files', self.widgets.apply, files),
        self.widgets.combine_select.view('Combine files', self.widgets.apply, [('combine', 'Combine files into one output'), ('seperate', 'Seperate to one output per file')], multiple=False),
        self.widgets.arcsin_factor.view('Arcsinh Factor', self.widgets.apply, numeric_validation=True, comment='Transformation: arcsinh(value * factor)'),
        self.widgets.apply.view())