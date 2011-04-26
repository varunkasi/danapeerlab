#!/usr/bin/env python
from odict import OrderedDict
from widget import Widget
from view import View
from view import render
from view import convert_to_html
from biology.dataindex import DataIndex
from django.utils.html import linebreaks

class ApplyButton(Widget):
  def __init__(self, id, parent):
    Widget.__init__(self, id, parent)

  def view(self):
    html = render('applybutton.html', {
        'id' : self._get_unique_id(),
        'widget_id' : self.id})
    v = View(
        self, 
        html, 
        ['ui-lightness/jquery-ui-1.8.11.custom.css'],
        ['jquery-ui-1.8.11.custom.min.js'])
    return v
