#!/usr/bin/env python
import sys
import os

PYTHON_26_DIR = r'c:\python26'
INSTALL_DIR = r'C:\Documents and Settings\roy\My Documents\My Dropbox\scf'
MATLAB_PATH = r'C:\MATLAB7'

def fix_path():
  # Todo: add mac support here
  dll_dir = os.path.join(INSTALL_DIR, 'depends', 'win', 'dll')
  gtk_dir = os.path.join(dll_dir, 'gtk', 'bin')
  libxml_dir = os.path.join(dll_dir, 'libxml2-2.7.6.win32', 'bin')
  sourceview_dir = os.path.join(dll_dir, 'gtksourceview', 'bin')
  matlab_dll_dir = os.path.join(MATLAB_PATH, 'bin', 'win32')

  py_dir = os.path.join(INSTALL_DIR, 'depends', 'win', 'py')

  old_path = os.getenv('PATH')
  new_path = ';'.join([PYTHON_26_DIR, gtk_dir, libxml_dir, sourceview_dir, matlab_dll_dir]) + ';' + old_path
  print new_path
  os.environ['PATH'] =  new_path
  sys.path.insert(0, py_dir )

if __name__ == '__main__':
  fix_path()
  print 'PATH is now: %s' % os.getenv('PATH')
  print 'Creating sub shell'
  os.system('cmd')