#!/usr/bin/env python
from odict import OrderedDict
from widget import Widget
from view import View
from view import render
from biology.dataindex import DataIndex
from django.utils.html import linebreaks

class ApplyButton(Widget):
  def __init__(self, id, parent):
    Widget.__init__(self, id, parent)
    self.values.clicked = False
    self.clicked = False
    self.clicked_once = False

  def on_load(self):
    # set click_once to True in case we are loading an old version
    if not 'clicked_once' in dir(self):
      self.clicked_once = True

    self.clicked = False
    if self.values.clicked:
      self.values.clicked = False
      self.clicked = True
      self.clicked_once = True
  
  def view(self, text='Apply'):  
    html = render('applybutton.html', {
        'text' : text,
        'id' : self._get_unique_id(),
        'widget_id' : self.id})
    v = View(
        self, 
        html, 
        ['ui-lightness/jquery-ui-1.8.11.custom.css'],
        ['jquery.blockUI.js'])
    return v
