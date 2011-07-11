#!/usr/bin/env python
import threading
import time
import hashlib
import os
import logging
import settings
import cPickle as pickle
import sys
import types
import inspect
from attrdict import AttrDict
import numpy as np

class GuiException(Exception):
  pass
  

class ScriptServices(object):
  """A legacy class for old functions. Note that cache does nothing. 
  """
  def __init__(self):
    self.cache_dir = os.path.join(settings.FREECELL_DIR, 'cache')
    self._cache = {}
    self._text = []

  def print_text(self, text):
    self._text.append(text)
  
  def cache(self, key, new_func):
    data = AttrDict()
    new_func(data)
    return data


services = ScriptServices()
