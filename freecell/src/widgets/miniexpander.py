#!/usr/bin/env python
from widget import Widget
from view import View
from view import render
from biology.dataindex import DataIndex
from django.utils.html import linebreaks

class MiniExpander(Widget):
  def __init__(self, id, parent, shown=True):
    Widget.__init__(self, id, parent)
    if shown:
      self.values.shown = 'shown'
    else:
      self.values.shown = 'hidden'
  
  def view(self, collapsed_view, expanded_view):
    html = render('miniexpander.html', {
        'widget_id' : self.id,
        'id' : self._get_unique_id(),
        'collapsed' : collapsed_view.main_html,
        'expanded' : expanded_view.main_html,
        'shown' : self.values.shown == 'shown'})
    v = View(self, html, [], [])
    v.append_view_files(collapsed_view)
    v.append_view_files(expanded_view)
    return v
