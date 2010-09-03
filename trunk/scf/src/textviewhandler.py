#!/usr/bin/env python
import logging
import gobject

class TextViewHandler(logging.Handler):
  """An handler to send log messages to a given gtk textview."""
  def __init__(self, textview, level=logging.NOTSET):
    self.textview = textview
    logging.Handler.__init__(self, level)

  def emit(self, record):
    def emit_gui(self, record):
      buffer = self.textview.get_buffer()
      buffer.insert(buffer.get_end_iter(), self.format(record))
      buffer.insert(buffer.get_end_iter(), '\n')
      textmark = buffer.create_mark(None, buffer.get_end_iter())
      self.textview.scroll_to_mark(textmark, 0.0)
      buffer.delete_mark(textmark)
    gobject.idle_add(emit_gui, self, record)
