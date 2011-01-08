#!/usr/bin/env python
from widget import Widget
from view import View
from view import render
from biology.dataindex import DataIndex
from django.utils.html import linebreaks
import StringIO, Image

class Figure(Widget):
  def __init__(self):
    Widget.__init__(self)
    
  def view(self, fig):
    imgdata = StringIO.StringIO()
    fig.savefig(imgdata, format='png')
    id = self._get_unique_id()
    image_filename = '%s.png' % id
    html = '<img src="/images/%s" />' % image_filename
    return View(
      self,
      html,
      [],
      [],
      {image_filename : imgdata})