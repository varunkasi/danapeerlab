#!/usr/bin/env python
from odict import OrderedDict
from widget import Widget
from view import View
from view import render
from view import convert_to_html
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
    
  def view(self, header_names, lines, vertical_header=None, initial_sort=[], decimal_points=3):
    sub_views = []
    conv_lines = []
    # turn lines to html
    for line in lines:
      conv_line, sub_sub_views = convert_to_html(line)
      conv_lines.append(conv_line)
      sub_views += sub_sub_views
      
    conv_sort = []
    for s in initial_sort:
      dir = 0
      if s[1] == 'asc':
        dir = 0
      elif s[1] == 'desc':
        dir = 1
      else:
        raise Exception('Sort must either be asc or desc')
      conv_sort.append('[%d,%d]' % (header_names.index(s[0]), dir))
    conv_sort = ', '.join(conv_sort)
    conv_sort = '[%s]' % conv_sort
    data = OrderedDict()
    for i in xrange(len(header_names)):
      data[header_names[i]] = [l[i] for l in conv_lines]
    html = render('table.html', {
        'vertical_header' : vertical_header,
        'data' : data,
        'id' : self._get_unique_id(),
        'header_names': header_names,
        'lines': conv_lines,
        'sort': conv_sort})
    v = View(self, html, ['table.css'], ['jquery.tablesorter.js'])
    for sub in sub_views:
      v.append_view_files(sub)
    return v