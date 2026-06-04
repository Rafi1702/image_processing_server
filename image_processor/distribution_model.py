
import numpy as np
from sklearn.mixture import GaussianMixture

class GaussianModel:
    def __init__(self, source:np.ndarray, n_components:int = 2):
        X_rgb = np.array([
            [240,  50,  45],  # Kluster 1: Merah
            [235,  62,  50],  
            [220,  55,  40],  
            [245,  70,  55],  
            [210,  48,  38],  
            [ 35, 180,  60],  # Kluster 2         : Hijau
            [ 42, 195,  65],  
            [ 50, 175,  55],  
            [ 30, 160,  50],  
            [ 45, 188,  70]   
        ], dtype=np.float64)

        # Bobot awal untuk masing-masing kluster (harus berupa array seukuran K)
        init_weights = np.array([0.5, 0.5])

        # Tebakan pusat warna (Mean Vector) awal untu   k kluster 1 (Merah) dan kluster 2 (Hijau)
        # Ukurannya harus (n_components, n_features) -> (2, 3)
        init_means = np.array([
            [230.0,  55.0,  45.0],  # Tebakan pusat Merah
            [ 40.0, 180.0,  60.0]   # Tebakan pusat Hijau
        ])

        # Matriks Kovarians awal untuk tiap kluster (Menggunakan matriks diagonal / varians independen)
        # Ukurannya harus (n_components, n_features, n_features) -> (2, 3, 3)
        init_covariances = np.array([
            [[100.0,   0.0,   0.0], [  0.0, 100.0,   0.0], [  0.0,   0.0, 100.0]], # Kovarians Kluster 1
            [[100.0,   0.0,   0.0], [  0.0, 100.0,   0.0], [  0.0,   0.0, 100.0]]  # Kovarians Kluster 2
        ])

        # 3. Inisialisasi Model GMM dengan Parameter Dummy
        # Kita set `covariance_type='full'` agar GMM bisa membentuk elips miring jika dibutuhkan
        self.model = GaussianMixture(
            n_components=n_components,
            weights_init=init_weights,
            means_init=init_means,
            precisions_init=None, # Biarkan scikit-learn menghitung invers dari cov_init otomatis
            covariance_type='full',
            max_iter=100,
            random_state=42 # Menjaga hasil tetap konsisten jika ada proses acak internal
        )

        # Set matriks kovarians manual secara langsung ke parameter inisialisasi internal scikit-learn
        # Catatan: scikit-learn membutuhkan parameter covariances dikirim lewat parameter init atau disuntikkan sebelum fit
        self.model.covariances_init = init_covariances

        # 4. Latih Model menggunakan Data Dummy Anda
        self.model.fit(source)

        # # 5. Uji Coba Prediksi Kluster data baru (misal warna pink kemerahan)
        # piksel_baru = np.array([[250, 60, 60]])
        # hasil_kluster = self.model.predict(piksel_baru)
        # probabilitas = self.model.predict_p                   roba(piksel_baru)

        print("means_", self.model.means_)
        print("covariances_", self.model.covariances_)
        print("weights_", self.model.weights_)
        
# model = GaussianModel(source=None)
