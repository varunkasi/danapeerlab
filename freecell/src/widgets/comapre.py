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

class Compare(Widget):
  """ Compares different statistics across two populations. Background
  population is used as a null distribution.
  """
  
  def __init__(self, id, parent):
    global NETWORKS
    Widget.__init__(self, id, parent)
    self._add_widget('dims', Select)
    self._add_widget('edge_stat', Select)
    self._add_widget('node_stat', Select)
    self._add_widget('apply', ApplyButton)
    self._add_widget('layout', LeftPanel)
    
  def get_inputs(self):
    return ['table', 'background']

  def get_outputs(self):
    return []

  def title(self, short):
   return 'Comparison'

  def run(self, **tables):
    pass

  def view(self, **tables):
    self.widgets.edge_stat.guess_or_remember((tables, 'Compare'), [])
    self.widgets.node_stat.guess_or_remember((tables, 'Compare'), [])
    
    NODE_STATS = ['values']
    EDGE_STATS = []

    control_panel_view = stack_lines(
      self.widgets.edge_stat.view('Edge statistics', self.widgets.apply, sorted(EDGE_STATS)),
      self.widgets.node_stat.view('Node statistics', self.widgets.apply, sorted(NODE_STATS)),
      self.widgets.apply.view())
    
    
    data_tables = [t for t in tables.values() if t]
    networks = [n for n in self.widgets.network.values.choices if n in NETWORKS]
    main_views = []
    for network in networks:
      nodes = set()
      edges = set()
      for graph_entry in NETWORKS[network]:
        nodes.add((graph_entry[0], node_label(graph_entry[0], data_tables, self.widgets.node_stat.values.choices), 0))
        nodes.add((graph_entry[1], node_label(graph_entry[1], data_tables, self.widgets.node_stat.values.choices), 0))
        edges.add((edge_label(graph_entry[0], graph_entry[1], data_tables, self.widgets.edge_stat.values.choices), 0, graph_entry[0], graph_entry[1], True))
      main_views += [self._get_widget('graph_%s' % network).view(nodes, edges)]
      
    main_view = stack_left(*main_views)
    return self.widgets.layout.view(main_view, control_panel_view)
