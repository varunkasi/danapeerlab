#!/usr/bin/env python
import logging
import threading

from event import Event
from gapbuffer import GapBuffer


class ScriptMark(object):
  def __init__(self, position, script, gravity, name):
    if not gravity in ('left', 'right'):
      raise Exception('Gravity must either be \'left\' or \'right\'')
    self.position = position
    self.script = script
    self.gravity = gravity
    self.name = name
    self.script.text_inserted += self.on_script_text_inserted
    self.script.range_deleted += self.on_script_range_deleted

  def on_script_text_inserted(self, position, text, sender):
    if position < self.position or (
        position == self.position and self.gravity == 'right'):
      self.position += len(text)
      #if self.name == 'mark 2':
        #logging.debug('1moved marker %s to %d' % (self.name, self.position))


  def on_script_range_deleted(self, start, end, sender):
    #logging.debug('on_script_range_deleted %d %d' % (start, end))
    if end <= self.position:
      self.position -= (end-start)
      #if self.name == 'mark 2':
        #logging.debug('2moved marker %s to %d' % (self.name, self.position))
    elif self.position < end and self.position > start:
      self.position = start
      #if self.name == 'mark 2':
        #logging.debug('3moved marker %s to %d' % (self.name, self.position))

  def invalidate(self):
    self.script.text_inserted -= self.on_script_text_inserted
    self.script.range_deleted -= self.on_script_range_deleted    

class Script(object):
  """Represents a script in the editor"""
  def __init__(self, script_str=''):
    self.code = GapBuffer(script_str)
    self.text_inserted = Event()
    self.range_deleted = Event()
    self.lock = threading.RLock()
    self.marks = {}
    self.name_counter = 0

  def add_mark(self, position, gravity='left', name=None):
    """Adds a mark in the script which maintains a relative position
    when text is added/deleted.
    
    Thread safe.
    """
    with self.lock:
      if not name:
        name = 'mark %d' % self.name_counter
        self.name_counter += 1
      if name in self.marks:
        raise Excpetion('name %s is already used' % name)
      self.marks[name] = ScriptMark(position, self, gravity, name)
      return name

  def remove_mark(self, name):
    """Removes the given mark"""
    with self.lock:
      if not name in self.marks:
        raise Excpetion('mark %s is not found' % name)
      self.marks[name].invalidate()
      del self.marks[name]

  def clear_marks(self):
    """Clears all marks"""
    with self.lock:
      names_to_delete = self.marks.keys()
      for name in names_to_delete:
        self.remove_mark(name)

  def mark_position(self, name):
    """Gets the position for the given mark
    
    Thread safe.
    """
    with self.lock:
      if not name in self.marks:
        raise Excpetion('mark %s is not found' % name)
      return self.marks[name].position

  def insert_text(self, position, text, sender=None):
    """Inserts text to the script and calls the text_inserted event.
    
    Thread safe.
    """
    #logging.debug('inserted text to script: %s', text)   
    with self.lock:
      text = str(text)
      if type(position) != int:
        position = self.mark_position(position)
      self.code.insert(position, text)
      self.text_inserted(position, text, sender)
  
  def delete_range(self, start=None, end=None, sender=None):
    """Delete text from the script and calls the text_deleted event.
    
    Thread safe.
    """
    with self.lock:
      #logging.debug('deleting from %s to %s' % (start, end))
      start, end = self._fix_start_end(start, end)
      #logging.debug('deleted: %s' % self.code[start:end])
      del self.code[start:end]
      self.range_deleted(start, end, sender)
    
  def clear(self, sender=None):
    """Clears the script.
    
    Thread safe.
    """
    with self.lock:
      self.delete_range(0, len(self.code), sender)
      self.code.slim()

  def _fix_start_end(self, start, end):
    with self.lock:
      if not start:
        start = 0
      if not end:
        end = len(self.code)
      if type(start) != int:
        start = self.mark_position(start)
      if type(end) != int:
        end = self.mark_position(end)
      return start, end

  def get_code_as_str(self, start=None, end=None):
    """Gets the code as a string.
    
    Thread safe.
    """
    with self.lock:
      start, end = self._fix_start_end(start, end)
      return str(self.code[start:end])
