import http.server
import socketserver
import json
from datetime import datetime

PORT = 8083

class SimpleAuraAPI(http.server.BaseHTTPRequestHandler):
    
    def do_GET(self):
        print(f"📥 GET request: {self.path}")
        
        if self.path == '/api/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "status": "healthy",
                "service": "Simple AURA API",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0"
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = """
            <html>
            <head><title>AURA API Dashboard</title></head>
            <body>
                <h1>🚀 Simple AURA API Running!</h1>
                <p>Endpoints:</p>
                <ul>
                    <li><a href="/api/health">/api/health</a> - Health check</li>
                </ul>
                <script>
                    // Test the API
                    fetch('/api/health')
                        .then(r => r.json())
                        .then(data => {
                            document.body.innerHTML += '<p>✅ API Status: ' + data.status + '</p>';
                        });
                </script>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
        else:
            self.send_error(404, "Not found")
    
    def do_POST(self):
        print(f"📥 POST request: {self.path}")
        
        if self.path == '/api/parse':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "success": True,
                "message": "AURA parsing completed",
                "timestamp": datetime.now().isoformat(),
                "data_received": len(post_data)
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_error(404, "Not found")

def start_server():
    print("🚀 Starting Simple AURA API Server...")
    print(f"📍 Port: {PORT}")
    print(f"🌐 Dashboard: http://localhost:{PORT}")
    print("⏹️  Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        with socketserver.TCPServer(("", PORT), SimpleAuraAPI) as httpd:
            httpd.serve_forever()
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {PORT} is already in use!")
            print("💡 Try: netstat -ano | findstr :{PORT}")
            print("💡 Or change PORT variable to 8084")
        else:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    start_server()
