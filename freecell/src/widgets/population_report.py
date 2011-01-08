#!/usr/bin/env python
from widget import Widget
from view import View
from view import render
from biology.dataindex import DataIndex
from table import Table
  
class PopulationReport(Widget):
  def __init__(self):
    Widget.__init__(self)
    self.widgets.pair_table = PairTable()

  def view(self):
    def all_pairs(l):
      for i in xrange(len(l)):
        for j in xrange(i):
          yield ((l[i], l[j]))
    index = DataIndex.load(r'c:\cytof54_clustered\cytof54.index')
    t = index.load_table(cluster_name='CD8+ T-cells')
    samples_percent = min((10000. / t.num_cells) * 100, 100)
    num_samples = int((samples_percent/100) * t.data.shape[0])
    truncate_cells_mi = True
    t_samp = t.random_sample(num_samples)
    t_mi = t_samp.get_mutual_information(
        ignore_negative_values=truncate_cells_mi)
    return self.widgets.pair_table.view(all_pairs(t_mi.dims), t_mi)


class PairTable(Widget):
  def __init__(self):
    Widget.__init__(self)
    self.widgets.table = Table()
    
  def view(self, pairs, mi_table):
    lines = []
    for p in pairs:
      i1 = mi_table.dims.index(p[0])
      i2 = mi_table.dims.index(p[1])
      line = []
      line.append(p[0])
      line.append(p[1])
      line.append(mi_table.data[i1, i2])
      lines.append(line)
    return self.widgets.table.view(
        ['Dimension 1', 'Dimension 2', 'Mutual Information'], 
        lines, None, [('Mutual Information', 'desc')])