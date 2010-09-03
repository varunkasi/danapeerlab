#!/usr/bin/env python

import logging

from event import Event
import gobject

class FileManager(object):
  """Manages the script files (new, open, save, save as etc)"""
  def __init__(self, script):
    self.current_file = None
    self.current_file_changed = Event()
    self.script = script
    self.script.text_inserted += self.on_script_text_inserted
    self.script.range_deleted += self.on_script_range_deleted
    self.need_save = False
    self.need_save_changed = Event()
    
  def _set_need_save(self, val):
    if self.need_save != val:
      self.need_save = val
      self.need_save_changed()

  def _set_current_file(self, val):
    self.current_file = val
    self.current_file_changed()

  def new(self):
    self.script.clear(self)
    self._set_current_file(None)
    self._set_need_save(False)
  
  def save(self):
    if not self.current_file:
      raise Exception('Must have a filename')
    with open(self.current_file, 'w') as dest:
      dest.write(self.script.code)
    self._set_need_save(False)
  
  def save_as(self, filename):
    self._set_current_file(filename)
    self.save()

  def open(self, filename):
    with open(filename, 'r') as src:
      lines = src.read()
    self._set_current_file(filename)
    self.script.clear(self)
    self.script.insert_text(0, lines, self)
    self._set_need_save(False)

  def on_script_text_inserted(self, position, text, sender):
    def on_script_text_inserted_gui(position, text):
      self._set_need_save(True)
    if sender != self:
      gobject.idle_add(on_script_text_inserted_gui, position, text)

  def on_script_range_deleted(self, start, end, sender):
    def on_script_range_deleted_gui(start, end):
      self._set_need_save(True)
    if sender != self:
      gobject.idle_add(on_script_range_deleted_gui, start, end)
