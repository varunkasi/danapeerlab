#!/usr/bin/env python
import unittest
import sys
from parameterchanger import ParameterChangerManager
sys.path.insert(0, '../settings')
import settings

class TestDepends(unittest.TestCase):

    def setUp(self):
        pass

    def test_numpy(self):
      import numpy
      
    def test_scipy(self):
      import scipy
    
    def test_gapbuffer(self):
      import gapbuffer
    
    def test_pygtk(self):
      import pygtk
    
    def test_matlabraw(self):
      import settings
      mlabraw_name = 'mlabraw_matlab_%s.mlabraw' % settings.MATLAB_VERSION
      __import__(mlabraw_name)
      mlabraw = sys.modules[mlabraw_name]



if __name__ == '__main__':
    unittest.main()