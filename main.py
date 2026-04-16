import socket
import cv2 as cv
import json
import numpy as np
import base64

from http.server import HTTPServer, BaseHTTPRequestHandler


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

class SimpleHTTPHandler(BaseHTTPRequestHandler):
    # Menangani request GET
    def do_GET(self):
        # Mengirimkan status code 200 OK
        self.send_response(200)
        
        # Menentukan Header
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        
        # Menyiapkan respon
        respons = "Server HTTP menerima request GET Anda!"
        
        # Mengirim respon balik ke client
        self.wfile.write(respons.encode('utf-8'))

    # Menangani request POST (Opsional, jika ingin menerima data)
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        self.send_response(200)
        self.end_headers()
        
        respons = f"Server menerima data POST: {post_data}"
        self.wfile.write(respons.encode('utf-8'))
        print(f"[>] Pesan diterima via POST: {post_data}")

def main():
    host = '127.0.0.1'
    port = 65432
    
    server_address = (host, port)
    httpd = HTTPServer(server_address, ImageUploadHandler)
    
    print(f"[*] HTTP Server mendengarkan di http://{host}:{port}")
    
    try:
        # Menjalankan server selamanya
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Server dimatikan.")
        httpd.server_close()
        return

if __name__ == "__main__":
    main()
