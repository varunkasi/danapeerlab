import controls
reload(controls)
t = load_data_table(choose_file(r'C:\Projects\scf\files\newer\CyTOF54_Tube29_Day2_Dasatinib+Flt3L_curated.fcs_eventnum_Ungated_Dasatinib+Flt3L_Day2_normalized_29_Dasatinib+Flt3L_Singlets.fcs'))

p1 = t.add_reduced_dims(
    'PCA', 
    2, 
    get_markers('surface'))

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
      '153-pMAPKAPK2', p1)[1:5]
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
      [-14.245368869503492, 10.753268501734926, -14.245368869503492, 10.883000876361489],
      '110_114-CD3', p3)[1:5]
  controls.scatter(p3, [x,y], None, color)