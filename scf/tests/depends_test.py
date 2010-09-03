#!/usr/bin/env python
import unittest
import parameterchanger
from script import Script
import parameterchanger
from parameterchanger import ParameterChangerManager

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
    
    def test_matlabwrap(self):
      import mlabraw


if __name__ == '__main__':
    unittest.main()