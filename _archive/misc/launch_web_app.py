"""
================================================================================
Production Budget & Risk Management System
Copyright © 2024-2025. All Rights Reserved.

PROPRIETARY AND CONFIDENTIAL

This file contains trade secrets and proprietary information. Unauthorized
copying, distribution, modification, or use is strictly prohibited.

File: launch_web_app.py
Version: 1.0.0
Last Modified: November 2025

For licensing inquiries: [YOUR_EMAIL]
================================================================================
"""
"""
Launcher for the Production Budget Analysis Web Application
----------------------------------------------------------
Simple launcher script to start the web application.
"""
import os
import webbrowser
import threading
import time
import sys

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        import pandas
        import matplotlib
        return True
    except ImportError as e:
        print(f"Missing dependency: {str(e)}")
        print("Please install required packages:")
        print("pip install flask pandas matplotlib")
        return False

def open_browser(port):
    """Open web browser after a short delay"""
    time.sleep(1.5)  # Wait for the server to start
    webbrowser.open(f'http://127.0.0.1:{port}/')

def main():
    """Main entry point"""
    print("=" * 70)
    print("     PRODUCTION BUDGET ANALYSIS WEB APPLICATION LAUNCHER")
    print("=" * 70)
    
    # Check dependencies
    if not check_dependencies():
        print("Missing dependencies. Please install required packages.")
        return 1
    
    # Ensure input and output directories exist
    os.makedirs("data/input", exist_ok=True)
    os.makedirs("data/output", exist_ok=True)
    
    # Set port
    port = 5000
    
    # Determine which web app file to use
    web_app_file = "web_app_simple.py"
    if not os.path.exists(web_app_file):
        web_app_file = "web_app.py"
        if not os.path.exists(web_app_file):
            print("Error: Could not find web application file.")
            print("Please make sure web_app_simple.py or web_app.py exists.")
            return 1
    
    print(f"\nUsing web application file: {web_app_file}")
    
    # Open browser automatically
    print("\nStarting web browser...")
    threading.Thread(target=open_browser, args=(port,)).start()
    
    # Run the Flask app
    print(f"\nStarting web server on http://127.0.0.1:{port}/")
    print("Press Ctrl+C to stop the server.")
    
    # Launch the web app as a subprocess
    import subprocess
    try:
        subprocess.run([sys.executable, web_app_file], check=True)
    except KeyboardInterrupt:
        print("\nWeb server stopped.")
    except subprocess.CalledProcessError:
        print("\nWeb server encountered an error.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

