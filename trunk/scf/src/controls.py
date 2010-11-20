 #!/usr/bin/env python
import logging
import random
import pygtk
import gtk
import gobject
import threading
import matplotlib
import matplotlib.cm as cm
from matplotlib.figure import Figure
# uncomment to select /GTK/GTKAgg/GTKCairo
#from matplotlib.backends.backend_gtk import FigureCanvasGTK as FigureCanvas
from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas
#from matplotlib.backends.backend_gtkcairo import FigureCanvasGTKCairo as FigureCanvas
# or NavigationToolbar for classic
#from matplotlib.backends.backend_gtk import NavigationToolbar2GTK as NavigationToolbar
#from matplotlib.backends.backend_gtkagg import NavigationToolbar2GTKAgg as NavigationToolbar
import parameterchanger
from controlsmanager import register_control
from controlsmanager import register_changer
from scriptservices import services
from scriptservices import create_sync_wrapper
from scriptservices import Space
from parameterchanger import PARAMETER_CHANGER_FUNCTIONS
import numpy as np
import controls
import biology.markers
from biology.markers import Markers
from biology.datatable import DimRange
import biology.markers

def file_dialog(title):
  dialog = gtk.FileChooserDialog(
  title=title,
  action=gtk.FILE_CHOOSER_ACTION_OPEN,
  buttons=(
      gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
      gtk.STOCK_OPEN, gtk.RESPONSE_OK))
  dialog.set_default_response(gtk.RESPONSE_OK)
  filename = None
  if dialog.run() == gtk.RESPONSE_OK:
    filename = dialog.get_filename()
  dialog.destroy()   
  return filename

@register_changer
def file_control(filename, title='Filename'):
  def cache(data):
    def button_click(button, changer):
        new_file = file_dialog(title)
        if new_file:
          changer.set_parameter(0, repr(new_file))
          services.replay_script()
    data.button = gtk.Button(label=filename)
    data.button.set_size_request(250,-1)
    data.button.connect('clicked', button_click, services.get_current_changer())
    data.title_label = services.add_widget_in_control_box(title, data.button)
  data = services.cache(None, cache, False, True)
  data.title_label.set_markup('<b>%s</b>' % title)
  if filename:
    data.button.set_label(filename)
  else:
    data.button.set_label('No file selected')
    #raise Exception('Missing filename')
  return filename


@register_changer
def text_control(text, title='Description'):
  def cache(data):
    data.text_label = gtk.Label(text)
    data.text_label.set_alignment(0, 0)
    data.text_label.set_size_request(250,-1)
    data.text_label.set_line_wrap(True)
    data.title_label = services.add_widget_in_control_box(title, data.text_label)
  data = services.cache(None, cache, False, True)
  data.title_label.set_markup('<b>%s</b>' % title)
  data.text_label.set_label(text)
  return text

#@register_changer
#def multi_picker_control

@register_changer
def slider_control(val, min_val, max_val, title='Number'):
  def cache(data):
    def button_release(range, event, changer):
      changer.set_parameter(0, range.get_value())
      services.replay_script()
    data.slider = gtk.HScale()
    data.slider.set_value_pos(gtk.POS_LEFT)
    data.slider.set_range(min_val, max_val)
    data.slider.connect(
        'button-release-event', button_release, services.get_current_changer())
    #data.slider.set_size_request(150,-1)
    data.title_label = services.add_widget_in_control_box(title, data.slider)
  data = services.cache(None, cache, False, True)
  data.title_label.set_markup('<b>%s</b>' % title)
  data.slider.set_value(val)  
  return val
  
@register_changer
def picker_control(choice, options, title='Choice'):
  def cache(data):
    def changed(combobox, changer):
      changer.set_parameter(0, repr(combobox.get_active_text()))
      services.replay_script()
    data.box = gtk.combo_box_new_text() 
    for option in options:
      data.box.append_text(option)
    data.handler_id = data.box.connect(
        'changed', changed, services.get_current_changer())
    #data.slider.set_size_request(150,-1)
    data.title_label = services.add_widget_in_control_box(title, data.box)
  data = services.cache(None, cache, False, True)
  data.title_label.set_markup('<b>%s</b>' % title)
  if choice in options:
    data.box.handler_block(data.handler_id)
    data.box.set_active(options.index(choice))
    data.box.handler_unblock(data.handler_id)
  return choice


def spaces_ml(rows_per_page, cols_per_page, how_many, name='data'):
  Space(name, rows_per_page, cols_per_page)
  spaces = []
  for i in xrange(how_many):
    row = i / rows_per_page
    col = i % cols_per_page
    spaces.append(Space(name, row, col, row+1, col+1))
  return spaces

def spaces(how_many, name='data'):
  Space(name, how_many, how_many)
  spaces = []
  for i in xrange(how_many):
    for j in xrange(how_many):
      spaces.append(Space(name, i, j, i+1, j+1))
  return spaces


def four_spaces(name='data'):
  Space(name, 2, 2)
  space_1 = Space(name, 0, 0, 1, 1)
  space_2 = Space(name, 0, 1, 1, 2)
  space_3 = Space(name, 1, 0, 2, 1)
  space_4 = Space(name, 1, 1, 2, 2)
  return space_1, space_2, space_3, space_4
  
def big_small_space(name='data'):
  Space(name, 10, 1)
  big = Space(name, 0, 0, 9, 1)
  small = Space(name, 9, 0, 10, 1)
  return big, small
 
def fix_axis():
  ax = services.get_ax()
  
  

class Gater(object):
  def __init__(self, ax, all_markers, rect_range, color_label, only_x=False, no_selection=False):
    self.all_markers = all_markers
    self.ax = ax
    self.color_label = color_label
    self.rect = None
    self.press = None
    self.ignore_next_on_press = False
    self.only_x = only_x
    self.no_selection = no_selection
    if not self.no_selection:
      self.renew_rect(rect_range)
    self.connect()
    global services
    self.changer = services.get_current_changer()
    
  def renew_rect(self, rect_range):
    if self.rect in self.ax.patches:
      self.ax.patches.remove(self.rect)
    if rect_range:
      if self.only_x:
        ymin, ymax = self.ax.get_ylim()
        self.rect = matplotlib.patches.Rectangle(
            (rect_range[0], 0),
            rect_range[1] - rect_range[0], 
            ymax - ymin,
            alpha=0.5, fc='white', zorder=10000)
      else:
        self.rect = matplotlib.patches.Rectangle(
            (rect_range[0], rect_range[1]),
            rect_range[2] - rect_range[0], 
            rect_range[3] - rect_range[1],
            alpha=0.5, fc='white', zorder=10000)
    else:
      self.rect = matplotlib.patches.Rectangle(
          (0,0), 0, 0, alpha=0.5, fc='white')
    self.ax.add_patch(self.rect)
    self.rect.figure.canvas.draw()
      
  def connect(self):
    'connect to all the events we need'
    self.cidpress = self.ax.figure.canvas.mpl_connect(
        'button_press_event', self.on_press)
    self.cidrelease = self.ax.figure.canvas.mpl_connect(
        'button_release_event', self.on_release)
    self.cidmotion = self.ax.figure.canvas.mpl_connect(
        'motion_notify_event', self.on_motion)        
    self.cidpick = self.ax.figure.canvas.mpl_connect(
        'pick_event', self.on_pick)
            
  def on_pick(self, event):
    #logging.debug('allpick')
    if event.artist == self.color_label and not self.only_x:
      # luckily the on_pick is called before the on_press so we can 
      # do this ugly hack (this is because on_pick doesn't work with labels)
      self.ignore_next_on_press = True
      selected_marker = choose_marker(None, self.all_markers, False)
      if selected_marker:
        self.changer.set_parameter(3, repr(selected_marker))
        services.replay_script(self)

  def on_press(self, event):
    'on button press we will see if the mouse is over us and store some data'
    #logging.info('press')
    if self.ignore_next_on_press:
      self.ignore_next_on_press = False
      #logging.info('ignored press')
    elif self.rect and event.inaxes == self.rect.axes:
      self.rect.set_xy((event.xdata, event.ydata))
      self.rect.set_width(0)
      self.rect.set_height(0)
      self.press = event.xdata, event.ydata
      self.rect.figure.canvas.draw()
    else:
      width, height = self.ax.figure.canvas.get_width_height()
      #logging.info('ccc' + str(width) +' ' + str(height))
      #logging.info('ccdc' + str(event.x) +' ' + str(event.y))
      #logging.info('ccdc' + str(event.x/ width) +' ' + str(event.y / height))
      is_x = event.y/height < 0.2 and event.x/width > 0.2
      is_y = event.y/height > 0.2 and event.x/width < 0.2
      if is_x or (not self.only_x and is_y):
        selected_marker = choose_marker(None, self.all_markers, False)
      if selected_marker:
        if is_x:
          self.changer.set_parameter(0, repr(selected_marker))
        elif is_y:
          self.changer.set_parameter(1, repr(selected_marker))
        services.replay_script(self)

  def on_motion(self, event):
    'on motion we will move the rect if the mouse is over us'
    if self.press is None: return
    if event.inaxes != self.ax: return
    if self.no_selection: return
    #logging.info('motion')
    xpress, ypress = self.press
    dx = abs(event.xdata - xpress)
    new_x = min(xpress, event.xdata)
    if self.only_x:
      new_y = 0
      ymin, ymax = self.ax.get_ylim()
      dy = ymax - ymin
    else:
      new_y = min(ypress, event.ydata)
      dy = abs(event.ydata - ypress)
    
    self.rect.set_xy((new_x, new_y))
    self.rect.set_width(dx)
    self.rect.set_height(dy)
    self.rect.figure.canvas.draw()
    
    x_min = self.rect.get_x()
    y_min = self.rect.get_y()
    x_max = x_min + self.rect.get_width()
    y_max = y_min + self.rect.get_height()
    if self.only_x:
      self.changer.set_parameter(2, str([x_min, x_max]))
    else:
      self.changer.set_parameter(2, str([x_min, y_min, x_max, y_max]))

  def on_release(self, event):
    'on release we reset the press data'
    if self.press:
      self.press = None
      self.rect.figure.canvas.draw()
      services.replay_script(self)
    

  def disconnect(self):
    'disconnect all the stored connection ids'
    self.ax.figure.canvas.mpl_disconnect(self.cidpress)
    self.ax.figure.canvas.mpl_disconnect(self.cidrelease)
    self.ax.figure.canvas.mpl_disconnect(self.cidmotion)
    self.ax.figure.canvas.mpl_disconnect(self.cidpick)
    if self.rect and self.rect in self.ax.patches:
      self.ax.patches.remove(self.rect)

@register_changer
def dim_choose(x_marker, y_marker, datatable=None):
  ax = services.get_ax()
  def gate_cache(data):
    ax = services.get_ax()
    all_markers = None
    if datatable:
      all_markers = datatable.dims
    data.gater = Gater(ax, all_markers, None, None, False, True)
  data = services.cache((ax), gate_cache, True, False)  
  
  ax.set_ylabel(y_marker)    
  ax.set_xlabel(x_marker)
  return (x_marker, y_marker)

#def set_labels(x_label, y_label, color_label): \
#  def cache(data):
#    data.text =  ax.figure.text(0.01, 0.01, '', picker=1, size='x-small')
#  ax.set_ylabel(x_label)    
#  ax.set_xlabel(x_label)
#  data.text.set_text('Color: %s' % str(color_label))

@register_changer
def dim_color_choose(x_marker, y_marker, color_marker, datatable=None):
  ax = services.get_ax()
  def gate_cache(data):
    ax = services.get_ax()
    all_markers = None
    if datatable:
      all_markers = datatable.dims
    data.text =  ax.figure.text(0.01, 0.01, '', picker=1, size='x-small')
    data.gater = Gater(ax, all_markers, None, data.text, False, True)
  data = services.cache((ax), gate_cache, True, False)    
  ax.set_ylabel(y_marker)    
  ax.set_xlabel(x_marker)
  data.text.set_text('Color: %s' % str(color_marker))
  return (x_marker, y_marker, color_marker)

 
@register_changer      
def gate(x_marker, y_marker, rect, color_marker=None, datatable=None): 
  ax = services.get_ax()
  def gate_cache(data):
    ax = services.get_ax()
    all_markers = None
    if datatable:
      all_markers = datatable.dims
    data.text =  ax.figure.text(0.01, 0.01, '', picker=1, size='x-small')
    data.gater = Gater(ax, all_markers, rect, data.text)
  data = services.cache((ax), gate_cache, True, False)  
  ax.set_xlabel(x_marker)
  ax.set_ylabel(y_marker)
  if color_marker:
    data.text.set_text('Color: %s' % str(color_marker))
  
  data.gater.renew_rect(rect)
  
  if not rect:
    rect = [None, None, None, None]
  dim_ranges = [
      DimRange(x_marker, rect[0], rect[2]),
      DimRange(y_marker, rect[1], rect[3])]

  #if title:
  #  data.ax.set_title(title)
  return (dim_ranges, x_marker, y_marker, rect, color_marker)

@register_changer      
def gatex(x_marker, y_text, rect, datatable=None): 
  ax = services.get_ax()
  def gate_cache(data):
    ax = services.get_ax()
    all_markers = None
    if datatable:
      all_markers = datatable.dims
    data.gater = Gater(ax, all_markers, rect, None, True)
  data = services.cache((ax), gate_cache, True, False)  
  
  ax.set_xlabel(x_marker)
  ax.set_ylabel(y_text)  
  data.gater.renew_rect(rect)
  
  if not rect:
    rect = [None, None]
  dim_ranges = [DimRange(x_marker, rect[0], rect[1])]

  return (dim_ranges, x_marker, rect)

class Picker(object):
  def __init__(self, ax, dims):
    self.ax = ax
    self.changer = services.get_current_changer()
    self.cidrelease = self.ax.figure.canvas.mpl_connect(
        'button_release_event', self.on_release)
    self.dims = dims
 
  def on_release(self, event):
    #logging.info('x:%s, y:%s' % (event.xdata, event.ydata))
    #logging.info('x:%s, y:%s' % (np.round(event.xdata), np.round(event.ydata)))    
    dim_x = self.dims[int(np.round(event.xdata))]
    dim_y = self.dims[int(np.round(event.ydata))]
    self.changer.set_parameter(1, repr(dim_x))
    self.changer.set_parameter(2, repr(dim_y))
    services.replay_script(self)     

@register_changer
def color_table(datatable, dim_x=None, dim_y=None):
  def cache(data):
    ax = services.get_ax()
    Picker(ax, datatable.dims)  
  ax = services.get_ax()
  services.cache(ax, cache, True, False)
  #print dim_x
  #print dim_y
  display_matrix(datatable.data, cmap=cm.jet)
  ax.set_xticks(np.arange(len(datatable.dims)))
  ax.set_yticks(np.arange(-1, len(datatable.dims)+1))
  ax.set_xticklabels(datatable.dims)
  ax.set_yticklabels([''] + datatable.dims)
  ylabels = ax.yaxis.get_ticklabels()
  xlabels = ax.xaxis.get_ticklabels()
  
  for i in xrange(len(ylabels)):
    x_index = i-1
    ylabels[i].set_fontsize('xx-small')
    if ylabels[i].get_text() == dim_y:
      ylabels[i].set_weight('bold')
    else:
      ylabels[i].set_weight('normal')
    if x_index >=0 and x_index < len(xlabels):
      xlabels[x_index].set_fontsize('xx-small')
      if ylabels[i].get_text() == dim_x :
        xlabels[x_index].set_weight('bold')
      else:
        xlabels[x_index].set_weight('normal')
      xlabels[x_index].set_rotation(90)

  #ax.update_params(left=0, bottom=0)
  ax.figure.canvas.draw()

  return (dim_x, dim_y)
  #ax.grid(which='major', color='r', linestyle='-', linewidth=1)

def scatter(datatable, markers, range=None, color_marker=None, min_cells_per_bin=1, no_bins=512j, *args, **kargs):
  def cached(data):
    cols = datatable.get_cols(*markers)
    if not range:
      fixed_range = [
          min(cols[0]),
          min(cols[1]),
          max(cols[0]),
          max(cols[1])]    
    else:
      fixed_range = range
      
    hist, data.x_edges, data.y_edges = np.histogram2d(
        cols[0], 
        cols[1], 
        [
            np.r_[fixed_range[0]:fixed_range[2]:no_bins], 
            np.r_[fixed_range[1]:fixed_range[3]:no_bins]])
    data.final_hist = np.sign(np.subtract(
        np.clip(np.abs(hist), min_cells_per_bin, np.inf),
        min_cells_per_bin))

    if color_marker:
      data.is_colored = True
      weights = datatable.get_cols(color_marker)[0]     
      weighted_hist, x_edges, y_edges = np.histogram2d(
          cols[0], 
          cols[1], 
          [
              np.r_[fixed_range[0]:fixed_range[2]:no_bins], 
              np.r_[fixed_range[1]:fixed_range[3]:no_bins]], None, False, weights)
      data.colored_hist = np.multiply(
          np.true_divide(weighted_hist, hist), data.final_hist)
    else:
      data.is_colored = False

  data = services.cache((datatable, markers, range, color_marker, args, kargs), cached, True, False)  

  if data.is_colored:
    data_to_draw = data.colored_hist
    cmap = cm.jet
  else:
    data_to_draw = data.final_hist
    cmap = cm.gist_yarg
    
  controls.display_image(
      data_to_draw.T, origin='lower', 
      extent=[
          data.x_edges[0],
          data.x_edges[-1],
          data.y_edges[0],
          data.y_edges[-1]], 
      interpolation=None,
      cmap=cmap, *args, **kargs)

def kde1d(datatable, marker, min_x=None, max_x=None):
  def cached(data):
    if type(datatable) is np.ndarray:    
      points = datatable
    else:
      points = datatable.get_cols(marker)[0]
    range = np.max(points) - np.min(points)
    min_x_ = min_x
    max_x_ = max_x
    if min_x == None:
      min_x_ = np.min(points) - range / 10
    if max_x == None:
      max_x_ = np.max(points) + range / 10
    
    from mlabwrap import mlab
    data.bandwidth, data.density, data.xmesh = mlab.kde(
        points, 2**12, min_x_, max_x_, nout=3)
    data.xmesh = data.xmesh[0]
    #print 'den:' + str(np.shape(data.density[0]))
    data.density = data.density.T[0]
  if type(datatable) is np.ndarray:    
    data = services.cache((None, marker, min_x, max_x), cached, False, False)
  else:
    data = services.cache((datatable, marker, min_x, max_x), cached, False, False)
  display_graph(data.xmesh, data.density)
    
  
def kde2d(datatable, markers, range, title=None, *args, **kargs):
  ax = services.get_ax()
  #markers = biology.markers.normalize_markers(markers)
  def cached(data):
    from mlabwrap import mlab
    a, w = datatable.get_cols(markers[0], markers[1])
    if range:
      min_a = range[0]
      max_a = range[2]
      min_w = range[1]
      max_w = range[3]
    else:
      min_w = min(w)
      max_w = max(w)
      min_a = min(a)
      max_a = max(a)
    points = datatable.get_points(markers[0], markers[1])
    bandwidth,data.density, data.X, data.Y = mlab.kde2d(
        points, 256,        
        [[min_a, min_w]],
        [[max_a, max_w]],
        nout=4)
        
#    if X[0,0] > X[0,-1]: 
#      X = X[:,::-1]
#      density = density[::-1,:]
#    if Y[0,0] > Y[-1,0]:  
#      Y = Y[::-1,:]
#      density = density[:,::-1]  
  data = services.cache((datatable, markers, range, args, kargs), cached, True, False)  
  if title:
    data.ax.set_title(title)
  ax.set_xlabel(str(markers[0]) + '   ')
  ax.set_ylabel(str(markers[1]) + '   ')
  display_image(
    data.density,
    origin='lower', 
    extent=[
        data.X[0,0],
        data.X[0,-1],
        data.Y[0,0],
        data.Y[-1,0]],
        interpolation=None, *args, **kargs)
  ax.figure.canvas.draw()
  
    
def display_text(text):
  def create_data(data):
    data.widget = gtk.Label()
    services.add_widget_in_current_location(data.widget)
  data = services.cache(None, create_data, True, True)
  gobject.idle_add(data.widget.set_text, text)

def display_image(Z, extent, *args, **kargs):
  def create_data(data):
    #logging.info('yoooo')
    data.ax = services.get_ax()
    #from matplotlib.colors import LightSource
    #ls = LightSource(azdeg=0,altdeg=65)
    #rgb = ls.shade(Z, cm.jet)
    data.image = data.ax.imshow(Z, extent=extent, *args, **kargs)
    data.ax.set_aspect('auto')
  
  def update_gui(data):
    #from matplotlib.colors import LightSource
    #ls = LightSource(azdeg=0,altdeg=65)
    #rgb = ls.shade(Z, cm.jet)   
    data.image.set_extent(extent)
    data.image.set_data(Z)
    #print data.image.get_clim()
    data.image.autoscale()
    #print data.image.get_clim()
    data.ax.figure.canvas.draw()

  data = services.cache((args, kargs), create_data, True, False)
  update_gui(data)
  #gobject.idle_add(update_gui, data)

def display_matrix(Z, *args, **kargs):
  def create_data(data):
    data.ax = services.get_ax()
    data.image = data.ax.matshow(Z, *args, **kargs)
  
  def update_gui(data):
    data.image.set_data(Z)
    data.image.autoscale()
    data.ax.figure.canvas.draw()
    
  data = services.cache((Z.shape, args, kargs), create_data, True, False)
  update_gui(data)

    
def display_graph(x_vals, y_vals, x_min=None, x_max=None, y_min=None, y_max=None):
  def create_data(data):
    data.ax = services.get_ax()
    data.line, = data.ax.plot([0], [0])
    data.predefined_axes = False
    if not None in (x_min, x_max, y_min, y_max):
      data.predefined_axes = True
      data.ax.set_xlim(x_min, x_max)
      data.ax.set_ylim(y_min, y_max)
  def update_widget(data):
    #if self.line:
    #  self.line.remove()
    #self.line, = self.ax.plot(x_vals, y_vals)
    data.line.set_xdata(x_vals)
    data.line.set_ydata(y_vals)
    if not data.predefined_axes:
      data.ax.set_xlim(min(x_vals), max(x_vals))
      data.ax.set_ylim(min(y_vals), max(y_vals))
    #self.ax.plot(x_vals, y_vals)
    data.ax.figure.canvas.draw()
    #draw?
  data = services.cache((x_min, x_max, y_min, y_max), create_data, True, False)
  gobject.idle_add(update_widget, data)
 
@register_control('number_slider', True) 
class NumberSliderGui(object):
  def create_widget(self, num, min_val, max_val, inc=None):
    self.widget = gtk.HScale()
    self.widget.set_draw_value(True)
    self.widget.set_digits(5)
    #self.widget.connect('change-value', self.value_changed)
    self.should_sample = False
    self.widget.connect('button-press-event', self.button_press)
    self.widget.connect('button-release-event', self.button_release)

  def button_press(self, widget, event):
    #logging.debug('SCROLL_START')
    self.should_sample = True
    gobject.timeout_add(30, self.update_script)

  def button_release(self, widget, event):
    #logging.debug('SCROLL_END')
    self.should_sample = False
   
  def update_script(self):
    self.changer.set_parameter(0, self.widget.get_value())
    self.services.replay_script(self)  
    return self.should_sample  

  def update_widget(self, num, min_val, max_val, inc=None):
    if self.services.get_script_sender() == self:
      return num
    if not inc:
      inc = max_val - min_val / 100
    gobject.idle_add(self.widget.set_range, min_val, max_val)
    gobject.idle_add(self.widget.set_increments, inc, inc * 5)
    gobject.idle_add(self.widget.set_value, num)
    return num

@register_changer
def choose_marker(marker=None, all_markers=None, change_param=True):
  global services
  if marker != None:
    return marker
  markers_box = gtk.combo_box_new_text()
  if not all_markers:
    all_markers = biology.markers.get_marker_names()
  for name in all_markers:
      markers_box.append_text(name)
  markers_box.show()
  
  dia = gtk.Dialog('Marker Picker',
               services.get_top_widget(),
               gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,  #binary flags or'ed together
               (gtk.STOCK_OK, gtk.RESPONSE_OK, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
  dia.vbox.pack_start(gtk.Label('Pick A marker'))
  dia.vbox.pack_start(markers_box)
  dia.show()
  result = dia.run()
  dia.destroy()
  if result == gtk.RESPONSE_OK:
    #res = biology.markers.marker_from_name(markers_box.get_active_text())
    res = markers_box.get_active_text()
    if change_param:
      services.get_current_changer().set_parameter(0, repr(res))
    return res
  elif result == gtk.RESPONSE_CANCEL:
    return None
    


@register_changer
def choose_file(filename=None):
  if filename != None:
    return filename
  def run_dialog_gui():
    dialog = gtk.FileChooserDialog(
    title='Choose file',
    action=gtk.FILE_CHOOSER_ACTION_OPEN,
    buttons=(
        gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
        gtk.STOCK_OPEN, gtk.RESPONSE_OK))
    dialog.set_default_response(gtk.RESPONSE_OK)
    filename = None
    if dialog.run() == gtk.RESPONSE_OK:
      filename = dialog.get_filename()
    dialog.destroy()   
    return filename

  synced_run_dialog_gui = create_sync_wrapper(run_dialog_gui)
  filename = synced_run_dialog_gui()
  if not filename:
    raise Exception('No file chosen')
  global services
  services.get_current_changer().set_parameter(0, "r'%s'" % filename)
  return filename

  
    