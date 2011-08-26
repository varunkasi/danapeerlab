#!/usr/bin/env python
import logging
from odict import OrderedDict

TAG_ORDER = {}
TAG_ORDER['patient'] = [str(i) for i in xrange(100)]
TAG_ORDER['marrow'] = ['marrow1', 'marrow2']

def tag_position(tag_name, tag_value):
  global TAG_ORDER
  if not tag_name in TAG_ORDER:
    return 0
  if not tag_value in TAG_ORDER[tag_name]:
    return len(TAG_ORDER[tag_name])
  return TAG_ORDER[tag_name].index(tag_value)

def tag_sort_key(tag_name):
  return lambda tag_value: (tag_position(tag_name, tag_value), tag_value)

def multiple_tag_sort_key(tag_names):
  return lambda tag_values: tuple([tag_sort_key(name)(tag_values[i]) for i,name in enumerate(tag_names)])