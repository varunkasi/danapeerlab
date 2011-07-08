#!/usr/bin/env python
from odict import OrderedDict
from widget import Widget
from view import View
from view import render
from view import convert_to_html
from biology.dataindex import DataIndex
from django.utils.html import linebreaks

class FreecellMenu(Widget):
  def __init__(self, id, parent):
    Widget.__init__(self, id, parent)

  def view(self, report_id):
    html = render('freecellmenu.html', {
        'report_id' : report_id})
    v = View(self, html, [], [])
    return v
