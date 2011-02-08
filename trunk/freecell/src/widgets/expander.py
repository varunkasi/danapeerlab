#!/usr/bin/env python
from widget import Widget
from view import View
from view import render
from view import convert_to_html
from biology.dataindex import DataIndex
from django.utils.html import linebreaks

class Expander(Widget):
  def __init__(self):
    Widget.__init__(self)
   
  def view(self, main_title, collapsed, expanded):
    collapsed_html, collapsed_views  = convert_to_html(collapsed)
    expanded_html, expanded_views  = convert_to_html(expanded)
    html = render('expander.html', {
        'id' : self._get_unique_id(),
        'main_title' : main_title,
        'items' : zip(collapsed_html, expanded_html)})
    v = View(self, html, ['expander.css'], ['expand.js'])
    for sub in (collapsed_views + expanded_views):     
      v.append_view_files(sub)
    return v
