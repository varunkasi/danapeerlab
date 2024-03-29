﻿import time 
import sys
import logging

class Timer(object):
  def __init__(self, name, wait_before_print_sec=3):
    self.wait_before_print_sec = wait_before_print_sec
    if sys.platform == "win32":
      # On Windows, the best timer is time.clock()
      self.timer = time.clock
    else:
      # On most other platforms the best timer is time.time()
      self.timer = time.time

    self.name = name

  def __enter__(self):
    self.start = self.timer()
  
  def __exit__(self, type, value, traceback):
    self.end = self.timer()
    elapsed = self.end - self.start
    if elapsed > self.wait_before_print_sec:
      logging.info('%s took %.2f seconds' % (self.name, elapsed))