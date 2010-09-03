#!/usr/bin/env python
import threading
import logging
import sys
import gtk
import types
import gobject
import inspect
from attrdict import AttrDict
from spacemanager import WidgetLocation
import numpy as np
#from autoreloader import AutoReloader

class GuiException(Exception):
  pass
  
class Space(object):
  def __init__(self, name='data', row=0, col=0, end_row=None, end_col=None):
    self.ax = None
    self.ca = None
    if not end_row:
      end_row = row + 1
    if not end_col:
      end_col = col + 1
    self.name = name
    self.col = col
    self.row = row
    self.end_col = end_col
    self.end_row = end_row
    self.prev_location = None
    if not services.space_exists(name):
      if row == 0:
        row = 3
      if col == 0:
        col = 3
      services.add_space(name, True, row, col)

  def get_location(self):
    return WidgetLocation(
        self.name, self.col, self.row, self.end_col, self.end_row)

  def add_ax(self):
    self.ax = services.get_ax(self.get_location())
    return self

  def __enter__(self):
    #if self.ax:
    #  self.ax.clear()
    global services
    self.prev_location = services.get_widget_location()
    services.set_widget_location(WidgetLocation(
        self.name, self.col, self.row, self.end_col, self.end_row))
    if self.ax:
      return self.ax
    else:
      return self

  def __exit__(self, type, value, traceback):
    services.redraw_ax_if_used(self.get_location())
    services.set_widget_location(self.prev_location)
    

class ScriptServices(object):
  """This is the API provided to scripts in the editor.
  Functions here can run from the script thread, or from the GUI thread.
  """
  def init(self, space_manager, changer_manager, script_server, top_widget, control_box_manager):
    """Inits the class, should only be called by main.py"""
    self.control_box_manager = control_box_manager
    self._space_manager = space_manager
    self._changer_manager = changer_manager
    self._script_server = script_server
    self._script_request_counter = 0;
    self._script_request_sender = None
    self.top_widget = top_widget
    # Wrapped functions from space manager, these will run in the GUI thread:
    self.add_space = self._sync_wrapper(self._space_manager.add_space)
    self.remove_space = self._sync_wrapper(self._space_manager.remove_space)
    self.add_widget = self._sync_wrapper(self._space_manager.add_widget)
    self.remove_widget = self._sync_wrapper(self._space_manager.remove_widget)
    
    """Current widget location is usually defined by the client. Modules
    refer to the current location when creating new widget. A list is used 
    so that in the future we can also define 'secondary' locations etc"""
    self.current_widget_locations = [WidgetLocation('data',0,0,1,1)]
    
    self._cache = {}

  def _set_script_sender(self, sender):
    self._script_request_sender = sender

  def get_script_sender(self):
    return self._script_request_sender

  def replay_script(self, sender=None):
    """Adds a request to run the script again when the script currently running 
    is finished"""
    self._script_server.add_to_queue(
        'script %d' % self._script_request_counter,
        sender)
    self._script_request_counter +=1
    
  def space_exists(self, name):
    return self._space_manager.space_exists(name)
    
  def set_current_changer(self, changer_index, func):
    """Automatically called by the annonated script to set the relevant 
    changer for each function. See ParameterChangerManager.annonate_script."""
    return self._changer_manager.set_current_changer(changer_index, func)
    
  def get_current_changer(self):
    """Gets a ParameterChanger that can change the parameters of the 
    current function. Functions using this command must register their name in 
    parameterchanger.PARAMETER_CHANGER_FUNCTIONS"""
    return self._changer_manager.get_current_changer()

  def set_widget_location(self, widget_location):
    self.current_widget_locations[0] = widget_location

  def get_widget_location(self):
    return self.current_widget_locations[0]

  def add_widget_in_current_location(self, widget, data=None):
    self.add_widget(widget, self.current_widget_locations[0], data)

  def get_widget_in_current_location(self, data_test=None):
    return self.get_widget(self.current_widget_locations[0], data_test)
    
  def add_widget_in_control_box(self, title, widget):
    self.control_box_manager.add_widget(title, widget)
    
  def on_canvas_draw(self, event):
    print 'hi draw event'
    import matplotlib.transforms as mtransforms
    def get_bbox_for_labels(labels):
      bboxes = []
      for label in labels:
        bbox = label.get_window_extent()
        # the figure transform goes from relative coords->pixels and we
        # want the inverse of that
        bboxi = bbox.inverse_transformed(fig.transFigure)
        bboxes.append(bboxi)
      # this is the bbox that bounds all the bboxes, again in relative
      # figure coords
      bbox = mtransforms.Bbox.union(bboxes)
      return bbox

    fig = event.canvas.figure
    # assume only one axes.
    ax = fig.get_axes()[0]
       
    ylabels = ax.yaxis.get_ticklabels()   
    bbox = get_bbox_for_labels(ylabels)   
    for l in ylabels:
      #new_size = l.get_size() * (0.1 / bbox.width)
      #new_size = min(new_size, 8)     
      l.set_size(8)
    
    xlabels = ax.xaxis.get_ticklabels()   
    bbox = get_bbox_for_labels(xlabels)       
    for l in xlabels:
      #new_size = l.get_size() * (0.1 / bbox.height)
      #new_size = min(new_size, 8)
      l.set_size(8)
      
    box_y = get_bbox_for_labels(ylabels)   
    box_x = get_bbox_for_labels(xlabels)
    left = 0.1
    right = 0.9
    top = 0.9
    bottom = 0.1
    
    if ax.yaxis.get_ticks_position() == 'right':
      right = min(right, 1 - box_y.width - 0.03)
    else:
      left = max(left, box_y.width + 0.03)
    #if ax.xaxis.get_ticks_position() == 'top':
    #  left = max(left, box_y.width + 0.03)
    #if ax.xaxis.get_ticks_position() == 'bottom':
    #  right = min(right, 1 - box_y.width - 0.03)
      
    fig.subplots_adjust(top=0.9, left=left, bottom=0.1, right=right)
    fig.canvas.draw()
    
    return False

    
    
  def get_ax(self, custom_location=None):
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas
    if custom_location:
      widget = self.get_widget(custom_location)
    else:
      widget = self.get_widget_in_current_location(self)
    if not widget or not widget.get_data('ax'):
      logging.debug('creating ax')
      widget = gtk.Frame()
      fig = Figure(dpi=100)
      ax = fig.add_subplot(111)
      ax.set_aspect('auto')
      canvas = FigureCanvas(fig)
      canvas.mpl_connect('draw_event', self.on_canvas_draw)
      canvas.show()
      widget.add(canvas)
      if custom_location:
        services.add_widget(widget, custom_location)
      else:
        services.add_widget(widget, self.current_widget_locations[0])
      widget.set_data('ax', ax)
    return widget.get_data('ax')
  
  def redraw_ax_if_used(self, custom_location=None):
    if custom_location:
      widget = self.get_widget(custom_location)
    else:
      widget = self.get_widget_in_current_location(self)
    if widget and widget.get_data('ax'):
      print 'redraw!@#!@#!@'
      widget.get_data('ax').figure.canvas.draw()
      #widget.queue_draw()

    

  def get_widget(self, location, deprecated=None):
    return self._space_manager.get_widget(location)

  def get_top_widget(self):
      return self.top_widget

  def cache(self, key, new_func, cache_location=True, use_widget=True):
    if cache_location:
      key = (key, self.current_widget_locations[0])
    key = (key, inspect.stack()[1][3])
    key = self.make_hashable(key)
    #logging.info(key)
    if not key in self._cache:
      #if run_in_gui_thread:
      #  new_func = create_sync_wrapper(new_func, 3)
      data = AttrDict()
      new_func(data)      
      self._cache[key] = data
      if use_widget:
        self.add_widget_in_current_location(data.widget)
    return self._cache[key]
  
  def make_hashable(self, x):
    if isinstance(x, (list, tuple)):
      return tuple(map(self.make_hashable, x))
    elif isinstance(x, dict):
      return self.make_hashable(sorted(x.items()))
    return x
    
        

  def _sync_wrapper(self, func):
    """Gets a function, and returns a new function which:  
    1. Calls the given function in the GUI thread. 
    2. If we are not in the GUI thread: 
       Waits for the call (in the GUI thread) to be over, or throws timeout
        exception.
    3. Returns what the function in the GUI thread returned (or throws
    the same exception)

    The function is binded to the instance.

    """
    def new_func(self, *args, **kargs):
      # if we are in the GUI thread, just call the function
      if threading.current_thread().name != 'SCRIPT_THREAD':
        return func(*args, **kargs)
      TIMEOUT = 3
      thread_event = threading.Event()
      exception = [None]
      ret_val = [None]
      def func_gui(thread_event, exception, ret_val, *args, **kargs):
        try:
          ret_val[0] = func(*args, **kargs)
        except:
          logging.exception('GUI Exception')
          exception[0] = sys.exc_info()[:2] #type, value
        thread_event.set()
      gobject.idle_add(
          func_gui, thread_event, exception, ret_val, *args, **kargs)
      thread_event.wait(TIMEOUT)
      if not thread_event.is_set():
        raise Exception(
            'Timeout (%d seconds) for function %s' % (TIMEOUT, func))
      if exception[0]:
        raise GuiException('Gui error, see log for details')
      return ret_val[0]
    return types.MethodType(new_func, self, ScriptServices)
    #prev line bind the method, see 
    #http://stackoverflow.com/questions/1015307/python-bind-an-unbound-method

def create_sync_wrapper(func, timeout=None):
  """Gets a function, and returns a new function which:  
  1. Calls the given function in the GUI thread. 
  2. If we are not in the GUI thread: 
     Waits for the call (in the GUI thread) to be over, or throws timeout
      exception.
  3. Returns what the function in the GUI thread returned (or throws
  the same exception)

  """
  def new_func(*args, **kargs):
    # if we are in the GUI thread, just call the function
    if threading.current_thread().name != 'SCRIPT_THREAD':
      return func(*args, **kargs)
    thread_event = threading.Event()
    exception = [None]
    ret_val = [None]
    def func_gui(thread_event, exception, ret_val, *args, **kargs):
      try:
        ret_val[0] = func(*args, **kargs)
      except:
        logging.exception('GUI Exception')
        exception[0] = sys.exc_info()[:2] #type, value
      thread_event.set()
    gobject.idle_add(
        func_gui, thread_event, exception, ret_val, *args, **kargs)
    thread_event.wait(timeout)
    if not thread_event.is_set():
      raise Exception(
          'Timeout (%d seconds) for function %s' % (timeout, func))
    if exception[0]:
      raise GuiException('Gui error, see log for details')
    return ret_val[0]
  return new_func

# global services
services = ScriptServices()
