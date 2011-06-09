#!/usr/bin/env python
import os
import axes
from widget import Widget
from view import View
from view import render
from biology.dataindex import DataIndex
from django.utils.html import linebreaks
import settings
import StringIO
import matplotlib
#matplotlib.use('Agg')
#import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg

from axes import DPI

def get_line_parameters(x1, y1, x2, y2):
  # y1 = ax1 + b
  # y2 = ax2 + b
  #print (x1, y1, x2, y2)
  a = (y1 - y2) / (x1 - x2) 
  b =  y1 - a * x1
  return a, b

class Figure(Widget):
  def __init__(self, id, parent):
    Widget.__init__(self, id, parent)

  def view(self, fig, id=None, small_ticks=True):
    if small_ticks:
      for ax in fig.get_axes():
        axes.small_ticks(ax)
    if not id:
      id = self._get_unique_id()
    image_filename = '%s.png' % id
    full_filename = os.path.join(settings.FREECELL_DIR, 'temp', image_filename)
    
    def on_draw(event):
      fig = event.canvas.figure
      ax = fig.axes[0]
      self.data_point1 = (0,0)
      self.data_point2 = (1,1)
      # The conversion between pixels and data is linear, so we try to get 
      # the line parameters. This has to be done in the draw event of the print.
      # (Otherwise the transData misbehaves)
      self.pixel_point1 = ax.transData.transform(self.data_point1)
      self.pixel_point2 = ax.transData.transform(self.data_point2)

      
    canvas = FigureCanvasAgg(fig)
    canvas.mpl_connect('draw_event', on_draw)
    canvas.print_figure(full_filename, dpi=DPI)
    
    data = {}
    data['a_pixel_x'], data['b_pixel_x'] = get_line_parameters(self.data_point1[0], self.pixel_point1[0], self.data_point2[0], self.pixel_point2[0])
    data['a_pixel_y'], data['b_pixel_y'] = get_line_parameters(self.data_point1[1], self.pixel_point1[1], self.data_point2[1], self.pixel_point2[1])
    data['a_data_x'], data['b_data_x'] = get_line_parameters(self.pixel_point1[0], self.data_point1[0], self.pixel_point2[0], self.data_point2[0])
    data['a_data_y'], data['b_data_y'] = get_line_parameters(self.pixel_point1[1], self.data_point1[1], self.pixel_point2[1], self.data_point2[1])
    data['pixel_width'] = fig.get_size_inches()[0] * DPI
    data['pixel_height'] = fig.get_size_inches()[1] * DPI
    data['id'] = id
    data['id_function'] = id.replace('-','_')
    html = render('figure.html', data)

    with open(full_filename, 'rb') as f:
      imgdata = f.read()     
     
    return View(
      self,
      html,
      [],
      [],
      {image_filename : imgdata})