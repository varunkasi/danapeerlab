#!/usr/bin/env python
from depends import fix_path
fix_path(True)
import matplotlib
matplotlib.use('Agg')
import logging
import web
import os
import settings
from time import gmtime, strftime
from widgets.graph import Graph
from report import REPORTS
from reportrunner import ReportRunner
from widgets.population_report import PopulationReport
from widgets.histogram_report import HistogramReport
from widgets.correlation_report import CorrelationReport
from widgets.population_report import SlicesReport
urls = (
    '/', 'Main',
    '/new_report', 'NewReport', 
    '/set_value', 'SetValue', 
    '/report', 'ShowReport', 
    '/images/(.*)', 'Images' #this is where the image folder is located....
)
app = web.application(urls, globals(), autoreload=False)
runner = ReportRunner()


class Main:
    def __init__(self):
      pass
      
    def GET(self):
      return ''

class SetValue:
    def __init__(self):
      pass
      
    def GET(self):
      with REPORTS.lock:
        i = web.input(**{'value[]':[]})
        r = REPORTS.load(i.report)
        if 'value[]' in i:
          r.set_value(i.widget, i.key, i['value[]'])
        else:
          r.set_value(i.widget, i.key, i.value)
        REPORTS.save(r)
        return 'ok'
      #print '***BEFORE SAVE***'
      #print str(r.widget)
      #REPORTS.save(r)
      #r = REPORTS.load(r.id)
      #print '***AFTER SAVE***'
      #print str(r.widget)
      #return 'ok'

class NewReport:
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

class ShowReport:
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

class Images:
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
    from django.conf import settings
    settings.configure()
    
    # Start report runner
    runner.start()

    #report = SlicesReport()
    #report = PopulationReport()
    #report = CorrelationReport()
    #report = HistogramReport()
    #report = Graph()
    #view = report.view(None, None)    
    #view = report.view()    

    app.run()
    
    runner.end()