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
  
class PopulationReport(Widget):
  def __init__(self):
    Widget.__init__(self)
    self.widgets.pair_table = PairTable()

  def view(self):
    def all_pairs_with_mi_sorted(mi_table):
      res = []
      for i in xrange(len(mi_table.dims)):
        for j in xrange(i):
          res.append((mi_table.dims[i], mi_table.dims[j], mi_table.data[i, j]))
      res.sort(key=lambda n:n[2], reverse=True)
      return res
    index = DataIndex.load(r'c:\cytof54_clustered\cytof54.index')
    t = index.load_table(cluster_name='CD8+ T-cells')
    samples_percent = min((10000. / t.num_cells) * 100, 100)
    num_samples = int((samples_percent/100) * t.data.shape[0])
    truncate_cells_mi = True
    t_samp = t.random_sample(num_samples)
    t_mi = t_samp.get_mutual_information(
        ignore_negative_values=truncate_cells_mi)
    return self.widgets.pair_table.view(all_pairs_with_mi_sorted(t_mi)[:200], t, t_mi)


class PairTable(Widget):
  def __init__(self):
    Widget.__init__(self)
    self.widgets.table = Table()
    self.widgets.kde2d_fig = Figure()
    
  def view(self, pairs, table, mi_table):
    lines = []
    logging.info('Creating pairtable for %d pairs...' % len(pairs))
    timer = MultiTimer(len(pairs))
    for p in pairs:
      gc.collect()
      i1 = mi_table.dims.index(p[0])
      i2 = mi_table.dims.index(p[1])
      line = []
      line.append(p[0])
      line.append(p[1])
      line.append(mi_table.data[i1, i2])
      table_positive = table.remove_bad_cells(p[0], p[1])
      if table_positive.num_cells > 100:
        fig = new_figure(300,300)
        axes.kde2d_color_hist(fig, table_positive, (p[0], p[1]), None, 'y', 0.001)
        line.append(self.widgets.kde2d_fig.view(fig))

        fig = new_figure(300,300)
        axes.kde2d_color_hist(fig, table_positive, (p[1], p[0]), None, 'y', 0.001)
        line.append(self.widgets.kde2d_fig.view(fig))
        ax = new_axes(300,300)
        axes.scatter(ax, table_positive, (p[0], p[1]))
        line.append(self.widgets.kde2d_fig.view(ax.figure))

        
      lines.append(line)
      timer.complete_task('%s, %s' % p[:2])
    return self.widgets.table.view(
        ['Dimension 1', 'Dimension 2', 'Mutual Information'], 
        lines, None, [('Mutual Information', 'desc')])