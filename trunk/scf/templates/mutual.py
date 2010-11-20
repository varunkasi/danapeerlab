controls.text_control("""Shows a mutual information matrix, and a plot for the selected dimensions.""")

filename = controls.file_control(None)
mi_samples = int(controls.slider_control(15000, 500, 50000, 'Samples to use for mutual information calculation'))
truncate_cells_mi = controls.picker_control('Yes', ['Yes', 'No'], 'Remove cells with negative values when calculating mutual information') == 'Yes'
truncate_cells = controls.picker_control('Yes', ['Yes', 'No'], 'Remove cells with negative values in the plot') == 'Yes'
disp_full = controls.picker_control('Full Data', ['Full Data', 'Sampled Data'], 'Display full data in plot') == 'Full Data'

t = load_data_table(filename)
t_samp = t.random_sample(mi_samples)
t2 = t_samp.get_mutual_information(ignore_negative_values=truncate_cells_mi)

Space('data', 10, 10)

with Space('data', 0, 0, 6, 10):
  dim1, dim2 = controls.color_table(t2, '115-CD45', '167-CD38')

dim1_idx = t2.dims.index(dim1)
dim2_idx = t2.dims.index(dim2)
controls.text_control(str(t2.data[dim2_idx, dim1_idx]), 'Mutual Information for %s, %s' % (dim1, dim2))

with Space('data', 6, 0, 10, 10):
  if truncate_cells:
    t = t.remove_bad_cells(dim1, dim2)
    t_samp = t_samp.remove_bad_cells(dim1, dim2)
  services.print_text('Number of cells in plot (original data): %d' % t.data.shape[0], weight=700, foreground='black')
  services.print_text('Number of cells in plot (sampled data): %d' % t_samp.data.shape[0], weight=700, foreground='black')
  if disp_full:
    controls.kde2d(t, [dim1, dim2], None)
  else:
    controls.kde2d(t_samp, [dim1, dim2], None)