from datetime import timedelta
from timeit import default_timer as timer
from time import strftime, localtime

# https://github.com/CornDoggSoup/python-date-time/blob/main/TaskTimer.py

class TaskTimer:
  '''A utility class for capturing a task's processing time.
  * Uses `localtime()` for real-world start and stop times. 
  * Uses the default `perf_counter()` for relative elapsed time.
  '''
  def __init__(self):

    self.start_timer = None
    self.time_start = None
    self.stop_timer = None
    self.time_stop = None
    self.time_elapsed = None
    self.timer_results = {'time_start': None, 'time_stop': None, 'time_elapsed': None}

  def __repr__(self):
    '''Return a string representation of the timer.
    '''
    return self.timer_results

  def start(self):
    '''Start the timer and capture the start time.
    '''
    self.start_timer = timer()
    self.time_start = strftime("%Y-%m-%d %H:%M:%S", localtime())
    self.timer_results['time_start'] = self.time_start

  def stop(self):
    '''Stop the timer and capture the stop time.
    '''
    self.stop_timer = timer()
    self.time_stop = strftime("%Y-%m-%d %H:%M:%S", localtime())
    self.timer_results['time_stop'] = self.time_stop

  def elapsed(self):
    '''Calculates the elapsed time.
    '''
    elapsed = timedelta(seconds=self.stop_timer-self.start_timer)
    elapsed = elapsed - timedelta(microseconds=elapsed.microseconds)
    self.time_elapsed = str(elapsed)
    self.timer_results['time_elapsed'] = self.time_elapsed

  def print(self):
    '''Prints timer results to console.
    '''
    for k in self.timer_results:
      print(f'{k}: {self.timer_results[k]}')

