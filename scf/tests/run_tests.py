#!/usr/bin/env python
import unittest
import logging
import sys
sys.path.insert(0, '../src')
from depends import fix_path
fix_path()
from parameterchanger_test import TestParameterChanger
from script_test import TestScript
from kdtree_test import TestKDTree
from depends_test import TestDepends

if __name__ == '__main__':
    logging.getLogger('').setLevel(logging.DEBUG)
    fix_path()
    unittest.main()
