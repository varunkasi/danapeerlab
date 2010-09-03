from mlabwrap import mlab; from numpy import *
xx = arange(-2*pi, 2*pi, 0.2)
mlab.surf(subtract.outer(sin(xx),cos(xx)))