
import numpy as np
from sklearn.mixture import GaussianMixture

class GaussianModel:
    def __init__(self, source: np.ndarray, n_components: int = 5):
        # 1. Handle constraints on the number of samples
        if source is None or len(source) == 0:
            raise ValueError("Cannot train GMM with empty color source.")
            
        source = np.asarray(source, dtype=np.float64)
        n_samples = source.shape[0]

        # 1. Tentukan jumlah komponen secara adaptif
        # Komponen tidak boleh melebihi jumlah sampel yang ada
        effective_components = min(n_components, n_samples)
        
        if n_samples < n_components * 2:
            jitter = np.random.normal(0, 1e-3, size=source.shape)
            source = source + jitter

        self.model = GaussianMixture(
            n_components=n_components,
            covariance_type='full',
            max_iter=100,
            reg_covar=1e-5,
            random_state=42
        )
            
        # if n_components == 2:
        #     init_weights = np.array([0.5, 0.5])

        #     # Tebakan pusat warna (Mean Vector) awal untuk kluster 1 (Merah) dan kluster 2 (Hijau)
        #     init_means = np.array([
        #         [230.0,  55.0,  45.0],  # Tebakan pusat Merah
        #         [ 40.0, 180.0,  60.0]   # Tebakan pusat Hijau
        #     ])

        #     # Matriks Kovarians awal untuk tiap kluster
        #     init_covariances = np.array([
        #         [[100.0,   0.0,   0.0], [  0.0, 100.0,   0.0], [  0.0,   0.0, 100.0]], # Kovarians Kluster 1
        #         [[100.0,   0.0,   0.0], [  0.0, 100.0,   0.0], [  0.0,   0.0, 100.0]]  # Kovarians Kluster 2
        #     ])

        #     self.model = GaussianMixture(
        #         n_components=n_components,
        #         weights_init=init_weights,
        #         means_init=init_means,
        #         precisions_init=None,
        #         covariance_type='full',
        #         max_iter=100,
        #         reg_covar=1e-5,  # Add small regularization to avoid singular matrix errors
        #         random_state=42
        #     )
        #     self.model.covariances_init = init_covariances
        # else:
        #     # For n_components != 2, use standard automatic k-means initialization
       

        # 3. Latih Model
        self.model.fit(source)

        print("means_", self.model.means_)
        print("covariances_", self.model.covariances_)
        print("weights_", self.model.weights_)

        
# model = GaussianModel(source=None)
