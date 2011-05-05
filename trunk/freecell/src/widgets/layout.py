#!/usr/bin/env python
from widget import Widget
from view import View
from view import render
from view import convert_to_html

class Layout(Widget):
  def __init__(self, id, parent):
    Widget.__init__(self, id, parent)
   
  def view(self, center, west=None, north=None, east=None, south=None):
    def convert_to_html_or_none(sub_item):
      if sub_item == None:
        return None, []
      html,views = convert_to_html([sub_item])
      html = ''.join(html)
      return html,views
    
    center_html, center_views  = convert_to_html_or_none(center)
    west_html, west_views  = convert_to_html_or_none(west)
    north_html, north_views  = convert_to_html_or_none(north)
    east_html, east_views  = convert_to_html_or_none(east)
    south_html, south_views = convert_to_html_or_none(south)
    html = render('layout.html', {
        'id' : self._get_unique_id(),
        'center_html' : center_html,
        'west_html' : west_html,
        'north_html' : north_html,
        'east_html' : east_html,
        'south_html' : south_html})
    v = View(self, html, ['layout-default-latest.css'], ['jquery.layout-latest.js'])
    for sub in sum([center_views, west_views, north_views, east_views, south_views], []):
      v.append_view_files(sub)
    return v
