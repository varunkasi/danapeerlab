#!/usr/bin/env python

import logging
import controls
from parameterchanger import PARAMETER_CHANGER_FUNCTIONS
from scriptservices import services

def register_control(function_name, changes_params=False):
  def decorator(control_class):
    if changes_params:
      global PARAMETER_CHANGER_FUNCTIONS
      PARAMETER_CHANGER_FUNCTIONS.append(function_name)     
    
    def control_func(*arguments, **keywords):
      global services
      def create_data(data):
        print 'asdfasdasdfasdfasdfasdfasdfsdfffffffffff'
        global services
        # Creating an instance of the control class.
        # The control is expected to have a parameter-less constructor
        data.control = control_class()
        data.control.services = services
        if changes_params:
          data.control.changer = services.get_current_changer()
        # The control can assume it has a services variable, and changer.
        # There should be a control.widget after this function is done.
        data.control.create_widget(*arguments, **keywords)
        data.widget = data.control.widget
      data = services.cache(None, create_data, True) 
      if changes_params and (not data.control.changer or not data.control.changer.is_valid):
        data.control.changer = services.get_current_changer()
      # The control can assume it has a changer when this function is called.
      return data.control.update_widget(*arguments, **keywords)
    
    setattr(controls, function_name, control_func)
    return control_class
  return decorator

def register_changer(func):
  global PARAMETER_CHANGER_FUNCTIONS
  PARAMETER_CHANGER_FUNCTIONS.append(func.func_name)
  return func
