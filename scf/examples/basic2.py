Space('moshe', 10, 10)

with Space('moshe', 0, 0):
  display_text('hello')

with Space('moshe', 0, 1):
  display_text('hello2')

with Space('moshe', 0, 2):
  display_text('hello3')

with Space('moshe', 1, 0):
  num = number_slider(
      3.02817,0,5)

with Space('moshe', 2, 0):
  num2 = number_slider(
      3.23944,0,5)

with Space('moshe', 1, 1, 5, 5):
  display_text('Number %f' % (num*num2))