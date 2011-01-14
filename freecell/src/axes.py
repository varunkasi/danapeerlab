import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from scriptservices import services 
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.cm as cm


def new_axes(x_size=256, y_size=256):
  DPI = 100
  return Figure(figsize=(x_size / DPI, y_size / DPI)).add_subplot(111)

def new_figure(x_size=256, y_size=256):
  DPI = 100
  return Figure(figsize=(x_size / DPI, y_size / DPI))


def scatter(ax, datatable, markers, range=None, color_marker=None,
    min_cells_per_bin=1,no_bins=512j):
  def cached(data):
    cols = datatable.get_cols(*markers)
    if not range:
      fixed_range = [min(cols[0]), min(cols[1]), max(cols[0]), max(cols[1])]
    else:
      fixed_range = range
    hist, data.x_edges, data.y_edges = np.histogram2d(
        cols[0], 
        cols[1], 
        [
            np.r_[fixed_range[0]:fixed_range[2]:no_bins], 
            np.r_[fixed_range[1]:fixed_range[3]:no_bins]])
    data.final_hist = np.sign(np.subtract(
        np.clip(np.abs(hist), min_cells_per_bin, np.inf),
        min_cells_per_bin))
    if color_marker:
      data.is_colored = True
      weights = datatable.get_cols(color_marker)[0]     
      weighted_hist, x_edges, y_edges = np.histogram2d(
          cols[0], 
          cols[1], 
          [
              np.r_[fixed_range[0]:fixed_range[2]:no_bins], 
              np.r_[fixed_range[1]:fixed_range[3]:no_bins]], None, False, weights)
      data.colored_hist = np.multiply(
          np.true_divide(weighted_hist, hist), data.final_hist)
    else:
      data.is_colored = False
  data = services.cache((datatable, markers, range, color_marker), cached)  
  if data.is_colored:
    data_to_draw = data.colored_hist
    cmap = cm.jet
  else:
    data_to_draw = data.final_hist
    cmap = cm.gist_yarg
  extent=[
        data.x_edges[0],
        data.x_edges[-1],
        data.y_edges[0],
        data.y_edges[-1]]
  image = ax.imshow(data_to_draw, extent=extent, cmap=cmap)
  ax.set_xlabel(str(markers[0]) + '   ', size='x-small')
  ax.set_ylabel(str(markers[1]) + '   ', size='x-small')
  ax.figure.subplots_adjust(bottom=0.15)
  ax.figure.colorbar(image)
  ax.set_aspect('auto')
  return ax

def kde2d_color_hist(
    fig, datatable, markers, range, norm_axis=None, norm_axis_thresh = None, res=256):
  ax_main = fig.add_subplot(111)
  #ax_main.set_aspect(1.)
  divider = make_axes_locatable(ax_main)
  ax_hist_x = divider.append_axes("top", 0.1, pad=0, sharex=ax_main)
  ax_hist_y = divider.append_axes("right", 0.1, pad=0, sharey=ax_main)
  plt.setp(
      ax_hist_x.get_xticklabels() +
      ax_hist_x.get_xticklines()  +
      ax_hist_x.get_yticklabels() +
      ax_hist_x.get_yticklines()  +
      ax_hist_y.get_xticklabels() +
      ax_hist_y.get_xticklines()  +
      ax_hist_y.get_yticklabels() +
      ax_hist_y.get_yticklines(), visible=False)
  for tl in ax_hist_x.get_xticklines():
    tl.set_visible(False)
  for tl in ax_hist_y.get_xticklines():
    tl.set_visible(False)
  density, X, Y = kde2d(
      ax_main, datatable, markers, range, norm_axis, norm_axis_thresh, res)
  x_hist, x_top_edges = np.histogram(datatable.get_cols(markers[0]), bins=X[0])
  image = ax_hist_x.imshow(np.log([x_hist]), extent=(X[0,0], X[0,-1], 0, 1), cmap=cm.jet)
  y_hist, y_top_edges = np.histogram(datatable.get_cols(markers[1]), bins=Y[:,0])
  image = ax_hist_y.imshow(np.log([y_hist]).T, extent=(0,1,Y[0,0], Y[-1,0]), cmap=cm.jet)

  #for i in xrange(len(X[0])):
  #  print X[0,i], top_edges[i]
  #print '*'
  #print (X[0,0], X[0,-1])
  #print '*'
  
  
  
  
def kde2d(
    ax, datatable, markers, range, norm_axis=None, norm_axis_thresh = None, res=256):
  def cached(data):
    from mlabwrap import mlab
    a, w = datatable.get_cols(markers[0], markers[1])
    if range:
      min_a = range[0]
      max_a = range[2]
      min_w = range[1]
      max_w = range[3]
    else:
      min_w = min(w)
      max_w = max(w)
      min_a = min(a)
      max_a = max(a)
    points = datatable.get_points(markers[0], markers[1])
    bandwidth,data.density, data.X, data.Y = mlab.kde2d(
        points, res,        
        [[min_a, min_w]],
        [[max_a, max_w]],
        nout=4)    
  data = services.cache((datatable, markers, range), cached)  
  display_data = data.density
  if norm_axis == 'x':
    max_dens_x = np.array([np.max(data.density, axis=1)]).T
    if norm_axis_thresh:
      max_dens_x[max_dens_x < norm_axis_thresh] = np.inf
    data.density_x = data.density / max_dens_x
    display_data = data.density_x
  elif norm_axis == 'y':
    max_dens_y = np.array([np.max(data.density, axis=0)])
    if norm_axis_thresh:
      max_dens_y[max_dens_y < norm_axis_thresh] = np.inf
    data.density_y = data.density / max_dens_y
    display_data = data.density_y
  ax.set_xlabel(str(markers[0]) + '   ', size='x-small')
  ax.set_ylabel(str(markers[1]) + '   ', size='x-small')
  ax.figure.subplots_adjust(bottom=0.15)
  extent=[
      data.X[0,0],
      data.X[0,-1],
      data.Y[0,0],
      data.Y[-1,0]]    
  image = ax.imshow(display_data, extent=extent)
  #ax.figure.colorbar(image)
  ax.set_aspect('auto')
  return data.density, data.X, data.Y
