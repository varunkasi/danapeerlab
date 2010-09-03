s_1, s_2, s_3, s_4 = controls.four_spaces()
filename = choose_file(
  r'C:\Projects\scf\files\newer\CyTOF54_Tube01_Day1_Unstim1_curated.fcs_eventnum_Ungated_Jnstim1_Day1_normalized_1_Unstim1_Singlets.fcs')

t = load_data_table(filename)

with s_1:
  services.get_ax().set_title(
      'Region for zoom')
  rng, x1, y1, rect1 = controls.gate(      
      '191-DNA', '142-CD19', 
      [6.5696972589776816, 0.15691527060891253, 7.9632107899443927, 6.23531733209101],
      None, t)[:4]
  t = t.remove_bad_cells(x1,y1)      
  controls.kde2d(t, [x1,y1], None)

with s_2:
  services.get_ax().set_title(
      'Zoomed View - choose region to gate')
  rng, x2, y2, rect2 = controls.gate(      
      x1, y1, 
      [6.8876843191031343, 3.8039565074981709, 7.6994793795901817, 5.9003298407026632],
      None, t)[:4]
  controls.kde2d(t, [x1,y1], rect1)


t2 = t.gate(*rng)

with s_3:
  services.get_ax().set_title(
      'Gated View') 
  x3, y3, rect3 = controls.gate(      
      '152-Ki67', '166-IkBalpha', 
      [1.2993938786917489, 3.0962854980947521, 2.5233559741520768, 4.1346079378727776],
      None, t)[1:4]
  controls.kde2d(t2, [x3,y3], None)

with s_4.add_ax() as ax:
  ax.clear()
  ax.set_title('Histogram for CD38 (in gated rect)')
  ax.hist(
      t2.get_points(str(Markers.CD38_167)), 100)
