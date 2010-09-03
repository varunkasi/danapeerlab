from biology.datatable import DataTable

t = load_data_table(choose_file(r'C:\Projects\scf\files\newer\CyTOF54_Tube29_Day2_Dasatinib+Flt3L_curated.fcs_eventnum_Ungated_Dasatinib+Flt3L_Day2_normalized_29_Dasatinib+Flt3L_Singlets.fcs'))

t = t.random_sample(2000)

points = t.get_points(*get_markers('surface'))
extra_points = mlab.compute_mapping(points, 'LLE', 2, nout=1)
print np.shape(extra_points)
print np.shape(t.data)

t2 = DataTable(extra_points, ['lle1', 'lle2'])
controls.scatter(t2, ['lle1', 'lle2'], None, None)





'''
p2 = t.add_reduced_dims(
    'PCA', 
    2, 
    get_markers('signal'))

p3 = t.add_reduced_dims(
    'PCA', 
    2, 
    get_markers('surface', 'signal'))


s_1, s_2, s_3, s_4 = four_spaces()

with s_1:
  services.get_ax().set_title(
      'PCA for surface markers')
  x, y, rect, color = controls.gate(      
      'PCA0', 'PCA1', 
      None,
      '110-CD3', p1)[1:5]
  controls.scatter(p1, [x,y], None, color)


with s_2:
  services.get_ax().set_title(
      'PCA for signaling markers')
  x, y, rect, color = controls.gate(      
      'PCA0', 'PCA1', 
      None,
      '176-pCREB', p2)[1:5]
  controls.scatter(p2, [x,y], None, color)


with s_3:
  services.get_ax().set_title(
      'PCA for all markers')
  x, y, rect, color = controls.gate(      
      'PCA0', 'PCA1', 
      None,
      '110_114-CD3', p3)[1:5]
  controls.scatter(p3, [x,y], None, color)
'''