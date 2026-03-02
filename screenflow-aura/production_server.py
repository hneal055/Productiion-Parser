import http.server
import socketserver
import os
import sys
import threading
import webbrowser
from datetime import datetime

class AURAProductionHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f'[{timestamp}] {format % args}')
    
    def end_headers(self):
        # Security headers
        self.send_header('X-Frame-Options', 'SAMEORIGIN')
        self.send_header('X-XSS-Protection', '1; mode=block')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Cache-Control', 'public, max-age=3600')
        super().end_headers()

def start_production_server(port=8080):
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        with socketserver.TCPServer(("", port), AURAProductionHandler) as httpd:
            print("=" * 60)
            print("AURA ENTERPRISE DASHBOARD - PRODUCTION SERVER")
            print("=" * 60)
            print(f"URL: http://localhost:{port}")
            print(f"URL: http://127.0.0.1:{port}")
            print(f"Serving from: {os.getcwd()}")
            print("=" * 60)
            print("Production-ready with security headers")
            print("Access logs enabled")
            print("Basic security headers implemented")
            print("=" * 60)
            
            # Open browser automatically
            def open_browser():
                webbrowser.open(f'http://localhost:{port}')
            
            threading.Timer(1.5, open_browser).start()
            
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nProduction server stopped by user")
    except OSError as e:
        if e.errno == 48 or e.errno == 10048:  # Address already in use
            print(f"Port {port} is already in use. Trying port {port+1}")
            start_production_server(port+1)
        else:
            raise

if __name__ == "__main__":
    start_production_server(8080)