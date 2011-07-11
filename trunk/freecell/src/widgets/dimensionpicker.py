#!/usr/bin/env python
from odict import OrderedDict
from widget import Widget
from view import View
from view import render
from view import stack_left
from view import stack_lines
from biology.dataindex import DataIndex
from widgets.expander import Expander
from widgets.select import Select
from widgets.applybutton import ApplyButton
import settings

class DimensionPicker(Widget):
  def __init__(self, id, parent):
    Widget.__init__(self, id, parent)
    self._add_widget('dimension_select', Select)  
    
  def on_load(self):
    self.dims = self.widgets.experiment_select.values.choices

  def view(self, apply_button, datatable):
    experiments = settings.EXPERIMENTS.keys()
    if not self.experiment:
      return stack_lines(
          self.widgets.experiment_select.view('Please Select an experiment', self.widgets.apply, experiments, False),
          self.widgets.apply.view())
    
    if not self.experiment in self.experiment_to_widgets:
      index = self._get_index()
      widgets = []
      if type(settings.EXPERIMENTS[self.experiment]) == tuple:
        editable_tags = settings.EXPERIMENTS[self.experiment][1]
      else:
        editable_tags = index.all_tags()
      for tag in editable_tags:
        new_widget = self._add_widget('%s_%s' % (self.experiment, tag), Select)
        new_widget.tag = tag
        new_widget.vals = index.all_values_for_tag(tag)        
        widgets.append(new_widget)
      self.experiment_to_widgets[self.experiment] = widgets
    
    views = [w.view(w.tag, self.widgets.apply, w.vals) for w in self.experiment_to_widgets[self.experiment]]
    stacked_views = stack_left(*views)
      
    expanded = stack_lines(
        self.widgets.experiment_select.view(
            'Experiment', self.widgets.apply, experiments, False),
        stacked_views,
        View(None, '<p style="clear: both"></p>'),
        self.widgets.apply.view())
    #return expanded
    return self.widgets.expander.view('',[self.summary], [expanded])