#!/usr/bin/env python
import numpy as np
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
from biology.datatable import combine_tables
from biology.datatable import DimRange
from view import stack_lines
import matplotlib.cm as cm

class SlicesReport(Widget):
  def __init__(self):
    Widget.__init__(self)
    self.widgets.pair_table = PairTable()

  def view(self):
    index = DataIndex.load(r'c:\cytof54_clustered\cytof54.index')
    t = index.load_table(cluster_name='CD8+ T-cells')
    dim_x = '152-Ki67'
    dim_y = '167-CD38'
    t = t.remove_bad_cells(dim_x, dim_y)
    from histogram_report import FitTable
    splitted = t.split(dim_x, 100j)
    views = []
    for s in splitted:
      views.append(View(self, '<h1>%s</h1>' % s.name))
      views.append(View(self, '<h1>%d cells</h1>' % s.num_cells))     
      views.append(FitTable().view(s, [dim_y]))
    views = [PairTable().view([[dim_x, dim_y]], t)] + views
    return stack_lines(*views)
    
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
    #t = t.gate(
    #    DimRange('167-CD38', -20, 6.2),
    #    DimRange('146-CD8', 4, 6))
    #t = fake_table((1,0.1), (20,1))
    samples_percent = min((10000. / t.num_cells) * 100, 100)
    num_samples = int((samples_percent/100) * t.data.shape[0])
    truncate_cells_mi = True
    t_samp = t.random_sample(num_samples)
    #t_mi = t_samp.get_mutual_information(
    #    ignore_negative_values=truncate_cells_mi)
    #return self.widgets.pair_table.view(all_pairs_with_mi_sorted(t_mi)[:5], t, t_mi)
    t_mi = None
    return self.widgets.pair_table.view([('167-CD38', '152-Ki67')], t, t_mi)


def get_mins(a):
  return [np.r_[False, a[1:] < a[:-1]] & np.r_[a[:-1] < a[1:], False]]

def find_discontinuities(t, dim_x, dim_y, ax=None):
    from scipy.ndimage.filters import gaussian_filter1d    
    hist, extent, x_edges, y_edges = axes.scatter_data(t, (dim_x, dim_y), no_bins=512j)

    summed = np.sum(hist, axis=0)
    middles = (y_edges[:-1] + y_edges[1:]) / 2.
    smoothed = gaussian_filter1d(summed, 15)
    points = middles[get_mins(smoothed)]
    if ax:
      ax.plot(middles, summed)
      ax.plot(middles, smoothed)
      for p in points:
        ax.axvline(p)
    return points
      
class PairFitSplit(Widget):
  def __init__(self):
    Widget.__init__(self)
    self.widget.pair = PairFit()
    
  def view(self, table, dim_x, dim_y):
      ax_dis = new_axes(300,300)
      dis_points = find_discontinuities(table_positive, dim_x, dim_y, ax_dis)
      
    
class PairFit(Widget):
  def __init__(self):
    Widget.__init__(self)
    self.widgets.fig = Figure()

  def view(self, table, dim_x, dim_y):
    splitted = table.split(dim_x, 100j)
    stats = [s.get_stats_multi_dim(dim_x, dim_y) for s in splitted if s.num_cells>=5]
    if not stats:
      return View(None, 'Not enough cells in each bin')

    joined = combine_tables(stats)
    ax = new_axes(300, 300)
    ax, hist = axes.scatter(ax, table, (dim_x, dim_y), norm_axis=None, no_bins=300j)
    axes.points(ax, joined, (dim_x+'_average', dim_y + '_average'))
    
    summed = np.sum(hist, axis=0)
    #print hist
    #print summed
    ax_kde1d = new_axes(300,300)
    ax_kde1d.plot(summed)
    #ax_conv = new_axes(300,300)
    #conv_data = np.convolve(summed,summed)
    #ax_conv.plot(conv_data)
    
    from scipy.ndimage.filters import gaussian_filter1d    
    ax_gauss = new_axes(300,300)
    gauss_data = gaussian_filter1d(summed,15)
    ax_gauss.plot(gauss_data)

    return stack_lines(
        self.widgets.fig.view(ax.figure),
        self.widgets.fig.view(ax_kde1d.figure),
     #   self.widgets.fig.view(ax_conv.figure),
     #  str(get_mins(conv_data)),
        self.widgets.fig.view(ax_gauss.figure),
        str(get_mins(gauss_data)))
        

def old_code():
  pass
  #stats = set(stats)
  # gaussian_fit_name = '%s_gaussian_fit' % dim_y
  # num_cells_name = '%s_num_cells' % dim_y
  # print [(s[gaussian_fit_name],s[num_cells_name]) for s in stats]
  # stats_split = [s for s in stats if s[gaussian_fit_name] > 0.5]
  # stats_split_enough_cells = [s for s in stats_split if s[num_cells_name] > 20]
  # stats_to_remove = []
  # stats_to_add = []
  # print stats_split_enough_cells
  # for s in stats_split_enough_cells:
  # ((cluster1, cluster2), llh) = s.properties['original_table'].emgm([dim_y], 2, True)
  # stats1 = cluster1.get_stats_multi_dim(dim_x, dim_y)
  # stats2 = cluster2.get_stats_multi_dim(dim_x, dim_y)
  #if max(stats1[gaussian_fit_name], stats2[gaussian_fit_name]) > s[gaussian_fit_name]:
  # continue
  # stats_to_add.append(stats1)
  # stats_to_add.append(stats2)
  # stats_to_remove.append(s) 
  # stats = stats - set(stats_to_remove)
  # stats = stats | set(stats_to_add)
  # stats = list(stats)
          

  #ax_kde = new_axes(300, 300)
  #display_data, extent, density, X, Y = axes.kde2d_data(
  #  table, (dim_x, dim_y), norm_axis='y', res=300)
  #thresh = 0.2   
  #display_data[display_data<thresh] = 0
  #display_data[display_data>=thresh] = 1
  #ax_kde.imshow(display_data, extent=extent, origin='lower', cmap=cm.gist_yarg)
  
class PairTable(Widget):
  def __init__(self):
    Widget.__init__(self)
    self.widgets.table = Table()
    self.widgets.kde2d_fig = Figure()
    self.widgets.pair_fit = PairFit()
    
  def view(self, pairs, table, mi_table=None):
    lines = []
    logging.info('Creating pairtable for %d pairs...' % len(pairs))
    timer = MultiTimer(len(pairs))
    for p in pairs:
      gc.collect()
      line = []
      line.append(p[0])
      line.append(p[1])
      if mi_table:
        i1 = mi_table.dims.index(p[0])
        i2 = mi_table.dims.index(p[1])
        line.append(mi_table.data[i1, i2])
      else:
        line.append('')
      table_positive = table.remove_bad_cells(p[0], p[1])
      if table_positive.num_cells > 100:
        fig = new_figure(300,300)
        axes.kde2d_color_hist(fig, table_positive, (p[0], p[1]), None, 'y', 0.001)       
        ax_dis = new_axes(300,300)
        dis_points = find_discontinuities(table_positive, p[0], p[1], ax_dis)
        line.append(stack_lines(
            self.widgets.kde2d_fig.view(fig),
            self.widgets.kde2d_fig.view(ax_dis.figure),
            dis_points,
            self.widgets.pair_fit.view(table_positive, p[0], p[1])))


        fig = new_figure(300,300)
        ax_dis = new_axes(300,300)
        dis_points = find_discontinuities(table_positive, p[1], p[0], ax_dis)
        axes.kde2d_color_hist(fig, table_positive, (p[1], p[0]), None, 'y', 0.001)
        line.append(stack_lines(
            self.widgets.kde2d_fig.view(fig),
            self.widgets.kde2d_fig.view(ax_dis.figure),
            dis_points,
            self.widgets.pair_fit.view(table_positive, p[1], p[0])))
        
        #line.append(self.widgets.kde2d_fig.view(ax.figure))
        
        ax = new_axes(300,300)
        axes.scatter(ax, table_positive, (p[0], p[1]), norm_axis=None, no_bins=300j)
        line.append(self.widgets.kde2d_fig.view(ax.figure))

        
      lines.append(line)
      timer.complete_task('%s, %s' % tuple(p[:2]))
    return self.widgets.table.view(
        ['Dimension 1', 'Dimension 2', 'Mutual Information', 'Normalized Plot1','Normalized Plot2','Scatter Plot'], 
        lines, None, [('Mutual Information', 'desc')])