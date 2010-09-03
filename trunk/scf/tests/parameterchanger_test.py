#!/usr/bin/env python
import unittest
import parameterchanger
from script import Script
import parameterchanger
from parameterchanger import ParameterChangerManager

class TestParameterChanger(unittest.TestCase):

    def setUp(self):
        pass
    def test_changer(self):
      script_str = r'''
x = func1(a,b,c)
func2(1,2,3)'''
      modified_script_str = r'''
x = func1(00,11,22)
func2(1,2,3)'''

      script = Script(script_str)
      manager = ParameterChangerManager(script)
      changer = manager._create_changer_from_pos(0)
      changer.set_parameters(['00', '11', '22'])
      self.assertEqual(script.get_code_as_str(), modified_script_str)
      params = changer.get_parameters()
      self.assertEqual(params[0], '00')
      self.assertEqual(params[1], '11')
      self.assertEqual(params[2], '22')
      

      changer.set_parameters(['a','b', 'c'])
      self.assertEqual(script.get_code_as_str(), script_str)
      params = changer.get_parameters()
      self.assertEqual(params[0], 'a')
      self.assertEqual(params[1], 'b')
      self.assertEqual(params[2], 'c')
      

      
    def test_create_changer_from_pos(self):
      script_str = r'''
func1(
    param1,
    param2,
    func32(adfd),
    func3(1,2,3,4,
        "abcdefg(fsdsd)"),
    func39(1,2,3,4,
        "abc'defg(fsdsd)"),
    [1, 2, 3, 4],
    func4(1,2,3,4,
        "abc'd\"ef'g(fsdsd)"),
    ")))))))",
    '((((((')
func2(1,2,3)'''
      script = Script(script_str)
      manager = ParameterChangerManager(script)
      changer = manager._create_changer_from_pos(0)
      params = changer.get_parameters()
      self.assertEqual(params[0], 'param1')
      self.assertEqual(params[1], 'param2')
      self.assertEqual(params[2], 'func32(adfd)')
      self.assertEqual(params[3], 'func3(1,2,3,4,\n        "abcdefg(fsdsd)")')
      self.assertEqual(params[4], 'func39(1,2,3,4,\n        "abc\'defg(fsdsd)")')
      self.assertEqual(params[5], '[1, 2, 3, 4]')
      self.assertEqual(params[6], 'func4(1,2,3,4,\n        "abc\'d\\"ef\'g(fsdsd)")')
      self.assertEqual(params[7], '")))))))"')
      self.assertEqual(params[8], '\'((((((\'')
      
    def test_annonate_script(self):
      prev_function_names = parameterchanger.PARAMETER_CHANGER_FUNCTIONS
      parameterchanger.PARAMETER_CHANGER_FUNCTIONS = [
          'func_32','func3','func1','func2', 'func4']
      try:
        script_str = r'''
func1(
    param1,
    param2,
    func_32(adfd),
    func3(1,2,3,4,
        "abcdefg(fsdsd)"),
    func39(1,2,3,4,
        "abc'defg(fsdsd)"),
    func4(1,2,3,4,
        "abc'd\"ef'g(fsdsd)"),
    ")))))))",
    '((((((')
func2(1,2,3)'''
        script = Script(script_str)
        manager = ParameterChangerManager(script)
        res = manager.annonate_script()
        annoated_str = r'''
services.set_current_changer(0,func1)(
    param1,
    param2,
    services.set_current_changer(1,func_32)(adfd),
    services.set_current_changer(2,func3)(1,2,3,4,
        "abcdefg(fsdsd)"),
    func39(1,2,3,4,
        "abc'defg(fsdsd)"),
    services.set_current_changer(3,func4)(1,2,3,4,
        "abc'd\"ef'g(fsdsd)"),
    ")))))))",
    '((((((')
services.set_current_changer(4,func2)(1,2,3)'''
        self.assertEqual(res, annoated_str)
      finally:
        parameterchanger.PARAMETER_CHANGER_FUNCTIONS = prev_function_names


if __name__ == '__main__':
    unittest.main()