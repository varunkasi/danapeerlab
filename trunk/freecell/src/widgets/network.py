#!/usr/bin/env python
import os
from odict import OrderedDict
from widget import Widget
from view import View
from view import render
from view import stack_left
from view import stack_lines
from biology.dataindex import DataIndex
from biology.datatable import combine_tables
from widgets.expander import Expander
from widgets.select import Select
from widgets.graph import Graph
from widgets.leftpanel import LeftPanel
from input import Input
from biology.loaddatatable import load_data_table
from widgets.applybutton import ApplyButton
import settings


NETWORKS = {
    'network1' : [('pP38','pNFkB'), ('pERK1/2', 'pNFkB'), ('IkBalpha', 'pNFkB')]
    }

EDGE_STATS = {
  'corr' : lambda table, dim_x, dim_y: table.get_correlation(dim_x, dim_y),
  'mi' : lambda table, dim_x, dim_y: table.get_mutual_information(dim_x, dim_y) }

def edge_label(dim1, dim2, tables, stats):
  global EDGE_STATS
  edge_labels = []
  for edge_key in sorted(stats):
    vals = '/'.join(['%.2f' % EDGE_STATS[edge_key](t, dim1, dim2) for t in tables])
    edge_labels.append('%s: %s' % (edge_key, vals))
  return '\\n'.join(edge_labels)

def node_label(dim, tables, stats):
  global NODE_STATS
  node_labels = [dim]
  for node_key in sorted(stats):
    vals = '/'.join(['%.2f' % NODE_STATS[node_key](t, dim) for t in tables])
    node_labels.append('%s: %s' % (node_key, vals))
  return '\\n'.join(node_labels)
  
  
NODE_STATS = {
  'avg' : lambda table, dim: table.get_average(dim),
  'std' : lambda table, dim: table.get_std(dim) }

class Network(Widget):
  """ Shows a network of markers with correlation on the edges.
  """
  
  def __init__(self, id, parent):
    global NETWORKS
    Widget.__init__(self, id, parent)
    self._add_widget('network', Select)
    self._add_widget('edge_stat', Select)
    self._add_widget('node_stat', Select)
    self._add_widget('apply', ApplyButton)
    self._add_widget('layout', LeftPanel)
    for network in NETWORKS:
      self._add_widget('graph_%s' % network, Graph)
    self.network_to_widget = {}
    
  def get_inputs(self):
    return ['tables']

  def get_outputs(self):
    return []

  def title(self, short):
   if not self.widgets.network.values.choices:
     return 'Please select a network'
   return ', '.join(self.widgets.network.values.choices)

  def run(self, **tables):
    pass

  def view(self, tables):
    global NETWORKS
    self.widgets.network.guess_or_remember((tables, 'Network'), [])
    self.widgets.edge_stat.guess_or_remember((tables, 'Network'), [])
    self.widgets.node_stat.guess_or_remember((tables, 'Network'), [])
      
    control_panel_view = stack_lines(
      self.widgets.network.view('Network', self.widgets.apply, sorted(NETWORKS.keys())),
      self.widgets.edge_stat.view('Edge statistic to show', self.widgets.apply, sorted(EDGE_STATS.keys())),
      self.widgets.node_stat.view('Node statistic to show', self.widgets.apply, sorted(NODE_STATS.keys())),
      self.widgets.apply.view())
    
    networks = [n for n in self.widgets.network.values.choices if n in NETWORKS]
    main_views = []
    for network in networks:
      nodes = set()
      edges = set()
      for graph_entry in NETWORKS[network]:
        nodes.add((graph_entry[0], node_label(graph_entry[0], tables, self.widgets.node_stat.values.choices), 0))
        nodes.add((graph_entry[1], node_label(graph_entry[1], tables, self.widgets.node_stat.values.choices), 0))
        edges.add((edge_label(graph_entry[0], graph_entry[1], tables, self.widgets.edge_stat.values.choices), 0, graph_entry[0], graph_entry[1], True))
      main_views += [self._get_widget('graph_%s' % network).view(nodes, edges)]
      
    main_view = stack_left(*main_views)
    return self.widgets.layout.view(main_view, control_panel_view)
