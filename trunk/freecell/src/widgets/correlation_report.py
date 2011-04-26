#!/usr/bin/env python
import itertools
import logging
import gc
from widget import Widget
from multitimer import MultiTimer
from view import View
from view import render
from biology.dataindex import DataIndex
from table import Table
from figure import Figure
import axes
from axes import kde2d
from axes import new_axes
from axes import new_figure
from biology.datatable import fake_table
import matplotlib.cm as cm
  
class CorrelationReport(Widget):
  def __init__(self):
    Widget.__init__(self)
    self.widgets.kde2d_fig = Figure()

  def view(self):
    #cluster = 'B-cells CD20+'
    cluster = 'Progenitor cells CD38+'
    stim='PVO4' #'All'
    index = DataIndex.load(r'c:\cytof54_clustered\cytof54.index')
    t = index.load_table(cluster_name=cluster, stim=stim)
    dims = t.get_markers('signal')
    width =  800
    height = 800
    left_space = 80./width
    top_space = 80./height
    sub_width  = (1. - left_space) / len(dims)
    sub_height =(1. - top_space) / len(dims)
    fig = new_figure(width, height)
    for i in xrange(len(dims)):
        y_pos = 1 - sub_height - top_space - i * sub_height
        x_pos = 0
        ax = fig.add_axes((x_pos,y_pos, left_space, sub_height))
        ax.text(
            0.5, 0.5,dims[i],
            fontsize='xx-small',
            rotation='horizontal',
            horizontalalignment='center',           
            verticalalignment='center',
            transform = ax.transAxes)
        axes.remove_ticks(ax)
    for j in xrange(len(dims)):
        y_pos = 1 - top_space
        x_pos = left_space + j * sub_width
        ax = fig.add_axes((x_pos,y_pos, sub_width, top_space))
        ax.text(
            0.5, 0.5,dims[j],
            fontsize='xx-small',
            rotation='vertical',
            horizontalalignment='center',           
            verticalalignment='center',
            transform = ax.transAxes)
        axes.remove_ticks(ax)
    timer = MultiTimer(len(dims)**2 - len(dims))        
    for i in xrange(len(dims)):
      for j in xrange(len(dims)):
        if i==j:
          continue
        dim1 = dims[i]
        dim2 = dims[j]
        table_positive = t.remove_bad_cells(dim1, dim2)
        y_pos = 1 - sub_height - top_space - i * sub_height
        x_pos = left_space + j * sub_width
        ax = fig.add_axes((x_pos,y_pos, sub_width, sub_height), axisbg=cm.jet(0))
        #print ''
        #print (x_pos,y_pos, sub_width, sub_height)
        axes.kde2d(
            ax, table_positive, (dim1, dim2), None, 'y', 0.001)
        axes.remove_ticks(ax)
        timer.complete_task('%s, %s' % (dim1,dim2))
    return self.widgets.kde2d_fig.view(fig)

    
# def view(self):
#   index = DataIndex.load(r'c:\cytof54_clustered\cytof54.index')
#   t = index.load_table(cluster_name='CD8+ T-cells')
#   dims = t.get_markers('surface')
#   lines = []
#   timer = MultiTimer(len(dims)**2)
#   for dim1 in dims:
#     line = [dim1]
#     for dim2 in dims:
#       table_positive = t.remove_bad_cells(dim1, dim2)
#       fig = new_figure(50,50)
#       ax = fig.add_axes((0,0,1,1))
#       axes.kde2d(
#           ax, table_positive, (dim1, dim2), None, 'y', 0.001)
#       axes.remove_ticks(ax)
#       line.append(self.widgets.kde2d_fig.view(fig))
#       timer.complete_task('%s, %s' % (dim1,dim2))
#     lines.append(line)
#   return self.widgets.table.view(['']+dims, lines)
