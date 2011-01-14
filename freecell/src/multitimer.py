import time 
import sys

class MultiTimer(object):
  def __init__(self, num_tasks):
    self.num_tasks = num_tasks
    self.start = time.clock()
    self.task_times = []

    self.prog_bar = '[]'
    self.fill_char = '#'
    self.width = 10
  
  def complete_task(self, message=''):
    self.task_times.append(time.clock())
    self.__update_bar(message)
    if sys.platform.lower().startswith('win'):
      sys.stdout.write('\r')
    else:
      sys.stdout.write(chr(27) + '[A')
    sys.stdout.write(self.prog_bar)
    sys.stdout.flush()
    if len(self.task_times) == self.num_tasks:
      sys.stdout.write('\n')
  
  def __update_bar(self, message):
    percent_done = int(round(len(self.task_times) / float(self.num_tasks) * 100.0))
    all_full = self.width - 2
    num_hashes = int(round((percent_done / 100.0) * all_full))
    self.prog_bar = '[' + self.fill_char * num_hashes + ' ' * (all_full - num_hashes) + ']'
    pct_place = (len(self.prog_bar) / 2) - len(str(percent_done))
    pct_string = '%d%%' % percent_done
    self.prog_bar = self.prog_bar[0:pct_place] + \
        (pct_string + self.prog_bar[pct_place + len(pct_string):])
    
    tasks_done = len(self.task_times)
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