import json
from http.server import BaseHTTPRequestHandler 
from base_response import BaseResponse, KMeansResponse
from typing import TypeVar, Callable

T = TypeVar('T')

class Util:
    @staticmethod
    def send_data(base_http_handler: BaseHTTPRequestHandler, process: Callable[[], T]):
        content_length = int(base_http_handler.headers['Content-Length'])
        post_data = base_http_handler.rfile.read(content_length)
           # 3. Decode bytes ke string dan parse ke JSON (jika data JSON)
        try:
            data = json.loads(post_data.decode('utf-8'))
            print(f"Data diterima: {data}")
            
            # Berikan respon sukses
            base_http_handler.send_response(200)
            base_http_handler.send_header('Content-type', 'application/json')
            base_http_handler.end_headers()
            
            processed_data = process()
            response = BaseResponse[T](success = True,messaqge = 'Respons sukses', data =  processed_data)
            base_http_handler.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            # Handle jika data bukan JSON atau error lain
            base_http_handler.send_response(400)
            base_http_handler.end_headers()
            base_http_handler.wfile.write(b"Gagal memproses data")    