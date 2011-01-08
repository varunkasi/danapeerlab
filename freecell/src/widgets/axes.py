#!/usr/bin/env python
from widget import Widget
from view import View
from view import render
from biology.dataindex import DataIndex
from django.utils.html import linebreaks

class Figure(Widget):
  def __init__(self):
    Widget.__init__(self)
    
  def view(self, axes):
    