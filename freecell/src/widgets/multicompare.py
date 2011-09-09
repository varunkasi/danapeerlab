#!/usr/bin/env python
import axes
import numpy as np
import view
import logging
import biology.datatable as datatable
from biology.tagorder import multiple_tag_sort_key
from multitimer import MultiTimer
from operator import itemgetter
from widget import Widget
from widgetwithcontrolopanel import WidgetWithControlPanel
from view import View
from view import render
from view import stack_lines
from select import options_from_table
from input import Input
from applybutton import ApplyButton
from figure import Figure
from areaselect import AreaSelect
from odict import OrderedDict
from table import Table
from select import Select
from cache import cache
from motionchart import MotionChart

class MultiCompare(WidgetWithControlPanel):
  """ This module allows the user to compare multiple populations. The
  populations are overlayed over a 2d map.
  """
  def __init__(self, id, parent):
    WidgetWithControlPanel.__init__(self, id, parent)
    self._add_widget('average_dims', Select)
    self._add_widget('std_dims', Select)
    self._add_widget('scroll_tags', Select)
    self._add_widget('id_tags', Select)
    self._add_widget('reduce_dims1', Select)
    self._add_widget('reduce_dims2', Select)
    self._add_widget('reduce_method', Select)
    self._add_widget('apply', ApplyButton)
    self._add_widget('motion_chart', MotionChart)
  
    
  def title(self, short):
    """Title for the module, the short version is displayed in menus, 
    the long version is displayed in the expander title.
    """
    return 'MultiCompare'
      
  def get_inputs(self):
    """ Returns the names input list.
    """
    return ['tables']
    
  def get_outputs(self):
    """ Returns the output list.
    """
    return ['tables']
  
  def run(self, tables):
    """ The run method for this module doesn't do anything.
    """
    id_tags = self.widgets.id_tags.get_choices()
    selected_id_tag_values = self.widgets.motion_chart.get_selected_ids()
    # convert from a string represeting a list to a list:
    selected_id_tag_values = [eval(x) for x in selected_id_tag_values]
    ret = []
    for values in selected_id_tag_values:
      for table in tables:
        skip = False
        for i, tag in enumerate(id_tags):
          if table.tags[tag] != values[i]:
            skip = True
            break
        if not skip and not table in ret:
          ret.append(table)
    return {'tables':ret}
  
  def separate_tables_by_time(self, tables, time_col):
    return [tables], [range(len(tables))]
    time_to_tables = OrderedDict()
    time_to_idx = OrderedDict()
    for i, time in enumerate(time_col):
      time_to_tables.setdefault(time, []).append(tables[i])
      time_to_idx.setdefault(time, []).append(i)
    return time_to_tables.values(), time_to_idx.values()
    
  def dim_reduce_pca(self, tables, dims):
    if not dims:
      return [0] * len(tables), [0] * len(tables), None
    average_vectors = np.array([t.get_average(*dims) for t in tables])
    print average_vectors.shape
    from mlabwrap import mlab
    #extra_points, mapping = mlab.compute_mapping(
    #    average_vectors, 'PCA', 2, nout=2)
    coeffs, extra_points = mlab.princomp(average_vectors, nout=2)
    print extra_points.shape
    return extra_points.T[0], extra_points.T[1], coeffs
    
  def dim_reduce_average(self, tables, dims):
    if not dims:
      return [0] * len(tables)
    average_vectors = [t.get_average(*dims) for t in tables]
    return np.average(average_vectors, axis=1)

  def dim_reduce_ks(self, tables, dims):
    if not dims:
      return [0] * len(tables), [0] * len(tables)
    # get distances
    distances = [datatable.ks_distances(tables, dim) for dim in dims]
    # average
    mean_distances = datatable.tables_mean(distances, p=3)
    from mlabwrap import mlab
    Y, eig = mlab.cmdscale(mean_distances.data, nout=2)
    return Y.T[0], Y.T[1], eig
  
  def control_panel(self, tables):
    self.widgets.motion_chart.guess_or_remember(('multicompare motionchart', tables), None)
    self.widgets.average_dims.guess_or_remember(('multicompare average dims', tables), tables[0].dims)
    self.widgets.std_dims.guess_or_remember(('multicompare std dims', tables), [])
    self.widgets.reduce_dims1.guess_or_remember(('multicompare reduce dims', tables), [])
    self.widgets.reduce_dims2.guess_or_remember(('multicompare reduce dims2', tables), [])
    # always revert to pca:
    #self.widgets.reduce_method.guess_or_remember(('multicompare reduce method', tables), ['pca'])
    if not self.widgets.reduce_method.values.choices:
      self.widgets.reduce_method.values.choices = ['pca']
    self.widgets.scroll_tags.guess_or_remember(('multicompare scroll', tables), [])
    self.widgets.id_tags.guess_or_remember(('multicompare id', tables), ['name'])
    # Create the control panel view. This will enable users to choose the dimensions. 
    control_panel_view = stack_lines(
        self.widgets.reduce_method.view('Dimensionality reduction method', self.widgets.apply,
            [('pca', 'PCA over averaged reduce_dimensions1'),
             ('ks', 'Distances are ks-score between histogram of reduce_dimensions1'),
             ('average', 'Averages over reduce dimensions 1 and 2)')], multiple=False),
        self.widgets.reduce_dims1.view('Dimensionality reduction dims 1', self.widgets.apply, options_from_table(tables[0])),    
        self.widgets.reduce_dims2.view('Dimensionality reduction dims 2', self.widgets.apply, options_from_table(tables[0])),    
        self.widgets.average_dims.view('Calculate average for', self.widgets.apply, options_from_table(tables[0])),
        self.widgets.std_dims.view('Calculate std for', self.widgets.apply, options_from_table(tables[0])),
        self.widgets.id_tags.view('Id tags', self.widgets.apply, tables[0].tags.keys()),
        self.widgets.scroll_tags.view('Animation Scroll tags', self.widgets.apply, tables[0].tags.keys()),
        self.widgets.apply.view())
    return control_panel_view
  
  @cache('multicompare')
  def main_view(self, tables):
    comments = []
    col_names = []
    cols = []
    
    # Add id column
    tag_names_for_id = self.widgets.id_tags.get_choices()
    col_names.append('id')
    cols.append([str(t.get_tags(tag_names_for_id)) for t in tables])

    # Add time column
    tag_names_for_time = self.widgets.scroll_tags.get_choices()
    tag_combinations_found = []
    col_names.append('time')
    time_col = []
    for table in tables:
      time_tags = table.get_tags(tag_names_for_time)
      if not time_tags in tag_combinations_found:
        tag_combinations_found.append(time_tags)
    tag_combinations_found.sort(key=multiple_tag_sort_key(tag_names_for_time))
    for table in tables:    
      time_tags = table.get_tags(tag_names_for_time)
      time_col.append(tag_combinations_found.index(time_tags))        
    cols.append(time_col)

    # Add cell count column
    col_names.append('number of cells')
    cols.append([t.num_cells for t in tables])

    # Add the tags columns:
    for tag in tables[0].tags:
      col_names.append(tag)
      tag_col = []
      for table in tables:
        if tag in table.tags:
          tag_col.append(table.tags[tag])
        else:
          tag_col.append('NONE')
      cols.append(tag_col)
    
    # Add dimensionality reduction column
    method = self.widgets.reduce_method.values.choices[0]
    dims1 = self.widgets.reduce_dims1.get_choices()
    dims2 = self.widgets.reduce_dims2.get_choices()
    separated_tables, separated_indexes = self.separate_tables_by_time(tables, time_col)
    final_col1 = [-1] * len(tables)
    final_col2 = [-1] * len(tables)
    for sep_tables, sep_idx in zip(separated_tables, separated_indexes):
      if method == 'average':
        col_reduce1 = self.dim_reduce_average(tables, dims1)
        col_reduce2 = self.dim_reduce_average(tables, dims2)
      elif method == 'pca':
        col_reduce1, col_reduce2, coeffs = self.dim_reduce_pca(tables, dims1)
        if coeffs != None:
          comments.append(', '.join(['%s: %.2f' % (dims1[i], coeffs[0][i]) for i,dim in enumerate(dims1)]))
          comments.append(', '.join(['%s: %.2f' % (dims1[i], coeffs[1][i]) for i,dim in enumerate(dims1)]))
      elif method == 'ks':
        col_reduce1, col_reduce2, eigen = self.dim_reduce_ks(tables, dims1)
        comments.append(','.join(['%.3f' % val for val in eigen[:4]]))
      else:
        raise Exception('Unimplemented dim reduce method')
      for i, idx in enumerate(sep_idx):
        final_col1[idx] = col_reduce1[i]
        final_col2[idx] = col_reduce2[i]
        
    col_names.append('dim reduce 1')
    col_names.append('dim reduce 2')
    cols.append(final_col1)
    cols.append(final_col2)
    
    # Add average columns:
    average_cols = []
    for dim in self.widgets.average_dims.get_choices():
      col_names.append('%s avg' % dim)
      dim_col = [t.get_average(dim) for t in tables]
      cols.append(dim_col)
      average_cols.append(dim_col)

    # Add std columns
    for dim in self.widgets.std_dims.get_choices():
      col_names.append('%s std' % dim)
      dim_col = [t.get_std(dim) for t in tables]
      cols.append(dim_col)
      
    # Add dim-reduce columns
    #distances = datatable.ks_distances(tables, dim)
    if not self.widgets.motion_chart.values.state:
      self.widgets.motion_chart
    return self.widgets.motion_chart.view(col_names, zip(*cols), [str(t) for t in tag_combinations_found], '\n'.join(comments))