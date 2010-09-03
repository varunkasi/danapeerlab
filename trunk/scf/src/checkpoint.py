#!/usr/bin/env python


class Checkpoint:
  """Represents the complete state in a certain point of the script.
  
  A checkpoint enables us to continue running the script from a certain
  point directly, without running the code before the point.
  
  """
  pass
  
class CheckpointManager:
  """Saves a list of checkpoints encoutered while running the script"""
  def __init__(self):
    self.checkpoints = []
  
  def add_checkpoint(self, checkpoint):
    self.checkpoints.append(checkpoint)

  def delete_after(self, checkpoint):
    index = self.checkpoints.index(checkpoint)
    self.checkpoints = self.checkpoints[:index]
	#TODO(daniv): make sure memory is released here.
	