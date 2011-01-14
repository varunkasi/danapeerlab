#!/usr/bin/env python
import threading
import logging
import sys
import types
import inspect
from attrdict import AttrDict
import numpy as np

class GuiException(Exception):
  pass
  
class ScriptServices(object):
  """This is the API provided to scripts in the editor.
  """
  def __init__(self):
    self._cache = {}
    self._text = []

  def print_text(self, text):
    self._text.append(text)
  
  def cache(self, key, new_func):
    data = AttrDict()
    new_func(data)
    return data

    key = self.make_hashable(key)
    if not key in self._cache:
      data = AttrDict()
      new_func(data)
      self._cache[key] = data
    return self._cache[key]
  
  def make_hashable(self, x):
    if isinstance(x, (list, tuple)):
      return tuple(map(self.make_hashable, x))
    elif isinstance(x, dict):
      return self.make_hashable(sorted(x.items()))
    return x

services = ScriptServices()