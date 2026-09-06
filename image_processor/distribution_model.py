
import numpy as np
from sklearn.mixture import GaussianMixture

class GaussianModel:
    def __init__(self, source: np.ndarray, n_components: int = 5): 
        if source is None or len(source) == 0:
            raise ValueError("Cannot train GMM with empty color source.")
        
        source = np.asarray(source, dtype=np.float64)
        # Strip Alpha channel if 4 channels (RGBA/BGRA) are provided
        if source.ndim > 1 and source.shape[1] > 3:
            source = source[:, :3]

        # Scale [0, 255] color values to [0, 1] range for numerical stability
        if source.max() > 1.0:
            source = source / 255.0

        n_unique_samples = np.unique(source, axis=0).shape[0]
        effective_components = max(1, min(n_components, n_unique_samples))

        self.model = GaussianMixture(
            n_components=effective_components,
            covariance_type='full',
            max_iter=100,
            reg_covar=1e-3,  
            random_state=42
        )

        self.model.fit(source)

    def log_likelihood(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=np.float64)
        if X.ndim > 1 and X.shape[1] > 3:
            X = X[:, :3]

        # Scale [0, 255] color values to [0, 1] range
        if X.max() > 1.0:
            X = X / 255.0

        return self.model.score_samples(X)

    # def score_samples(self, X: np.ndarray) -> np.ndarray:
    #     return -self.log_likelihood(X)


class GaussianMixtureScratch:
    def __init__(self, components: int, user_seeds: np.ndarray):
        self.clusters = []
        self.covariance = []
        self.mean = 0
        for i in range(components):
            clusters.append([])

        
        
    @property
    def mean(self): return self.mean

    @property
    def covariance(self): return self.covariance

    def __move_cluster(self):
        raise NotImplementedError()
    
    def __assign_point(self):
        raise NotImplementedError()
