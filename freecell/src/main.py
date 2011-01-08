#!/usr/bin/env python
from depends import fix_path
fix_path()
import web
import os
import settings

from widgets.population_report import PopulationReport

urls = (
    '/', 'Report'
    '/images/(.*)', 'Images' #this is where the image folder is located....

)
app = web.application(urls, globals(), autoreload=True)

class Report:
    def __init__(self):
      pass
      
    def GET(self):
      return view.create_page()

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
    # To serve from the static dir:
    os.chdir(settings.FREECELL_DIR)
    
    # Use django default settings:
    from django.conf import settings
    settings.configure()

    report = PopulationReport()
    view = report.view()

    app.run()