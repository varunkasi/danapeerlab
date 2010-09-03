import random

Space('data', 10, 1)

filename = choose_file(
    r'C:\Projects\scf\files\newer\CyTOF54_Tube29_Day2_Dasatinib+Flt3L_curated.fcs_eventnum_Ungated_Dasatinib+Flt3L_Day2_normalized_29_Dasatinib+Flt3L_Singlets.fcs')
t = load_data_table(filename)

a,w = t.get_cols(
    Markers.CD4_145,
    Markers.CD8_146)


big, small = big_small_space()
with small:
  num = number_slider(231.67849, 0, 400)

#i1 = [i for i,n in enumerate(a) if a[i] > 0 and w[i] > 0]
#a = a[i1]
#w = w[i1]

#i1 = [i for i in xrange(len(a)) if w[i] > 0 and a[i] > 0]
#a = a[i1]
#w = w[i1]

i2 = random.sample(xrange(len(a)), 5000)
a = a[i2]
w = w[i2]



hist, x_edges, y_edges = histogram2d(
    a, 
    w, 
    [
        np.r_[-5:10:256j], 
        np.r_[-5:10:256j]])

with big:
  controls.display_image(
      hist, origin='lower', 
      extent=[
          x_edges[0],
          x_edges[-1],
          y_edges[0],
          y_edges[-1]], 
      interpolation=None,
      cmap=cm.jet)
