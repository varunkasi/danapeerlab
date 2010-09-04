#!/usr/bin/env python
import sys
import os
sys.path.insert(0, '../settings')
import settings

def fix_path():
  # Todo: add mac support here
  dll_dir = os.path.join(settings.SCF_DIR, 'depends', 'win', 'dll')
  gtk_dir = os.path.join(dll_dir, 'gtk', 'bin')
  libxml_dir = os.path.join(dll_dir, 'libxml2-2.7.6.win32', 'bin')
  sourceview_dir = os.path.join(dll_dir, 'gtksourceview', 'bin')
  matlab_dll_dir = os.path.join(settings.MATLAB_PATH, 'bin', 'win32')

  py_dir = os.path.join(settings.SCF_DIR, 'depends', 'win', 'py')

  old_path = os.getenv('PATH')
  new_path = ';'.join([settings.PYTHON_26_DIR, gtk_dir, libxml_dir, sourceview_dir, matlab_dll_dir]) + ';'
  if not new_path in old_path:
     os.environ['PATH'] =  new_path + old_path
     print 'PATH is now: %s' % os.getenv('PATH')
  sys.path.insert(0, py_dir )

if __name__ == '__main__':
  fix_path()
  print 'PATH is now: %s' % os.getenv('PATH')
  print 'Creating sub shell'
  os.system('cmd')