controls.text_control("""Shows histogram for all markers.""")

file_name = controls.file_control(None)
t = load_data_table(file_name)
hide_neg = controls.picker_control('Yes', ['Yes', 'No'], 'Hide negative values') == 'Yes'

markers = t.get_markers('surface')
s = controls.spaces(4, 'Surface Markers')

min_x = None
if hide_neg:
  min_x = 0
  
num_cells = float(t.data.shape[0])
services.print_text('Number of cells: %d' % num_cells, weight=700)

for i in xrange(len(markers)):
  neg_cells = (t.get_cols(markers[i])[0] < 0).sum()
  color='black'
  if neg_cells/num_cells > 0.5:
    color='red'
  services.print_text('Number of positive cells for %s: %d (%d%%)' % (markers[i], num_cells-neg_cells, 100*neg_cells/num_cells), weight=700, foreground=color)

  with s[i].add_ax() as ax:
    ax.figure.text(
        0.5, 0.92,       
        markers[i], 
        horizontalalignment='center',
        size='xx-small')
    controls.kde1d(t, markers[i], min_x)


markers = t.get_markers('signal')
s = controls.spaces_ml(4, 4, 100, 'Signaling Markers')
for i in xrange(len(markers)):
  neg_cells = (t.get_cols(markers[i])[0] < 0).sum()
  color='black'
  if neg_cells/num_cells > 0.5:
    color='red'
  services.print_text('Number of positive cells for %s: %d (%d%% are negative)' % (markers[i], num_cells-neg_cells, 100*neg_cells/num_cells), weight=700, foreground=color)
  with s[i].add_ax() as ax:   
    ax.figure.text(
        0.5, 0.92,       
        markers[i], 
        horizontalalignment='center',
        size='xx-small')
    controls.kde1d(t, markers[i], min_x)
