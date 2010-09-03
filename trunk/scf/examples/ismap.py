from biology.datatable import DataTable

big, small = big_small_space()

t = load_data_table(choose_file(r'C:\Projects\scf\files\newer\CyTOF54_Tube29_Day2_Dasatinib+Flt3L_curated.fcs_eventnum_Ungated_Dasatinib+Flt3L_Day2_normalized_29_Dasatinib+Flt3L_Singlets.fcs'))

t = t.random_sample(2000)

points = t.get_points(*get_markers('surface'))
extra_points, m = mlab.compute_mapping(points, 'Isomap', 2, nout=2)
print np.shape(m.conn_comp)
print np.shape(extra_points)
print np.shape(t.data)

t2 = DataTable(extra_points, ['lle1', 'lle2'])
with big.add_ax() as ax:
  ax.scatter(extra_points.T[0], extra_points.T[1])
  



