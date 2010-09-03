import numpy as np
import scipy.spatial as ssp

d = lambda u,v: ssp.distance.minkowski(u, v, 2)
def evaluate_sum(point, func, points, res=1000):
  """Evaluates the sum of a monotone distance function on given distances.
  
  This method estimates sum(func(distance(x, x_i))) for x_i in points.
  It returns val, error.  
  point - a tuple representing a point.
  func - a monotone function from R to R.
  points - a scipy.spatial.kdtree with points to evaluate
  res - resolution
  """
  max_r = max(
      d((points.mins[0], points.mins[1]), point),
      d((points.maxes[0], points.mins[1]), point),
      d((points.maxes[0], points.maxes[1]), point),
      d((points.mins[0], points.maxes[1]), point))
  
  point = ssp.KDTree([point])
  
  radii = [max_r / (i + 1) for i in xrange(res)]
  radii += [0] # add a last circle with 0 radius
  
  func_vals = [func(r) for r in radii]
    
  counts = points.count_neighbors(point, radii)
  #counts = len(radii) * [5]
    
  points_per_ring = [counts[i] - counts[i+1] for i in xrange(res)]
  min_val_per_ring = [func_vals[i] * points_per_ring[i] for i in xrange(res)]
  max_val_per_ring = [func_vals[i+1] * points_per_ring[i] for i in xrange(res)]
  
  min_val = sum(min_val_per_ring)
  max_val = sum(max_val_per_ring)
  
  error = max_val - min_val
  val = (min_val + max_val) / 2
  return val, error

def create_gaussian_kernel(bandwidth):
  def gaussian_kernel(d): 
    return (2*np.pi) ** (-0.5) * np.exp(-(d ** 2)/(2 * (bandwidth **2)))
  return gaussian_kernel
    
def kde2d(sample_points, data, bandwidth):
  kernel = create_gaussian_kernel(bandwidth)
  vals = []
  errors = []
  for p in sample_points:
    val, err = evaluate_sum(p, kernel, data)
    vals.append(val)
    errors.append(err)
  return np.array(vals), np.array(errors)