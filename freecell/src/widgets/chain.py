#!/usr/bin/env python
import os
import time
import axes
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
from expander import Expander
from miniexpander import MiniExpander
from histogram import HistogramPlot
import plots
from populationpicker import PopulationPicker

CHAINABLE_WIDGETS = [
    ('Population Picker', PopulationPicker),
    ('Histogram Plot', HistogramPlot),
    ('Scatter Plot', plots.ScatterPlot),
    ('Density Plot', plots.DensityPlot),
    ('Function Plot', plots.FunctionPlot),
    ('Scatter Gater', plots.ScatterGater),
    ('Density Gater', plots.DensityGater),
    ('Function Gater', plots.FunctionGater)]

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
    self._add_widget('input_panel', MiniExpander, False)
    self._add_widget('input_apply', ApplyButton)
    if self.widgets.sub_widget.has_method('get_inputs'):
      inputs = self.widgets.sub_widget.get_inputs()
    else:
      inputs = ['table']
    self.input_to_select = OrderedDict()
    for i, input in enumerate(inputs):
      w = self._add_widget('input_select_%d' % i, Select)
      self.input_to_select[input] = w
      w.values.choices = [self.get_default_input(input, previous_widgets)]
  
  def get_default_input(self, input, previous_widgets):   
    for i in xrange(len(previous_widgets)-1, -1, -1):
      if input in previous_widgets[i].get_outputs():
        return '%d,%s' % (i, input)
    return 'None'
  
  def get_outputs(self):  
    if self.widgets.sub_widget.has_method('get_outputs'):
      outputs = self.widgets.sub_widget.get_outputs()
    else:
      outputs = ['table']
    return outputs

  def get_idx_output(self, input):
    if self.input_to_select[input].values.choices[0] == 'None':
      return (None, None)
    else:
      idx = int(self.input_to_select[input].values.choices[0].split(',')[0])
      out = self.input_to_select[input].values.choices[0].split(',')[1]
      return (idx, out)
    
    
  def create_input_map(self, data):
    input_map = {}
    for input in self.input_to_select:
      idx, out = self.get_idx_output(input)
      if idx == None:
        input_map[input] = None
      else:
        input_map[input] = data[idx][out]   
    return input_map

      
      
  def run(self, data):
    if self.widgets.sub_widget.has_method('run'):
        return self.widgets.sub_widget.run(**self.create_input_map(data))
    
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
           k, self.widgets.input_apply, possible_inputs, multiple=False))
    input_content_views.append(self.widgets.input_apply.view())
    input_content = view.stack_lines(*input_content_views)    
    try:
      sub_widget_view = self.widgets.sub_widget.view(**self.create_input_map(data))
    except Exception as e:
      logging.exception('Exception in view')
      sub_widget_view = View(self, str(e))

    delete_view = self.widgets.delete_button.view('Delete')
    delete_view.main_html = '<div style="position:absolute; top:0; right:0;">%s</div>' % delete_view.main_html

    sub_view = view.stack_lines(
        delete_view,
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
    self._add_widget('apply', ApplyButton)
    self.widgets_in_chain = []
  
  def on_load(self):
    # add new modules
    if self.widgets.new_widget_select.values.choices:
      type_to_create, args, kargs = widget_name_to_type(self.widgets.new_widget_select.values.choices[0])
      self.widgets.new_widget_select.values.choices = []
      w = self._add_widget('chain_%d' % len(self.widgets_in_chain), WidgetInChain, type_to_create, self.widgets_in_chain, args, kargs)
      self.widgets_in_chain.append(w)
    # delete modules
    for i, w in enumerate(self.widgets_in_chain):
      if w.widgets.delete_button.clicked:
        for following_widget in self.widgets_in_chain[i+1:]:
          for input in following_widget.input_to_select.iterkeys():
            idx, out = following_widget.get_idx_output(input)
            if idx == i:
              following_widget.input_to_select[input].values.choices[0] = 'None'
        self.widgets_in_chain.remove(w)
        self._remove_widget(w)
        break
  
  def widget_in_chain_to_inputs(self, widget_in_chain, place_in_chain):
    ret = []
    for output in widget_in_chain.get_outputs():
      if output == 'table':
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
      view_start = time.clock()
      #logging.info('Getting view for Widget %d %s' % (i, widget.title(i, True)))
      views.append(widget.view(data, i, possible_inputs))
      view_time = time.clock() - view_start
      logging.info('Widget %d view: %.3f seconds' % (i+1, view_time))
      possible_inputs += self.widget_in_chain_to_inputs(widget, i)
      #logging.info('Running Widget %d %s' % (i, widget.title(i)))
      try:
        run_start = time.clock()
        widget_data = widget.run(data)
        data.append(widget_data)
        run_time = time.clock() - run_start
        logging.info('Widget %d run: %.3f seconds' % (i+1, run_time))
        if widget_data and 'view' in widget_data:
          views.append(widget_data['view'])
          del widget_data['view']
      except Exception as e:
        logging.exception('Exception in run')
        views.append('Exception when running %s: %s' % (widget.title(i), str(e)))
        break
    del data
    widgets_view = stack_lines(*views)
    add_view = stack(
        self.widgets.new_widget_select.view(
            'Add new module', self.widgets.apply, zip(*CHAINABLE_WIDGETS)[0], False),
        self.widgets.apply.view())
    return stack_lines(widgets_view, add_view)