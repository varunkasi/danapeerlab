import controls
reload(controls)
s_1, s_2, s_3, s_4 = controls.four_spaces()
filename = choose_file(
  r'C:\Projects\scf\files\newer\CyTOF54_Tube01_Day1_Unstim1_curated.fcs_eventnum_Ungated_Jnstim1_Day1_normalized_1_Unstim1_Singlets.fcs')

t = load_data_table(filename)

with s_1:
  rect = controls.scatter(
      t,
      [str(Markers.CD3_110_114), str(Markers.CD19_142)],
      [-5,-5,10,10],
      '166-IkBalpha')

