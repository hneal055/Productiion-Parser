import http.server
import socketserver
import json
import time
from datetime import datetime

PORT = 8083

class EnhancedAuraAPI(http.server.BaseHTTPRequestHandler):
    
    # Track metrics
    request_count = 0
    successful_parses = 0
    
    def do_GET(self):
        self.request_count += 1
        print(f"📥 GET {self.path}")
        
        if self.path == '/api/health':
            self.serve_json({
                "status": "healthy",
                "service": "Enhanced AURA API",
                "aura_integration": "active",
                "requests_processed": self.request_count,
                "successful_parses": self.successful_parses,
                "timestamp": datetime.now().isoformat()
            })
            
        elif self.path == '/api/metrics':
            success_rate = (self.successful_parses / self.request_count * 100) if self.request_count > 0 else 0
            self.serve_json({
                "requests_total": self.request_count,
                "successful_parses": self.successful_parses,
                "success_rate": round(success_rate, 1),
                "uptime_seconds": round(time.time() - self.start_time, 2)
            })
            
        elif self.path == '/':
            self.serve_dashboard()
        else:
            self.send_error(404, "Endpoint not found")
    
    def do_POST(self):
        self.request_count += 1
        print(f"📥 POST {self.path}")
        
        if self.path == '/api/parse':
            self.handle_parse_request()
        elif self.path == '/api/batch/parse':
            self.handle_batch_parse()
        else:
            self.send_error(404, "Endpoint not found")
    
    def handle_parse_request(self):
        """Handle single screenplay parsing"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            screenplay_content = request_data.get('screenplay', '')
            print(f"📝 Parsing screenplay: {len(screenplay_content)} characters")
            
            # Simulate AURA parsing logic
            result = self.aura_parse_screenplay(screenplay_content)
            
            self.successful_parses += 1
            self.serve_json({
                "success": True,
                "data": result,
                "aura_enhanced": True,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            self.serve_json({
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }, status=500)
    
    def handle_batch_parse(self):
        """Handle batch screenplay parsing"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            screenplays = request_data.get('screenplays', [])
            print(f"📦 Batch parsing: {len(screenplays)} screenplays")
            
            # Process each screenplay
            results = []
            for screenplay in screenplays:
                result = self.aura_parse_screenplay(screenplay)
                results.append(result)
            
            self.successful_parses += len(screenplays)
            self.serve_json({
                "success": True,
                "batch_size": len(screenplays),
                "processed": len(results),
                "results": results,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            self.serve_json({
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }, status=500)
    
    def aura_parse_screenplay(self, screenplay_text):
        """Enhanced AURA parsing logic"""
        # This is where your AURA parsing magic happens
        word_count = len(screenplay_text.split())
        line_count = screenplay_text.count('\n') + 1
        
        return {
            "processed": True,
            "word_count": word_count,
            "line_count": line_count,
            "character_count": len(screenplay_text),
            "estimated_pages": round(word_count / 250, 1),
            "analysis": "AURA enhanced parsing completed",
            "timestamp": datetime.now().isoformat()
        }
    
    def serve_json(self, data, status=200):
        """Serve JSON response with CORS"""
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        response = json.dumps(data, indent=2)
        self.wfile.write(response.encode('utf-8'))
    
    def serve_dashboard(self):
        """Serve enhanced dashboard"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        dashboard = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Enhanced AURA API Dashboard</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .card { background: #f5f5f5; padding: 20px; margin: 10px 0; border-radius: 8px; }
                .success { color: green; }
                .error { color: red; }
            </style>
        </head>
        <body>
            <h1>🚀 Enhanced AURA API Dashboard</h1>
            
            <div class="card">
                <h3>API Endpoints</h3>
                <ul>
                    <li><a href="/api/health">GET /api/health</a> - System health</li>
                    <li><a href="/api/metrics">GET /api/metrics</a> - Performance metrics</li>
                    <li>POST /api/parse - Parse single screenplay</li>
                    <li>POST /api/batch/parse - Batch parse screenplays</li>
                </ul>
            </div>
            
            <div class="card">
                <h3>Test the API</h3>
                <button onclick="testHealth()">Test Health</button>
                <button onclick="testParse()">Test Parse</button>
                <button onclick="testBatchParse()">Test Batch Parse</button>
                <div id="results"></div>
            </div>
            
            <script>
                async function testHealth() {
                    const response = await fetch('/api/health');
                    const data = await response.json();
                    showResult('Health: ' + data.status);
                }
                
                async function testParse() {
                    const response = await fetch('/api/parse', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            screenplay: "INT. OFFICE - DAY\\nJohn sits at his desk, typing.\\nHe looks up, surprised.\\nJOHN\\nThis is a test screenplay.",
                            format: "standard"
                        })
                    });
                    const data = await response.json();
                    showResult('Parse: ' + (data.success ? 'SUCCESS' : 'FAILED'));
                }
                
                async function testBatchParse() {
                    const response = await fetch('/api/batch/parse', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            screenplays: [
                                "Screenplay 1 content...",
                                "Screenplay 2 content...",
                                "Screenplay 3 content..."
                            ]
                        })
                    });
                    const data = await response.json();
                    showResult('Batch Parse: ' + data.batch_size + ' screenplays');
                }
                
                function showResult(message) {
                    document.getElementById('results').innerHTML = 
                        '<p class="success">✅ ' + message + '</p>';
                }
            </script>
        </body>
        </html>
        """
        self.wfile.write(dashboard.encode('utf-8'))

def start_server():
    EnhancedAuraAPI.start_time = time.time()
    
    print("🚀 ENHANCED AURA API SERVER STARTING...")
    print("=" * 50)
    print(f"📍 Port: {PORT}")
    print(f"🌐 Dashboard: http://localhost:{PORT}")
    print("🔧 Enhanced Endpoints:")
    print("   - GET  /api/health     - System health with metrics")
    print("   - GET  /api/metrics    - Performance metrics")
    print("   - POST /api/parse      - Single screenplay parsing")
    print("   - POST /api/batch/parse - Batch screenplay parsing")
    print("⏹️  Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        with socketserver.TCPServer(("", PORT), EnhancedAuraAPI) as httpd:
            httpd.serve_forever()
    except OSError as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    start_server()
