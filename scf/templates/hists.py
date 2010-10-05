controls.text_control("""Shows histogram for all markers.""")

file_name = controls.file_control(None)
t = load_data_table(file_name)

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
