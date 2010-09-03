t = load_data_table(choose_file(r'C:\Projects\scf\files\newer\CyTOF54_Tube29_Day2_Dasatinib+Flt3L_curated.fcs_eventnum_Ungated_Dasatinib+Flt3L_Day2_normalized_29_Dasatinib+Flt3L_Singlets.fcs'))

markers = t.get_markers('surface')
s = controls.spaces(4, 'Surface Markers')
for i in xrange(len(markers)):
  with s[i].add_ax() as ax:
    ax.figure.text(
        0.5, 0.92,       
        markers[i], 
        horizontalalignment='center',
        size='xx-small')
    controls.kde1d(t, markers[i], 0)


markers = t.get_markers('signal')
s = controls.spaces_ml(4, 4, 100, 'Signaling Markers')
for i in xrange(len(markers)):
  with s[i].add_ax() as ax:   
    ax.figure.text(
        0.5, 0.92,       
        markers[i], 
        horizontalalignment='center',
        size='xx-small')
    controls.kde1d(t, markers[i], 0)

'''
with s[0].add_ax() as ax:
  ax.clear()
  ax.set_title(
      'Progression by event number')
  x, y, rect, color = controls.gate(
      'EventNum', '191-DNA', 
      None,
      None, t2)[1:5]
  ax.scatter(
      t2.get_cols(x),
      t2.get_cols(y), 1)
  ax.set_ylim(-3,10)

with s[1].add_ax() as ax:
  ax.clear()
  ax.set_title(
      'Progression by event number')
  x, y, rect, color = controls.gate(      
      'EventNum', '144-CD11b', 
      [143484.84848484845, 1.6725075528700903, 146515.15151515149, 1.6725075528700903],
      None, t2)[1:5]
  ax.scatter(
      t2.get_cols(x),
      t2.get_cols(y), 1)
  ax.set_ylim(-3,10)

with s[2]:
  x_marker = controls.gatex(
      '144-CD11b', 'Density', None)[1]
  controls.kde1d(t, x_marker)
'''