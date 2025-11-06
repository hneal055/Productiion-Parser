"""
================================================================================
Production Budget & Risk Management System
Copyright © 2024-2025. All Rights Reserved.

PROPRIETARY AND CONFIDENTIAL

This file contains trade secrets and proprietary information. Unauthorized
copying, distribution, modification, or use is strictly prohibited.

File: web_app_simple.py
Version: 1.0.0
Last Modified: November 2025

For licensing inquiries: [YOUR_EMAIL]
================================================================================
"""
"""
Simple Web Application for Production Budget Analysis
------------------------------------------------------
A web interface for budget analysis tools.
"""
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import json
import time
from datetime import datetime
import uuid
import shutil
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, jsonify

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'data/input'
app.config['OUTPUT_FOLDER'] = 'data/output'
app.config['ALLOWED_EXTENSIONS'] = {'xlsx', 'xls', 'csv'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
app.secret_key = os.urandom(24)  # For flash messages

def allowed_file(filename):
    """Check if file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    """Home page with file upload form"""
    # Get list of existing analysis reports
    reports = []
    
    if os.path.exists(app.config['OUTPUT_FOLDER']):
        for file in os.listdir(app.config['OUTPUT_FOLDER']):
            if file.endswith('.html'):
                file_path = os.path.join(app.config['OUTPUT_FOLDER'], file)
                timestamp = os.path.getmtime(file_path)
                date = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
                
                reports.append({
                    'filename': file,
                    'date': date
                })
    
    # Sort reports by date (newest first)
    reports.sort(key=lambda x: x['date'], reverse=True)
    
    return render_template('index.html', reports=reports[:10])

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and start analysis"""
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        # Create a unique filename
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{unique_id}_{file.filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Make sure directory exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Save the uploaded file
        file.save(file_path)
        
        # Start analysis
        return redirect(url_for('analyze', filename=filename))
    
    flash('Invalid file type. Please upload an Excel or CSV file.')
    return redirect(url_for('index'))

@app.route('/analyze/<filename>')
def analyze(filename):
    """Run the budget analysis and show results"""
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(file_path):
        flash("File not found")
        return redirect(url_for('index'))
    
    try:
        # Create a unique output directory for this analysis
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(app.config['OUTPUT_FOLDER'], f"analysis_{timestamp}")
        os.makedirs(output_dir, exist_ok=True)
        
        # Run analysis
        df = pd.read_excel(file_path)
        total_budget = df["Amount"].sum()
        
        # Create visualizations
        vis_paths = {}
        
        # 1. Top budget items
        plt.figure(figsize=(10, 6))
        top_items = df.nlargest(10, "Amount").sort_values("Amount")
        plt.barh(top_items["Description"], top_items["Amount"])
        plt.xlabel("Amount ($)")
        plt.title("Top 10 Budget Items")
        plt.tight_layout()
        
        bar_path = os.path.join(output_dir, f"top_items_{timestamp}.png")
        plt.savefig(bar_path)
        plt.close()
        vis_paths["top_items"] = bar_path
        
        # 2. Department breakdown if available
        if "Department" in df.columns:
            plt.figure(figsize=(8, 8))
            dept_data = df.groupby("Department")["Amount"].sum()
            plt.pie(dept_data, labels=dept_data.index, autopct='%1.1f%%')
            plt.title("Budget by Department")
            plt.axis('equal')
            
            pie_path = os.path.join(output_dir, f"departments_{timestamp}.png")
            plt.savefig(pie_path)
            plt.close()
            vis_paths["departments"] = pie_path
        
        # Create report
        report_data = {
            "filename": filename,
            "total_budget": float(total_budget),
            "line_items": len(df),
            "department_breakdown": {},
            "high_cost_items": []
        }
        
        # Add department data if available
        if "Department" in df.columns:
            report_data["departments"] = df["Department"].nunique()
            for dept, data in df.groupby("Department")["Amount"].agg(["sum", "count"]).iterrows():
                report_data["department_breakdown"][dept] = {
                    "amount": float(data["sum"]),
                    "percentage": float(data["sum"] / total_budget * 100),
                    "item_count": int(data["count"])
                }
        
        # Add high-cost items (>5% of total)
        threshold = total_budget * 0.05
        high_cost = df[df["Amount"] >= threshold].sort_values("Amount", ascending=False)
        for _, row in high_cost.iterrows():
            report_data["high_cost_items"].append({
                "description": row["Description"],
                "department": row.get("Department", "Unknown"),
                "amount": float(row["Amount"]),
                "percentage": float(row["Amount"] / total_budget * 100)
            })
        
        # Generate HTML report
        html_path = generate_html_report(report_data, vis_paths, output_dir, timestamp)
        
        # Copy HTML report to main output folder for easy access
        report_filename = f"budget_analysis_{timestamp}.html"
        shutil.copy2(html_path, os.path.join(app.config['OUTPUT_FOLDER'], report_filename))
        
        # Redirect to the report
        return redirect(url_for('view_report', report_name=report_filename))
        
    except Exception as e:
        flash(f"Error analyzing budget: {str(e)}")
        return redirect(url_for('index'))

@app.route('/reports/<report_name>')
def view_report(report_name):
    """View an analysis report"""
    report_path = os.path.join(app.config['OUTPUT_FOLDER'], report_name)
    
    if not os.path.exists(report_path):
        flash("Report not found")
        return redirect(url_for('index'))
    
    with open(report_path, "r") as f:
        report_html = f.read()
    
    return report_html

@app.route('/output/<path:filename>')
def output_files(filename):
    """Serve files from the output directory"""
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

def generate_html_report(report_data, vis_paths, output_dir, timestamp):
    """Generate an HTML report from analysis data"""
    # Create HTML content
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Production Budget Analysis</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1, h2 {{ color: #2c3e50; }}
            .section {{ margin-bottom: 30px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f2f2f2; }}
            tr:hover {{ background-color: #f5f5f5; }}
            .chart {{ margin: 20px 0; max-width: 100%; }}
            .top-bar {{ background-color: #2c3e50; color: white; padding: 10px; margin-bottom: 20px; }}
            .top-bar a {{ color: white; margin-right: 15px; text-decoration: none; }}
            .top-bar a:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <div class="top-bar">
            <a href="/">Home</a>
            <span>Budget Analysis Tool</span>
        </div>
        
        <h1>Production Budget Analysis</h1>
        <p>File: {report_data['filename']}</p>
        <p>Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        
        <div class="section">
            <h2>Budget Summary</h2>
            <p>Total Budget: <strong>${report_data['total_budget']:,.2f}</strong></p>
            <p>Number of Line Items: <strong>{report_data['line_items']}</strong></p>
        </div>
    """
    
    # Add department breakdown if available
    if report_data["department_breakdown"]:
        html += """
        <div class="section">
            <h2>Department Breakdown</h2>
            <table>
                <tr>
                    <th>Department</th>
                    <th>Amount</th>
                    <th>Percentage</th>
                    <th>Items</th>
                </tr>
        """
        
        # Sort departments by amount
        sorted_depts = sorted(report_data["department_breakdown"].items(), 
                              key=lambda x: x[1]["amount"], 
                              reverse=True)
        
        for dept, data in sorted_depts:
            html += f"""
                <tr>
                    <td>{dept}</td>
                    <td>${data['amount']:,.2f}</td>
                    <td>{data['percentage']:.1f}%</td>
                    <td>{data['item_count']}</td>
                </tr>
            """
        
        html += """
            </table>
        </div>
        """
    
    # Add high-cost items
    if report_data["high_cost_items"]:
        html += """
        <div class="section">
            <h2>High-Cost Items (>5% of budget)</h2>
            <table>
                <tr>
                    <th>Description</th>
                    <th>Department</th>
                    <th>Amount</th>
                    <th>Percentage</th>
                </tr>
        """
        
        for item in report_data["high_cost_items"]:
            html += f"""
                <tr>
                    <td>{item['description']}</td>
                    <td>{item['department']}</td>
                    <td>${item['amount']:,.2f}</td>
                    <td>{item['percentage']:.1f}%</td>
                </tr>
            """
        
        html += """
            </table>
        </div>
        """
    
    # Add visualizations
    if vis_paths:
        html += """
        <div class="section">
            <h2>Visualizations</h2>
        """
        
        for desc, path in vis_paths.items():
            if os.path.exists(path):
                # Copy image to output directory
                img_name = os.path.basename(path)
                shutil.copy2(path, os.path.join(app.config['OUTPUT_FOLDER'], img_name))
                
                html += f"""
            <div>
                <h3>{desc.replace('_', ' ').title().replace('Pie', 'Chart').replace('Bar', 'Chart')}</h3>
                <img src="/output/{img_name}" alt="{desc}" class="chart">
            </div>
                """
        
        html += """
        </div>
        """
    
    html += """
    </body>
    </html>
    """
    
    # Save the HTML report
    report_path = os.path.join(output_dir, f"report_{timestamp}.html")
    with open(report_path, "w") as f:
        f.write(html)
    
    return report_path

def create_templates():
    """Create the HTML templates folder and files"""
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    # Create index.html template
    index_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Production Budget Analysis Tool</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background-color: #2c3e50; color: white; padding: 20px; margin-bottom: 30px; }
        .card { background-color: white; border-radius: 5px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .card h2 { margin-top: 0; color: #2c3e50; }
        .btn { background-color: #3498db; color: white; padding: 10px 15px; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; }
        .btn:hover { background-color: #2980b9; }
        .btn-secondary { background-color: #95a5a6; }
        .btn-secondary:hover { background-color: #7f8c8d; }
        .reports { margin-top: 30px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { text-align: left; padding: 12px 8px; border-bottom: 1px solid #ddd; }
        th { background-color: #f2f2f2; color: #2c3e50; }
        tr:hover { background-color: #f5f5f5; }
        .flash-message { background-color: #e74c3c; color: white; padding: 10px; border-radius: 5px; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <h1>Production Budget Analysis Tool</h1>
            <p>Upload and analyze production budgets for film and TV projects</p>
        </div>
    </div>
    
    <div class="container">
        {% if get_flashed_messages() %}
        <div class="flash-message">
            {% for message in get_flashed_messages() %}
            <p>{{ message }}</p>
            {% endfor %}
        </div>
        {% endif %}
        
        <div class="card">
            <h2>Analyze Budget</h2>
            <p>Upload a production budget file to analyze risks and cost distribution.</p>
            <form action="/upload" method="post" enctype="multipart/form-data">
                <p><input type="file" name="file" accept=".xlsx,.xls,.csv" required></p>
                <p><button type="submit" class="btn">Analyze Budget</button></p>
            </form>
        </div>
        
        {% if reports %}
        <div class="reports">
            <h2>Recent Reports</h2>
            <table>
                <tr>
                    <th>Date</th>
                    <th>Actions</th>
                </tr>
                {% for report in reports %}
                <tr>
                    <td>{{ report.date }}</td>
                    <td><a href="/reports/{{ report.filename }}" class="btn btn-secondary">View Report</a></td>
                </tr>
                {% endfor %}
            </table>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""
    
    with open(os.path.join(templates_dir, 'index.html'), 'w') as f:
        f.write(index_template)

if __name__ == "__main__":
    # Create templates directory and files
    create_templates()
    
    # Ensure the upload and output directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    
    # Run the Flask application
    app.run(debug=True)

