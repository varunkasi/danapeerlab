#!/usr/bin/env python
from django.template import Template
from django.template import Context 
import settings
import os

class View(object):
  def __init__(self, sender, main_html, css_files=[], js_files=[], images={}):
    self.main_html = main_html
    self.css_files = set(css_files)
    self.js_files = set(js_files)
    self.images = images
    
  def append_view(self, other_view):
    self.main_html += other_view.main_html
    self.append_view_files(other_view)
    
  def append_view_files(self, other_view):
    self.css_files.append(other_view.css_fies)
    self.js_files.append(other_view.css_fies)
    self.images.update(other_view.images)
    
  def create_page(self):
    c = Context({
        'css': self.css_files,
        'js': self.js_files,
        'main_html': self.main_html})
    return render('main.html', c)

def render(template_file, context):
    template_path = os.path.join(
        settings.FREECELL_DIR , 'templates', template_file)
    with open(template_path) as f:
      template_contents = f.read()
    t = Template(template_contents)
    return t.render(Context(context))

