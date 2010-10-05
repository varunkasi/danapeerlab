import numpy as np
import numpy.random as rand
import scipy.spatial as spatial

def unique_sample(points, n):
  #for i in xrange(10):
  print len(points)
  sampled = rand.randint(0, len(points))
  point = np.array([points[sampled]])
  distances = spatial.distance.cdist(
    np.array([points[sampled]]), points, metric='euclidean', p=1)
  points = points[:,distances.T > 5]
  print len(points)
  #print np.sort(distances)
  #print np.max(distances)
  return distances