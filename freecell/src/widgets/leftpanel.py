#!/usr/bin/env python
from widget import Widget
from view import View
from view import render
from view import convert_to_html

class LeftPanel(Widget):
  def __init__(self, id, parent):
    Widget.__init__(self, id, parent)
   
  def view(self, center, left):
    html = render('leftpanel.html', {
      'id' : self._get_unique_id(),
      'center' : center.main_html,
      'left' : left.main_html})
    v = View(self, html, [], [])
    v.append_view_files(center)
    v.append_view_files(left)
    return v
