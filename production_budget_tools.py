"""
================================================================================
Production Budget & Risk Management System
Copyright © 2024-2025. All Rights Reserved.

PROPRIETARY AND CONFIDENTIAL

This file contains trade secrets and proprietary information. Unauthorized
copying, distribution, modification, or use is strictly prohibited.

File: production_budget_tools.py
Version: 1.0.0
Last Modified: November 2025

For licensing inquiries: [YOUR_EMAIL]
================================================================================
"""
"""
Production Budget Analysis Tools - Main Menu
-------------------------------------------
Unified interface for all production budget analysis tools.
"""
import os
import sys
from datetime import datetime

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the application header"""
    clear_screen()
    print("=" * 70)
    print("                PRODUCTION BUDGET ANALYSIS TOOLS")
    print("=" * 70)
    print()

def print_menu():
    """Print the main menu options"""
    print("MAIN MENU:")
    print("  1. Analyze a budget file")
    print("  2. Compare multiple budget files")
    print("  3. Optimize a budget")
    print("  4. Start web interface")
    print("  5. View recent reports")
    print("  0. Exit")
    print()

def get_choice():
    """Get user menu choice"""
    while True:
        try:
            choice = input("Enter your choice (0-5): ")
            return int(choice)
        except ValueError:
            print("Please enter a number between 0 and 5.")

def get_file_path(prompt, check_exists=True, multiple=False):
    """Get a file path from the user"""
    if multiple:
        print(prompt)
        print("Enter one file path per line. Enter a blank line when done.")
        paths = []
        while True:
            path = input("> ").strip()
            if not path:
                if paths:
                    break
                print("Please enter at least one file path.")
                continue
                
            if check_exists and not os.path.exists(path):
                print(f"File not found: {path}")
                continue
                
            paths.append(path)
        return paths
    else:
        while True:
            path = input(prompt).strip()
            if not path:
                print("Please enter a file path.")
                continue
                
            if check_exists and not os.path.exists(path):
                print(f"File not found: {path}")
                continue
                
            return path

def get_output_dir():
    """Get output directory from user or use default"""
    while True:
        path = input("Enter output directory (default: data/output): ").strip()
        if not path:
            path = "data/output"
        
        try:
            os.makedirs(path, exist_ok=True)
            return path
        except Exception as e:
            print(f"Error creating directory: {str(e)}")

def analyze_budget():
    """Run the budget analysis tool"""
    print_header()
    print("BUDGET ANALYSIS")
    print("This tool analyzes a production budget file and identifies risks.")
    print()
    
    file_path = get_file_path("Enter the path to the budget Excel file: ")
    output_dir = get_output_dir()
    
    print("\nRunning analysis...")
    try:
        import enhanced_budget_tool_fixed
        enhanced_budget_tool_fixed.analyze_budget(file_path, output_dir)
    except ImportError:
        print("Enhanced budget tool not found. Using basic analysis...")
        import subprocess
        subprocess.run(["python", "budget_analyzer.py", file_path])
    
    input("\nPress Enter to return to the main menu...")

def compare_budgets():
    """Run the budget comparison tool"""
    print_header()
    print("BUDGET COMPARISON")
    print("This tool compares multiple production budget files side by side.")
    print()
    
    file_paths = get_file_path("Enter paths to the budget Excel files to compare:", multiple=True)
    output_dir = get_output_dir()
    
    print("\nRunning comparison...")
    try:
        import budget_comparison_fixed
        budget_comparison_fixed.compare_budgets(file_paths, output_dir)
    except ImportError:
        print("Budget comparison tool not found.")
        print("Please make sure budget_comparison_fixed.py is in the current directory.")
    
    input("\nPress Enter to return to the main menu...")

def optimize_budget():
    """Run the budget optimization tool"""
    print_header()
    print("BUDGET OPTIMIZATION")
    print("This tool suggests optimizations for a production budget based on industry benchmarks.")
    print()
    
    file_path = get_file_path("Enter the path to the budget Excel file: ")
    output_dir = get_output_dir()
    
    print("\nRunning optimization...")
    try:
        import budget_optimizer_fixed
        budget_optimizer_fixed.optimize_budget(file_path, output_dir)
    except ImportError:
        print("Budget optimizer tool not found.")
        print("Please make sure budget_optimizer_fixed.py is in the current directory.")
    
    input("\nPress Enter to return to the main menu...")

def start_web_interface():
    """Start the web interface"""
    print_header()
    print("STARTING WEB INTERFACE")
    print("This will start a local web server for the budget analysis tools.")
    print("The server will run until you press Ctrl+C.")
    print()
    
    try:
        import web_app
        print("Starting web server... Press Ctrl+C to stop.")
        web_app.app.run(debug=False)
    except ImportError:
        print("Web interface not found.")
        print("Please make sure web_app.py is in the current directory.")
    except KeyboardInterrupt:
        print("\nWeb server stopped.")
    
    input("\nPress Enter to return to the main menu...")

def view_reports():
    """View recent reports"""
    print_header()
    print("RECENT REPORTS")
    output_dir = "data/output"
    
    if not os.path.exists(output_dir):
        print(f"No reports found. The directory {output_dir} does not exist.")
        input("\nPress Enter to return to the main menu...")
        return
    
    reports = []
    for file in os.listdir(output_dir):
        if file.endswith(".html"):
            file_path = os.path.join(output_dir, file)
            reports.append((file, os.path.getmtime(file_path), file_path))
    
    if not reports:
        print("No reports found.")
        input("\nPress Enter to return to the main menu...")
        return
    
    # Sort by modification time (newest first)
    reports.sort(key=lambda x: x[1], reverse=True)
    
    print(f"Found {len(reports)} reports:\n")
    for i, (file, mtime, _) in enumerate(reports[:10], 1):
        timestamp = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
        print(f"{i}. {file} - {timestamp}")
    
    if len(reports) > 10:
        print(f"... and {len(reports) - 10} more.")
    
    print("\nChoose a report to open, or press Enter to return to the main menu.")
    choice = input("Enter report number: ").strip()
    
    if choice and choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(reports[:10]):
            report_path = reports[idx][2]
            try:
                import webbrowser
                webbrowser.open(f"file://{os.path.abspath(report_path)}")
                print(f"Opened {reports[idx][0]} in web browser.")
            except Exception as e:
                print(f"Error opening report: {str(e)}")
                print(f"Report path: {report_path}")
    
    input("\nPress Enter to return to the main menu...")

def main():
    """Main application entry point"""
    while True:
        print_header()
        print_menu()
        
        choice = get_choice()
        
        if choice == 0:
            print("Exiting. Thank you for using Production Budget Analysis Tools!")
            break
        elif choice == 1:
            analyze_budget()
        elif choice == 2:
            compare_budgets()
        elif choice == 3:
            optimize_budget()
        elif choice == 4:
            start_web_interface()
        elif choice == 5:
            view_reports()
        else:
            print("Invalid choice. Please try again.")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()

