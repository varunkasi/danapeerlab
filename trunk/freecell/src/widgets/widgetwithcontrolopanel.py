#!/usr/bin/env python
import logging
from odict import OrderedDict
from widget import Widget
from view import View
from leftpanel import LeftPanel

class WidgetWithControlPanel(Widget):
  """A widget that has control panel. You can inherit from this class
  and implement a main_view and a control_panel methods."""
  def __init__(self, id, parent):
    Widget.__init__(self, id, parent)
    self._add_widget('layout', LeftPanel)
      
  def view(self, *args, **kargs):
    if not any(list(args) + list(kargs.values())):
      return View(self, 'No tables to display')
    control_panel_view = self.control_panel(*args, **kargs)
    try:
      main_view = self.main_view(*args, **kargs)
      if not main_view:
        main_view = View(self, '')
    except Exception as e:
      logging.exception('Exception in main_view')
      main_view = View(self, str(e))     
    return self.widgets.layout.view(main_view, control_panel_view)     