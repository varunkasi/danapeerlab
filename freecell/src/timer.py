import time 

class Timer(object):
  def __init__(self, name):
    self.name = name

  def __enter__(self):
    self.start = time.clock()
  
  def __exit__(self, type, value, traceback):
    self.end = time.clock()
    elapsed = self.end - self.start
    print '%s took %f seconds' % (self.name, elapsed)