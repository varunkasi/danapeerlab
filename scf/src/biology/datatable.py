#!/usr/bin/env python
import logging
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
#from biology.kdtree import KDTree
#from biology.kdtree import Rectangle
from scriptservices import services
from biology.markers import normalize_markers
from autoreloader import AutoReloader

DimRange = namedtuple('DimRange', ['dim','min', 'max'])

def combine_tables(datatables):
  def cache(data):
    print '~!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
    print datatables
    assert len(datatables)
    assert all([datatables[0].dims == t.dims for t in datatables])
    new_data = np.concatenate([t.data for t in datatables])
    data.new_table = DataTable(
        new_data, datatables[0].dims, datatables[0].legends)
  data = services.cache((datatables), cache, False, False)
  return data.new_table

class DataTable(AutoReloader):
  def __init__(self, data, dims, legends=None):
    """Creates a new data table. This class is immuteable.
    
    data -- a 2 dimension array with the table data
    dims -- object that are associated with table's columns.
    legends -- a list from dim index to a dictionary that gives string
    representation for numeric values.
    """
    self.data = data
    self.num_cells = float(data.shape[0])
    self.dims = dims
    self.legends = legends


  def min(self, dim):
    return np.min(self.get_cols(dim)[0])

  def max(self, dim):
    return np.max(self.get_cols(dim)[0])

  def get_markers(self, group):
    return [d for d in self.dims if marker_from_name(d) and marker_from_name(d).group == group] 
  
  def get_cols(self, *dims):
    return self.get_points(*dims).T
  
  def get_points(self, *dims):
    indices = [self.dims.index(d) for d in dims]
    return self.data[:,indices]    
  
  def get_subtable(self, rows):
    return DataTable(self.data[rows,:], self.dims)  
  
  def gate2(self, *dim_ranges):
    def kd_tree_cache(data):
      points = self.get_points(*[r.dim for r in dim_ranges])
      data.tree = KDTree(points)
    global services
    data = services.cache((self, [r.dim for r in dim_ranges]), kd_tree_cache, False, False)
    rect = Rectangle(
        [r.min for r in dim_ranges],
        [r.max for r in dim_ranges])
    new_indices = data.tree.query_range(rect)
    return DataTable(self.data[new_indices], self.dims)
    
  def gate(self, *dim_ranges):
    def gate_cache(data):
      relevant_data = self.get_points(*[r.dim for r in dim_ranges])
      mins = np.array([r.min for r in dim_ranges])
      maxes = np.array([r.max for r in dim_ranges])
      test1 = np.alltrue(relevant_data >= mins, axis=1)
      test2 = np.alltrue(relevant_data <= maxes, axis=1)
      final = np.logical_and(test1, test2)
      data.table = DataTable(self.data[final], self.dims)
    data = services.cache((self, dim_ranges), gate_cache, False, False)
    return data.table
    
  def windowed_medians(self, progression_dim, window_size=1000, overlap=500):
    window_size = int(window_size)
    overlap = int(overlap)
    def cache(data):
      # first sort by the given dim:
      xdim_index = self.dims.index(progression_dim)
      sorted_data = self.data[self.data[:,xdim_index].argsort(),]
      # create windows:
      from segmentaxis import segment_axis
      seg_data = segment_axis(sorted_data, window_size, overlap, axis=0)
      med_data = np.median(seg_data, axis=1)   
      data.table = DataTable(med_data, self.dims)
    data = services.cache((self, progression_dim, window_size, overlap), cache, False, False)
    return data.table
  
  def log_transform(self):
    def cache(data):
      data_copy = np.copy(self.data)      
      data_copy = np.log(data_copy)
      data.table = DataTable(data_copy, self.dims)
    data = services.cache(self, cache, False, False)
    return data.table

  def arcsinh_transform(self):
    def cache(data):
      data_copy = np.copy(self.data)      
      data_copy = np.arcsinh(data_copy)
      data.table = DataTable(data_copy, self.dims)
    data = services.cache(self, cache, False, False)
    return data.table
    
  def add_reduced_dims(self, method, no_dims, dims_to_use=None, *args, **kargs):
    if not dims_to_use:
      dims_to_use = self.dims
    def add_reduced_dims_cache(data):
      points = self.get_points(*dims_to_use)
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
      data.new_table = DataTable(new_data, new_dims)
    global services
    data = services.cache((self, method, no_dims, dims_to_use, args, kargs), add_reduced_dims_cache, False, False)
    return data.new_table
    
  def remove_bad_cells(self, *dims):
    ranges = [DimRange(d, 0, np.inf) for d in dims]
    return self.gate(*ranges)
    
  def random_sample(self, n):
    def random_sample_cache(data):
      indices = random.sample(xrange(np.shape(self.data)[0]), n)
      data.table = DataTable(self.data[indices], self.dims)
    data = services.cache((self, n), random_sample_cache, False, False)
    return data.table
  
  def get_mutual_information(self, ignore_negative_values=True):
    def cache(data):
      from mlabwrap import mlab
      bad_dims = self.get_markers('surface_ignore')
      bad_dims.append('Cell Length')
      bad_dims.append('Time')
      bad_dims.append('191-DNA')
      bad_dims.append('cluster_name')
      bad_dims.append('stim')
      bad_dims.append('cluster_num')
      dims_to_use = self.dims[:]
      dims_to_use = [d for d in dims_to_use if not d in bad_dims]    
      num_dims = len(dims_to_use)
      res = np.zeros((num_dims, num_dims))
      for i in xrange(num_dims):
        for j in xrange(i):
          logging.info('Calculating mutual information between %s and %s' % (dims_to_use[i], dims_to_use[j]))
          arr = self.get_points(dims_to_use[i], dims_to_use[j])
          if ignore_negative_values:
            arr = arr[np.all(arr > 0, axis=1)]
            if arr.shape[0] < 100:
              services.print_text('Less than 100 cells in MI calculation for (%s, %s)' % (dims_to_use[i], dims_to_use[j]), weight=700, foreground='red')
              res[j,i] = 0
              res[i,j] = 0
              continue
          #print arr.shape
          res[i,j] = mlab.mutualinfo_ap(arr, nout=1)
          res[j,i] = 0
      data.res = DataTable(res, dims_to_use)
    data = services.cache((self,ignore_negative_values), cache, False, False)
    return data.res
    
  
  #def get_vectors(self, *dims):
