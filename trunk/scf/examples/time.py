import controls
reload(controls)
import biology.datatable
reload(biology.datatable)

t = load_data_table(choose_file(r'C:\Projects\scf\files\newer\CyTOF54_Tube29_Day2_Dasatinib+Flt3L_curated.fcs_eventnum_Ungated_Dasatinib+Flt3L_Day2_normalized_29_Dasatinib+Flt3L_Singlets.fcs'))
t2 = t.windowed_medians('EventNum', 100, 50)

s_1,s_2 = big_small_space()

with s_1.add_ax() as ax:
  ax.clear()
  ax.set_title(
      'Progression by event number')
  x, y, rect, color = controls.gate(      
      'EventNum', '152-Ki67', 
      [143484.84848484845, 1.6725075528700903, 146515.15151515149, 1.6725075528700903],
      None, t2)[1:5]
  ax.scatter(
      t2.get_cols(x),
      t2.get_cols(y), 1)