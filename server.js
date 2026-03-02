import http.server
import socketserver
import webbrowser
import os

PORT = 5500

# Change to the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

print(f"Current working directory: {os.getcwd()}")
print(f"Files in directory: {os.listdir('.')}")

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {format % args}")

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("=" * 60)
    print("🚀 AURA ENTERPRISE DASHBOARD SERVER")
    print("=" * 60)
    print(f"📍 URL: http://localhost:{PORT}")
    print(f"📍 URL: http://127.0.0.1:{PORT}")
    print(f"📂 Serving from: {os.getcwd()}")
    print("=" * 60)
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Try to open browser automatically
    try:
        webbrowser.open(f'http://localhost:{PORT}')
    except:
        pass
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")