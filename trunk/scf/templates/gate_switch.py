controls.text_control("""The first pane allows you to choose a region to zoom.

The second pane shows the zoomed region, and allows you to choose a region to gate.

The gated region is displayed in the two lower panes.""")
t = controls.load_table(None, None, None)

s_1, s_2, s_3, s_4 = controls.four_spaces()



hist_dim = controls.picker_control(None, t.dims, title='Dimension for histogram')

with s_1.add_ax() as ax:
  ax.set_title('Choose a region for zoom')
  rng, x1, y1, rect1 = controls.gate(      
      '191-DNA', '142-CD19', 
      None,
      None, t)[:4]
  t = t.remove_bad_cells(x1,y1)      
  controls.kde2d(t, [x1,y1], None)

with s_2.add_ax() as ax:
  ax.set_title(
      'Zoomed View - choose region to gate')
  rng, x2, y2, rect2 = controls.gate(      
      x1, y1, 
      None,
      None, t)[:4]
  controls.kde2d(t, [x1,y1], rect1)


t2 = t.gate(*rng)

with s_3.add_ax() as ax:
  ax.set_title(
      'Gated View') 
  x3, y3 = controls.dim_choose('152-Ki67', '166-IkBalpha', t)
  controls.kde2d(t2, [x3,y3], None)

with s_4.add_ax() as ax:
  ax.clear()
  ax.set_title('Histogram for %s (in gated rect)' % hist_dim)
  ax.hist(
      t2.get_points(hist_dim), 100)
