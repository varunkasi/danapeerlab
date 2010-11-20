import biology.datatable
reload(biology.datatable)
import controls
reload(controls)

#s = controls.spaces(2 )
filename = controls.file_control('C:\\Projects\\svn\\danapeerlab\\scf\\1.fcs')
t = load_data_table(filename)
t_sampled = t.random_sample(5)
t2 = t_sampled.get_mutual_information()

Space('data', 10, 10)

with Space('data', 0, 0, 6, 10):
  dim1, dim2 = controls.color_table(t2, '146-CD8', '170-CD90')

with Space('data', 6, 0, 10, 10):
  controls.kde2d(t2, [dim1, dim2], None)