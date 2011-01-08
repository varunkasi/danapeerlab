#!/usr/bin/env python
from widget import Widget
from view import View
from view import render
from biology.dataindex import DataIndex
from django.utils.html import linebreaks
import StringIO, Image
import Figure

class Kde2d(Widget):
  def __init__(self):
    Widget.__init__(self)
    self.widgets.figure = Figure()

  def view(self, datatable, markers, range, norm_axis=None, norm_axis_thresh = None):
    def cached(data):
      from mlabwrap import mlab
      a, w = datatable.get_cols(markers[0], markers[1])
      if range:
        min_a = range[0]
        max_a = range[2]
        min_w = range[1]
        max_w = range[3]
      else:
        min_w = min(w)
        max_w = max(w)
        min_a = min(a)
        max_a = max(a)
      points = datatable.get_points(markers[0], markers[1])
      bandwidth,data.density, data.X, data.Y = mlab.kde2d(
          points, 256,        
          [[min_a, min_w]],
          [[max_a, max_w]],
          nout=4)    
    data = services.cache((datatable, markers, range), cached, True, False)  
    display_data = data.density
    if norm_axis == 'x':
      max_dens_x = np.array([np.max(data.density, axis=1)]).T
      if norm_axis_thresh:
        max_dens_x[max_dens_x < norm_axis_thresh] = np.inf
      data.density_x = data.density / max_dens_x
      display_data = data.density_x
    elif norm_axis == 'y':
      max_dens_y = np.array([np.max(data.density, axis=0)])
      if norm_axis_thresh:
        max_dens_y[max_dens_y < norm_axis_thresh] = np.inf
      data.density_y = data.density / max_dens_y
      display_data = data.density_y
  
  ax.set_xlabel(str(markers[0]) + '   ')
  ax.set_ylabel(str(markers[1]) + '   ')
  display_image(
    display_data,
    origin='lower', 
    extent=[
        data.X[0,0],
        data.X[0,-1],
        data.Y[0,0],
        data.Y[-1,0]],
        interpolation=None, *args, **kargs)
  ax.figure.canvas.draw()


  