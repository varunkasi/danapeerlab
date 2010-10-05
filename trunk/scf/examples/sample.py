import biology.unique_sample 
reload (biology.unique_sample)
from biology.unique_sample import unique_sample
from biology.markers import get_markers
from timer import Timer
import controls
reload(controls)

file_name = controls.file_control('C:\\Projects\\svn\\danapeerlab\\scf\\1.fcs')
t = load_data_table(file_name)
points = t.get_points(*t.get_markers('surface'))
with Timer('bla'):
  unique_sample(points, 1)
s = controls.spaces(4, 'Surface Markers')
with s[i].add_ax() as ax:
  controls.kde1d(t, markers[i], 0)
  from mlabwrap import mlab
  bandwidth, density, xmesh = mlab.kde(
      points, 2**12, min_x_, max_x_, nout=3)
  controls.display_graph(xmesh, density)


del unique_sample