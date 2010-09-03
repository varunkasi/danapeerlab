mode = 'LLE'
res = 100j
t = load_data_table(choose_file(r'C:\Projects\scf\files\newer\CyTOF54_Tube29_Day2_Dasatinib+Flt3L_curated.fcs_eventnum_Ungated_Dasatinib+Flt3L_Day2_normalized_29_Dasatinib+Flt3L_Singlets.fcs'))
t = t.random_sample(1000)

p1 = t.add_reduced_dims(
    mode, 
    2, 
    get_markers('surface'))

p2 = t.add_reduced_dims(
    mode, 
    2, 
    get_markers('signal'))

p3 = t.add_reduced_dims(
    mode, 
    2, 
    get_markers('surface', 'signal'))


s_1, s_2, s_3, s_4 = four_spaces()

with s_1:
  services.get_ax().set_title(
      'Isomap for surface markers')
  x, y, rect, color = controls.gate(      
      mode+'0', mode+'1', 
      [-0.51019805704783749, -0.18468234803386349, -0.12089094521581778, -0.08358457210086595],
      '110_114-CD3', p1)[1:5]
  controls.scatter(p1, [x,y], None, color,
      no_bins=res)


with s_2:
  services.get_ax().set_title(
      'Isomap for signaling markers')
  x, y, rect, color = controls.gate(      
      mode+'0', mode+'1', 
      None,
      color, p2)[1:5]
  controls.scatter(p2, [x,y], None, color,
      no_bins=res)


with s_3:
  services.get_ax().set_title(
      'Isomap for all markers')
  x, y, rect, color = controls.gate(      
      mode+'0', mode+'1', 
      [-39.573435629862971, 35.714673791573787, -36.406933481837171, 38.749354771283024],
      color, p3)[1:5]
  controls.scatter(p3, [x,y], None, color,
      no_bins=res)