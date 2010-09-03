Space('moshe')
with Space('moshe', 0, 1):
  num = number_slider(3.60215053763,0,5)
with Space('moshe', 1, 1):
  display_text('Number %d' % num)
