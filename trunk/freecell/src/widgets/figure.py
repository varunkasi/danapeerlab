#!/usr/bin/env python
import os
from widget import Widget
from view import View
from view import render
from biology.dataindex import DataIndex
from django.utils.html import linebreaks
import settings
import StringIO
import matplotlib
matplotlib.use('Agg')
#import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg

class Figure(Widget):
  def __init__(self):
    Widget.__init__(self)
    
  def view(self, fig):
    id = self._get_unique_id()
    image_filename = '%s.png' % id
    full_filename = os.path.join(settings.FREECELL_DIR, 'static', 'images', image_filename)
    #imgdata = StringIO.StringIO()
    
    canvas = FigureCanvasAgg(fig)
    canvas.print_figure(full_filename, dpi=100)
    #with open(full_filename, 'w') as imgdata:
      #fig.savefig(imgdata, format='png')
      

    html = '<img src="/static/images/%s" />' % image_filename
    return View(
      self,
      html,
      [],
      [])
      #{image_filename : imgdata})