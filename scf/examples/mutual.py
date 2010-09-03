import biology.datatable
reload(biology.datatable)
import controls
reload(controls)

s = controls.spaces(1)
filename = choose_file(
  r'C:\Projects\scf\files\newer\CyTOF54_Tube01_Day1_Unstim1_curated.fcs_eventnum_Ungated_Jnstim1_Day1_normalized_1_Unstim1_Singlets.fcs')

t = load_data_table(filename)
t = t.random_sample(50000)
t2 = t.get_mutual_information()
#t2.data = np.random.rand(*t2.data.shape)

with s[0]:
  controls.color_table(t2)
