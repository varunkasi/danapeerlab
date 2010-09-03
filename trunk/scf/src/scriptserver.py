#!/usr/bin/env python

import logging
import time
import sys
import Queue
import ctypes
import inspect
import controls
import gobject
from threading import Thread
from scriptservices import services
from scriptservices import GuiException
from compiler import compile_script
from event import Event

class ScriptRequest(object):
  """Used by the ScriptServer to represent a request to run a script."""
  def __init__(self, name, script, sender):
    self.name = name
    self.script = script
    self.sender = sender

class ScriptAbortedException(Exception):
  """An exception we use to abort a running script in the terminate_server
  function"""
  pass

class ScriptServer(object):
  """Maintains a queue of scripts, and runs them in order on a seperate thread.
  """
  def __init__(self, changer_manager):
    self.changer_manager = changer_manager
    self.script_queue = Queue.Queue(1)
    self.thread = None
    #self.start_server()
    # Note that the following events run in the script server's thread:
    # TODO(daniv): consider to add message to the GUI loop in here and no in the 
    # handler
    self.script_started = Event()
    self.script_ended = Event()
    self.exit_object = object()
    
    if sys.platform == "win32":
      # On Windows, the best timer is time.clock()
      self.timer = time.clock
    else:
      # On most other platforms the best timer is time.time()
      self.timer = time.time

  def start_server(self):
    if self.thread and self.thread.is_alive():
      raise Exception("Server is already active.")
    self.thread = Thread(None, self.server_loop, 'SCRIPT_THREAD')
    self.thread.start()

  def end_server(self, timeout):
    """Ends the script server. Returns when the server is down or after timeout 
    seconds had passed. If the server had ended successfuly True is returned.""" 
    if not self.thread or not self.thread.is_alive():
      raise Exception("Server is already down.")
    self.script_queue.put(self.exit_object)
    self.thread.join(timeout)
    return not self.thread.is_alive()

  def add_to_queue(self, script_name, sender=None):
    with self.changer_manager.script.lock:
      script = self.changer_manager.annonate_script()
      req = ScriptRequest(script_name, script, sender)
      gobject.idle_add(self.run_script, req)
      #self.script_queue.put(req)
      #logging.info('script %s was added to queue', script_name)

  def terminate_script(self):
    if not self.thread or not self.thread.is_alive():
      raise Excetion('tried to terminate a script when there is no server')
    _async_raise(self.thread.ident, ScriptAbortedException)
    if not self.thread.is_alive():
      logging.warn('Script termination killed the scrtip server, restarting.')
      self.start_server()

  def run_script(self, req):
    self.script_started(req.name)
    try:
      start = self.timer()
      compiled = compile_script(req.script)
      services._set_script_sender(req.sender)
      
      # Default headers:
      global services #global script services in scriptservices.py
      from scriptservices import Space
      from controls import display_text
      from controls import display_graph
      from controls import number_slider
      from controls import choose_file
      from controls import four_spaces
      import numpy as np
      import controls
      import biology.loaddatatable
      load_data_table = biology.loaddatatable.load_data_table
      
      
      from mlabwrap import mlab
      from controls import big_small_space
      import biology.markers
      from biology.markers import Markers
      from biology.markers import get_markers
      # End default headers
      
      exec compiled
      end = self.timer()
      logging.info('Done running script %s in %f', req.name, end - start)
    #except GuiException:
    #  logging.error('GUI Exception while running script %s', req.name)
    except:
      logging.exception('Exception while running script %s', req.name)
      #print req.script
    finally:
      #logging.info('Clearing script queue')
      self.script_ended(req.name)
        
  def server_loop(self):
    logging.info('script server is up.')
    while True:
      req = self.script_queue.get()
      self.run_script(req)
      self.script_queue.task_done()

def _async_raise(tid, exctype):
  """Raises an exception in the threads with id tid. 
  This is used to kill the thread's server_loops when it's running a script.
  The server loop should be restarted after that.
  
  See: http://stackoverflow.com/questions/323972/is-there-any-way-to-kill-a-thread-in-python
  TODO(daniv): consider restarting the application in a new process after
  this function is called / running scripts in a seperate process.
  """
  if not inspect.isclass(exctype):
    raise TypeError("Only types can be raised (not instances)")
  res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
    tid, ctypes.py_object(exctype))
  if res == 0:
    raise ValueError("invalid thread id")
  elif res != 1:
    # """if it returns a number greater than one, you're in trouble, 
    # and you should call it again with exc=NULL to revert the effect"""
    ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, 0)
    raise SystemError("PyThreadState_SetAsyncExc failed")
