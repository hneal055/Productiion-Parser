import http.server
import socketserver
import os

# Use port 5501 instead of 5500
PORT = 5501

# Change to current directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), handler) as httpd:
    print(f"Server running at http://localhost:{PORT}")
    print("Press Ctrl+C to stop the server")
    httpd.serve_forever()