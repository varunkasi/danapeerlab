import matplotlib
from matplotlib.figure import Figure
from numpy import arange, sin, pi

Space('data', 5, 1)
with Space('data', 3, 0, 4, 0):  
  num1 = number_slider(
      1.3678, 1, 2)
with Space('data', 4, 0, 5, 0):
  num2 = number_slider(0.17966, 0, 1)
t = arange(num2,num1,0.01)
print len(t)
s = sin(2*pi*t)
with Space('data', 0, 0, 3, 0):
  display_graph(t,s,0,2,-1,1)