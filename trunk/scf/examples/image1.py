import controls
reload(controls)

from scipy import *
from pylab import *
Space('data', 10, 1)
with Space('data', 9, 0, 10, 1):
  num = number_slider(0.86288, 0, 10)
x,y = ogrid[-1.:1.:.01, -1.:1.:.01]
z = 3*y*(3*x**2-y**2)/4 + .5*cos(num*pi * sqrt(x**2 +y**2) + arctan2(x,y))
print z.shape

with Space('data', 0, 0, 9, 1):
  controls.display_image(
      z, origin='lower', extent=[-1,1,-1,1], 
      interpolation='nearest')