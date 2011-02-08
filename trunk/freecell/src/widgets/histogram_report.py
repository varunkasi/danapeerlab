#!/usr/bin/env python
import numpy as np
import itertools
import logging
import gc
from widget import Widget
from multitimer import MultiTimer
import view
from view import View
from view import render
from biology.dataindex import DataIndex
from table import Table
from figure import Figure
import axes
from axes import kde2d
from axes import new_axes
from axes import new_figure
from expander import Expander
from table import Table
from biology.datatable import combine_tables
from biology.datatable import DimRange
  
class HistogramReport(Widget):
  def __init__(self):
    Widget.__init__(self)
    self.widgets.expander = Expander()
    self.widgets.surface_table = FitTable()
    self.widgets.signal_table = FitTable()
    #self.widgets.dim_table = DimTable()

  def view(self):
    cluster_name = 'CD8+ T-cells'
    index = DataIndex.load(r'c:\cytof54_clustered\cytof54.index')
    t = index.load_table(cluster_name=cluster_name)
    #t = t.gate(
    #    DimRange('167-CD38', -20, 6.2),
    #    DimRange('146-CD8', 4, 6))
    surface_table = self.widgets.surface_table.view(t, t.get_markers('surface'))
    signal_table = self.widgets.surface_table.view(t, t.get_markers('signal'))
    return self.widgets.expander.view(
        'Histogram report for %s' % cluster_name,
        ('Surface Markers' ,'Signaling Markers'),
        (surface_table, signal_table))
    
    
    #t = fake_table((1,0.1), (20,1))
    #return self.widgets.dim_table.view(all_pairs_with_mi_sorted(t_mi)[:500], t, t_mi)

    
class FitTable(Widget):
  def __init__(self):
    Widget.__init__(self)
    self.widgets.table = Table()
    self.widgets.kde1d_fig = Figure()
    self.widgets.stat_table = Table()

  def view(self, table, dims, remove_negative_values=True, size=200):
    if table.num_cells < 10:
      return View(self, 'Not enough cells')
    lines = []
    timer = MultiTimer(len(dims))
    for dim in dims:
      if remove_negative_values:
        positive_table = table.remove_bad_cells(dim)
      else:
        positive_table = table
      if positive_table.num_cells < 10:
        # TODO: add print error here
        continue

      line = []
      # 1 - Dimension
      line.append(dim)
      # 2 - Kde1d
      axes_main = new_axes(size,size)
      try:
        axes.kde1d(axes_main, positive_table, dim)
      except: 
        logging.exception('kde1d exception')
        print positive_table.num_cells
      kde_view = self.widgets.kde1d_fig.view(axes_main.figure)
      stat_table = positive_table.get_stats(dim)
      stats_view = self.widgets.stat_table.view(stat_table.dims, stat_table.data, True)
      line.append(view.stack_left(kde_view, stats_view))
          
      # 4 - GMM
      axes_clusters = new_axes(size,size)
      ((cluster1, cluster2), llh) = positive_table.emgm((dim,), 2, auto_centers=True)
      if cluster1.num_cells < 10 or cluster2.num_cells < 10:
        line.append('Not enough cells in one of the clusters')
      else:
        try:
          axes.kde1d(axes_clusters, cluster1, dim, norm = cluster1.num_cells / positive_table.num_cells)
        except:
          logging.exception('kde1d failed')
        try:
          axes.kde1d(axes_clusters, cluster2, dim, norm = cluster2.num_cells / positive_table.num_cells)
        except:
          logging.exception('kde1d failed')
        combined_stats = combine_tables([cluster1.get_stats(dim), cluster2.get_stats(dim)])
        line.append(
            view.stack_left(
                self.widgets.kde1d_fig.view(axes_clusters.figure),
                self.widgets.stat_table.view(combined_stats.dims, combined_stats.data, True)))
      line.append(llh)
      
      if False:
        #5 - KMEANS
        axes_clusters = new_axes(size,size)
        cluster1, cluster2 = positive_table.kmeans((dim,), 2)
        if cluster1.num_cells > 100:
          axes.kde1d(axes_clusters, cluster1, dim, norm = cluster1.num_cells / positive_table.num_cells)
        if cluster2.num_cells > 100:
          axes.kde1d(axes_clusters, cluster2, dim, norm = cluster2.num_cells / positive_table.num_cells)
        line.append(self.widgets.kde1d_fig.view(axes_clusters.figure))
      
      line.append('')
      
      lines.append(line)
      timer.complete_task(dim)
    return self.widgets.table.view(
        ['Dimension', 'Histogram', 'Gaussian Mixture','GM Log likelihood 2 clusters',  'K-Means'], 
        lines, None, [('Dimension', 'asc')])