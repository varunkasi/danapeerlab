﻿#!/usr/bin/env python
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
from biology.markers import get_markers
from populationpicker import PopulationPicker
from select import Select
from applybutton import ApplyButton
  
class HistogramReport(Widget):
  def __init__(self, id, parent):
    Widget.__init__(self, id, parent)
    self._add_widget('histogram_table', HistogramTable)
    self._add_widget('population_picker', PopulationPicker)
    self._add_widget('dim_picker', Select)
    self._add_widget('negative_values_picker', Select)
    self._add_widget('apply', ApplyButton)
  
  def view(self):
    if not self.widgets.population_picker.is_ready():
      return self.widgets.population_picker.view()
      
    if not self.widgets.negative_values_picker.values.choices:
      self.widgets.negative_values_picker.values.choices = ['remove']
    
    table = self.widgets.population_picker.get_data()
    
    return view.stack_lines(
        self.widgets.population_picker.view(),
        self.widgets.dim_picker.view(
            'Dimension',
            self.widgets.apply,
            table.dims, True, [
                ('Signal Markers', get_markers('signal')),
                ('Surface Markers', get_markers('surface'))]),
        self.widgets.negative_values_picker.view(
            'Negative Values',
            self.widgets.apply,
            [('remove', 'Remove negative values'),
             ('keep', 'Keep negative values')], False),
        self.widgets.apply.view(),
        self.widgets.histogram_table.view(
            table,
            self.widgets.dim_picker.values.choices,
            'remove' in self.widgets.negative_values_picker.values.choices))
            
            

  
class FitReport(Widget):
  def __init__(self, id, parent):
    Widget.__init__(self, id, parent)
    self.widgets.expander = Expander()
    self.widgets.surface_table = FitTable()
    self.widgets.signal_table = FitTable()
    #self.widgets.dim_table = DimTable()

  def view(self):
    cluster_name = 'B-cells CD20+'    
    stim='Unstim_' #'All'
    index = DataIndex.load(r'c:\cytof54_clustered\cytof54.index')
    t = index.load_table(cluster_name=cluster_name, stim=stim)
    #t = t.gate(
    #    DimRange('167-CD38', -20, 6.2),
    #    DimRange('146-CD8', 4, 6))
    surface_table = self.widgets.surface_table.view(t, t.get_markers('surface'))
    signal_table = self.widgets.surface_table.view(t, t.get_markers('signal'))
    return self.widgets.expander.view(
        'Histogram report for %s, %s' % (cluster_name, stim),
        ('Surface Markers' ,'Signaling Markers'),
        (surface_table, signal_table))
    
    
    #t = fake_table((1,0.1), (20,1))
    #return self.widgets.dim_table.view(all_pairs_with_mi_sorted(t_mi)[:500], t, t_mi)

    
class HistogramTable(Widget):
  def __init__(self, id, parent):
    Widget.__init__(self, id, parent)
    self._add_widget('table', Table)
    self._add_widget('kde1d_fig', Figure)
    self._add_widget('stat_table', Table)

  def view(self, table, dims, remove_negative_values=True, cluster=False, size=200):
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
          
      if cluster:
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
      
      lines.append(line)
      timer.complete_task(dim)
    
    if cluster:
      titles = ['Dimension', 'Histogram', 'Gaussian Mixture','GM Log likelihood 2 clusters']
    else:
      titles = ['Dimension', 'Histogram']
    return self.widgets.table.view(
        titles, 
        lines, None, [('Dimension', 'asc')])