#!/usr/bin/env python
import sys
import os
import logging
sys.path.insert(0, '../settings')
try:
  import settings
except ImportError:
  logging.exception('Can\'t start, settings file is missing.\nPlease edit freecell/settings/_settings.py and save it as settings.py')
  sys.exit()

  
def set_matlab_path():
  def add_path(path):
    from mlabwrap import mlab
    path_str = mlab.path(nout=1)
    paths = path_str.split(';')
    if not path in paths:
      mlab.path(path_str, path)

  matlab_path = os.path.join(settings.FREECELL_DIR, 'depends', 'common', 'matlab')
  isomap_path = os.path.join(matlab_path, 'isomap')
  dr_path = os.path.join(matlab_path, 'drtoolbox')
  dr_tech_path = os.path.join(dr_path, 'techniques')
  dr_gui_path = os.path.join(dr_path, 'gui')
  emgm_path = os.path.join(matlab_path, 'emgm') 
  add_path(matlab_path)
  add_path(isomap_path)
  add_path(dr_path)
  add_path(dr_tech_path)
  add_path(dr_gui_path)
  add_path(emgm_path)

def get_platform():
  is_64 = "64 bits" in sys.version
  is_win = sys.platform == 'win32'
  is_mac = sys.platform =='darwin'  
  if is_win and is_64:
    return 'win64'
  elif is_win:
    return 'win32'
  elif is_mac and is_64:
    return 'maci64'
  elif is_mac:
    return 'maci32'
  else:
    raise Exception('Unknown Platform')
  
def set_python_path():
  platform = get_platform()
  common_py_dir = os.path.join(settings.FREECELL_DIR, 'depends', 'common', 'python')
  src_dir = os.path.join(settings.FREECELL_DIR, 'src') 
  py_dir = os.path.join(settings.FREECELL_DIR, 'depends', platform, 'py')
  sys.path.insert(0, common_py_dir)
  sys.path.insert(0, py_dir)
  sys.path.insert(0, src_dir)

symlinks = []
def add_symlink(head, tail):
  source = os.path.join(head,tail)
  if not os.path.exists(tail):
    os.symlink(source, tail)
    global symlinks
    symlinks.append(tail)

def set_env_vars():
  platform = get_platform()
  matlab_dll_dir = os.path.join(settings.MATLAB_PATH, 'bin', platform)
  if sys.platform == 'win32':    
    old_path = os.getenv('PATH')
    new_path = ';'.join([matlab_dll_dir]) + ';'
    if not new_path in old_path:
      os.environ['PATH'] =  new_path + old_path
  if sys.platform == 'darwin':
    # We are trying hard not to set DYLD_LIBRARY_PATH. 
    # fix for MATLAB 2010:   
    add_symlink(matlab_dll_dir, 'libtbb.dylib')   
    add_symlink(matlab_dll_dir, 'libtbbmalloc.dylib')
    
    #lib_dir = os.path.join(settings.SCF_DIR, 'depends', 'osx', 'lib')
    #old_path = os.getenv('DYLD_LIBRARY_PATH') or ''
    #new_path = ':'.join([matlab_dylib_dir])
    #if not new_path in old_path:
    #  os.environ['DYLD_LIBRARY_PATH'] = old_path + ":" +  new_path
    #print 'DYLD_LIBRARY_PATH is now: %s' % os.getenv('DYLD_LIBRARY_PATH')
      
def fix_path(skip_matlab=False):
  set_env_vars()
  set_python_path()
  if not skip_matlab:
    print 'Loading matlab...'
    set_matlab_path()
    
if __name__ == '__main__':
  fix_path()
  print 'Creating sub shell'
  if sys.platform == 'win32':
    os.system('cmd')
  if sys.platform == 'darwin':
    os.system('sh')
