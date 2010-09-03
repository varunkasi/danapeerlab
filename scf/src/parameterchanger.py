#!/usr/bin/env python
import string
import re
import logging
from collections import namedtuple

"""A list of function names which will be annonated. If you call 
ParameterChangerManager.get_current_changer from any of these function you will 
get a ParameterChanger that can change the parameters of the function in the 
current script"""
PARAMETER_CHANGER_FUNCTIONS = []

class ParameterChangerManager:
  def __init__(self, script):
    self.changers = []
    self.script = script
    self.changers_valid = False
    self.script.text_inserted += self.on_script_text_inserted
    self.script.range_deleted += self.on_script_range_deleted
    self.is_valid = True
    self.current_changer = -1
    self.name_to_annonate = []    
  
  def _create_changer_from_pos(self, pos):
    """This function creates a new parameter changer assuming pos is an 
    offset to a function name in a script. 
    
    The function also adds the needed marks for the changer in the script.
    """
    regions = []
    start_mark = None
    script_str = self.script.get_code_as_str()
    params_start = script_str.find('(', pos)
    if params_start == -1:
      raise Exception('Could not parse parameters')
    brackets_count = 1
    LOOKING_FOR_START = 0
    LOOKING_FOR_END = 1
    DONE = 2
    state = LOOKING_FOR_START
    in_string = None   
    params = []
    for pos in xrange(params_start + 1, len(script_str)):
      #logging.debug('current char: %s, current state:%d' % (script_str[pos], state))
      # Create markers.
      if state == LOOKING_FOR_START:
        if script_str[pos] == ')':
          start_mark = self.script.add_mark(pos, 'left')
          state = LOOKING_FOR_END
        elif not script_str[pos] in string.whitespace:
          start_mark = self.script.add_mark(pos, 'left')
          state = LOOKING_FOR_END
      if state == LOOKING_FOR_END and not in_string and brackets_count == 1:
        if script_str[pos] == ',' or script_str[pos] == ')':
          end_mark = self.script.add_mark(pos, 'right')
          regions.append(ParameterRegion(start_mark, end_mark))
          #logging.debug('********* APPENDED REGION*********')
          state = LOOKING_FOR_START
      # Handle strings. we want to know if we are in a ' or in a " type
      # of string.
      in_escape = pos > 1 and script_str[pos-1] == '\\' and script_str[pos-2] != '\\'
      if script_str[pos] == "'" or script_str[pos] == '"':
        if not in_string:
          in_string = script_str[pos]
          #logging.debug('We are in a %s string' % in_string)
        elif in_string == script_str[pos] and not in_escape:
          in_string = None
          #logging.debug('We are no longer in string')
      # Update bracket count.      
      if not in_string:
        if script_str[pos] == '(' or script_str[pos] == '[':
          brackets_count += 1
        if script_str[pos] == ')' or script_str[pos] == ']':
          brackets_count -= 1
      # Break when we get to the last bracket
      if brackets_count == 0:
        break
    return ParameterChanger(regions, self.script, self)

  
  def annonate_script(self):
    """Annonates the script with calls that set the current changed. 
    If changers are invalid, this also creates new changers.
    
    Annonation means turning a function call func(1,2,3) to 
    set_current_changer(changer_index, func)(1,2,3)
    
    changer_index is the index of the changer that sets the parameters of 
    the function func.    
    
    We only annonate functions which are in names_to_annonate.
    """

    def re_visitor(match):
      """Called by the regex engine for each function found while annonating"""
      if not self.is_valid:
        # we need a new ParameterChanger for this function.
        new_changer = self._create_changer_from_pos(match.start())
        self.changers.append(new_changer)
      # Note that if is_valid == True we assume no new functions were added
      # So we use the old changers in their original order.
      
      # We now save the function call code with annonation:
      debug_func = 'services.set_current_changer'
      annonated =  '%s(%d,%s)(' % (
          debug_func, self.function_counter, match.group()[:-1])
      self.function_counter += 1
      return annonated

    with self.script.lock:
      script_str = self.script.get_code_as_str()
      # This re captures all functions calls (I hope):
      # [\w.]+\(
      # To catch only function with the given names we need:
      # [\w.]*(?:name1|name2|name3)\(
      # TODO(daniv): ignore function calls inside strings
      # TODO(daniv): def with the same name will create an error...
      global PARAMETER_CHANGER_FUNCTIONS
      func_names = '|'.join(PARAMETER_CHANGER_FUNCTIONS)
      expression = r'[\w.]*(?:%s)\(' % func_names
      self.function_counter = 0
      if PARAMETER_CHANGER_FUNCTIONS:
        res = re.sub(
            expression,
            re_visitor,
            script_str)
      else:
        res = script_str
      self.is_valid = True
      return res
    
  def invalidate(self):
    with self.script.lock:
      self.is_valid = False
      for c in self.changers:
        c.is_valid = False
      self.script.clear_marks()
      self.changers = []
  
  def on_script_text_inserted(self, position, text, sender):
    # we don't invalidate changes created by this class, because these
    # changes are always parameter changes (so no new functions to annonate).
    with self.script.lock:
      if sender != self and self.is_valid:
        self.invalidate()
      
  def on_script_range_deleted(self, start, end, sender):
    with self.script.lock:
      if sender != self and self.is_valid:
        self.invalidate()
  
  def set_current_changer(self, changer_index, func_to_return):
    """Called by annonated functions in the script.
    
    This method is called from the script (only) after it had been annonated
    (see compiler.py). For each function whose name is in the annonated names
    list, the annotator turns the call func(a,b,c) to
    services.set_script_location(curset_location, func)(a,b,c)
    """
    self.current_changer = changer_index
    return func_to_return
    
  def get_current_changer(self):
    #TODO(daniv): check stack, only from script thread
    return self.changers[self.current_changer]
   
ParameterRegion = namedtuple('ParameterRegion',
    ['begin_mark_name','end_mark_name'])

class ParameterChanger:
  def __init__(self, regions, script, manager):
    self.regions = regions
    self.manager = manager
    self.script = script
    self.is_valid = True
    
  def get_parameters(self):
    with self.script.lock:
      if not self.is_valid:
        raise Exception('regions are not valid')
      return [
          self.script.get_code_as_str(r.begin_mark_name, r.end_mark_name)
          for r in self.regions]

  def set_parameters(self, parameters):
    #TODO(daniv): check that parameters are simple
    with self.script.lock:
      if not self.is_valid:
        raise Exception('regions are not valid')
      if len(parameters) != len(self.regions):
        raise Exception('parameter length mismatch')
      for i in xrange(len(parameters)):
        r = self.regions[i]
        self.script.delete_range(
            r.begin_mark_name, r.end_mark_name, self.manager)
        self.script.insert_text(
            r.begin_mark_name, parameters[i], self.manager)
  
  def set_parameter(self, index, val):
    with self.script.lock:
      if not self.is_valid:
        raise Exception('regions are not valid')
      if len(self.regions) <= index:
        raise Exception('parameter index')
      r = self.regions[index]
      self.script.delete_range(
          r.begin_mark_name, r.end_mark_name, self.manager)
      self.script.insert_text(
          r.begin_mark_name, val, self.manager)
    