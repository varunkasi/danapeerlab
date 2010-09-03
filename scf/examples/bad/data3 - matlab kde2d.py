import numpy as np
from biology.datatable import load_data_table
from biology.markers import Markers
from scipy.stats import gaussian_kde
import time
from mlabwrap import mlab

filename = choose_file(
  r'C:\Projects\scf\files\newer\CyTOF54_Tube01_Day1_Unstim1_curated.fcs_eventnum_Ungated_Jnstim1_Day1_normalized_1_Unstim1_Singlets.fcs')
t = load_data_table(filename)
a,w = t.get_cols(
    str(Markers.CD8_146), str(Markers.CD4_145))

i1 = [i for i,n in enumerate(a) if a[i] > 0 and w[i] > 0]
a = a[i1]
w = w[i1]

#mlab.hist(a,500, nout=0)
#mlab.scatter(a,w,0.1)

min_a = -5
max_a = 10
min_w = -5
max_w = 10

points = np.append(
    a.reshape(1,-1),
    w.reshape(1,-1),
    axis=0).T

logging.info('eval')
bandwidth,density,X,Y = mlab.kde2d(
    points,
    256,
    [[max_a, max_w]],
    [[min_a, min_w]],
    nout=4)
logging.info('end_eval')
#mlab.contour(X,Y,density, 30)
big, small = big_small_space()
#with Space('data', 0, 9, 1, 10):
#  num = number_slider(105.83446, 0, 1
density[::-1,::-1]
if X[0,0] > X[0,-1]: 
  X = X[:,::-1]
  density = density[::-1,:]
if Y[0,0] > Y[-1,0]:  
  Y = Y[::-1,:]
  density = density[:,::-1]    
  
with big:
  controls.display_image(
      density, origin='lower', 
      extent=[
          X[0,0],
          X[0,-1],
          Y[0,0],
          Y[-1,0]],
      interpolation=None)
