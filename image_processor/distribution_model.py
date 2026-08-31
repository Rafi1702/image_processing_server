
import numpy as np
from sklearn.mixture import GaussianMixture

class GaussianModel:
    def __init__(self, source: np.ndarray, n_components: int = 5):
        
        if source is None or len(source) == 0:
            raise ValueError("Cannot train GMM with empty color source.")
        
        source = np.asarray(source, dtype=np.float64)
        n_samples = source.shape[0]
        effective_components = min(n_components, n_samples)

        self.model = GaussianMixture(
                n_components=effective_components,
                covariance_type='full',
                max_iter=100    ,
                reg_covar=1e-5,
                random_state=42
            )

        self.model.fit(source)

        print(f"labels_ {self.model.predict(source)}")
        print("means_", self.model.means_)
        print("covariances_", self.model.covariances_)
        print("weights_", self.model.weights_)
        return

        
# model = GaussianModel(source=None)
