#!/usr/bin/env python
from django.template import Template
from django.template import Context 
import settings
import codecs
import os

def convert_to_html(sub_items): 
  from django.utils.html import escape
  def _int_format(value, decimal_points=3, seperator=u'.'):
    value = str(value)
    if len(value) <= decimal_points:
        return value
    # say here we have value = '12345' and the default params above
    parts = []
    while value:
        parts.append(value[-decimal_points:])
        value = value[:-decimal_points]
    # now we should have parts = ['345', '12']
    parts.reverse()
    # and the return value should be u'12.345'
    return seperator.join(parts)
  
  sub_views = []
  converted = []
  # turn lines to html
  for item in sub_items:   
    if type(item) == View:
      sub_views.append(item)
      cell_str = item.main_html
    elif type(item) in (float, int):
      cell_str = _int_format(item, decimal_points)
    else:
      cell_str = escape(str(item)).replace('\n', '<br />')
    converted.append(cell_str)
  return converted, sub_views

def stack(*sub_items):  
  html_items, sub_views = convert_to_html(sub_items)
  html = ' '.join(html_items)
  ret = View(None, html)
  for v in sub_views:
    ret.append_view_files(v)
  return ret

def left_right(left, right):  
  html = render('left_right.html', {'left':left.main_html, 'right':right.main_html})
  ret = View(None, html)
  ret.append_view_files(left)
  ret.append_view_files(right)
  return ret

def stack_left(*sub_items):  
  html_items, sub_views = convert_to_html(sub_items)
  html = render('stack_left.html', {'items':html_items})
  ret = View(None, html)
  for v in sub_views:
    ret.append_view_files(v)
  return ret

def stack_lines(*sub_items):
  html_items, sub_views = convert_to_html(sub_items)
  html = render('lines.html', {'items':html_items})
  ret = View(None, html)
  for v in sub_views:
    ret.append_view_files(v)
  return ret
  

  

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
    self.css_files = self.css_files.union(other_view.css_files)
    self.js_files = self.js_files.union(other_view.js_files)
    self.images.update(other_view.images)
    
  def create_page(self):
    for filename, img in self.images.iteritems():
      full_filename = os.path.join(settings.FREECELL_DIR, 'static', 'images', filename)
      with open(full_filename, 'wb') as f:
        f.write(img)

    c = Context({
        'css': self.css_files,
        'js': self.js_files,
        'main_html': self.main_html})
    return render('main.html', c)

def render(template_file, context):
    template_path = os.path.join(
        settings.FREECELL_DIR , 'templates', template_file)
    with codecs.open(template_path,'r','utf8') as f:
      template_contents = f.read()
    #print template_contents[0:50]
    t = Template(template_contents)
    return t.render(Context(context))

