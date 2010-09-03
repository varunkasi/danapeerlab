reload(controls)
filename = choose_file(r'C:\Projects\scf\files\newer\CyTOF54_Tube01_Day1_Unstim1_curated.fcs_eventnum_Ungated_Jnstim1_Day1_normalized_1_Unstim1_Singlets.fcs')
t = load_data_table(filename)
a,w = t.get_cols(
    Markers.CD8_146, Markers.CD4_145)


big, small = big_small_space()
with big:
  controls.display_scatter(a,w, 5000)
