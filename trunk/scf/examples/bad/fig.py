import matplotlib
from matplotlib.figure import Figure
from numpy import arange, sin, pi

Space('data', 4, 1)
with Space('data', 0, 3, 0, 4):  
  num = number_slider(0.698181818182, 0, 3)
fig = Figure(figsize=(5,4), dpi=100)
ax = fig.add_subplot(111)
t = arange(0.0,num,0.01)
s = sin(2*pi*t)
ax.plot(t,s)
with Space('data', 0, 0, 0, 3):  
  display_figure(fig)
