import json
import cv2 as cv
import json
import numpy as np
import base64
from http.server import BaseHTTPRequestHandler
from util import Util
from base_response import KMeansResponse
from typing import Tuple, List

class ImageDataHandler(BaseHTTPRequestHandler):
    def _process_kmeans(self, data_points: np.ndarray, k: int):
        criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        ret, labels, centers = cv.kmeans(
            data_points, 
            k, 
            None, 
            criteria, 
            10, 
            cv.KMEANS_PP_CENTERS
        )
        labels = labels.flatten().tolist(), 

        cv.gmm

        # Kembalikan dictionary agar serializable ke JSON
        return {
            "ret": ret, 
            "labelSize": len(labels[0]),
            "labels": labels, 
            "centers": centers.tolist()
        }
    
    def do_POST(self):
    # Kita definisikan cara memproses datanya di sini
        def processor(json_data):
            # Ambil 'points' dan 'k' dari JSON request body
            # Contoh body: {"points": [[1,2], [3,4]], "k": 3}
            points = np.array(json_data['points'], dtype=np.float32)
            k_val = json_data.get('k', 50)
            return self._process_kmeans(points, k_val)

        # Panggil helper untuk handle pembacaan stream dan pengiriman respon
        Util.send_data(self, processor)



class ImageUploadHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # 1. Hitung panjang data
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        # 2. Decode JSON
        data = json.loads(post_data.decode('utf-8'))
        img_base64 = data['image']

        # 3. Ubah Base64 kembali menjadi format OpenCV (Mat)
        img_bytes = base64.b64decode(img_base64)
        np_array = np.frombuffer(img_bytes, dtype=np.uint8)
        frame = cv.imdecode(np_array, cv.IMREAD_COLOR)

        if frame is not None:
            # --- AREA PENGELOLAAN (OpenCV) ---
            # Contoh: Ubah jadi hitam putih atau simpan
            
            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

            success, buffer = cv.imencode('.jpg', gray)

            if success:
            # 2. Encode byte array tersebut ke Base64
                img_base64 = base64.b64encode(buffer).decode('utf-8')
                
                # Sekarang 'img_base64' adalah string yang siap dikirim via JSON
                print(img_base64[:50] + "...") 
                cv.imwrite("hasil_terima.jpg", frame)
                print("[+] Gambar diterima dan berhasil dikelola OpenCV!")
        
                self.send_response(200)
                self.end_headers()

                response_body = {
                    "status": "success",
                    "message": "Gambar berhasil diproses",
                    "processed_image":  img_base64
                }
                self.wfile.write(json.dumps(response_body).encode('utf-8'))
                print("[+] Gambar berhasil diproses dan dikirim balik.")
                self.wfile.write(b"Server: Gambar Berhasil Diterima!")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Gagal memproses gambar")