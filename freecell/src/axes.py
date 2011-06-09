import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from scriptservices import services 
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.cm as cm
DPI = 100

def new_axes(x_size=256, y_size=256):
  return Figure(figsize=(x_size / DPI, y_size / DPI)).add_subplot(111)

def new_figure(x_size=256, y_size=256):
  return Figure(figsize=(x_size / DPI, y_size / DPI))

def small_ticks(ax):
  for label in  ax.yaxis.get_ticklabels() + ax.xaxis.get_ticklabels():
    label.set_fontsize('xx-small')

def points(ax, datatable, markers):
  points = datatable.get_cols(*markers)
  ax.scatter(points[0], points[1], s=1, marker='o')
  ax.set_xlabel(str(markers[0]) + '   ', size='x-small')
  ax.set_ylabel(str(markers[1]) + '   ', size='x-small')
  ax.figure.subplots_adjust(bottom=0.15)
  
def scatter_data(datatable, markers, range=None, norm_axis=None, norm_axis_thresh=0, no_bins=512j):
  cols = datatable.get_cols(*markers)
  if not range:
    range = [min(cols[0]), min(cols[1]), max(cols[0]), max(cols[1])]
  hist, x_edges, y_edges = np.histogram2d(
      cols[0], 
      cols[1], 
      [
          np.r_[range[0]:range[2]:no_bins], 
          np.r_[range[1]:range[3]:no_bins]])
  extent=[
      x_edges[0],
      x_edges[-1],
      y_edges[0],
      y_edges[-1]]
  
  if norm_axis == 'y':
    max_dens_x = np.array([np.max(hist, axis=1)]).T
    if norm_axis_thresh:
      max_dens_x[max_dens_x < norm_axis_thresh] = np.inf
    hist = hist / max_dens_x
  elif norm_axis == 'x':
    max_dens_y = np.array([np.max(hist, axis=0)])
    if norm_axis_thresh:
      max_dens_y[max_dens_y < norm_axis_thresh] = np.inf
    hist = hist / max_dens_y
  return hist, extent, x_edges, y_edges
  
def scatter(
    ax, datatable, markers, range=None, norm_axis=None, norm_axis_thresh=None, no_bins=512j):
  hist, extent, x_edges, y_edges = scatter_data(datatable, markers, range, norm_axis, norm_axis_thresh, no_bins)
  image = ax.imshow(hist.T, extent=extent, cmap=cm.gist_yarg, origin='lower')
  ax.set_xlabel(str(markers[0]) + '   ', size='x-small')
  ax.set_ylabel(str(markers[1]) + '   ', size='x-small')
  ax.figure.subplots_adjust(bottom=0.15)
  #ax.figure.colorbar(image)
  ax.set_aspect('auto')
  return ax, hist
            
  
  
def scatter2(ax, datatable, markers, range=None, color_marker=None,
    min_cells_per_bin=1,no_bins=256j):
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
      averages = np.true_divide(weighted_hist, hist)
      averages[np.isnan(averages)] = np.NaN
      averages[data.final_hist == 0] = np.NaN
      data.colored_hist = averages
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
  image = ax.imshow(data_to_draw.T, extent=extent, cmap=cmap, origin='lower')
  ax.set_xlabel(str(markers[0]) + '   ', size='x-small')
  ax.set_ylabel(str(markers[1]) + '   ', size='x-small')
  ax.figure.subplots_adjust(bottom=0.15)
  cbar = ax.figure.colorbar(image)
  if color_marker:
    cbar.set_label(color_marker, fontsize='xx-small')
    #label = cbar.get_label()
    #label.set_fontsize('xx-small')
  ax.set_aspect('auto')
  return ax

def remove_ticks(ax):
  plt.setp(
      ax.get_xticklabels() +
      ax.get_xticklines()  +
      ax.get_yticklabels() +
      ax.get_yticklines(), visible=False)
  
def kde2d_color_hist(
    fig, datatable, markers, range, norm_axis=None, norm_axis_thresh = None, res=256):
  ax_main = fig.add_subplot(111, axisbg=cm.jet(0))
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
  image = ax_hist_x.imshow(np.log([x_hist]), extent=(X[0,0], X[0,-1], 0, 1), cmap=cm.jet, origin='lower')
  y_hist, y_top_edges = np.histogram(datatable.get_cols(markers[1]), bins=Y[:,0])
  image = ax_hist_y.imshow(np.log([y_hist]).T, extent=(0,1,Y[0,0], Y[-1,0]), cmap=cm.jet, origin='lower')
  ax_main.set_xlabel(str(markers[0]) + '   ', size='x-small')
  ax_main.set_ylabel(str(markers[1]) + '   ', size='x-small')
  ax_main.figure.subplots_adjust(bottom=0.15)

  #for i in xrange(len(X[0])):
  #  print X[0,i], top_edges[i]
  #print '*'
  #print (X[0,0], X[0,-1])
  #print '*'
  
  
def kde1d_points(ax, points, min_x=None, max_x=None, norm=1):
  range = np.max(points) - np.min(points)
  min_x_ = min_x
  max_x_ = max_x
  if min_x == None:
    min_x_ = np.min(points) - range / 10
  if max_x == None:
    max_x_ = np.max(points) + range / 10
  from mlabwrap import mlab
  bandwidth, density, xmesh = mlab.kde(
      np.array([points]).T, float(2**12), float(min_x_), float(max_x_), nout=3)
  xmesh = xmesh[0]
  density = density.T[0]
  density = np.multiply(density, float(norm))
  ax.plot(xmesh, density)
  return ax

def kde1d(ax, datatable, marker, min_x=None, max_x=None, norm=1):
  def cached(data):
    points = datatable.get_cols(marker)[0]
    range = np.max(points) - np.min(points)
    min_x_ = min_x
    max_x_ = max_x
    if min_x == None:
      min_x_ = np.min(points) - range / 10
    if max_x == None:
      max_x_ = np.max(points) + range / 10
    from mlabwrap import mlab
    data.bandwidth, data.density, data.xmesh = mlab.kde(
        points, float(2**12), float(min_x_), float(max_x_), nout=3)
    print data.xmesh
    # TODO(daniv): make sure this line isn't needed on mac
    #data.xmesh = data.xmesh[0]
    #print 'den:' + str(np.shape(data.density[0]))
    data.density = data.density.T[0]
    data.density = np.multiply(data.density, float(norm))
  data = services.cache((datatable, marker, min_x, max_x), cached) 
  ax.plot(data.xmesh, data.density)
  ax.set_title(marker)
  return ax
  
def kde2d(
    ax, datatable, markers, range=None, norm_axis=None, norm_axis_thresh = None, res=256):
  
  display_data, extent, density, X, Y = kde2d_data(
      datatable, markers, range, norm_axis, norm_axis_thresh, res)
  image = ax.imshow(display_data, extent=extent, origin='lower')
  #ax.figure.colorbar(image)
  ax.set_aspect('auto')
  #ax.set_xlim(-1,6)
  #ax.set_ylim(-1,6)

  return density, X, Y

def kde2d_data(
    datatable, markers, range=None, norm_axis=None, norm_axis_thresh = None, res=256):
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
        points, float(res),        
        [[float(min_a), float(min_w)]],
        [[float(max_a), float(max_w)]],
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
  extent=[
      data.X[0,0],
      data.X[0,-1],
      data.Y[0,0],
      data.Y[-1,0]]    
  return display_data, extent, data.density, data.X, data.Y

