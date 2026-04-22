from http.server import HTTPServer
from handler import ImageDataHandler


def main():
    host = '127.0.0.1'
    port = 65432
    
    server_address = (host, port)
    httpd = HTTPServer(server_address, ImageDataHandler)
    
    print(f"[*] HTTP Server mendengarkan di http://{host}:{port}")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Server dimatikan.")
        httpd.server_close()
        return

if __name__ == "__main__":
    main()
