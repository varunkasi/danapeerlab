import matplotlib
from matplotlib.figure import Figure
from numpy import arange, sin, pi

Space('data', 4, 1)
with Space('data', 3, 0, 4, 0):  
  num = number_slider(0.69858, 0, 3)
t = arange(0.0,num,0.01)
s = sin(2*pi*t)
with Space('data', 0, 0, 3, 0):
  display_graph(t,s)