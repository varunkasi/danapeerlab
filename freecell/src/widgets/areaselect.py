﻿#!/usr/bin/env python
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

class AreaSelect(Widget):
  def __init__(self, id, parent):
    Widget.__init__(self, id, parent)
    
  
  def view(self, figure_id, min_x_id, max_x_id, min_y_id, max_y_id, min_x, max_x, min_y, max_y):
    data = {
      'figure_id' : figure_id,
      'figure_id_func' : figure_id.replace('-', '_'),
      'min_x_id' : min_x_id,
      'max_x_id' : max_x_id,
      'min_y_id' : min_y_id,
      'max_y_id' : max_y_id,
      'min_x' :    min_x - 0.0001,
      'max_x' :    max_x - 0.0001,
      'min_y' :    min_y + 0.0001,
      'max_y' :    max_y + 0.0001}
    html = render('areaselect.html', data)
    return View(self, html, ['imageareaselect/imgareaselect-default.css'], ['jquery.imgareaselect.js'])