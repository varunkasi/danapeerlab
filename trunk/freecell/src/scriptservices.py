#!/usr/bin/env python
import threading
import hashlib
import os
import logging
import settings
import pickle
import sys
import types
import inspect
from attrdict import AttrDict
import numpy as np

class GuiException(Exception):
  pass
  
class Cache(object):
  def __init__(self, cache_dir):
    self.cache_dir = cache_dir
  
  def put(self, key, val, sub_dir='', file_prefix=''):
    def ensure_dir(f):
      d = os.path.dirname(f)
      if not os.path.exists(d):
        os.makedirs(d)

    assert type(key) in (str, unicode)
    hashed_key = hashlib.sha1(key).hexdigest()
    full_path_key = os.path.join(self.cache_dir, sub_dir, '%s.%s.key' % (file_prefix, hashed_key))
    full_path_val = os.path.join(self.cache_dir, sub_dir, '%s.%s.val' % (file_prefix, hashed_key))
    ensure_dir(full_path_key)
    with open(full_path_key, 'w') as f:
      f.write(key)
    with open(full_path_val, 'w') as f:
      pickle.dump(val, f)
  
  def find_file(self, key):
    hashed_key = hashlib.sha1(key).hexdigest()
    for root, dirs, files in os.walk(self.cache_dir):
      for name in files:
        splitted = name.split('.')
        if len(splitted) < 2: 
          continue
        if splitted[-1] == 'val' and splitted[-2] == hashed_key:
          return os.path.join(root, name)
    return None

  def __contains__(self, key):
    return self.find_file(key) != None
  
  def get(self, key):
    assert type(key) in (str, unicode)
    full_path = self.find_file(key)
    if not full_path:
      raise Exception('file for key %s not found' % key)
    with open(full_path, 'r') as f:
      return pickle.load(f)
    
CACHE = Cache(os.path.join(settings.FREECELL_DIR, 'cache'))

def cache(dir='', prefix=''):
  def cache_wrap(func):
    def cached_func(*args, **kargs):
      key = function_call_to_unique_string(func, args, kargs)
      if not key in CACHE:
        val = func(*args, **kargs)
        
        CACHE.put(key, val, dir, prefix)
      return CACHE.get(key)
    return cached_func
  return cache_wrap

class ScriptServices(object):
  """This is the API provided to scripts in the editor.
  """
  def __init__(self):
    self.cache_dir = os.path.join(settings.FREECELL_DIR, 'cache')
    self._cache = {}
    self._text = []

  def print_text(self, text):
    self._text.append(text)
  
 
  # def perm_cache(self, func, args, kargs):
    # key = function_call_to_unique_string(func, args, kargs)
    # key = make_hashable(key)
    # filename = '%s.cache' % hash(key)
    # full_path = os.path.join(self.cache_dir, filename)
    # if not os.path.exists(full_path):
      # ret = func(*args, **kargs)
      # with open(full_path, 'w') as f:
        # pickle.dump(ret, f)
        # print 'dumped'
    # with open(full_path, 'r') as f:
      # loaded = pickle.load(f)
    # return loaded
    
  
  def cache(self, key, new_func):
    data = AttrDict()
    new_func(data)
    return data

    key = make_hashable(key)
    if not key in self._cache:
      data = AttrDict()
      new_func(data)
      self._cache[key] = data
    return self._cache[key]


def comma_join(str_list):
  if str_list and max([len(s) for s in str_list]) > 80:
    ret = ',\n'.join(str_list)
    return ret.replace('\n','\n    ')
  else:
    return ', '.join(str_list)
    
def make_unique_str(obj):
  from biology.datatable import DataTable
  from biology.dataindex import DataIndex
  from widget import Widget
  import numpy as np
  import types
  if type(obj) in (float, int, complex, str, unicode, bool, np.float64, np.int64):
    return repr(obj)
  # We don't want to differentiate between lists and tuples
  elif type(obj) in (list, tuple):
    return '[%s]' % comma_join(map(make_unique_str, obj))
  elif type(obj) in (dict, AttrDict):
    items = sorted(obj.items())
    if items:
      keys, vals = zip(*items)
    else:
      keys = []
      vals = []
    keys_str = map(make_unique_str, keys)
    vals_str = map(make_unique_str, vals)
    return '{%s}' % comma_join(['%s: %s' % (k,v) for k,v in zip(keys_str, vals_str)])
  elif type(obj) == DataTable:
    h = hashlib.sha1()
    h.update(obj.data.flatten())
    h.update(repr(obj.dims))
    #dims_str = make_unique_str(obj.dims)
    return '<DataTable %s >' % (h.hexdigest())
  elif isinstance(obj, Widget):
    widget_name = type(obj).__name__
    sub_widgets_str = make_unique_str(obj.widgets)
    vals_str = make_unique_str(obj.values)
    return '<Widget %s %s %s>' % (widget_name, sub_widgets_str, vals_str)
  elif type(obj) == types.FunctionType:
    return '<function %s %s>' % (obj.__name__, obj.__module__)
  elif type(obj) == types.MethodType:
    return '<method %s %s %s>' % (obj.__name__, obj.im_class.__name__, obj.__module__)
  elif type(obj) == DataIndex:
    return '<DataIndex %s>' % obj.path
  raise Exception('Unsupported type %s' % type(obj))

def function_call_to_unique_string(func, args, kargs):
   function_call_name = make_unique_str(func)
   args_str = make_unique_str(args)
   kargs_str = make_unique_str(kargs)
   return '%s\n%s\n%s' % (function_call_name, args_str, kargs_str)
   
services = ScriptServices()

# def make_hashable(x):
  # if isinstance(x, (list, tuple)):
    # return tuple(map(make_hashable, x))
  # elif isinstance(x, dict):
    # return make_hashable(sorted(x.items()))
  # return x


