controls.text_control("""Shows plots of PCA components for some of the markers.\nPlots are colored by the specified marker.""")

t = controls.load_table(None, None, None)
color_marker = controls.picker_control(None, t.dims, title='Color marker')

p1 = t.add_reduced_dims(
    'PCA', 
    2, 
    get_markers('surface'))

p2 = t.add_reduced_dims(
    'PCA', 
    2, 
    get_markers('signal'))

p3 = t.add_reduced_dims(
    'PCA', 
    2, 
    get_markers('surface', 'signal'))


s_1, s_2, s_3, s_4 = four_spaces()

with s_1:
  services.get_ax().set_title(
      'PCA for surface markers')
  x, y, color = controls.dim_color_choose(      
      'PCA0', 'PCA1', 
      color_marker, p1)
  controls.scatter(p1, [x,y], None, color)


with s_2:
  services.get_ax().set_title(
      'PCA for signaling markers')
  x, y, color = controls.dim_color_choose(      
      'PCA0', 'PCA1', 
      color_marker, p2)
  controls.scatter(p2, [x,y], None, color)


with s_3:
  services.get_ax().set_title(
      'PCA for all markers')
  x, y, color = controls.dim_color_choose(      
      'PCA0', 'PCA1',      
      color_marker, p3)
  controls.scatter(p3, [x,y], None, color)