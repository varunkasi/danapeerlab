# partition Kai Zhang
from numpy import atleast_2d, zeros, vstack, arange, mean, std, exp, power, dot
from numpy import array, arange, pi, sqrt
from scipy.optimize import fmin as fminc
from scipy.stats import scoreatpercentile, cov
from scipy.linalg import det, inv
class fkde:
    """Fast Kernel Density Estimation, 
    a nonparametric method to evaluate the probability distribution function (pdf) of a sample.
    
    Usage
    -----
    1. Call the class constructor:
        kde = fkde(dataset, radius), where dataset is an array (dim, N)
        The radius determines the size of the clusters. Using too large a radius 
        decreases the number of clusters (and the accuracy) and using too small 
        a radius slows down the computations. Unfortunately, I'm not aware of a 
        wise trick to select it. 

    2. Evaluate the density at some points:    
        kde(points), where points is an array (dim, M)
    
    Class Attributes
    ----------------
    n_clusters: the number of clusters
    C         : the cluster centers    
    bandwidth : the bandwidth specifying the covariance of the kernel
    r         : the cluster radius
    
    Class Methods
    -------------
    evaluate(points, bandwidth='silverman') : Evaluates the pdf at the given points. 
    The bandwidth key can be used to pass the covariance matrix directly, or to select
    it using one of two methods, silverman or scotts.
    
    References
    ----------
    Algorithm taken from Zhang, K., M. Tang and James T. Kwok (2005), 
    Applying Neighborhood Consistency for Fast Clustering and Kernel Density Estimation, IEEE.
    
    Notes
    -----
    A lot of work is done during during class instantiation, where the data
    is clustered. Hence, if the kde is to be evaluated < 50 times, 
    gaussian_kde will be faster then fkde. On the other hand, when the kde
    is evaluated many times, the improvement is radical. 
    
    I have not yet found a critical evaluation of the algorithm, so please double check results 
    before using it seriously.

    To do : Improve the clustering algorithm.
    License : See Scipy License. 
    Address questions and comments to david.huard@gmail.com, May 2006.
    """

    def __init__(self, x, radius):
        
        x = atleast_2d(x)
        N,dim = x.shape                
        if N<dim:
            self.x = x.transpose()
            self.N, self.dim = dim, N
        else:
            self.x = x
            self.N, self.dim = N, dim
        self.r = radius
        self.C = self.x[0]
        self.index = zeros(self.N)
        
        # Recursive clustering
        self.Iterations = 4
        self.rC = {}
        self.rI = {}
        r0 = array(self.x.ptp()).max()/3.
        f = (r0/radius)**(1./(self.Iterations-1))
        r = r0/f**arange(self.Iterations)
  
        self.rI[0] = [range(self.N)]
        for it in range(1, self.Iterations):
            self.rC[it] = []
            self.rI[it] = []
            for indices in self.rI[it-1]:
                self._cluster(indices, r[it-1], it)
            

        self.C = self.rC[it]
        self.index = self.rI[it]
        self._averaging()
        
        #r = max(x.ptp())/4.
        #self.kernels = {'gaussian': lambda x: exp(x)} # normalized ? 

    def _cluster(self, indices, r, it):
        """Partitions the dataset into clusters. The number of clusters is inversely proportional to the radius.
        Clustering is the computational bottleneck of the algorithm. Selecting a radius that is too small slows the computations significatively."""        
        m = 0
        cC = [self.x[indices[0]]]
        index = [[]]
        for i in indices:
            e = atleast_2d((self.x[i] - cC)**2)
            d = e.sum( axis = 1)

            if (min(d) <= r**2):
                index[d.argmin()].append(i)
            else:
                cC.append(self.x[i])
                index.append([])
                m += 1
                index[m].append(i)
        
        
        self.rC[it].extend(cC)
        self.rI[it].extend(index)
        
    def _averaging(self):
        
        j = 0
        self.n = []    # Number of points in each cluster
        for i in self.index:
            self.n.append(len(i))
            self.C[j] = mean(self.x[i])  # Averaging of each cluster
            j += 1
        self.n_clusters = j        
            

    def evaluate(self, points, bandwidth = 'silverman', shape = 'gaussian'):
        """Evaluates the density at points.
        The bandwidth can be optimized using the bandwidth_selection method."""
        if bandwidth in ['silverman', 'scotts']:
            self._bandwidth_selection(bandwidth)
        else:
            self.bandwidth = atleast_2d(bandwidth)    
        
        self._inv_band = inv(self.bandwidth)

        points = atleast_2d(points)
        
        if (self.dim == points.shape[1]):
            self.points = points
        elif self.dim == points.shape[0]:
            self.points = points.transpose()
        else:
            msg = 'The dimension of the evaluation points is inconsistent with the dataset.'
            raise ValueError(msg)
        #kernel = self.kernels[shape]     
        result = zeros(points.shape[1])
        
        for j in range(self.n_clusters):
         #   z= ((self.points - self.C[j])/h)**2
         #   f += kernel(-z.sum(axis = 1))*self.n[j]
            diff = self.points - atleast_2d(self.C[j])
            
            tdiff = dot(diff, self._inv_band)
            energy = (diff*tdiff).sum(axis=1)/2.0
            result += exp(-energy)*self.n[j]
            det_cov = det(2*pi*self.bandwidth)
        result /= sqrt(det_cov)*self.N
        
        #f /= self.N * prod(h) *pi**(self.dim/2.)
        return result
        
        
    __call__ = evaluate
    
    
    def _bandwidth_selection(self, method = 'silverman'):
        """Returns the optimal bandwidth and assigns it to the class attribute bandwidth. 
        Available methods are silverman and scotts."""

        if method=='silverman':
            factor = self._silverman_factor()
        elif method=='scotts':
            factor = self._scotts_factor()
        else:
            raise TypeError, 'Unknown bandwidth selection method. Choose among scotts and silverman.'
            
        covx = atleast_2d(cov(self.x, rowvar = 0))
        self.bandwidth = covx*factor*factor             
   
 
    def _scotts_factor(self):
        return power(self.N, -1./(self.dim+4))

    def _silverman_factor(self):
        return power(self.N*(self.dim+2.0)/4.0, -1./(self.dim+4))

