s_1, s_2, s_3, s_4 = controls.four_spaces()
filename = choose_file(
  r'C:\Projects\scf\files\newer\CyTOF54_Tube01_Day1_Unstim1_curated.fcs_eventnum_Ungated_Jnstim1_Day1_normalized_1_Unstim1_Singlets.fcs')

t = load_data_table(filename)
with s_1:
  x_dim, y_dim, rect = controls.gate( 
    '152-Ki67',
    '153-pMAPKAPK2',
    [3.0235446122074867, -0.084223618772238495, 5.4536561594155861, 5.6060924810141142],
    None)[1:4]
  controls.kde2d(t, [x_dim, y_dim], None)

with s_2:
  x_dim, y_dim, rect = controls.gate( 
    '152-Ki67',
    '153-pMAPKAPK2',
    [3.0235446122074867, -0.084223618772238495, 5.4536561594155861, 5.6060924810141142],
    None)[1:4]
  controls.kde2d(t, [x_dim, y_dim], None)

with s_3:
  x_dim, y_dim, rect = controls.gate( 
    '145-CD4',
    '111-CD3',
    [8.0955414862079067, 7.8339815432236053, 8.1343014228997976, 7.8339815432236053],
    None)[1:4]
  controls.kde2d(t, [x_dim, y_dim], None)

with s_4:
  x_dim, y_dim, rect = controls.gate( 
    '152-Ki67',
    '153-pMAPKAPK2',
    [7.1743359791706096, 7.4161165685426136, 7.293569770291735, 7.4161165685426136],
    None)[1:4]
  controls.kde2d(t, [x_dim, y_dim], None)
