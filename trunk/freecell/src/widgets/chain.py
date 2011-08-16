#!/usr/bin/env python
import logging
from odict import OrderedDict
from widget import Widget
import view
from view import View
from view import render
from view import stack_lines
from view import stack_left
from view import stack
from select import Select
from input import Input
from applybutton import ApplyButton
from figure import Figure
from layout import Layout
from timer import Timer
from expander import Expander
from miniexpander import MiniExpander
from freecellmenu import FreecellMenu
from histogram import HistogramPlot
from loadfcs import LoadFcs
import plots
from network import Network
from populationpicker import PopulationPicker

""" A chain is a special widget that allows users to create interactive chains
of modules. This creates a pipeline that manipulates data and displays results
in the process.

A chain is made of modules. a module is a special kind of a widget (it will be
defined later). Every module has (optional) inputs and outputs. The users
connect modules' outputs to modules' inputs. The Chain widget runs the modules
one by one. Each module displays data, and manipulates data into its outputs.


How to create a module
----------------------
A module is firstly a regular widget. So It should behave like a widget (see
widget.py) namely:
  - Inherit from Widget
  - Have an __init__ like this: 
    def __init__(self, id, parent, arg1, arg2, arg3, arg4):
      Widget.__init__(self, id, parent) 
  - Have a view method that will display the module's controls and possibly
    visualization over the data input.
    The view method receives a **kargs dictionary of the form
    input_name --> input.
    It should return a View object like a regular view method for a widget.

A module should also have:
  - A run method that turns input data to output data. 
    The run method receives a **kargs dictionary of the form
    input_name --> input.    
    It can return None if it doesn't do anything, or return a dictionary of the
    form output_name --> output. An output can be anything, but right now 
    we only use DataTable lists. If an output is a list with datatables,
    they must have a name.
  - A get_inputs / get_outputs methods that return a list of inputs/outputs
    names.
  - A title(self, short) method that displays the modules title. The short
    title is used in the input menu when referencing other modules' outputs. 

Lastly, a module should appear in the CHAINABLE_WIDGETS list in this file.
Simple modules that can be used as exampels are: FcsLoader and Histogram.

Some Notes:
  - Anything can be passed as input / outputs, but right now we are only using
    DataTable lists. This way the user can connect a wrong output to an input by
    mistake.
  - If a user had chosen to connect two outputs to the same inputs, we will use
    the operator += to concatenate. 
  - The chain GUI displays a menu to help the user decide which outputs should
    be directed to which inputs. Some modules can accept None values for 
    certain inputs. 
  - The default output to connect to a given input, is the nearest output with
    the same name as the input.
  - The menu that lets the user select what output is connected to a certain
    input, displays module names. If there is more than one output for a 
    a module, then output names are also displayed. 
  - The run method can return a special output called 'view'. This output
    can contain a view that will be appended after the module's box. This is 
    used to display messages like '500 cells loaded'.

How modules are run
--------------------
The chain widget maintains a list of modules. Every module can get inputs 
from other modules outputs' as long as these modules appear before it in the
list.
When the chain widget view method is called, it starts running the chain. 
Each module is activated in order. First, the view method is called and
provided with the relevant inptus. Secondly, the run method is called,
and its outputs are saved for later use. 
Exceptions in view/run are printed on the report. If there is an exception in 
run, the chain execution is stopped (as some outputs will probably be missing). 
"""

CHAINABLE_WIDGETS = [
    ('FCS Loader', LoadFcs),
    ('Population Picker', PopulationPicker),
    ('Histogram Plot', HistogramPlot),
    ('Scatter Plot', plots.ScatterPlot),
    ('True Scatter Plot', plots.TrueScatterPlot),
    ('Density Plot', plots.DensityPlot),
    ('Function Plot', plots.FunctionPlot),
    ('Scatter Gater', plots.ScatterGater),
    ('Density Gater', plots.DensityGater),
    ('Function Gater', plots.FunctionGater),
    ('Network', Network)]

def widget_type_to_name(widget_type):
  global CHAINABLE_WIDGETS 
  entries = [e for e in CHAINABLE_WIDGETS if e[1] == widget_type]
  if not entries:
    raise Exception('Could not find entry %s' % str(widget_type))
  return entries[0][0]

def widget_name_to_type(name):
  global CHAINABLE_WIDGETS
  entries = [e for e in CHAINABLE_WIDGETS if e[0] == name]
  if not entries:
    raise Exception('Could not find entry %s' % str(name))
  args = []
  kargs = {}
  if len(entries[0]) > 2:
    args = entries[0][2]
  if len(entries[0]) > 3:
    kargs = entries[0][3]
  return entries[0][1], args, kargs

  
class WidgetInChain(Widget):
  def __init__(self, id, parent, sub_widget_type, previous_widgets, args, kargs):
    Widget.__init__(self, id, parent)
    self._add_widget('expander', Expander)
    self._add_widget('sub_widget', sub_widget_type, *args, **kargs)
    self._add_widget('delete_button', ApplyButton)

    self._add_widget('new_widget_select', Select)
    self._add_widget('apply_new_widget', ApplyButton)

    self._add_widget('input_panel', MiniExpander, False)
    self._add_widget('input_apply', ApplyButton)
    if self.widgets.sub_widget.has_method('get_inputs'):
      inputs = self.widgets.sub_widget.get_inputs()
    else:
      inputs = ['tables']
    self.input_to_select = OrderedDict()
    for i, input in enumerate(inputs):
      w = self._add_widget('input_select_%d' % i, Select)
      self.input_to_select[input] = w
      w.values.choices = [self.get_default_input(input, previous_widgets)]
  
  def on_load(self):
    self.outputs_from_run = None
    if not 'new_widget_select' in self.widgets:
      self._add_widget('new_widget_select', Select)
    if not 'apply_new_widget' in self.widgets:
      self._add_widget('apply_new_widget', ApplyButton)

  def get_default_input(self, input, previous_widgets):
    for i in xrange(len(previous_widgets)-1, -1, -1):
      if input in previous_widgets[i].get_outputs():
        return '%d,%s' % (i, input)
    return 'None'
  
  def get_outputs(self):
    #if self.outputs_from_run == None:
    #  raise Exception('Outputs can be queried only after run was called')
    
    #return self.outputs_from_run    
    if self.widgets.sub_widget.has_method('get_outputs'):
      outputs = self.widgets.sub_widget.get_outputs()
    else:
      outputs = ['tables']
    return outputs

  def get_idx_outputs(self, input):
    ret = []
    for input_choice in self.input_to_select[input].values.choices:
      idx = int(input_choice.split(',')[0])
      out = input_choice.split(',')[1]
      ret.append((idx, out))
    return ret
  
  def update_input_after_delete(self, input, deleted_index):
    choices_to_delete = []
    for i, input_choice in enumerate(self.input_to_select[input].values.choices):
      idx = int(input_choice.split(',')[0])
      out = input_choice.split(',')[1]
      if idx == deleted_index:
        choices_to_delete.append(input_choice)
      if idx > deleted_index:
        self.input_to_select[input].values.choices[i] = '%s,%s' % (idx - 1, out)
    for choice in choices_to_delete:
      self.input_to_select[input].values.choices.remove(choice)
  
  def update_input_after_add(self, input, add_index):
    for i, input_choice in enumerate(self.input_to_select[input].values.choices):
      idx = int(input_choice.split(',')[0])
      out = input_choice.split(',')[1]
      if idx >= add_index:
        self.input_to_select[input].values.choices[i] = '%s,%s' % (idx + 1, out)
    
  def create_input_map(self, data):
    input_map = {}
    for input in self.input_to_select:
      connected_outputs = self.get_idx_outputs(input)
      connected_outputs = [data[idx][out] for idx,out in connected_outputs]
      if connected_outputs:
        input_map[input] = sum(connected_outputs[1:], connected_outputs[0])
      else:
        input_map[input] = None
    return input_map     
      
  def run(self, data):
    self.outputs_from_run = []
    if self.widgets.sub_widget.has_method('run'):
        ret =  self.widgets.sub_widget.run(**self.create_input_map(data))
        #self.outputs_from_run = ret.keys()
        return ret
    
  def title(self, place_in_chain, short=False):
    if self.widgets.sub_widget.has_method('title'):
      ret = self.widgets.sub_widget.title(short)
    else:
      ret = widget_type_to_name(type(self.widgets.sub_widget))    
    if short:
      return '[%d] %s' % (place_in_chain + 1, ret)
    else:
      return '%d. %s' % (place_in_chain + 1, ret)

  def view(self, data, place_in_chain, possible_inputs):
    def create_inputs_summary():
      summary = []
      for input in self.input_to_select:
        choice = self.input_to_select[input].values.choices[0]
        choice_text = [p[1] for p in possible_inputs if p[0] == choice][0]
        #summary.append('%s: %s' % (input, choice_text))
        summary.append(choice_text)
      ret = ', '.join(summary)  
      if ret:
        return 'Inputs: %s ' % ret
      else:
        return ''

    #input_summary = View(self, '%sOutputs: %s' % (
    #    create_inputs_summary(),
    #    ', '.join(self.get_outputs())))
    
    input_summary = View(self, create_inputs_summary())

    input_content_views = []
    for k,v in self.input_to_select.items():
       input_content_views.append(v.view(
           k, self.widgets.input_apply, possible_inputs, multiple=True))
    input_content_views.append(self.widgets.input_apply.view())
    input_content = view.stack_lines(*input_content_views)    
    try:
      sub_widget_view = self.widgets.sub_widget.view(**self.create_input_map(data))
    except Exception as e:
      logging.exception('Exception in view')
      sub_widget_view = View(self, str(e))

    global CHAINABLE_WIDGETS
    widget_control_view = stack_left(
        self.widgets.new_widget_select.view('', self.widgets.apply_new_widget, zip(*CHAINABLE_WIDGETS)[0], False),
        self.widgets.apply_new_widget.view('Add before'),
        self.widgets.delete_button.view('Delete'))
    
    widget_control_view.main_html = '<div style="position:absolute; top:0; right:0;">%s</div>' % widget_control_view.main_html

    sub_view = view.stack_lines(
        widget_control_view,
        self.widgets.input_panel.view(input_summary, input_content), 
        view.vertical_seperator(),
        sub_widget_view)
    

    #sub_view = self.widgets.sub_widget.view(data)  
    #title_view = view.left_right(
    #    View(self, self.title(place_in_chain)), 
    #    self.widgets.delete_button.view('Delete'))
    title_view = View(self, self.title(place_in_chain))
    return self.widgets.expander.view(title_view, sub_view)

class Chain(Widget):
  def __init__(self, id, parent):
    Widget.__init__(self, id, parent)
    self._add_widget('new_widget_select', Select)
    self._add_widget('apply_new_widget', ApplyButton)
    self._add_widget('menu', FreecellMenu)
    
    self.widgets_in_chain = []
    self.widget_counter = 0
  
  def on_load(self):
    # add new modules
    if self.widgets.new_widget_select.values.choices:
      type_to_create, args, kargs = widget_name_to_type(self.widgets.new_widget_select.values.choices[0])
      self.widgets.new_widget_select.values.choices = []
      w = self._add_widget('chain_%d' % self.widget_counter, WidgetInChain, type_to_create, self.widgets_in_chain, args, kargs)
      self.widget_counter += 1
      self.widgets_in_chain.append(w)
    # delete modules
    for i, w in enumerate(self.widgets_in_chain):
      if w.widgets.delete_button.clicked:
        for following_widget in self.widgets_in_chain[i+1:]:
          for input in following_widget.input_to_select.iterkeys():
            following_widget.update_input_after_delete(input, i)
        self.widgets_in_chain.remove(w)
        self._remove_widget(w)
        break
    # add modules in between other moduels
    for i, w in enumerate(self.widgets_in_chain):
      if w.widgets.apply_new_widget.clicked:
        type_to_create, args, kargs = widget_name_to_type(w.widgets.new_widget_select.values.choices[0])
        w.widgets.new_widget_select.values.choices = []
        new_widget = self._add_widget('chain_%d' % self.widget_counter, WidgetInChain, type_to_create, self.widgets_in_chain, args, kargs)
        self.widget_counter += 1
        self.widgets_in_chain.insert(i, new_widget)
        for following_widget in self.widgets_in_chain[i+1:]:
         for input in following_widget.input_to_select.iterkeys():
            following_widget.update_input_after_add(input, i)
        break
    
  
  def widget_in_chain_to_inputs(self, widget_in_chain, place_in_chain):
    ret = []
    for output in widget_in_chain.get_outputs():
      if output == 'tables':
        name = widget_in_chain.title(place_in_chain, True)
      else:
        name = '%s --> %s' % (widget_in_chain.title(place_in_chain, True), output)
      code = '%d,%s' % (place_in_chain, output)
      ret.append((code, name))
    return ret
  
  def view(self):
    global CHAINABLE_WIDGETS
    # Run the chain:
    data = []
    views = []
    possible_inputs = [('None', 'None')]
    for i, widget in enumerate(self.widgets_in_chain):
      #logging.info('Getting view for Widget %d %s' % (i, widget.title(i, True)))
      with Timer('Module %d view' % (i+1)):
        views.append(widget.view(data, i, possible_inputs))
      possible_inputs += self.widget_in_chain_to_inputs(widget, i)
      #logging.info('Running Widget %d %s' % (i, widget.title(i)))
      try:
        with Timer('Module %d run' % (i+1)):
          widget_data = widget.run(data)
        data.append(widget_data)
        if widget_data and 'view' in widget_data:
          views.append(widget_data['view'])
          del widget_data['view']
        if widget_data:
          for item in widget_data.keys():
            from biology.datatable import DataTable
            if type(item) == list:
              for sub_item in item:
                if type(sub_item) == DataTable and not item.name:
                  raise Exception('DataTable outputs must have a name')
      except Exception as e:
        logging.exception('Exception in run')
        views.append('Exception when running %s: %s' % (widget.title(i), str(e)))
        break
    del data
    
    widgets_view = stack_lines(*views)
    add_view = stack(
        self.widgets.new_widget_select.view(
            'Add new module', self.widgets.apply_new_widget, zip(*CHAINABLE_WIDGETS)[0], False),
        self.widgets.apply_new_widget.view())
    return stack_lines(
        self.widgets.menu.view(self.parent.id),
        widgets_view,
        view.vertical_seperator(),
        add_view)
