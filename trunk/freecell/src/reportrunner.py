#!/usr/bin/env python

import logging
import depends
import time
import sys
import Queue
import threading
from threading import Thread
from report import REPORTS

class ReportRequest(object):
  """A request to run a report."""
  def __init__(self, name, report_id):
    self.name = name
    self.report_id = report_id   

class ReportRunner(object):
  """Maintains a queue of reports, and runs them in order on a seperate thread.
  """
  def __init__(self):
    self.queue = Queue.Queue()
    self.thread = None
    self.lock = threading.RLock()
    self.exit_object = object()
    self.waiting_report_id_to_request = {}
    self.report_id_to_result = {}
    self.working_lock = threading.RLock()
    
    if sys.platform == "win32":
      # On Windows, the best timer is time.clock()
      self.timer = time.clock
    else:
      # On most other platforms the best timer is time.time()
      self.timer = time.time

  def start(self):
    if self.thread and self.thread.is_alive():
      raise Exception("Report runner is already active.")
    self.thread = Thread(None, self.server_loop, 'REPORT_RUNNER_THREAD')
    self.thread.start()

  def end(self, timeout=5):
    """Ends the script server. Returns when the server is down or after timeout 
    seconds had passed. If the server had ended successfuly True is returned.""" 
    if not self.thread or not self.thread.is_alive():
      raise Exception("Server is already down.")
    self.queue.put(self.exit_object)
    self.thread.join(timeout)
    return not self.thread.is_alive()

  def add_to_queue(self, request_name, report_id):
    with self.lock:
      if report_id in self.waiting_report_id_to_request:
        req = self.waiting_report_id_to_request[report_id]
        raise Exception('Report %s is already in queue (%s)' % (req.report_id, req.name))
      req = ReportRequest(request_name, report_id)
      self.waiting_report_id_to_request[report_id] = req
    self.queue.put(req)
    logging.info('report %s was added to queue', request_name)

  def server_loop(self):
    logging.info('Report runner is up.')
    from depends import set_matlab_path
    set_matlab_path()
    while True:
      req = self.queue.get()
      with self.lock:
        if req == self.exit_object:
          self.queue.task_done()
          return
      with self.working_lock:
        r = REPORTS.load(req.report_id)
        logging.info('******RUNNING REPORT %s %s******' % (r.name, r.version))
        try:
          r.widget.run_on_load()
          start = time.clock()
          self.report_id_to_result[req.report_id] = (r, r.widget.view())
          view_time = time.clock() - start
          logging.info('Report runtime: %.3f seconds' % (view_time))
        except Exception as e:
          logging.exception('Exception while running a report.')
          self.report_id_to_result[req.report_id] = (r, e)
        # Save the report in case the last run modified its state.
        REPORTS.save(r)
      with self.lock:
        del self.waiting_report_id_to_request[req.report_id]
      self.queue.task_done()
      