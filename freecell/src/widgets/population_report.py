#!/usr/bin/env python
import scipy
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
from cache import cache
from widgets.select import Select
from widgets.applybutton import ApplyButton
from widgets.populationpicker import PopulationPicker
import matplotlib.cm as cm


    
def all_pairs_with_mi_sorted(mi_table):
  res = []
  for i in xrange(len(mi_table.dims)):
    for j in xrange(i):
      res.append((mi_table.dims[i], mi_table.dims[j], mi_table.data[i, j]))
  res.sort(key=lambda n:n[2], reverse=True)
  return res

class PopulationReport(Widget):
  def __init__(self, id, parent):
    Widget.__init__(self, id, parent)
    self._add_widget('pair_table', PairTable)
    self._add_widget('population_picker', PopulationPicker)

  def view(self):
    if self.widgets.population_picker.is_ready() and self.widgets.population_picker.get_data(True) > 2000:
      t = self.widgets.population_picker.get_data()
      #t = fake_table((1,0.1), (20,1))

      samples_percent = min((10000. / t.num_cells) * 100, 100)
      num_samples = int((samples_percent/100) * t.data.shape[0])
      truncate_cells_mi = True
      t_samp = t.random_sample(num_samples)
    
      t_mi = t_samp.get_mutual_information(
          t.get_markers('signal'),
          ignore_negative_values=truncate_cells_mi)
      table = self.widgets.pair_table.view(all_pairs_with_mi_sorted(t_mi)[:15], t, t_mi)
    elif self.widgets.population_picker.is_ready():
      table = 'Not enougth cells -- need at least 2000'
    else:
      table = ''
    
    return stack_lines(
        self.widgets.population_picker.view(),
        table)
#        self.widgets.choice.view('', self.widgets.apply, ('A','FASDFSDsdafsd','CCCCCCCCC')),
#        self.widgets.apply.view())
#        View(self, '<h1>Population Report for %s, %s</h1>' % (cluster, stim)),
#        View(self, '<h2>%d cells</h2>' % t.num_cells),
#        table)
    #return self.widgets.pair_table.view([('167-CD38', '152-Ki67')], t, t_mi)


def get_mins(a):
  return np.r_[False, a[1:] < a[:-1]] & np.r_[a[:-1] < a[1:], False]

def find_discontinuities(t, dim_x, dim_y, ax=None):
    from scipy.ndimage.filters import gaussian_filter1d    
    hist, extent, x_edges, y_edges = axes.scatter_data(t, (dim_x, dim_y), no_bins=512j)

    summed = np.sum(hist, axis=0)
    middles = (y_edges[:-1] + y_edges[1:]) / 2.
    smoothed = gaussian_filter1d(summed, 15)
    thresh = 0.15 * np.max(smoothed)   
    mins = get_mins(smoothed) & (smoothed < thresh)
    points = middles[[mins]]
    if ax:
      ax.plot(middles, summed)
      ax.plot(middles, smoothed)
      for p in points:
        ax.axvline(p)
    return points
      
class PairFitSplit(Widget):
  def __init__(self, id, parent):
    Widget.__init__(self, id, parent)
    self._add_widget('pair', PairFit)
    
  def view(self, table, dim_x, dim_y):
      #ax_dis = new_axes(300,300)
      dis_points = find_discontinuities(table, dim_x, dim_y, None)
      splits = []
      split_start = np.min(table.get_points(dim_y))
      dis_points = np.r_[dis_points, np.max(table.get_points(dim_y))]
      min_split_fraction = 0.1      
      for p in dis_points:
        split = table.gate(DimRange(dim_y, split_start, p))
        if split.num_cells >= min_split_fraction * table.num_cells:
          splits.append(split)
          split_start = p
      
      return stack_lines(
          *[self.widgets.pair.view(s, dim_x, dim_y) for s in splits])

def sigmoid(p,x):
    x0,y0,c,k=p
    y = c / (1 + np.exp(-k*(x-x0))) + y0
    return y


def find_error(x, y, func, params):
  std = np.std(y)
  errors = np.abs(func(params, x) - y) / std
  return np.average(errors)

def sigmoid_fit(x,y, p_guess=None):
  def residuals(p,x,y):
    return y - sigmoid(p,x)  #+ np.abs(p[2]) / 10.
  if not p_guess:
    p_guess=(np.median(x),np.median(y), 1.0, 1.0)
  p, cov, infodict, mesg, ier = scipy.optimize.leastsq(
    residuals,p_guess,args=(x,y),full_output=1) 
  return p  
  
class PairFit(Widget):
  def __init__(self, id, parent):
    Widget.__init__(self, id, parent)
    self._add_widget('fig', Figure)

  def view(self, table, dim_x, dim_y):
    splitted = table.split(dim_x, 100j)
    stats = [s.get_stats_multi_dim(dim_x, dim_y) for s in splitted if s.num_cells>=25]
    if len(stats) < 10:
      return View(None, 'Not enough cells in each bin')

    joined = combine_tables(stats)
    ax = new_axes(300, 300)
    ax, hist = axes.scatter(ax, table, (dim_x, dim_y), norm_axis=None, no_bins=300j)
       
    x_points = np.linspace(0,10,300)
    avg_points = joined.get_cols(dim_x+'_average', dim_y + '_average')
    std_points = joined.get_cols(dim_x+'_average', dim_y + '_std')
    
    std_fit, std_res, std_rank, std_s, std_r = np.polyfit(std_points[0], std_points[1], 1, full=True)
    avg_fit, avg_res, avg_rank, avg_s, avg_r = np.polyfit(avg_points[0], avg_points[1], 1, full=True)
    avg_sig_fit = sigmoid_fit(avg_points[0], avg_points[1])
    sig_error = find_error(avg_points[0], avg_points[1], sigmoid, avg_sig_fit)

    ax.plot(avg_points[0], avg_points[1], '.')
    #ax.plot(x_points, np.poly1d(avg_fit)(x_points), '-')
    ax.plot(x_points, sigmoid(avg_sig_fit, x_points), '-')
    #ax.scatter(avg_points[0], avg_points[1], s=1, marker='o', color='blue')
    ax.scatter(std_points[0], std_points[1], s=1, marker='o')
    
    ax.set_xlabel(dim_x + '   ', size='x-small')
    ax.set_ylabel(dim_y + '   ', size='x-small')
    ax.set_xlim(0,8)
    ax.set_ylim(0,8)
    
    
    return stack_lines(
        self.widgets.fig.view(ax.figure),
        str(avg_sig_fit),
        str(sig_error))
  
class PairTable(Widget):
  def __init__(self, id, parent):
    Widget.__init__(self, id, parent)
    self._add_widget('table', Table)
    self._add_widget('kde2d_fig', Figure)
    self._add_widget('pair_fit_split', PairFitSplit)
    
  def view_pair(self, p, table_positive):
      fig1 = new_figure(300,300)
      axes.kde2d_color_hist(fig1, table_positive, (p[0], p[1]), None, None, 0.001)
      fig = new_figure(300,300)
      axes.kde2d_color_hist(fig, table_positive, (p[0], p[1]), None, 'y', 0.001)       
      #ax_dis = new_axes(300,300)
      dis_points = find_discontinuities(table_positive, p[0], p[1], None)
      return stack_lines(
          self.widgets.kde2d_fig.view(fig1),
          self.widgets.kde2d_fig.view(fig),
#          self.widgets.kde2d_fig.view(ax_dis.figure),
          dis_points,
          self.widgets.pair_fit_split.view(table_positive, p[0], p[1]))

  @cache('PairTables')
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
      #table_positive = table
      print ' (%d cells)' % table_positive.num_cells
      if table_positive.num_cells > 100:
        fig = new_figure(300,300)
        axes.kde2d_color_hist(fig, table_positive, (p[0], p[1]), None, 'y', 0.001)       
        #ax_dis = new_axes(300,300)
        dis_points = find_discontinuities(table_positive, p[0], p[1], None)
        line.append(self.view_pair(p, table_positive))
        line.append(self.view_pair((p[1], p[0]), table_positive))
        ax = new_axes(300,300)
        axes.scatter(ax, table_positive, (p[0], p[1]), norm_axis=None, no_bins=300j)
        line.append(self.widgets.kde2d_fig.view(ax.figure))
      lines.append(line)
      timer.complete_task('%s, %s' % tuple(p[:2]))
    return self.widgets.table.view(
        ['Dimension 1', 'Dimension 2', 'Mutual Information', 'Normalized Plot1','Normalized Plot2','Scatter Plot'], 
        lines, None, [('Mutual Information', 'desc')])
        
class SlicesReport(Widget):
  def __init__(self):
    Widget.__init__(self)
    self.widgets.pair_table = PairTable()

  def view(self):
    index = DataIndex.load(r'c:\cytof54_clustered\cytof54.index')
    t = index.load_table(cluster_name='CD8+ T-cells', stim='Unstim1')
    #t = index.load_table(cluster_name='B-cells CD20+', stim='Unstim1')
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
