#!/usr/bin/env python
from widget import Widget
from view import View
from view import render
from biology.dataindex import DataIndex
from django.utils.html import linebreaks

class Expander(Widget):
  def __init__(self, id, parent):
    Widget.__init__(self, id, parent)
    self.values.shown = 'shown'

  
  def view(self, collapsed_view, expanded_view, extra_view=View(None, '')):
    html = render('expander.html', {
        'widget_id' : self.id,
        'id' : self._get_unique_id(),
        'collapsed' : collapsed_view.main_html,
        'expanded' : expanded_view.main_html,
        'extra' : extra_view.main_html,
        'shown' : self.values.shown == 'shown'})
    v = View(self, html, ['expander.css'], [])
    v.append_view_files(collapsed_view)
    v.append_view_files(expanded_view)
    return v
