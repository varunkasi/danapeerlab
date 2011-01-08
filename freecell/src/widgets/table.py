#!/usr/bin/env python
from widget import Widget
from view import View
from view import render
from biology.dataindex import DataIndex
from django.utils.html import linebreaks

class Table(Widget):
  def __init__(self):
    Widget.__init__(self)

  def _int_format(value, decimal_points=3, seperator=u'.'):
    value = str(value)
    if len(value) <= decimal_points:
        return value
    # say here we have value = '12345' and the default params above
    parts = []
    while value:
        parts.append(value[-decimal_points:])
        value = value[:-decimal_points]
    # now we should have parts = ['345', '12']
    parts.reverse()
    # and the return value should be u'12.345'
    return seperator.join(parts)
    
  def view(self, col_names, lines, color_col=None, initial_sort=[], decimal_points=3):
    sub_views = []
    conv_lines = []
    # turn lines to html
    for line in lines:
      conv_line = []
      conv_lines.append(conv_line)
      for i in xrange(len(line)):
        if type(line[i]) == View:
          sub_views.append(line[i])
          cell_str = line[i].main_html
        elif type(line[i]) in (float, int):
          cell_str = _int_format(line[i], decimal_points)
        else:
          cell_str = linebreaks(str(line[i]), autoescape=True)
        conv_line.append(cell_str)
    conv_sort = []
    for s in initial_sort:
      dir = 0
      if s[1] == 'asc':
        dir = 0
      elif s[1] == 'desc':
        dir = 1
      else:
        raise Exception('Sort must either be asc or desc')
      conv_sort.append('[%d,%d]' % (col_names.index(s[0]), dir))
    conv_sort = ', '.join(conv_sort)
    conv_sort = '[%s]' % conv_sort
    html = render('table.html', {
        'id' : self._get_unique_id(),
        'col_names': col_names,
        'lines': conv_lines,
        'sort': conv_sort})
    v = View(self, html, ['table.css'], ['jquery.tablesorter.js'])
    for sub in sub_views:
      v.append_view_files(sub)
    return v