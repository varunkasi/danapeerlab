#!/usr/bin/env python
import unittest
import parameterchanger
from script import Script
import parameterchanger
from parameterchanger import ParameterChangerManager
from biology.kdtree import Rectangle

class TestKDTree(unittest.TestCase):

    def setUp(self):
        pass

    def test_rectangle_intersect(self):
      r1 = Rectangle([1,2,3], [4,5,6])
      r2 = Rectangle([10,20,30], [40,50,60])
      self.assertEqual(r1.intersect(r2), None)
      self.assertEqual(r2.intersect(r1), None)
      r3 = Rectangle([2,2,2], [3,3,7])
      self.assertEqual(tuple(r1.intersect(r3).mins), (2, 2, 3))
      self.assertEqual(tuple(r1.intersect(r3).maxes), (3, 3, 6))
      self.assertEqual(tuple(r3.intersect(r1).mins), (2, 2, 3))
      self.assertEqual(tuple(r3.intersect(r1).maxes), (3, 3, 6))
      
    def test_rectangle_contains(self):
      r1 = Rectangle([1,2,3], [4,5,6])
      point1 = (2,3,4)
      point2 = (2,3,7)
      self.assertEqual(tuple(r1.contains([point1])), (True,))
      self.assertEqual(tuple(r1.contains([point2])), (False,))
      self.assertEqual(tuple(r1.contains((point1, point2))), (True, False))


if __name__ == '__main__':
    unittest.main()