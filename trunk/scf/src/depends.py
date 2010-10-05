#!/usr/bin/env python
import sys
import os
sys.path.insert(0, '../settings')
try:
  import settings
except ImportError:
  print 'Can\'t start, settings file is missing.\nPlease edit scf/settings/_settings.py and save it as settings.py'
  sys.exit()

  
def set_matlab_path():
  def add_path(path):
    from mlabwrap import mlab
    path_str = mlab.path(nout=1)
    paths = path_str.split(';')
    for p in paths: print p
    if not path in paths:
      mlab.path(path_str, path)

  matlab_path = os.path.join(settings.SCF_DIR, 'depends', 'matlab')
  isomap_path = os.path.join(matlab_path, 'isomap')
  dr_path = os.path.join(matlab_path, 'drtoolbox')
  dr_tech_path = os.path.join(dr_path, 'techniques')
  dr_gui_path = os.path.join(dr_path, 'gui')
  add_path(matlab_path)
  add_path(isomap_path)
  add_path(dr_path)
  add_path(dr_tech_path)
  add_path(dr_gui_path)
    
  
  
def set_python_path():
  if sys.platform == 'win32':
    py_dir = os.path.join(settings.SCF_DIR, 'depends', 'win', 'py')
  elif sys.platform =='darwin': # TODO(add 32 bit versions/ raise excpetion)
    py_dir = os.path.join(settings.SCF_DIR, 'depends', 'osx', 'x86_64', 'py')
  else:
    raise Exception('Unsupported platform')
  if not sys.path or not py_dir == sys.path[0]:
    sys.path.insert(0, py_dir)

symlinks = []
def add_symlink(head, tail):
  source = os.path.join(head,tail)
  if not os.path.exists(tail):
    os.symlink(source, tail)
    global symlinks
    symlinks.append(tail)

def set_env_vars():
  if sys.platform == 'win32':
    dll_dir = os.path.join(settings.SCF_DIR, 'depends', 'win', 'dll')
    gtk_dir = os.path.join(dll_dir, 'gtk', 'bin')
    libxml_dir = os.path.join(dll_dir, 'libxml2-2.7.6.win32', 'bin')
    sourceview_dir = os.path.join(dll_dir, 'gtksourceview', 'bin')
    matlab_dll_dir = os.path.join(settings.MATLAB_PATH, 'bin', 'win32')
    old_path = os.getenv('PATH')
    new_path = ';'.join([settings.PYTHON_26_DIR, gtk_dir, libxml_dir, sourceview_dir, matlab_dll_dir]) + ';'
    if not new_path in old_path:
      os.environ['PATH'] =  new_path + old_path
      print 'PATH is now: %s' % os.getenv('PATH')
  if sys.platform == 'darwin':
    # We are trying hard not to set DYLD_LIBRARY_PATH. 
    matlab_dylib_dir = os.path.join(settings.MATLAB_PATH, 'bin', 'maci64')
    # fix for MATLAB 2010:
    add_symlink(matlab_dylib_dir, 'libtbb.dylib')
    add_symlink(matlab_dylib_dir, 'libtbbmalloc.dylib')
    
    #lib_dir = os.path.join(settings.SCF_DIR, 'depends', 'osx', 'lib')
    #old_path = os.getenv('DYLD_LIBRARY_PATH') or ''
    #new_path = ':'.join([matlab_dylib_dir])
    #if not new_path in old_path:
    #  os.environ['DYLD_LIBRARY_PATH'] = old_path + ":" +  new_path
    #print 'DYLD_LIBRARY_PATH is now: %s' % os.getenv('DYLD_LIBRARY_PATH')
      
def fix_path():
  set_env_vars()
  set_python_path()
  print 'Loading matlab...'
  set_matlab_path()
    
if __name__ == '__main__':
  fix_path()
  print 'Creating sub shell'
  if sys.platform == 'win32':
    os.system('cmd')
  if sys.platform == 'darwin':
    os.system('sh')
    
try:
  import gtksourceview2
except ImportError:
  print 'Can\'t start: gtksourceview2 is missing. Make sure you extracted the dependency archives in the right place.'
  sys.exit()
