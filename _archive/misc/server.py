import http.server
import socketserver
import os
import webbrowser
import sys

# Try different ports if 5500 is busy
PORTS = [5500, 5501, 5502, 8000, 8080]

def start_server(port):
    # Get the current directory where this script is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)

    print("=" * 60)
    print("AURA ENTERPRISE DASHBOARD SERVER")
    print("=" * 60)
    print(f"Current directory: {current_dir}")
    print(f"Files in directory: {os.listdir('.')}")
    print("=" * 60)

    # Create a custom handler to show more info
    class CustomHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            print(f"[{self.log_date_time_string()}] {format % args}")

    try:
        # Start the server
        with socketserver.TCPServer(("", port), CustomHandler) as httpd:
            print(f"Server running at:")
            print(f"   http://localhost:{port}")
            print(f"   http://127.0.0.1:{port}")
            print("=" * 60)
            print("Starting server...")
            
            # Try to open browser automatically
            try:
                webbrowser.open(f'http://localhost:{port}')
                print("Browser opened automatically")
            except:
                print("Could not open browser automatically")
                print(f"Please manually visit: http://localhost:{port}")
            
            print("=" * 60)
            
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nServer stopped by user")
                
    except OSError as e:
        if "10048" in str(e) or "already in use" in str(e).lower():
            print(f"Port {port} is already in use. Trying next port...")
            return False
        else:
            raise e
    return True

# Try different ports
for port in PORTS:
    print(f"Trying port {port}...")
    if start_server(port):
        break
else:
    print("Could not find an available port. Please close other servers and try again.")
    input("Press Enter to exit...")