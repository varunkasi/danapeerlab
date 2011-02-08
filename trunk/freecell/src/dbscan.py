import numpy as np
from depends import fix_path
fix_path(skip_matlab=True)

NOISE_CLUSTER = 0
UNCLASSIFIED = -1

def simple_binned_clustering(D, min_val):
  next_cluster = 1
  shape = D.shape
  out = np.ones(shape) * UNCLASSIFIED
  for index in np.ndindex(*shape):
    if out[index] == UNCLASSIFIED:
  next_cluster = 1
  shape = D.shape
  out = np.ones(shape) * UNCLASSIFIED
  for index in np.ndindex(*shape):
    if out[index] == UNCLASSIFIED:
      sum_neighbors, neighbors_idx = get_neighbors_idx(index)
      #print neighbors_idx
      if sum_neighbors < min_points:
        out[index] = NOISE_CLUSTER
      else:
        print 'index: %d %d, sum:' % index, sum_neighbors
        print neighbors_idx
        #print neighbors
        out[index] = next_cluster
        neighbors_idx = set(
            [i for i in neighbors_idx if out[i]==UNCLASSIFIED])
        expand_cluster(out, next_cluster, neighbors_idx)
        next_cluster += 1
  return out
      


def DBSCAN_binned(D, distance, min_points):
  """A clustering algorithm based on DBSCAN for binned data. 
  
  Parameters:
      D - a histogram array.
      distance - when looking at a cell of index i, cells in the index range
          [i-distance, i+distance] are considered neighbors.
      min_points - if the sum of the neighboring cells of x is more than
          min_points, x is considered dense (otherwise it is noise).
    
  Algorithm:
      Take a cell x in D. If the sum of neighboring cells is less than
      min_points mark cell as noise. Otherwise, create a cluster c with the cell
      x inside. Add the neighbors of x to a candidates list. As long as there
      are candidates, add a candidate which is not noise to cluster c, and add
      its neighbors to the candidates list. Repeat until all cells are either 
      noise or in a cluster.
      
  Output:
    an array (shaped like D) specifying cluster assignments. 0 means noise."""
  
  global get_neighbors_idx_CACHE
  get_neighbors_idx_CACHE = {}
  def get_neighbors_idx(index):   
    global get_neighbors_idx_CACHE
    if not index in get_neighbors_idx_CACHE:
      index_arr = np.array(index)
      dims = len(D.shape)
      begin = np.clip(index_arr - distance, 0, D.shape)
      end = np.clip(index_arr + distance + 1, 0, D.shape)
      slices = [slice(begin[i], end[i]) for i in xrange(dims)]
      mesh = np.mgrid[slices]
      idx = mesh.T.reshape(mesh.size/dims, dims)
      idx = [tuple(i) for i in idx]
      #omesh = np.ogrid[slices]
      get_neighbors_idx_CACHE[index] =  (np.sum(D[slices]), idx)
    return get_neighbors_idx_CACHE[index]
    
  
  def expand_cluster(out, cluster_num, candidates_idx):
    candidates_idx = set(candidates_idx)
    while candidates_idx:
      index = candidates_idx.pop()
      #print index
      #print out[index]
      assert out[index] in (NOISE_CLUSTER, UNCLASSIFIED, cluster_num)
      if out[index] == cluster_num:
        continue
      sum_neighbors, neighbors_idx = get_neighbors_idx(index)
      if sum_neighbors < min_points:
        out[index] = NOISE_CLUSTER
      else:
        out[index] = cluster_num
        sum_new_neighbors, new_neighbors_idx = get_neighbors_idx(index)
        new_neighbors_idx = set(
            [i for i in new_neighbors_idx if out[i]==UNCLASSIFIED])
        candidates_idx |= new_neighbors_idx
        
  next_cluster = 1
  shape = D.shape
  out = np.ones(shape) * UNCLASSIFIED
  for index in np.ndindex(*shape):
    if out[index] == UNCLASSIFIED:
      sum_neighbors, neighbors_idx = get_neighbors_idx(index)
      #print neighbors_idx
      if sum_neighbors < min_points:
        out[index] = NOISE_CLUSTER
      else:
        print 'index: %d %d, sum:' % index, sum_neighbors
        print neighbors_idx
        #print neighbors
        out[index] = next_cluster
        neighbors_idx = set(
            [i for i in neighbors_idx if out[i]==UNCLASSIFIED])
        expand_cluster(out, next_cluster, neighbors_idx)
        next_cluster += 1
  return out
      
      
      
      
      
if __name__ == "__main__":
    import pylab as P
    import scipy as S
    import axes
    import matplotlib.cm as cm
    from biology.datatable import fake_table
    from biology.datatable import combine_tables
    t1 = fake_table((1,0.1), (20,1), num_cells = 1000)
    t2 = fake_table((10,0.1), (15,1), num_cells = 1000)
    t3 = fake_table((10,5), (10,5),  num_cells = 1000)
    t = combine_tables((t1,t2,t3))
    #ax = P.axes()
    hist, extent = axes.scatter_data(t, ('dim0', 'dim1'), no_bins=200j)
    print np.sum(hist)
    #ax.imshow(hist.T, extent=extent, cmap=cm.gist_yarg, origin='lower')
    res = DBSCAN_binned(hist, 3, t.num_cells * 0.01)
    
    def draw_cluster(ax, res, hist, cluster):     
      print 'Cluster %d' % cluster
      print '%d cells' % len(hist[res==cluster])
      print hist[res==cluster][:100]
      c = hist.copy()
      c[res != cluster] = 0
      ax.imshow(c.T, extent=extent, cmap=cm.gist_yarg, origin='lower', alpha=1)
    
    def get_ax(i, num=4):
      w = 1./num
      return P.axes((0,w*i, w ,w))
    draw_cluster(get_ax(0),res,hist,0)
    draw_cluster(get_ax(1),res,hist,1)
    draw_cluster(get_ax(2),res,hist,2)
    draw_cluster(get_ax(3),res,hist,3)

    
    #x = t.get_points('dim0')
    #y = t.get_points('dim1')   
    #P.scatter(x,y)
    
    P.show()

