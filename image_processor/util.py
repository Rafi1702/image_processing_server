import json
from http.server import BaseHTTPRequestHandler 
from base_response import BaseResponse, KMeansResponse
from typing import TypeVar, Callable, Any

T = TypeVar('T')

class Util:
    @staticmethod
    def send_data(base_http_handler: BaseHTTPRequestHandler, process_callback: Callable[[dict], Any]):
        try:
            # 1. Baca data dari body
            content_length = int(base_http_handler.headers.get('Content-Length', 0))
            post_data = base_http_handler.rfile.read(content_length)
            request_body = json.loads(post_data.decode('utf-8'))
            
            # 2. Jalankan callback dengan data yang sudah di-parse
            processed_data = process_callback(request_body)
            
            # 3. Kirim Respon
            base_http_handler.send_response(200)
            base_http_handler.send_header('Content-type', 'application/json')
            base_http_handler.end_headers()
            
            response = {
                "success": True,
                "message": "Respons sukses",
                "data": processed_data
            }
            base_http_handler.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            base_http_handler.send_response(400)
            base_http_handler.end_headers()
            error_resp = {"success": False, "message": str(e)}
            base_http_handler.wfile.write(json.dumps(error_resp).encode('utf-8'))