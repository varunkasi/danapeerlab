#!/usr/bin/env python
import logging
from odict import OrderedDict
from widget import Widget
from view import View
from view import stack_lines
from leftpanel import LeftPanel
from select import Select
from input import Input
from applybutton import ApplyButton
from miniexpander import MiniExpander


class WidgetWithControlPanel(Widget):
  """A widget that has control panel. You can inherit from this class
  and implement a main_view and a control_panel methods."""
  def __init__(self, id, parent):
    Widget.__init__(self, id, parent)
    self._section_begin = {}
    self._control_panel_views = None

  def _begin_section(self, section_name):
    """ Starts a section, all following add_* calls will be added to the section. 
    To end a section, call _end_section."""
    if section_name in self._section_begin:
      raise Exception('begin section %s called twice' % section_name)
    self._section_begin[section_name] = len(self._control_panel_views)

  def _end_section(self, section_name, initially_expanded=True):
    """ Ends a section, must be called after _begin_section.
    """
    if not section_name in self._section_begin:
      raise Exception('begin section %s must called before ending section' % section_name)
    section_begin = self._section_begin[section_name]
    widgets_in_section = self._control_panel_views[section_begin:]
    self._control_panel_views = self._control_panel_views[:section_begin]
    widget = self._add_widget_if_needed(section_name, MiniExpander, shown=initially_expanded)
    view = widget.view(View(self, section_name), stack_lines(*widgets_in_section))
    self._control_panel_views.append(view)
    del self._section_begin[section_name]
  
  def _add_select(self, widget_name, title, cache_key=None, default=[], options=[], is_multiple=True, comment=''):
    """Adds a select widget to the control panel view.
    Must be called from the control_panel function
    """
    widget = self._add_widget_if_needed(widget_name, Select)
    if cache_key:
      key = (str(type(self)), widget_name, cache_key)
      widget.guess_or_remember(key, default)
    elif not widget.values.choices:
      widget.values.choices = default
    view = widget.view(title, self.widgets.control_panel_apply, options, is_multiple, comment=comment)
    self._control_panel_views.append(view)

  def _add_input(self, widget_name, title, cache_key=None, default='', predefined_values=[], id=None, numeric_validation=True, comment='', non_empty_validation=True, size=20):
    """Adds an input widget to the control panel view.
    Must be called from the control_panel function
    """
    widget = self._add_widget_if_needed(widget_name, Input)
    if cache_key:
      key = (str(type(self)), widget_name, cache_key)
      widget.guess_or_remember(key, default)
    elif widget.values.value == None:
      widget.values.value = default_value
    view = widget.view(title, self.widgets.control_panel_apply, id=id, predefined_values=predefined_values, numeric_validation=numeric_validation, comment=comment, non_empty_validation=non_empty_validation, size=size)
    self._control_panel_views.append(view)
     
  def pre_run(self):
    """Checks if the module is ready to run."""
    if not self.widgets.control_panel_apply.clicked_once:
      raise Exception('Click on \'apply\' to run this module')
    
  def view(self, *args, **kargs):
    self._add_widget_if_needed('layout', LeftPanel)
    self._add_widget_if_needed('control_panel_apply', ApplyButton)
    
    if not any(list(args) + list(kargs.values())):
      return View(self, 'No tables to display')
    self._control_panel_views = []  
    extra_control_panel_view = self.control_panel(*args, **kargs)
    if extra_control_panel_view:
      self._control_panel_views.append(extra_control_panel_view)
    self._control_panel_views.append(self.widgets.control_panel_apply.view())
    if not self.widgets.control_panel_apply.clicked_once:
      main_view = View(self, 'Click on \'apply\' to run this module')
    else:
      try:
        main_view = self.main_view(*args, **kargs)
        if not main_view:
          main_view = View(self, '')
      except Exception as e:
        logging.exception('Exception in main_view')
        main_view = View(self, str(e))
    return self.widgets.layout.view(main_view, stack_lines(*self._control_panel_views))