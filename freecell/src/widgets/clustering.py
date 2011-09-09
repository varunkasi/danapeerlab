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

class ClusterModule(WidgetWithControlPanel):
  """ Base class for clustering modules. Inheritors should implement:
   - method_name() - returns the name of the clustering method
   - cluster(datatable) - returns a list of datables which are clusters of the given table.
   - _control_panel(tables) - custom controls
  """
  def __init__(self, id, parent):
    WidgetWithControlPanel.__init__(self, id, parent)
    self._add_widget('cluster_dims', Select)
    self._add_widget('apply', ApplyButton)
  
    
  def title(self, short):
    """Title for the module, the short version is displayed in menus, 
    the long version is displayed in the expander title.
    """
    
    return '%s over %s' % (self.method_name(), self.widgets.cluster_dims.get_choices()) 
      
  def get_inputs(self):
    """ Returns the names input list.
    """
    return ['tables']
    
  def get_outputs(self):
    """ Returns the output list.
    """
    return ['tables']
  
  def run(self, tables):
    """ Does the clustering.
    """
    ret = []
    timer = MultiTimer(len(tables))
    for table in tables:
      clusters = self.cluster(table)
      for i, cluster in enumerate(clusters):
        cluster.tags = table.tags.copy()
        cluster.name = '%s %d %s' % (self.method_name(), i, table.name)
        ret.append(cluster)
      timer.complete_task(table.name)  
    return {'tables':ret}
    
  def control_panel(self, tables):
    self.widgets.cluster_dims.guess_or_remember(('cluster dims', tables), [])
    # Create the control panel view. This will enable users to choose the dimensions. 
    control_panel_view = stack_lines(
        self.widgets.cluster_dims.view('Clustering dimensions', self.widgets.apply, options_from_table(tables[0])),
        self._control_panel(tables),
        self.widgets.apply.view())
    return control_panel_view
  
  def get_cluster_dims(self):
    return self.widgets.cluster_dims.get_choices()
  
  def main_view(self, tables):
    pass

class ClusterModuleWithNumClusters(ClusterModule):
  def __init__(self, id, parent):
    ClusterModule.__init__(self, id, parent)
    self._add_widget('num_clusters', Input)
  
  def _control_panel(self, tables):
    self.widgets.num_clusters.guess_or_remember(('cluster num', tables), '5')
    return self.widgets.num_clusters.view('Number of clusters', self.widgets.apply)
    
  def get_num_clusters(self):
    return int(self.widgets.num_clusters.value_as_float())

class KMeansClusterer(ClusterModuleWithNumClusters):
  def __init__(self, id, parent):
    ClusterModuleWithNumClusters.__init__(self, id, parent)
    
  def method_name(self):
    return 'k-means'
  
  def cluster(self, table):
    return table.kmeans(self.get_cluster_dims(), self.get_num_clusters())
