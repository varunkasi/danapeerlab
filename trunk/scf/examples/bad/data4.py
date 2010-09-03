import biology.kde
reload(biology.kde)
import numpy as np
import scipy.spatial as ssp
from biology.datatable import load_data_table
from biology.markers import Markers
from biology.kde import kde2d
import time

filename = choose_file(r'C:\Projects\scf\files\newer\CyTOF54_Tube29_Day2_Dasatinib+Flt3L_curated.fcs_eventnum_Ungated_Dasatinib+Flt3L_Day2_normalized_29_Dasatinib+Flt3L_Singlets.fcs')
t = load_data_table(filename)
a,w = t.get_cols(
    Markers.CD3_110_114, Markers.CD4_145)

    
a = a[1000:2000]
w = w[1000:2000]

data_points = np.array([a,w]).T
data_tree = ssp.KDTree(data_points)
x,y = np.mgrid[min(a):max(a):10j, min(w):max(w):10j]
flat_x = x.reshape(1,-1)
flat_y = y.reshape(1,-1)
sample_points = np.append(flat_x,flat_y,axis=0)
logging.info('eval')
start = time.clock()
ev, errs = kde2d(sample_points.T, data_tree, 10)
end = time.clock()
logging.info('end_eval %f' % (end - start))
res = ev.reshape(10,10)
logging.info(max(errs))

Space('data', 10, 1)
with Space('data', 0, 9, 1, 10):
  num = number_slider(1000.0, 0, 1000)

with Space('data', 0, 0, 1, 9):
  controls.display_image(
      res, origin='lower', 
      extent=[
          flat_y[0,0],
          flat_y[0,-1],
          flat_x[0,0],
          flat_x[0,-1]], 
      interpolation=None)
