#!/usr/bin/env python
import logging
from odict import OrderedDict
import sys
from StringIO import StringIO
import random
import struct
import os
from collections import namedtuple
import numpy as np
from numpy import array
import biology.markers
from biology.markers import Markers
from biology.markers import marker_from_name
from biology.markers import normalize_markers
from autoreloader import AutoReloader
from scriptservices import services
from cache import cache
from multitimer import MultiTimer
import hashlib

DimRange = namedtuple('DimRange', ['dim','min', 'max'])
def dim_range_to_str(dim_range):
  return '[%.3f < %s < %.3f]' % (dim_range.min, dim_range.dim, dim_range.max)

def fake_table(*args, **kargs):
  from numpy.random import normal
  num_cells = kargs.get('num_cells', 10000)
  add_zero_point = kargs.get('add_zero_point', True)
  vals = []
  for loc,scale in args:
    sample = normal(loc, scale, num_cells)
    if add_zero_point:
      sample = np.append(sample, np.zeros(1))
    vals.append(sample)
  dims = ['dim%d' % i for i in xrange(len(args))]
  data = np.array(vals).T
  return DataTable(data, dims)

def ks_test_function(dim, thresh):
  """ Generates functions to be used in distance_table.
  The function will do the ks test over the given dim on the two tables."""
  def ks_test(table1, table2):
    from scipy.stats import ks_2samp
    sample1 = table1.get_cols(dim)[0]
    sample2 = table2.get_cols(dim)[0]
    if thresh != None:
      sample1[sample1<thresh] = 0
      sample2[sample2<thresh] = 0
    ks, p_ks = ks_2samp(sample1, sample2)
    return ks
  return ks_test


def tables_mean(tables, p=1):
  """ Returns a table for which every data cell is the average of the corresponsing data
  cell in 'tables'
  """
  new_data = np.sum([t.data ** p for t in tables], axis=0)
  new_data = new_data / float(len(tables))
  new_data = new_data ** (1./p)
  return DataTable(new_data, tables[0].dims)
  

def distance_table(tables, distance_func):
  """ Returns a rectangular table in which cell i,j == cell j,i == distance(tables[i], tables[j]).
  """
  num_tables = len(tables)
  res = np.zeros((num_tables, num_tables))
  logging.info(
      'Calculating distance for %d pairs...' % ((num_tables ** 2 - num_tables) / 2))
  timer = MultiTimer((num_tables ** 2 - num_tables) / 2)
  for i in xrange(num_tables):
    for j in xrange(i):
      distance = distance_func(tables[i], tables[j])
      res[i,j] = distance
      res[j,i] = distance
      timer.complete_task('%s, %s' % (tables[i].name, tables[j].name))
  return DataTable(res, [t.name for t in tables])

@cache('ks_distances')
def ks_distances(tables, dim, thresh=None):
  return distance_table(tables, ks_test_function(dim, thresh))  

def combine_tables(datatables):
  assert len(datatables)
  assert all([datatables[0].dims == t.dims for t in datatables])
  new_data = np.concatenate([t.data for t in datatables])
  return DataTable(
      new_data, datatables[0].dims, datatables[0].legends)

class DataTable(AutoReloader):
  """ Represent a table with numeric values. 
  
  The values are saved in a numpy matrix, in the 'data' memeber.
  The column names are saved in 'dims'.
  Some column values have strings attached to them. A dictionary to convert
  from numeric value to a string is in the 'legends' list. If a certain 
  column has no legend, the legened list will contain None in the column's
  index. Currently, legends are only created for columns that represent tags
  in an experiment index (see dataindex.py). 
  
  To get data from the table use 
  """
  
  
  def __init__(self, data, dims, legends=None, name='', tags=None):
    """Creates a new data table. This class is immuteable.
    
    data -- a 2 dimension array with the table data
    dims -- string that are associated with table's columns.
    legends -- a list from dim index to a dictionary that gives string
    representation for numeric values.
    tags -- a dictionary of string to string, gives some properties of the
    table.
    """
    self.data = data
    self.dims = dims
    self.legends = legends
    self.num_cells = float(data.shape[0])
    if not tags:
      self.tags = {}
    if not name in self.tags:
      self.tags['name'] = name

  def __hash__(self):
    return hash(
        hashlib.sha1(self.data.flatten()).hexdigest())

  def __getitem__(self, dim):
    return self.get(dim)
  
  def set_name(self, new_name):
    self.tags['name'] = new_name
  
  def get_name(self):
    return self.tags['name']
  
  def get_tags(self, keys):
    if type(keys) in (str, unicode):
      return self.tags[keys]
    else:
      return [self.tags[key] for key in keys]
  
  name = property(get_name, set_name)
  
  def get(self, dim, index=0):
    if not dim in self.dims:
      raise ValueError('dim %s is not in table %s' % (dim, self.name))
    dim_i = self.dims.index(dim)
    return self.data[index, dim_i]
   
  def min(self, dim):
    return np.min(self.get_cols(dim)[0])

  def max(self, dim):
    return np.max(self.get_cols(dim)[0])

  def sub_name(self, sub_name):
    return self.name +' ' + sub_name

  def split(self, dim, bins):
    """ Splits the table into bins datatables. 
    the range of values for the dim column is splitted. Only rows 
    which match bin number i will appear in table table number i. 
    bins can either be a number, or a list of the threshold values for each
    bin.
    """
    if type(bins) in (int, complex):
      bins = np.r_[self.min(dim):self.max(dim):bins]
    p = self.get_cols(dim)[0]
    idx = np.digitize(p, bins)
    splitted = []
    for i in xrange(1,len(bins)):
      new_data = self.data[idx==i]
      splitted.append(DataTable(
          new_data,
          self.dims,
          self.legends,
          self.sub_name('%.2f<=%s<%.2f' % (bins[i-1], dim, bins[i]))))
    return splitted

  def gaussian_pdf_compare(self, dim, num_bins=100, gaussian_mean=None, gaussian_std=None):
    # get data
    p = self.get_points(dim)
    if not gaussian_std:
      gaussian_std = np.std(p)
    if not gaussian_mean:
      gaussian_mean = np.average(p)
    # normalize data
    #p = np.add(p, -gaussian_mean)
    #p = np.divide(p, gaussian_std)
    
    data_histogram, bins = np.histogram(p, num_bins, normed=False)
    data_histogram = data_histogram / float(np.sum(data_histogram))
    import scipy.stats
    rv = scipy.stats.norm(loc=gaussian_mean, scale=gaussian_std)
    gaussian_histogram = rv.cdf(bins[1:]) - rv.cdf(bins[:-1])
    #print dim
    #print 'gauss:%.2f' % sum(gaussian_histogram)
    #print 'data:%.2f' %  sum(data_histogram)
    diff = np.abs(gaussian_histogram - data_histogram)
    return sum(diff)

  def emgm(self, dims, k, auto_centers=False):
    """ runs emgm clustering on the datatable, result is k datatables
    with the rows for each cluster.
    """
    if auto_centers and len(dims)>1:
      raise Exception('k too big')
    
    points = self.get_points(*dims)
    from mlabwrap import mlab
    if auto_centers:
      centers = [np.r_[np.min(points) : np.max(points) : k*1j]]
      print centers
      idx, model, llh = mlab.emgm(points.T, centers, nout=3)
    else:
      idx, model, llh = mlab.emgm(points.T, k, nout=3)
    # we need to convert the index array from matlab to python (and remember
    # that python is 0-based and not 1-based)
    idx = idx.astype('int')[0]
    new_data = self.data[idx]
    tables = [DataTable(
        self.data[idx==(i+1)],
        self.dims,
        self.legends,
        self.sub_name('emgm cluster %d' % i)) for i in xrange(k)]
    for t in tables:
      t.tags['original_table'] = self
    #print llh
    return tables, llh[0][-1]

  def kmeans(self, dims, k):
    """ runs kmeans on the datatable, result is k datatables
    with the rows for each cluster.
    """
    points = self.get_points(*dims)
    from mlabwrap import mlab
    idx = mlab.kmeans(points, k, nout=1)
    
    # we need to convert the index array from matlab to python (and remember
    # that python is 0-based and not 1-based)
    idx = idx.astype('int')
    
    new_data = self.data[idx]
    tables = [DataTable(
        self.data[idx==(i+1)],
        self.dims,
        self.legends,
        self.sub_name('kmeans cluster %d' % i)) for i in xrange(k)]
    #for t in tables:
    #  t.properties['original_table'] = self
    return tables

  def get_stats_multi_dim(self, *dims):
    tables = [self.get_stats(dim, dim+'_') for dim in dims]
    new_data = np.hstack([t.data for t in tables])
    new_dims = sum([t.dims for t in tables], [])
    ret = DataTable(new_data, new_dims, self.legends)
    ret.properties['original_table'] = self
    return ret

  def get_correlation(self, dim1, dim2):
    return np.corrcoef(self.get_cols(dim1), self.get_cols(dim2))[0,1]
  
  def get_mutual_information(self, dim1, dim2):
    from mlabwrap import mlab
    return mlab.mutualinfo_ap(self.get_points(dim1, dim2), nout=1)

    return np.corrcoef(self.get_cols(dim1), self.get_cols(dim2))[0,1]

  def get_average(self, *dims):
    """Returns averages for the given dim. If there is only one dim
    a number is returned. Otherwise an array with averages is returned."""
    p = self.get_points(*dims)
    ret = np.average(p, axis=0)
    if ret.size == 1:
      return ret[0]
    return ret

  def get_std(self, dim):
    p = self.get_points(dim)
    return np.std(p)
    
  def get_stats(self, dim, prefix=''):
    """Get various 1d statistics for the datatable.
    """
    def add_stat(stats, key, val):
      stats[prefix+key] = val
    def get_stat(stats, key):
      return stats[prefix+key]
    #print dim
    #print self.num_cells
    #print self.data
    p = self.get_points(dim)
    s = OrderedDict()
    add_stat(s, 'num_cells', self.num_cells)
    add_stat(s, 'min', np.min(p))
    add_stat(s, 'max', np.max(p))
    add_stat(s, 'average', np.average(p))
    add_stat(s, 'std', np.std(p))
    add_stat(s, 'median', np.median(p))
    add_stat(s, 'gaussian_fit', 
        self.gaussian_pdf_compare(
            dim, 100,
            get_stat(s, 'average'),
            get_stat(s, 'std')))

    keys = s.keys()
    vals = np.array([s.values()])
    ret = DataTable(vals, keys, None, self.sub_name('stats for %s' % dim))
    ret.properties['original_table'] = self
    return ret
    
  def get_markers_not_in_groups(self, *groups):
    return [d for d in self.dims if not marker_from_name(d) or not marker_from_name(d).group in groups] 

  def get_markers(self, group):
    if group:
      return [d for d in self.dims if marker_from_name(d) and marker_from_name(d).group == group] 
    else:
      return [d for d in self.dims if not marker_from_name(d)] 
  
  def get_cols(self, *dims):
    """ Gets the specified dims as a list of cols
    """
    return self.get_points(*dims).T
  
  def get_points(self, *dims):
    """ Gets the specified dims as a list of rows
    """
    indices = [self.dims.index(d) for d in dims]
    return self.data[:,indices]    
  
  def get_subtable(self, rows):
    return DataTable(self.data[rows,:], self.dims)  
  
  def gate2(self, *dim_ranges):
    """ Gating using kd-tree, deprecated do not use
    """
    def kd_tree_cache(data):
      points = self.get_points(*[r.dim for r in dim_ranges])
      data.tree = KDTree(points)
    global services
    data = services.cache((self, [r.dim for r in dim_ranges]), kd_tree_cache)
    rect = Rectangle(
        [r.min for r in dim_ranges],
        [r.max for r in dim_ranges])
    new_indices = data.tree.query_range(rect)
    return DataTable(self.data[new_indices], self.dims)
    
  def gate(self, *dim_ranges):
    """ Gates the table. 
    Accepts DimRanges which are named tuples of (dim, min, max).
    """
    relevant_data = self.get_points(*[r.dim for r in dim_ranges])
    mins = np.array([r.min for r in dim_ranges])
    maxes = np.array([r.max for r in dim_ranges])
    test1 = np.alltrue(relevant_data >= mins, axis=1)
    test2 = np.alltrue(relevant_data <= maxes, axis=1)
    final = np.logical_and(test1, test2)   
    return DataTable(self.data[final], self.dims)

  def gate_out(self, *dim_ranges):
    """ Returns all the cells outside the given gate. 
    Accepts DimRanges which are named tuples of (dim, min, max).
    """
    relevant_data = self.get_points(*[r.dim for r in dim_ranges])
    mins = np.array([r.min for r in dim_ranges])
    maxes = np.array([r.max for r in dim_ranges])
    test1 = np.any(relevant_data < mins, axis=1)
    test2 = np.any(relevant_data > maxes, axis=1)
    final = np.logical_or(test1, test2)   
    return DataTable(self.data[final], self.dims)

    
  def window_agg(self, progression_dim, window_size=1000, overlap=500, agg_method='median'):
    """ Creates a sliding window that moves over the specified
    dimension and aggregates all values per window
    """
    window_size = int(window_size)
    overlap = int(overlap)
    # first sort by the given dim:
    xdim_index = self.dims.index(progression_dim)
    sorted_data = self.data[self.data[:,xdim_index].argsort(),]
    # create windows:
    from segmentaxis import segment_axis
    seg_data = segment_axis(sorted_data, window_size, overlap, axis=0)
    if agg_method == 'median':
      agg_data = np.median(seg_data, axis=1)   
    elif agg_method == 'average':
      agg_data = np.average(seg_data, axis=1)   
    else:
      raise Exception('Unknown agg method')
    return DataTable(agg_data, self.dims)
  
  def log_transform(self):
    data_copy = np.copy(self.data)      
    data_copy = np.log(data_copy)
    table = DataTable(data_copy, self.dims)
    return table

  def arcsinh_transform(self, factor=0.2):
    data_copy = np.copy(self.data)      
    data_copy = np.arcsinh(data_copy * factor)
    table = DataTable(data_copy, self.dims)   
    return table
    
  def add_reduced_dims(self, method, no_dims, dims_to_use=None, *args, **kargs):
    """ Add new columns with values determined by dimensionality reduction
    algorithms.
    """
    if not dims_to_use:
      dims_to_use = self.dims
    points = self.get_points(*dims_to_use)
    if method == 'tsne':
      extra_points = calc_tsne(points)
    else:
      from mlabwrap import mlab
      extra_points, mapping = mlab.compute_mapping(
          points, method, no_dims, *args, nout=2, **kargs)
    if method.lower() in ['isomap', 'lle']:
      # we need to convert the index array from matlab to python (and remember
      # that python is 0-based and not 1-based)
      indices = np.subtract(mapping.conn_comp.T[0].astype('int'), 1)
      old_data = self.data[indices,:]
    else:
      old_data = self.data
    new_data = np.concatenate((old_data, extra_points), axis=1)
    extra_dims = ['%s%d' % (method, i) for i in xrange(no_dims)]
    new_dims = self.dims + extra_dims
    return DataTable(new_data, new_dims)
    
  def remove_bad_cells(self, *dims):
    """ Removes rows which have negative values for the specified dims.
    """
    ranges = [DimRange(d, 0, np.inf) for d in dims]
    return self.gate(*ranges)

  @cache('not_so_random_samples')
  def random_sample(self, n):
    """ Returns a random sample of n rows from the table. 
    Note that this is cached in memory, so multiple runs will result 
    in the same sample.
    """
    indices = random.sample(xrange(np.shape(self.data)[0]), n)
    table = DataTable(self.data[indices], self.dims)
    return table
  
  @cache('mutual_information_tables')
  def get_mutual_information_table(self, dims_to_use=None, ignore_negative_values=True):
    """ Returns a table with mutual information between pairs in dims_to_use. 
    cell i,j is the  mutual information between dims_to_use[i] and dims_to_use[j]. 
    """
    from mlabwrap import mlab
    bad_dims = self.get_markers('surface_ignore')
    bad_dims.append('Cell Length')
    bad_dims.append('Time')
    bad_dims.append('191-DNA')
    bad_dims.append('193-DNA')
    bad_dims.append('103-Viability')
    bad_dims.append('cluster_name')
    bad_dims.append('stim')
    bad_dims.append('cluster_num')
    if not dims_to_use:
      dims_to_use = self.dims[:]
    dims_to_use = [d for d in dims_to_use if not d in bad_dims]    
    num_dims = len(dims_to_use)
    res = np.zeros((num_dims, num_dims))
    logging.info(
        'Calculating mutual information for %d pairs...' % ((num_dims ** 2 - num_dims) / 2))
    timer = MultiTimer((num_dims ** 2 - num_dims) / 2)
    for i in xrange(num_dims):
      for j in xrange(i):
        arr = self.get_points(dims_to_use[i], dims_to_use[j])
        if ignore_negative_values:
          arr = arr[np.all(arr > 0, axis=1)]
          if arr.shape[0] < 100:
            logging.warning('Less than 100 cells in MI calculation for (%s, %s)' % (dims_to_use[i], dims_to_use[j]))
            res[j,i] = 0
            res[i,j] = 0
            continue
        #print arr.shape
        res[i,j] = mlab.mutualinfo_ap(arr, nout=1)
        res[j,i] = 0
        timer.complete_task('%s, %s' % (dims_to_use[i], dims_to_use[j]))
    return DataTable(res, dims_to_use)
    
  
  #def get_vectors(self, *dims):
