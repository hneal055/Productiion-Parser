"""
================================================================================
Production Budget & Risk Management System
Copyright © 2024-2025. All Rights Reserved.

PROPRIETARY AND CONFIDENTIAL
Unauthorized copying, distribution, or use is strictly prohibited.

File: web_app_enhanced.py
Module: Enhanced Web Application
Purpose: Advanced dashboard with real-time analytics
================================================================================
"""
"""
================================================================================
Production Budget & Risk Management System
Copyright © 2024-2025. All Rights Reserved.

PROPRIETARY AND CONFIDENTIAL

This file contains trade secrets and proprietary information. Unauthorized
copying, distribution, modification, or use is strictly prohibited.

File: web_app_enhanced.py
Version: 1.0.0
Last Modified: November 2025

For licensing inquiries: [YOUR_EMAIL]
================================================================================
"""
"""
Enhanced Production Budget & Risk Management Web Application
"""
from flask import Flask, render_template_string, request, redirect, url_for, send_file, flash
import os
import pandas as pd
from werkzeug.utils import secure_filename
from datetime import datetime
import json
import hashlib

from risk_manager import RiskManager
from budget_tool import create_visualizations
from budget_optimizer import find_optimizations

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'data/input'
app.config['OUTPUT_FOLDER'] = 'data/output'
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024
app.secret_key = 'enhanced-prod-budget-2024'

ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

analysis_cache = {}

# Styles
STYLES = """
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
.container { max-width: 1400px; margin: 0 auto; padding: 30px; }
.header { background: white; padding: 30px; border-radius: 15px; margin-bottom: 30px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
h1 { font-size: 2.5em; color: #2c3e50; margin-bottom: 10px; }
.subtitle { color: #666; font-size: 1.1em; }
.nav-menu { background: white; padding: 15px 30px; border-radius: 10px; margin-bottom: 20px; display: flex; gap: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
.nav-link { color: #666; text-decoration: none; padding: 10px 20px; border-radius: 5px; transition: all 0.3s; font-weight: 500; }
.nav-link:hover, .nav-link.active { background: #667eea; color: white; }
.content-box { background: white; padding: 40px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); margin-bottom: 20px; }
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
.stat-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 12px; text-align: center; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3); }
.stat-value { font-size: 2.5em; font-weight: bold; margin: 10px 0; }
.stat-label { font-size: 0.9em; opacity: 0.9; text-transform: uppercase; letter-spacing: 1px; }
.upload-zone { border: 3px dashed #667eea; border-radius: 15px; padding: 80px 40px; text-align: center; background: rgba(102, 126, 234, 0.05); transition: all 0.3s; cursor: pointer; }
.upload-zone:hover { background: rgba(102, 126, 234, 0.1); transform: scale(1.02); }
.upload-icon { font-size: 4em; color: #667eea; margin-bottom: 20px; }
.btn { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 30px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: 600; text-decoration: none; display: inline-block; margin: 5px; transition: all 0.3s; }
.btn:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4); }
.btn-secondary { background: #6c757d; }
.btn-success { background: #28a745; }
table { width: 100%; border-collapse: collapse; margin: 20px 0; }
th, td { text-align: left; padding: 15px; border-bottom: 1px solid #e0e0e0; }
th { background: #f8f9fa; color: #667eea; font-weight: 600; text-transform: uppercase; font-size: 0.9em; }
tr:hover { background: rgba(102, 126, 234, 0.05); }
.alert { padding: 20px; border-radius: 10px; margin-bottom: 20px; display: flex; align-items: center; gap: 15px; }
.alert-success { background: #d4edda; border-left: 4px solid #28a745; color: #155724; }
.alert-error { background: #f8d7da; border-left: 4px solid #dc3545; color: #721c24; }
.alert-info { background: #d1ecf1; border-left: 4px solid #17a2b8; color: #0c5460; }
.badge { padding: 6px 12px; border-radius: 20px; font-size: 0.85em; font-weight: 600; }
.badge-low { background: #d4edda; color: #155724; }
.badge-medium { background: #fff3cd; color: #856404; }
.badge-high { background: #fff0e6; color: #d63900; }
.badge-critical { background: #f8d7da; color: #721c24; }
input[type="file"] { display: none; }
.chart-img { max-width: 100%; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin: 20px 0; }
</style>
"""

@app.route('/')
def index():
    total = len(analysis_cache)
    total_val = sum(a.get('total_budget', 0) for a in analysis_cache.values())
    avg_risk_val = sum(a.get('risk_score', 0) for a in analysis_cache.values()) / max(total, 1)
    savings_val = sum(a.get('potential_savings', 0) for a in analysis_cache.values())
    
    recent = []
    for file_id, data in list(analysis_cache.items())[-5:]:
        recent.append({
            'id': file_id,
            'filename': data.get('filename', 'Unknown'),
            'timestamp': data.get('timestamp', 'Unknown'),
            'total_budget': data.get('total_budget', 0),
            'risk_level': data.get('risk_level', 'Unknown')
        })
    recent.reverse()
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Production Budget Pro</title>
        """ + STYLES + """
    </head>
    <body>
        <div class="container">
            <div class="nav-menu">
                <a href="/" class="nav-link active">🏠 Dashboard</a>
                <a href="/upload" class="nav-link">📤 Upload</a>
                <a href="/history" class="nav-link">📋 History</a>
            </div>
    """
    
    # Flash messages
    html += """
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ category }}">
                            <strong>{{ '✓' if category == 'success' else '⚠' }}</strong>
                            {{ message }}
                        </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
    """
    
    html += """
            <div class="header">
                <h1>🎬 Production Budget Pro</h1>
                <p class="subtitle">Advanced Budget Analysis & Risk Management</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Total Analyzed</div>
                    <div class="stat-value">""" + str(total) + """</div>
                    <div>Budget files processed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Total Budget Value</div>
                    <div class="stat-value">$""" + f"{total_val/1000:.0f}" + """K</div>
                    <div>Across all projects</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Avg Risk Score</div>
                    <div class="stat-value">""" + f"{avg_risk_val:.1f}" + """/100</div>
                    <div>""" + ('Low' if avg_risk_val < 50 else 'Medium') + """ risk level</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Potential Savings</div>
                    <div class="stat-value">$""" + f"{savings_val/1000:.0f}" + """K</div>
                    <div>Optimization opportunities</div>
                </div>
            </div>
            
            <div class="content-box">
                <h2>Quick Actions</h2>
                <div style="margin-top: 20px;">
                    <a href="/upload" class="btn">📤 Upload New Budget</a>
                    <a href="/history" class="btn btn-secondary">📋 View History</a>
                </div>
            </div>
    """
    
    if recent:
        html += """
            <div class="content-box">
                <h2>Recent Analysis</h2>
                <table>
                    <thead>
                        <tr>
                            <th>File Name</th>
                            <th>Date</th>
                            <th>Budget</th>
                            <th>Risk Level</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        for file in recent:
            html += f"""
                        <tr>
                            <td><strong>{file['filename']}</strong></td>
                            <td>{file['timestamp']}</td>
                            <td>${file['total_budget']:,.2f}</td>
                            <td><span class="badge badge-{file['risk_level'].lower()}">{file['risk_level']}</span></td>
                            <td><a href="/analyze/{file['id']}" class="btn" style="padding: 8px 16px; font-size: 12px;">View</a></td>
                        </tr>
            """
        html += """
                    </tbody>
                </table>
            </div>
        """
    else:
        html += """
            <div class="content-box">
                <div class="alert alert-info">
                    <span>ℹ️</span>
                    <div>
                        <strong>No budgets analyzed yet</strong><br>
                        Upload your first budget to get started
                    </div>
                </div>
            </div>
        """
    
    html += """
        </div>
    </body>
    </html>
    """
    
    return render_template_string(html)

@app.route('/upload')
def upload_page():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Upload Budget</title>
        """ + STYLES + """
    </head>
    <body>
        <div class="container">
            <div class="nav-menu">
                <a href="/" class="nav-link">🏠 Dashboard</a>
                <a href="/upload" class="nav-link active">📤 Upload</a>
                <a href="/history" class="nav-link">📋 History</a>
            </div>
    """
    
    html += """
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ category }}">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
    """
    
    html += """
            <div class="header">
                <h1>Upload Production Budget</h1>
                <p class="subtitle">Upload Excel or CSV file for analysis</p>
            </div>
            
            <div class="content-box">
                <form method="POST" action="/process-upload" enctype="multipart/form-data" id="uploadForm">
                    <div class="upload-zone" id="dropZone" onclick="document.getElementById('fileInput').click()">
                        <div class="upload-icon">📁</div>
                        <h2>Drag & Drop your budget file here</h2>
                        <p style="color: #666; margin: 15px 0;">or click to browse</p>
                        <input type="file" id="fileInput" name="file" accept=".xlsx,.xls,.csv" required onchange="showFile()">
                        <div id="fileInfo" style="margin-top: 20px; display: none;">
                            <p style="color: #667eea; font-weight: 600;" id="fileName"></p>
                        </div>
                    </div>
                    <div style="text-align: center; margin-top: 30px;">
                        <button type="submit" class="btn" id="analyzeBtn" disabled>Analyze Budget</button>
                        <a href="/" class="btn btn-secondary">Cancel</a>
                    </div>
                </form>
            </div>
        </div>
        
        <script>
            function showFile() {
                const input = document.getElementById('fileInput');
                const fileInfo = document.getElementById('fileInfo');
                const fileName = document.getElementById('fileName');
                const btn = document.getElementById('analyzeBtn');
                
                if (input.files.length > 0) {
                    fileName.textContent = '📄 ' + input.files[0].name;
                    fileInfo.style.display = 'block';
                    btn.disabled = false;
                }
            }
            
            const dropZone = document.getElementById('dropZone');
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(e => {
                dropZone.addEventListener(e, evt => evt.preventDefault(), false);
            });
            
            dropZone.addEventListener('drop', e => {
                document.getElementById('fileInput').files = e.dataTransfer.files;
                showFile();
            }, false);
        </script>
    </body>
    </html>
    """
    
    return render_template_string(html)

@app.route('/process-upload', methods=['POST'])
def process_upload():
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('upload_page'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('upload_page'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_id = hashlib.md5(f"{timestamp}{filename}".encode()).hexdigest()[:12]
        unique_filename = f"{file_id}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(filepath)
        
        try:
            df = pd.read_excel(filepath) if filename.endswith(('.xlsx', '.xls')) else pd.read_csv(filepath)
            total_budget = df["Amount"].sum()
            
            risk_manager = RiskManager()
            risk_analysis = risk_manager.analyze_risks(df)
            optimizations = find_optimizations(df)
            
            analysis_cache[file_id] = {
                'id': file_id,
                'filename': filename,
                'filepath': filepath,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'total_budget': float(total_budget),
                'line_items': len(df),
                'risk_score': risk_analysis['summary']['overall_risk_score'],
                'risk_level': risk_analysis['summary']['risk_level'],
                'potential_savings': optimizations['potential_savings'],
                'df': df
            }
            
            flash('Budget analyzed successfully!', 'success')
            return redirect(url_for('view_analysis', file_id=file_id))
            
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('upload_page'))
    
    flash('Invalid file type', 'error')
    return redirect(url_for('upload_page'))

@app.route('/analyze/<file_id>')
def view_analysis(file_id):
    if file_id not in analysis_cache:
        flash('Analysis not found', 'error')
        return redirect(url_for('index'))
    
    data = analysis_cache[file_id]
    df = data['df']
    
    departments = {}
    if "Department" in df.columns:
        total = df["Amount"].sum()
        for dept, group in df.groupby("Department"):
            dept_total = group["Amount"].sum()
            departments[dept] = {
                "amount": float(dept_total),
                "percentage": float(dept_total / total * 100),
                "items": len(group)
            }
    
    risk_manager = RiskManager()
    risk_analysis = risk_manager.analyze_risks(df)
    
    vis_paths = create_visualizations(df, app.config['OUTPUT_FOLDER'])
    visualizations = []
    for key, path in vis_paths.items():
        if os.path.exists(path):
            visualizations.append({
                'title': key.replace('_', ' ').title(),
                'filename': os.path.basename(path)
            })
    
    report_file = f"analysis_{file_id}.json"
    report_path = os.path.join(app.config['OUTPUT_FOLDER'], report_file)
    with open(report_path, 'w') as f:
        json.dump({
            'filename': data['filename'],
            'total_budget': data['total_budget'],
            'risk_analysis': risk_analysis['summary']
        }, f, indent=2)
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Analysis Results</title>
        """ + STYLES + """
    </head>
    <body>
        <div class="container">
            <div class="nav-menu">
                <a href="/" class="nav-link">🏠 Dashboard</a>
                <a href="/upload" class="nav-link">📤 Upload</a>
                <a href="/history" class="nav-link">📋 History</a>
            </div>
            
            <div class="header">
                <h1>📊 Analysis Results</h1>
                <p class="subtitle">""" + data['filename'] + """</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Total Budget</div>
                    <div class="stat-value">$""" + f"{data['total_budget']:.0f}" + """</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Line Items</div>
                    <div class="stat-value">""" + str(data['line_items']) + """</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Departments</div>
                    <div class="stat-value">""" + str(len(departments)) + """</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Risk Level</div>
                    <div class="stat-value">""" + data['risk_level'] + """</div>
                </div>
            </div>
            
            <div class="content-box">
                <h2>Department Breakdown</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Department</th>
                            <th>Amount</th>
                            <th>Percentage</th>
                            <th>Items</th>
                        </tr>
                    </thead>
                    <tbody>
    """
    
    for dept, dept_data in departments.items():
        html += f"""
                        <tr>
                            <td>{dept}</td>
                            <td>${dept_data['amount']:,.2f}</td>
                            <td>{dept_data['percentage']:.1f}%</td>
                            <td>{dept_data['items']}</td>
                        </tr>
        """
    
    html += """
                    </tbody>
                </table>
            </div>
            
            <div class="content-box">
                <h2>Risk Analysis</h2>
                <p>Overall Risk Score: <strong>""" + f"{data['risk_score']:.1f}" + """/100</strong> (""" + data['risk_level'] + """)</p>
                <table>
                    <thead>
                        <tr>
                            <th>Risk Category</th>
                            <th>Items</th>
                            <th>Amount</th>
                            <th>Percentage</th>
                        </tr>
                    </thead>
                    <tbody>
    """
    
    for cat, cat_data in risk_analysis['summary']['risk_categories'].items():
        if cat_data['count'] > 0:
            html += f"""
                        <tr>
                            <td>{cat.replace('_', ' ').title()}</td>
                            <td>{cat_data['count']}</td>
                            <td>${cat_data['amount']:,.2f}</td>
                            <td>{cat_data['percentage']:.1f}%</td>
                        </tr>
            """
    
    html += """
                    </tbody>
                </table>
            </div>
    """
    
    if visualizations:
        html += """
            <div class="content-box">
                <h2>Visualizations</h2>
        """
        for viz in visualizations:
            html += f"""
                <div style="text-align: center; margin: 30px 0;">
                    <h3>{viz['title']}</h3>
                    <img src="/output/{viz['filename']}" class="chart-img">
                </div>
            """
        html += """
            </div>
        """
    
    html += f"""
            <div style="text-align: center; margin: 30px 0;">
                <a href="/" class="btn">Back to Dashboard</a>
                <a href="/download/{report_file}" class="btn btn-success">Download Report</a>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

@app.route('/history')
def history_page():
    files = list(analysis_cache.values())
    files.reverse()
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Analysis History</title>
        """ + STYLES + """
    </head>
    <body>
        <div class="container">
            <div class="nav-menu">
                <a href="/" class="nav-link">🏠 Dashboard</a>
                <a href="/upload" class="nav-link">📤 Upload</a>
                <a href="/history" class="nav-link active">📋 History</a>
            </div>
            
            <div class="header">
                <h1>📋 Analysis History</h1>
                <p class="subtitle">Previously analyzed budgets</p>
            </div>
    """
    
    if files:
        html += """
            <div class="content-box">
                <table>
                    <thead>
                        <tr>
                            <th>File Name</th>
                            <th>Date</th>
                            <th>Budget</th>
                            <th>Items</th>
                            <th>Risk</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        for file in files:
            html += f"""
                        <tr>
                            <td><strong>{file['filename']}</strong></td>
                            <td>{file['timestamp']}</td>
                            <td>${file['total_budget']:,.2f}</td>
                            <td>{file['line_items']}</td>
                            <td><span class="badge badge-{file['risk_level'].lower()}">{file['risk_level']}</span></td>
                            <td><a href="/analyze/{file['id']}" class="btn" style="padding: 8px 16px;">View</a></td>
                        </tr>
            """
        html += """
                    </tbody>
                </table>
            </div>
        """
    else:
        html += """
            <div class="content-box">
                <div class="alert alert-info">
                    <span>ℹ️</span>
                    <div>No analysis history. <a href="/upload">Upload a budget</a> to get started.</div>
                </div>
            </div>
        """
    
    html += """
        </div>
    </body>
    </html>
    """
    
    return html

@app.route('/output/<filename>')
def serve_output(filename):
    return send_file(os.path.join(app.config['OUTPUT_FOLDER'], filename))

@app.route('/download/<filename>')
def download_report(filename):
    return send_file(os.path.join(app.config['OUTPUT_FOLDER'], filename), as_attachment=True)

if __name__ == '__main__':
    os.makedirs('data/input', exist_ok=True)
    os.makedirs('data/output', exist_ok=True)
    
    print("=" * 70)
    print("🎬 Production Budget Pro - ENHANCED")
    print("=" * 70)
    print("\n✨ Features:")
    print("  • Modern dashboard with analytics")
    print("  • 8-category risk assessment")
    print("  • Budget optimization")
    print("  • Visual reports and charts")
    print("\n🚀 Starting server...")
    print("📱 Open: http://localhost:5000")
    print("⚡ Press CTRL+C to stop")
    print("=" * 70)
    
    app.run(debug=True, port=5000)

