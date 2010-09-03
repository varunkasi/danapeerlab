#!/usr/bin/env python

import re
import logging

def compile_script(source):
  """Compiles a script.
  
  In the future this will use cache to optimize compilation time.
  
  """
  #logging.info('compiling code')
  compiled = compile(source, 'blah', 'exec')
  #logging.info('compilation done')
  return compiled
