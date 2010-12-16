controls.text_control("""Shows a mutual information matrix, and a plot for the selected dimensions.""")

t = controls.load_table(None, None, None)
default_sample = min((10000. / t.num_cells) * 100, 100)
mi_samples = controls.slider_control(default_sample, 0, 100, 'Percent of samples to use for mutual information calculation')
mi_num_samples = int((mi_samples/100) * t.data.shape[0])
controls.text_control(str(mi_num_samples), 'Number of cells to sample')
norm_axis = controls.picker_control('None', ['None', 'X', 'Y'], 'Normalization axis in density plot')
norm_thresh = controls.slider_control(-3, -10, 0, 'Min density for rows/columns when normalizing (log scale)')
if norm_axis == 'None':
  norm_axis = 'None'
else:
  norm_axis = norm_axis.lower()
truncate_cells_mi = controls.picker_control('Yes', ['Yes', 'No'], 'Remove cells with negative values when calculating mutual information') == 'Yes'
truncate_cells = controls.picker_control('Yes', ['Yes', 'No'], 'Remove cells with negative values in the plot') == 'Yes'
disp_full = controls.picker_control('Full Data', ['Full Data', 'Sampled Data'], 'Display full data in plot') == 'Full Data'


t_samp = t.random_sample(mi_num_samples)
t2 = t_samp.get_mutual_information(ignore_negative_values=truncate_cells_mi)


Space('data', 10, 10)

with Space('data', 0, 0, 6, 10):
  dim1, dim2 = controls.color_table(t2, '103-Viability', '142-CD19')

dim1_idx = t2.dims.index(dim1)
dim2_idx = t2.dims.index(dim2)
controls.text_control(str(t2.data[dim2_idx, dim1_idx]), 'Mutual Information for %s, %s' % (dim1, dim2))

if truncate_cells:
  t = t.remove_bad_cells(dim1, dim2)
  t_samp = t_samp.remove_bad_cells(dim1, dim2)
services.print_text('Number of cells in plot (original data): %d' % t.data.shape[0], weight=700, foreground='black')
services.print_text('Number of cells in plot (sampled data): %d' % t_samp.data.shape[0], weight=700, foreground='black')
if disp_full:
  table_to_show = t
else:
  table_to_show = t_samp

with Space('data', 6, 0, 10, 5):
  controls.kde2d(table_to_show, [dim1, dim2], None, norm_axis=norm_axis, norm_axis_thresh=10**norm_thresh)

with Space('data', 6, 5, 10, 10):
  controls.scatter(table_to_show, [dim1, dim2], no_bins=256j)