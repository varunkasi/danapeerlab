import numpy as np
from biology.datatable import load_data_table
from biology.markers import Markers
from scipy.stats import gaussian_kde
import time

filename = choose_file(r'C:\Projects\scf\files\newer\CyTOF54_Tube29_Day2_Dasatinib+Flt3L_curated.fcs_eventnum_Ungated_Dasatinib+Flt3L_Day2_normalized_29_Dasatinib+Flt3L_Singlets.fcs')
t = load_data_table(filename)
a,w = t.get_cols(
    Markers.CD3_110_114, Markers.CD4_145)

a = a[100:200]
w = w[100:200]

#indices = [i for i,n in enumerate(a) if a[i] < -20 and w[i] < 4000]

#a = a[indices]
#w = w[indices]
#print len(indices)

min_a = -1000
max_a = max(a)
min_w = -1000
max_w = max(w)

gkde = gaussian_kde((a,w))
x,y = np.mgrid[min_a:max_a:256j, min_w:max_w:256j]
flat_x = x.reshape(1,-1)
flat_y = y.reshape(1,-1)
points = np.append(flat_x,flat_y,axis=0)
print points[0]
logging.info('eval')
ev = gkde.evaluate(points)
logging.info('end_eval')
res = ev.reshape(256, 256)
 

Space('data', 10, 1)
with Space('data', 0, 9, 1, 10):
  num = number_slider(105.83446, 0, 1000)

with Space('data', 0, 0, 1, 9):
  controls.display_image(
      res, origin='lower', 
      extent=[
          flat_y[0,0],
          flat_y[0,-1],
          flat_x[0,0],
          flat_x[0,-1]], 
      interpolation=None)
