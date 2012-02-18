#!/usr/bin/env python
""" Freecell is a flexible infrastructure to generate interactive reports for
data analysis. It currently supports Cytof data. 

Freecell has a low level programmatic interface to generate reports using
Widgets (see src/widget.py). It also has a high level graphical user interface 
that allows creating reports by chaining together modules (see 
src/widgets/chain.py). 

Some of the services Freecell provides are:
  - Interaction with Cytof data (see src/biology/datatable.py)
  - Caching (see caching.py)
  - Functions for plotting data (see src/axes.py)
  - Full matlab integration (see depends/common/python/mlabwrap.py)

"""
import os
import sys
def startup_tests():
  import struct;
  python_bits = ( 8 * struct.calcsize("P"))
  is_win = sys.platform == 'win32'
  is_mac = sys.platform =='darwin'
  has_error = False

  if sys.version_info < (2,7) or python_bits != 32:
    print '*************************************************************************'
    print 'You are running Freecell with the wrong version of Python.'
    print
    print 'Please open the following link to install Python2.7-32bit:'
    if is_mac:
      print 'http://python.org/ftp/python/2.7.2/python-2.7.2-macosx10.3.dmg'
    if is_win:
      print 'http://python.org/ftp/python/2.7.2/python-2.7.2.msi'
    print '*************************************************************************'
    print 
    print 'Your current Python version is: %s' % sys.version_info
    print 'You are using python %d bits.' % python_bits

    return False

  try:
    import numpy
  except:
    print '*************************************************************************'
    print 'numpy seems to be missing, please install it from:'
    if is_mac:
      print 'http://sourceforge.net/projects/numpy/files/NumPy/1.6.1/numpy-1.6.1-py2.7-python.org-macosx10.3.dmg'
    if is_win:
      print 'http://sourceforge.net/projects/numpy/files/NumPy/1.6.1/numpy-1.6.1-win32-superpack-python2.7.exe'
    print '*************************************************************************'
    return False

  try:
    import scipy
  except:
    print '*************************************************************************'
    print 'scipy seems to be missing, please install it from:'
    if is_mac:
      print 'http://sourceforge.net/projects/scipy/files/scipy/0.10.0/scipy-0.10.0-py2.7-python.org-macosx10.3.dmg'
    if is_win:
      print 'http://sourceforge.net/projects/scipy/files/scipy/0.10.0/scipy-0.10.0-win32-superpack-python2.7.exe'
    print '*************************************************************************'
    return False

  try:
    import matplotlib
  except:
    print '*************************************************************************'
    print 'matplotlib seems to be missing, please install it from:'
    if is_mac:
      print 'http://sourceforge.net/projects/matplotlib/files/matplotlib/matplotlib-1.1.0/matplotlib-1.1.0-py2.7-python.org-macosx10.3.dmg'
    if is_win:
      print 'http://sourceforge.net/projects/matplotlib/files/matplotlib/matplotlib-1.1.0/matplotlib-1.1.0.win32-py2.7.exe'
    print '*************************************************************************'
    return False
  return not True
  

if not startup_tests():
  sys.exit()
from depends import fix_path
print 'Fixing Path'
fix_path(True)
print 'Done'
import matplotlib
matplotlib.use('Agg')
import urllib
import logging
import web
import cPickle as pickle
import settings
from time import gmtime, strftime
from widgets.graph import Graph
from report import REPORTS
from reportrunner import ReportRunner
from widgets.population_report import PopulationReport
from widgets.histogram_report import HistogramReport
from widgets.correlation_report import CorrelationReport
from widgets.population_report import SlicesReport
from widgets.chain import Chain
print 'done imports'
urls = (
    '/', 'Main',
    '/new_report', 'NewReport', 
    '/upload_report', 'UploadReport', 
    '/freecell.chain', 'SaveReport', 
    '/set_value', 'SetValue', 
    '/report', 'ShowReport',
    '/url/(.*)', 'UrlReport',
    '/images/(.*)', 'Images' #this is where the image folder is located....
)
app = web.application(urls, globals(), autoreload=False)
runner = ReportRunner()


class Main:
    def __init__(self):
      pass
      
    def GET(self):
      from view import render
      from view import View
      
      reports = [
#          {'name': 'Population Report',
#           'type': 'PopulationReport',
#           'description': 'Function plots for the 15 pairs with the highest mutual information.'},
#          {'name': 'Histogram Report',
#           'type': 'HistogramReport',
#           'description': '1D histograms for markers.'},
          {'name': 'Chain',
           'type': 'Chain',
           'description': 'Create a custom chain.'}]
      return View(None, render('welcome.html', {'reports' : reports})).create_page()


class SetValue(object):
  def __init__(self):
    pass
    
  def GET(self):
    with REPORTS.lock:
      i = web.input(**{'value[]':[]})
      r = REPORTS.load(i.report)
      if 'value' in i:
        r.set_value(i.widget, i.key, i.value)
      else:
        # This will save the values as a list.
        r.set_value(i.widget, i.key, i['value[]'])
      REPORTS.save(r)
      return 'ok'
    #print '***BEFORE SAVE***'
    #print str(r.widget)
    #REPORTS.save(r)
    #r = REPORTS.load(r.id)
    #print '***AFTER SAVE***'
    #print str(r.widget)
    #return 'ok'

class NewReport(object):
  def __init__(self):
    pass

  def GET(self):
    i = web.input()
    if not 'name' in i:
      i.name = strftime('%d %b %Y %H:%M:%S', gmtime())
    if not 'author' in i:
      i.author = 'unknown'
    with REPORTS.lock:
      r = REPORTS.new(i.template, i.name, i.author)
      raise web.seeother('/report?id=%s' % r.id)

class ShowReport(object):
  def __init__(self):
    pass
    
  def GET(self):
    i = web.input()
    with REPORTS.lock:
      r = REPORTS.load(i.id)
    name = 'report requested on %s' % strftime('%d %b %Y %H:%M:%S', gmtime())
    
    if not 'min_version' in i:
      i.min_version  = r.version
    while True:
      if i.id in runner.report_id_to_result:
        report, result = runner.report_id_to_result[i.id]
        if report.version >= i.min_version:
          if isinstance(result, Exception):
            return result
          return result.create_page()
      
      if not i.id in runner.waiting_report_id_to_request:
        runner.add_to_queue(name, i.id)
      
      with runner.working_lock:
        pass

    return 'not_ready'

class Images(object):
  def GET(self,name):
      ext = name.split(".")[-1] # Gather extension

      cType = {
          "png":"images/png",
          "jpg":"image/jpeg",
          "gif":"image/gif",
          "ico":"image/x-icon"            }

      if name in view.images:  # Security
          web.header("Content-Type", cType[ext]) # Set the Header
          view.images[name].seek(0)
          return view.images[name].read() # Notice 'rb' for reading images
      else:
          raise web.notfound()

class SaveReport(object):
  def GET(self):
    i = web.input()
    with REPORTS.lock:
      path = REPORTS.id_to_path(i.id)
      with open(path, 'rb') as f:
        web.header("Content-Type", 'application/octet-stream') # Set the Header
        return f.read()

class UploadReport(object):
  def POST(self):
    i = web.input(myfile={})  
    # A hack to make pickle.load work:
    tmp_file = os.path.join(settings.FREECELL_DIR, 'temp', 'temp_report')
    with open (tmp_file, 'wb') as f:
      f.write(i['myfile'].file.read())
    with open (tmp_file, 'r') as f:              
      base_report = pickle.load(f)
    report_from_file(i, base_report)

  def GET(self):
    i = web.input()
    with REPORTS.lock:
        path = REPORTS.id_to_path(i.id)
        with open(path, 'rb') as f:
          web.header("Content-Type", 'application/octet-stream') # Set the Header
          return f.read()

def report_from_file(i, base_report):
  if not 'name' in i:
    i.name = strftime('%d %b %Y %H:%M:%S', gmtime())
  if not 'author' in i:
    i.author = 'unknown'
  with REPORTS.lock:
    r = REPORTS.new_from_report(base_report, i.name, i.author)
    raise web.seeother('/report?id=%s' % r.id)   

class UrlReport(object):
  def GET(self, url):
    i = web.input()
    chain_file = urllib.urlopen(url)
    base_report = pickle.load(chain_file)
    chain_file.close()
    report_from_file(i, base_report)

  
  
            
if __name__ == "__main__":
  # configuer logging for the application:
  logging.getLogger('').setLevel(logging.DEBUG)
  stream_handler = logging.StreamHandler()
  formatter = logging.Formatter(
      "[%(levelname)s] %(message)s", )
  stream_handler.setFormatter(formatter)
  logging.getLogger('').addHandler(stream_handler)   

  # To serve from the static dir:
  os.chdir(settings.FREECELL_DIR)

  # Use django default settings:
  from django.conf import settings as django_settings
  django_settings.configure()

  print '*************************************************************************'
  print 'Open your browser and type localhost:8080 to access Freecell GUI'
  print '*************************************************************************'
  
  # Start report runner
  runner.start()
  app.run()
  runner.end()