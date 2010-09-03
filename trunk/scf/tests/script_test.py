#!/usr/bin/env python
import unittest
from script import Script

class TestScript(unittest.TestCase):
  def test_marks(self):
    script = Script('helllllo')
    script.add_mark(1, gravity='left', name='left_mark')
    script.add_mark(1, gravity='right', name='right_mark')
    self.assertEqual(script.mark_position('left_mark'), 1)
    self.assertEqual(script.mark_position('right_mark'), 1)
    script.insert_text(0, '1234567890')
    self.assertEqual(script.mark_position('left_mark'), 11)
    self.assertEqual(script.mark_position('right_mark'), 11)    
    script.insert_text(12, '1234567890')
    self.assertEqual(script.mark_position('left_mark'), 11)
    self.assertEqual(script.mark_position('right_mark'), 11)    
    script.insert_text(11, '1234567890') 
    self.assertEqual(script.mark_position('left_mark'), 11)
    self.assertEqual(script.mark_position('right_mark'), 21)    
    script.delete_range(11, 13) 
    self.assertEqual(script.mark_position('left_mark'), 11)
    self.assertEqual(script.mark_position('right_mark'), 19)    
    script.delete_range(5) 
    self.assertEqual(script.mark_position('left_mark'), 5)
    self.assertEqual(script.mark_position('right_mark'), 5)    
   
    
    
if __name__ == '__main__':
    unittest.main()