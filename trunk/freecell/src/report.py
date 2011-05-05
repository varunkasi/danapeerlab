import os
import logging
import cPickle as pickle
import settings
import threading
from widget import ID_SEPERATOR

from widgets.population_report import PopulationReport
from widgets.histogram_report import HistogramReport
from widgets.correlation_report import CorrelationReport
from widgets.population_report import SlicesReport
from widgets.chain import Chain

TEMPLATES = [PopulationReport, HistogramReport, CorrelationReport, SlicesReport, Chain]



class ReportManager(object):
  def __init__(self, path):
    self.path = path
    self.lock = threading.RLock()
  
  @staticmethod
  def base36encode(number, alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    """Convert positive integer to a base36 string."""
    if not isinstance(number, (int, long)):
        raise TypeError('number must be an integer')
 
    # Special case for zero
    if number == 0:
        return alphabet[0]
 
    base36 = ''
 
    sign = ''
    if number < 0:
        sign = '-'
        number = - number
 
    while number != 0:
        number, i = divmod(number, len(alphabet))
        base36 = alphabet[i] + base36
 
    return sign + base36

  def id_to_path(self, id):
    return os.path.join(self.path, '%s.report' % id)
    
  def new_id(self):
    dirlist = os.listdir(self.path)
    files = [d.split('.')[0] for d in dirlist if d.endswith('.report')]
    numbers = [int(f, 36) for f in files]
    numbers += [0]
    return ReportManager.base36encode(max(numbers)+1)
  
  def new(self, template_name, report_name, author):
    global TEMPLATES
    template = [t for t in TEMPLATES if t.__name__ == template_name]
    if not template:
      raise Exception('Unknown template name')
    template = template[0]
    id = self.new_id()
    report = Report(template, report_name, author, id)    
    self.save(report)
    return report
    
  def save(self, report):
    with open(self.id_to_path(report.id), 'w') as f:
      pickle.dump(report, f)
    #print '****SAVED****'
    #print str(report.widget)
    #print '****SAVED****'
  
  def load(self, id):
    filename = self.check(id)
    with open(filename, 'r') as f:
      r = pickle.load(f)
    #print '****LOADED****'
    #print str(r.widget)
    #print '****LOADED****'
    return r 

  def check(self, id):
    filename = self.id_to_path(id)
    if not os.path.exists(filename):
      raise Exception('report %s not found' % id)    
    return filename

class Report(object):
  def __init__(self, widget_type, name, author, id):
    self.id = id
    self.widget = widget_type('base', self)
    self.name = name
    self.author = author
    self.version = 0

  
  def widget_from_id(self, id):
    splitted = id.split(ID_SEPERATOR)
    widget = self.widget 
    for split_item in splitted[1:]:
      if not split_item in widget.widgets:
        raise Exception('could not find id %s, failed at %s. Sub items are: %s' % (id, split_item, widget.widgets.keys()))
      widget = widget.widgets[split_item]
    return widget

  def set_value(self, widget_id, key, val):
    logging.info('setting value for widget %s. %s=%s' % (widget_id, key, val))
    widget = self.widget_from_id(widget_id)
    widget.set_value(key, val)
    #print widget_id
    #print key
    #print self.widgets[widget_id].values[key]
    self.version += 1
  
  # def update_ids(self):
    # self.widgets = {}
    # self.widget_by_class = {}
    # self._update_ids_internal(self.widget)
  
  # def _update_ids_internal(self, widget):
    # list = self.widget_by_class.setdefault(widget.__class__.__name__, [])
    # list.append(widget)
    # widget.id = '%s_%s_%d' % (self.id, widget.__class__.__name__, len(list) - 1)
    # self.widgets[widget.id] = widget
    # for w in widget.widgets.itervalues():
      # self._update_ids_internal(w)
    # widget.report = self
    # if 'on_load' in dir(widget):
      # widget.on_load()
      
  # def register_new_widget(self, new_widget):
    # """ Registers a new widget on runtime (not inside the __init__).
    
    # The caller must also add the widget to its .widgets dictionary.
    # """
    # self._update_ids_internal(new_widget)
    
      

REPORTS = ReportManager(os.path.join(settings.FREECELL_DIR, 'reports'))
