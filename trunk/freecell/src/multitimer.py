import time 
import sys

class MultiTimer(object):
  def __init__(self, num_tasks, update_every=1):
    self.num_tasks = num_tasks
    self.update_every = update_every
    
    self.task_times = []
    self.completed = 0

    self.prog_bar = '[]'
    self.fill_char = '#'
    self.width = 10
    if sys.platform == "win32":
      # On Windows, the best timer is time.clock()
      self.timer = time.clock
    else:
      # On most other platforms the best timer is time.time()
      self.timer = time.time
    self.start = self.timer()
  
  def complete_task(self, message=''):
    self.task_times.append(self.timer())
    if len(self.task_times) > 5:
      self.task_times = self.task_times[-5:]
    self.completed += 1
    if self.completed % self.update_every == 0:
      self.__update_bar(message)
      sys.stdout.write('\r')
      sys.stdout.write(self.prog_bar)
      sys.stdout.flush()
    if self.completed == self.num_tasks:
      sys.stdout.write('\n')
  
  def __update_bar(self, message):
    percent_done = int(round(self.completed / float(self.num_tasks) * 100.0))
    all_full = self.width - 2
    num_hashes = int(round((percent_done / 100.0) * all_full))
    self.prog_bar = '[' + self.fill_char * num_hashes + ' ' * (all_full - num_hashes) + ']'
    pct_place = (len(self.prog_bar) / 2) - len(str(percent_done))
    pct_string = '%d%%' % percent_done
    self.prog_bar = self.prog_bar[0:pct_place] + \
        (pct_string + self.prog_bar[pct_place + len(pct_string):])
    
    tasks_done = self.completed
    tot_time = self.task_times[-1] - self.start
    if tasks_done == 1:
      last_time = tot_time
    else:
      last_time = self.task_times[-1] - self.task_times[-2]
    
    self.prog_bar += '%d/%d [Avg: %.2fs, Last: %.2fs, Left:%.0fs] %s' % (
        tasks_done,
        self.num_tasks,
        tot_time / tasks_done,
        last_time,
        (tot_time / tasks_done) * (self.num_tasks - tasks_done),
        message)
    self.prog_bar = self.prog_bar[:79]