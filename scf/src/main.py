#!/usr/bin/env python
from depends import fix_path
fix_path()
import sys
import time
import logging
import pygtk
import os.path
pygtk.require('2.0')
import gtk
import gtksourceview2
import gobject
import pango
gobject.threads_init()
from script import Script
from textviewhandler import TextViewHandler
from scriptserver import ScriptServer
from filemanager import FileManager
from spacemanager import SpaceManager
from controlboxmanager import ControlBoxManager
from parameterchanger import ParameterChangerManager
from scriptservices import ScriptServices
from scriptservices import services
#from gtkcodebuffer import CodeBuffer
#from gtkcodebuffer import SyntaxLoader
 
class Gui(object):
  def __init__(self):
    builder = gtk.Builder()
    builder.add_from_file('gui.glade')
    builder.connect_signals(self)
    
    self.window = builder.get_object('window')
    self.toolbutton_run = builder.get_object('toolbutton_run')
    self.toolbutton_abort = builder.get_object('toolbutton_abort')
    self.main_notebook = builder.get_object('main_notebook')
    self.left_notebook = builder.get_object('left_notebook')
    self.templates_menu_item = builder.get_object('imagemenuitem_new_template')
    
    submenu = self.create_templates_menu()
    self.templates_menu_item.set_submenu(submenu)

    
    self.textbuffer_script = gtksourceview2.Buffer()
    lm = gtksourceview2.LanguageManager()
    lang = lm.get_language('python')
    self.textbuffer_script.set_highlight_syntax(True)
    self.textbuffer_script.set_language(lang)    
    #syntax_loader = SyntaxLoader('python')
    #self.textbuffer_script = CodeBuffer(None, syntax_loader)
    self.textbuffer_script.connect('delete-range', 
        self.on_textbuffer_script_delete_range)
    self.textbuffer_script.connect('insert-text', 
        self.on_textbuffer_script_insert_text)
    self.source_view = gtksourceview2.View(self.textbuffer_script)
    self.source_view.set_auto_indent(True)
    self.source_view.set_indent_on_tab(True)
    self.source_view.set_indent_width(2)
    self.source_view.set_insert_spaces_instead_of_tabs(True)
    self.source_view.set_show_line_numbers(True)
    self.source_view.set_smart_home_end(True)
    self.source_view.set_show_line_marks(True)
    scheme = gtksourceview2.style_scheme_manager_get_default().get_scheme(
        'tango')
    self.textbuffer_script.set_style_scheme(scheme)
    self.source_view.set_show_line_marks(True)
    
    
    font_desc = pango.FontDescription('monospace 10')
    if font_desc:
        self.source_view.modify_font(font_desc)
    #self.source_view = gtk.TextView(self.textbuffer_script)
    self.source_view.set_size_request(400, -1)
    
    
    scrolled_win = gtk.ScrolledWindow()
    scrolled_win.show()
    scrolled_win.add(self.source_view)
    self.source_view.show()
    self.left_notebook.append_page(scrolled_win, gtk.Label('Code'))
    
    scrolled_win_control_box = gtk.ScrolledWindow()
    scrolled_win_control_box.show()
    vbox_control = gtk.VBox()
    vbox_control.show()
    
    table_control = gtk.Table(1,1)
    table_control.show()
    
    scrolled_win_control_box.add_with_viewport(table_control)
    self.left_notebook.append_page(scrolled_win_control_box, gtk.Label('Controls'))
    
    self.control_box_manager = ControlBoxManager(table_control)
    self.control_box_manager.add_widget('yo1aaaaaaaaaaaaaaaaaaaaaaaaa11', gtk.Button(label='asdaf'))
    self.control_box_manager.add_widget('yo22', gtk.Button(label='asdfa  sdf'))
    self.control_box_manager.add_widget('yo33333', gtk.Button(label='asdfasdasdasdf'))
  
    self.script = Script()
    self.script.text_inserted += self.on_script_text_inserted
    self.script.range_deleted += self.on_script_range_deleted


    # configuer logging for the application:
    logging.getLogger('').setLevel(logging.DEBUG)
    textview_log = builder.get_object('textview_log')
    gui_handler = TextViewHandler(textview_log)
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s")
    gui_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)
    logging.getLogger('').addHandler(gui_handler)
    logging.getLogger('').addHandler(stream_handler)
    
    
    self.file_manager = FileManager(self.script)
    self.file_manager.current_file_changed += self.on_current_file_changed
    self.file_manager.need_save_changed += self.on_need_save_changed
    
    # TODO(daniv): These are ugly hacks to pervent raising events when the
    # is not the user.
    self.ignore_next_on_textbuffer_script_delete_range = False
    self.ignore_next_on_textbuffer_script_insert_text = False
    
    self.space_manager = SpaceManager(self.main_notebook)
    self.changer_manager = ParameterChangerManager(self.script)
    self.script_server = ScriptServer(self.changer_manager)
    self.script_server.script_started += self.on_script_started
    self.script_server.script_ended += self.on_script_ended
    
    
    
    
    global services
    services.init(self.space_manager, self.changer_manager, self.script_server, self.window.get_toplevel(), self.control_box_manager)
    
    
    
    self._updateWindowTitle()

  def template_menu_activate(self, menu_item, template_name, template_path):
     with open(template_path) as f:
       template = f.read()
     self.on_imagemenuitem_new_activate(None)
     self.script.insert_text(0, template, None)
     
  def create_templates_menu(self):
    current_filename = os.path.realpath(__file__)
    templates_path = os.path.dirname(current_filename) + '/../templates'
    templates_path = os.path.realpath(templates_path)
    templates = [
        ('Quality Control', 'qc.py')]
    templates_menu = gtk.Menu()
    templates_menu.show()
    for t in templates:
      t_path = os.path.join(templates_path, t[1])
      item = gtk.MenuItem(label = t[0])
      item.show()
      item.connect('activate', self.template_menu_activate, t[0], t_path)
      print 'dfasasdasdfasdfasdfasdfasdfyo'
      templates_menu.append(item)
    return templates_menu
  
  def on_toolbutton_run_clicked(self, toolbutton):
    global services
    services._cache = {} # todo(daniv) is thread safe?
    self.space_manager.clear_spaces()
    self.control_box_manager.clear()
    script_name = self.file_manager.current_file
    if not script_name:
      script_name = 'Untitled'
    script_name +='_%.2f' % time.time()
    self.script_server.add_to_queue(script_name)
    self.toolbutton_run.set_sensitive(False)

  def on_toolbutton_abort_clicked(self, toolbutoon):
    try:
      self.script_server.terminate_script()
      self.toolbutton_abort.set_sensitive(False)    
    except:
      logging.exception('could not terminate script')

  def on_window_destroy(self, widget, data=None):
    logging.info('closing script server')
    #while not self.script_server.end_server(1):
    #  self.script_server.terminate_script()
    gtk.main_quit()

  # Script textview events (from GUI to DOM)
  def on_textbuffer_script_delete_range(self, txtbuffer, start, end):
    if not self.ignore_next_on_textbuffer_script_delete_range:
      self.script.delete_range(start.get_offset(), end.get_offset(), self)
    self.ignore_next_on_textbuffer_script_delete_range = False

  def on_textbuffer_script_insert_text(self, txtbuffer, iter, text, length):
    if not self.ignore_next_on_textbuffer_script_insert_text:
      self.script.insert_text(iter.get_offset(), text, self)
    self.ignore_next_on_textbuffer_script_insert_text = False

  # Internal script events (from DOM to GUI)
  # The _gui versions run on the gui thread (and must return false).
  def on_script_text_inserted(self, position, text, sender):
    def on_script_text_inserted_gui(position, text):
      pos_iter =  self.textbuffer_script.get_iter_at_offset(position)
      # TODO(daniv): maybe count here, or think of a less ugly solution
      if text:
        self.ignore_next_on_textbuffer_script_insert_text = True
        self.textbuffer_script.insert(pos_iter, text)
    if sender != self:
      gobject.idle_add(on_script_text_inserted_gui, position, text)

  def on_script_range_deleted(self, start, end, sender):
    def on_script_range_deleted_gui(start, end):
      start_iter =  self.textbuffer_script.get_iter_at_offset(start)
      end_iter =  self.textbuffer_script.get_iter_at_offset(end)
      if start_iter.get_offset() != end_iter.get_offset():
        self.ignore_next_on_textbuffer_script_delete_range = True
        self.textbuffer_script.delete(start_iter, end_iter)
    if sender != self:
      gobject.idle_add(on_script_range_deleted_gui, start, end)

  # Script server events
  def on_script_started(self, script_name):
    def on_script_started_gui(self, script_name):
      self.toolbutton_run.set_visible_horizontal(False)
      self.toolbutton_run.set_visible_vertical(False)
      self.toolbutton_abort.set_visible_horizontal(True)
      self.toolbutton_abort.set_visible_vertical(True)
      self.toolbutton_abort.set_sensitive(True)
    gobject.idle_add(on_script_started_gui, self, script_name)

  def on_script_ended(self, script_name):
    def on_script_ended_gui(self, script_name):
      self.toolbutton_run.set_visible_horizontal(True)
      self.toolbutton_run.set_visible_vertical(True)
      self.toolbutton_abort.set_visible_horizontal(False)
      self.toolbutton_abort.set_visible_vertical(False)
      self.toolbutton_run.set_sensitive(True)
    gobject.idle_add(on_script_ended_gui, self, script_name)

  # Menu events
  
  def _show_save_changes_dialog(self):
    """Returns false if we need to cancel"""
    dia = gtk.Dialog(
        'Save File?',
        self.window.get_toplevel(),
        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
        ('Yes', 1, 
            'No', 2, 
            'Cancel', 3))
    dia.vbox.pack_start(gtk.Label('Do you want to play a game?'))
    dia.show()
    result = dia.run()
    dia.destroy()
    if result == 1:
       self.on_imagemenuitem_save_activate(None)
    return result == 1 or result == 2
#   code for when the users closes the dialog: gtk.RESPONSE_CLOSE
    
    
  def on_imagemenuitem_new_activate(self, menuitem):
    if self.file_manager.need_save and not self._show_save_changes_dialog():
      return
    self.file_manager.new()

  def on_imagemenuitem_open_activate(self, menuitem):
    if self.file_manager.need_save and not self._show_save_changes_dialog():
      return
    dialog = gtk.FileChooserDialog(
        title='Open',
        action=gtk.FILE_CHOOSER_ACTION_OPEN,
        buttons=(
            gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
            gtk.STOCK_OPEN, gtk.RESPONSE_OK))
    dialog.set_default_response(gtk.RESPONSE_OK)
    filter = gtk.FileFilter()
    filter.set_name("Python Scripts")
    filter.add_pattern("*.py")
    dialog.add_filter(filter)
    filter = gtk.FileFilter()
    filter.set_name("All files")
    filter.add_pattern("*")
    dialog.add_filter(filter)
    if dialog.run() == gtk.RESPONSE_OK:
      filename = dialog.get_filename()
      self.file_manager.open(filename)
    dialog.destroy()

  def on_imagemenuitem_quit_activate(self, menuitem):
    pass
  
  def on_imagemenuitem_save_activate(self, menuitem):
    if not self.file_manager.current_file:
      return self.on_imagemenuitem_save_as_activate(menuitem)
    self.file_manager.save()

  def on_imagemenuitem_save_as_activate(self, menuitem):
    dialog = gtk.FileChooserDialog(
        title='Save as',
        action=gtk.FILE_CHOOSER_ACTION_SAVE,
        buttons=(
            gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,
            gtk.STOCK_SAVE,gtk.RESPONSE_OK))
    dialog.set_default_response(gtk.RESPONSE_OK)
    dialog.set_do_overwrite_confirmation(True)
    py_filter = gtk.FileFilter()
    py_filter.set_name("Python Scripts")
    py_filter.add_pattern("*.py")
    dialog.add_filter(py_filter)
    filter = gtk.FileFilter()
    filter.set_name("All files")
    filter.add_pattern("*")
    dialog.add_filter(filter)
    if dialog.run() == gtk.RESPONSE_OK:
      filename = dialog.get_filename()
      #if dialog.get_filter() == py_filter and filename.find('.') == -1:
      #  filename += '.py'
      self.file_manager.save_as(filename)
    dialog.destroy()

  # File manager events  
  def _updateWindowTitle(self):
    program_name = 'editor'
    filename = self.file_manager.current_file
    if filename == None:
      filename = 'Untitled'
    save_str = ''
    if self.file_manager.need_save:
      save_str='*'
    title = '%s%s - %s' % (save_str, filename, program_name)
    #logging.debug('updating window title to %s', title)
    self.window.set_title(title)

  def on_need_save_changed(self):
    def on_need_save_changed_gui(self):
      self._updateWindowTitle()
    gobject.idle_add(on_need_save_changed_gui, self)

  def on_current_file_changed(self):
    def on_current_file_changed(self):
      self._updateWindowTitle()
    gobject.idle_add(on_current_file_changed, self)

if __name__ == "__main__":
  editor = Gui()
  editor.window.show()
  gtk.main()
