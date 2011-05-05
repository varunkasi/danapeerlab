#!/usr/bin/env python
import os
import axes
import logging
import odict
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
import plots
from populationpicker import PopulationPicker

CHAINABLE_WIDGETS = [
    ('Population Picker', PopulationPicker),
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
  def __init__(self, id, parent, sub_widget_type, args, kargs):
    Widget.__init__(self, id, parent)
    self._add_widget('expander', Expander)
    self._add_widget('sub_widget', sub_widget_type, *args, **kargs)
    self._add_widget('delete_button', ApplyButton)

  def run(self, data):
    if self.widgets.sub_widget.has_method('run'):
      return self.widgets.sub_widget.run(data)
    
  def title(self, place_in_chain):
    if self.widgets.sub_widget.has_method('title'):
      ret = self.widgets.sub_widget.title()
    else:
      ret = widget_type_to_name(type(self.widgets.sub_widget))
    return '%d. %s' % (place_in_chain + 1, ret)

  def view(self, data, place_in_chain):
    sub_view = self.widgets.sub_widget.view(data)  
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
    if self.widgets.new_widget_select.values.choices:
      type_to_create, args, kargs = widget_name_to_type(self.widgets.new_widget_select.values.choices[0])
      self.widgets.new_widget_select.values.choices = []
      w = self._add_widget('chain_%d' % len(self.widgets_in_chain), WidgetInChain, type_to_create, args, kargs)
      self.widgets_in_chain.append(w)
  
  def view(self):
    global CHAINABLE_WIDGETS
    # Run the chain:
    data = {}
    views = []
    for i, widget in enumerate(self.widgets_in_chain):
      logging.info('Getting view for Widget %d %s' % (i, widget.title(i)))
      try:
        views.append(widget.view(data, i))
      except Exception as e:
        logging.exception('Exception in view')
        views.append(str(e))
        break
      logging.info('Running Widget %d %s' % (i, widget.title(i)))
      try:
        widget.run(data)
        if 'view' in data:
          views.append(data['view'])
          del data['view']
      except Exception as e:
        logging.exception('Exception in run')
        views.append('Exception when running %s: %s' % (widget.title(i), str(e)))
        break
    
    widgets_view = stack_lines(*views)
    add_view = stack(
        self.widgets.new_widget_select.view(
            'Add new widget', self.widgets.apply, zip(*CHAINABLE_WIDGETS)[0], False),
        self.widgets.apply.view())
    return stack_lines(widgets_view, add_view)