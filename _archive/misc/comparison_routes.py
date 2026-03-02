"""
Budget Comparison Routes - ADD TO web_app_enhanced_PATH_A.py

This file contains the new routes and functions needed for budget comparison.
Add these to your existing Flask app.

Copyright © 2024-2025. All Rights Reserved.
PROPRIETARY AND CONFIDENTIAL
"""

# ADD THESE IMPORTS at the top of your file (after existing imports):
from budget_comparison import compare_budgets
from comparison_charts import generate_comparison_chart_html

# ADD THIS GLOBAL VARIABLE (after analysis_cache = {}):
# Store budget history for each session
budget_history = {}


# ADD THIS ROUTE - Budget History Page
@app.route('/budget-history')
def budget_history_page():
    """Display list of uploaded budgets for comparison"""
    session_id = request.cookies.get('session_id', 'default')
    history = budget_history.get(session_id, [])
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Budget History - Comparison Tool</title>
        <link rel="stylesheet" href="/static/css/modern-styles.css">
    </head>
    <body>
        <div class="container">
            <div class="header fade-in">
                <h1>📊 Budget History & Comparison</h1>
                <p>Select two budgets to compare side-by-side</p>
            </div>
            
            <div class="section fade-in">
                {generate_history_html(history)}
            </div>
            
            <div class="btn-group fade-in">
                <a href="/" class="btn btn-primary">🏠 Back to Dashboard</a>
                <a href="/upload" class="btn btn-success">➕ Upload New Budget</a>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html


# ADD THIS HELPER FUNCTION
def generate_history_html(history):
    """Generate HTML for budget history list"""
    if not history:
        return """
        <div class="alert alert-info">
            <h3>📂 No budgets uploaded yet</h3>
            <p>Upload at least 2 budgets to start comparing them.</p>
            <a href="/" class="btn btn-primary">Upload Your First Budget</a>
        </div>
        """
    
    if len(history) < 2:
        return f"""
        <div class="alert alert-warning">
            <h3>📂 You have {len(history)} budget</h3>
            <p>Upload at least one more budget to enable comparisons.</p>
            <a href="/" class="btn btn-primary">Upload Another Budget</a>
        </div>
        
        <div class="budget-list">
            <h3>Your Budgets:</h3>
            <ul>
                <li><strong>{history[0]['name']}</strong> - Uploaded on {history[0]['timestamp']}</li>
            </ul>
        </div>
        """
    
    # Generate comparison form
    html = """
    <div class="comparison-form-card">
        <h2>🔄 Compare Two Budgets</h2>
        <form action="/compare" method="post" class="comparison-form">
            <div class="form-row">
                <div class="form-group">
                    <label for="budget1">First Budget:</label>
                    <select name="budget1_id" id="budget1" class="form-control" required>
                        <option value="">Select first budget...</option>
    """
    
    for budget in history:
        html += f"""
                        <option value="{budget['id']}">{budget['name']} (${budget['total']:,.0f})</option>
        """
    
    html += """
                    </select>
                </div>
                
                <div class="comparison-arrow">→</div>
                
                <div class="form-group">
                    <label for="budget2">Second Budget:</label>
                    <select name="budget2_id" id="budget2" class="form-control" required>
                        <option value="">Select second budget...</option>
    """
    
    for budget in history:
        html += f"""
                        <option value="{budget['id']}">{budget['name']} (${budget['total']:,.0f})</option>
        """
    
    html += """
                    </select>
                </div>
            </div>
            
            <button type="submit" class="btn btn-primary btn-large">
                🔍 Compare Budgets
            </button>
        </form>
    </div>
    
    <div class="section">
        <h3>📂 Your Budget History</h3>
        <div class="budget-grid">
    """
    
    for budget in reversed(history):  # Most recent first
        html += f"""
            <div class="budget-card">
                <div class="budget-card-header">
                    <h4>{budget['name']}</h4>
                    <span class="budget-badge">${budget['total']:,.0f}</span>
                </div>
                <div class="budget-card-body">
                    <p><strong>Items:</strong> {budget['items']}</p>
                    <p><strong>Uploaded:</strong> {budget['timestamp']}</p>
                </div>
                <div class="budget-card-footer">
                    <a href="/view-analysis/{budget['id']}" class="btn btn-sm btn-secondary">View Details</a>
                </div>
            </div>
        """
    
    html += """
        </div>
    </div>
    """
    
    return html


# ADD THIS ROUTE - Compare Budgets
@app.route('/compare', methods=['POST'])
def compare_budgets_route():
    """Compare two selected budgets"""
    try:
        budget1_id = request.form.get('budget1_id')
        budget2_id = request.form.get('budget2_id')
        
        if not budget1_id or not budget2_id:
            flash('Please select two budgets to compare', 'error')
            return redirect(url_for('budget_history_page'))
        
        if budget1_id == budget2_id:
            flash('Please select two different budgets', 'error')
            return redirect(url_for('budget_history_page'))
        
        # Get budgets from cache
        if budget1_id not in analysis_cache or budget2_id not in analysis_cache:
            flash('Budget not found. Please re-upload.', 'error')
            return redirect(url_for('budget_history_page'))
        
        budget1_data = analysis_cache[budget1_id]
        budget2_data = analysis_cache[budget2_id]
        
        # Perform comparison
        comparison_result = compare_budgets(
            budget1_data['df'],
            budget2_data['df'],
            budget1_data['filename'],
            budget2_data['filename']
        )
        
        # Store comparison result
        comparison_id = f"comp_{budget1_id}_{budget2_id}"
        analysis_cache[comparison_id] = {
            'comparison': comparison_result,
            'budget1_id': budget1_id,
            'budget2_id': budget2_id,
            'timestamp': datetime.now()
        }
        
        # Redirect to comparison view
        return redirect(url_for('view_comparison', comparison_id=comparison_id))
        
    except Exception as e:
        flash(f'Error comparing budgets: {str(e)}', 'error')
        import traceback
        traceback.print_exc()
        return redirect(url_for('budget_history_page'))


# ADD THIS ROUTE - View Comparison Results
@app.route('/comparison/<comparison_id>')
def view_comparison(comparison_id):
    """Display detailed comparison results"""
    if comparison_id not in analysis_cache:
        flash('Comparison not found', 'error')
        return redirect(url_for('budget_history_page'))
    
    try:
        comp_data = analysis_cache[comparison_id]
        comparison = comp_data['comparison']
        
        # Generate HTML
        html = generate_comparison_html(comparison)
        
        return html
        
    except Exception as e:
        flash(f'Error displaying comparison: {str(e)}', 'error')
        import traceback
        traceback.print_exc()
        return redirect(url_for('budget_history_page'))


# ADD THIS HELPER FUNCTION
def generate_comparison_html(comparison: Dict) -> str:
    """Generate complete HTML page for comparison results"""
    
    # Summary metrics HTML
    total_change_color = 'red' if comparison['total_change'] > 0 else 'green'
    total_change_icon = '⬆' if comparison['total_change'] > 0 else '⬇'
    
    summary_html = f"""
    <div class="comparison-summary-grid">
        <div class="comparison-summary-card">
            <h3>{comparison['budget1_name']}</h3>
            <div class="big-number">${comparison['budget1_total']:,.0f}</div>
            <p>{comparison['budget1_items']} line items</p>
        </div>
        
        <div class="comparison-arrow-card">
            <div class="change-indicator {total_change_color}">
                {total_change_icon} {abs(comparison['percent_change']):.1f}%
            </div>
            <p style="font-size: 18px; margin-top: 10px;">
                ${abs(comparison['total_change']):,.0f}
            </p>
        </div>
        
        <div class="comparison-summary-card">
            <h3>{comparison['budget2_name']}</h3>
            <div class="big-number">${comparison['budget2_total']:,.0f}</div>
            <p>{comparison['budget2_items']} line items</p>
        </div>
    </div>
    """
    
    # Insights HTML
    insights_html = '<div class="section fade-in"><h2>💡 Key Insights</h2><div class="insights-list">'
    for i, insight in enumerate(comparison.get('insights', []), 1):
        icon = '🔴' if 'increased' in insight.lower() else ('🟢' if 'decreased' in insight.lower() else '💡')
        insights_html += f"""
        <div class="insight-card">
            <div class="insight-icon">{icon}</div>
            <div class="insight-text">{insight}</div>
        </div>
        """
    insights_html += '</div></div>'
    
    # Department changes table
    dept_table = '<div class="section fade-in"><h2>🏢 Department Changes</h2><div class="table-responsive"><table class="comparison-table">'
    dept_table += """
    <thead>
        <tr>
            <th>Department</th>
            <th>{}</th>
            <th>{}</th>
            <th>Change ($)</th>
            <th>Change (%)</th>
            <th>Status</th>
        </tr>
    </thead>
    <tbody>
    """.format(comparison['budget1_name'], comparison['budget2_name'])
    
    dept_changes = comparison.get('department_changes', {})
    sorted_depts = sorted(dept_changes.items(), 
                         key=lambda x: abs(x[1]['difference']), 
                         reverse=True)
    
    for dept, data in sorted_depts:
        change_class = 'increase' if data['difference'] > 0 else ('decrease' if data['difference'] < 0 else 'unchanged')
        change_icon = '🔴' if data['difference'] > 0 else ('🟢' if data['difference'] < 0 else '⚪')
        
        dept_table += f"""
        <tr class="{change_class}">
            <td><strong>{dept}</strong></td>
            <td>${data['budget1_amount']:,.0f}</td>
            <td>${data['budget2_amount']:,.0f}</td>
            <td>${abs(data['difference']):,.0f}</td>
            <td>{abs(data['percent_change']):.1f}%</td>
            <td>{change_icon} {data['status'].capitalize()}</td>
        </tr>
        """
    
    dept_table += '</tbody></table></div></div>'
    
    # New items section
    new_items_html = ''
    if comparison.get('total_new_items', 0) > 0:
        new_items_html = f"""
        <div class="section fade-in">
            <h2>➕ New Items in {comparison['budget2_name']}</h2>
            <p class="section-subtitle">
                {comparison['total_new_items']} new line items added
                {' (showing top 10)' if comparison['total_new_items'] > 10 else ''}
            </p>
            <div class="table-responsive">
                <table class="comparison-table">
                    <thead>
                        <tr>
                            <th>Description</th>
                            <th>Department</th>
                            <th>Category</th>
                            <th>Amount</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for item in comparison.get('new_items', []):
            new_items_html += f"""
                        <tr class="new-item">
                            <td>{item['description']}</td>
                            <td>{item['department']}</td>
                            <td>{item['category']}</td>
                            <td>${item['amount']:,.0f}</td>
                        </tr>
            """
        
        new_items_html += """
                    </tbody>
                </table>
            </div>
        </div>
        """
    
    # Removed items section
    removed_items_html = ''
    if comparison.get('total_removed_items', 0) > 0:
        removed_items_html = f"""
        <div class="section fade-in">
            <h2>➖ Removed Items from {comparison['budget1_name']}</h2>
            <p class="section-subtitle">
                {comparison['total_removed_items']} line items removed
                {' (showing top 10)' if comparison['total_removed_items'] > 10 else ''}
            </p>
            <div class="table-responsive">
                <table class="comparison-table">
                    <thead>
                        <tr>
                            <th>Description</th>
                            <th>Department</th>
                            <th>Category</th>
                            <th>Amount</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for item in comparison.get('removed_items', []):
            removed_items_html += f"""
                        <tr class="removed-item">
                            <td>{item['description']}</td>
                            <td>{item['department']}</td>
                            <td>{item['category']}</td>
                            <td>${item['amount']:,.0f}</td>
                        </tr>
            """
        
        removed_items_html += """
                    </tbody>
                </table>
            </div>
        </div>
        """
    
    # Generate charts HTML
    charts_html = generate_comparison_chart_html(comparison)
    
    # Build complete page
    complete_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Budget Comparison Results</title>
        <link rel="stylesheet" href="/static/css/modern-styles.css">
        <link rel="stylesheet" href="/static/css/comparison-styles.css">
        <script src="/static/js/chart.umd.js"></script>
    </head>
    <body>
        <div class="container">
            <div class="header fade-in">
                <h1>🔄 Budget Comparison Results</h1>
                <p>Comparing {comparison['budget1_name']} vs {comparison['budget2_name']}</p>
            </div>
            
            {summary_html}
            
            {insights_html}
            
            {charts_html}
            
            {dept_table}
            
            {new_items_html}
            
            {removed_items_html}
            
            <div class="btn-group fade-in" style="margin: 40px 0;">
                <a href="/budget-history" class="btn btn-primary">← Back to History</a>
                <a href="/" class="btn btn-secondary">🏠 Dashboard</a>
                <button onclick="window.print()" class="btn btn-warning">🖨️ Print Report</button>
            </div>
        </div>
    </body>
    </html>
    """
    
    return complete_html


# MODIFY EXISTING analyze_budget ROUTE
# ADD THIS CODE after line where you save to analysis_cache:

# Add to budget history
session_id = request.cookies.get('session_id')
if not session_id:
    session_id = str(uuid.uuid4())
    
if session_id not in budget_history:
    budget_history[session_id] = []

budget_history[session_id].append({
    'id': file_id,
    'name': file.filename,
    'total': data['total_budget'],
    'items': data['line_items'],
    'timestamp': data['timestamp'].strftime('%B %d, %Y at %I:%M %p')
})

# Keep only last 10 budgets per session
if len(budget_history[session_id]) > 10:
    budget_history[session_id] = budget_history[session_id][-10:]


# ADD THIS TO HOMEPAGE (modify existing index route)
# Add a "Compare Budgets" button after the upload form:

"""
<div class="feature-card fade-in">
    <div class="feature-icon">🔄</div>
    <h3>Compare Budgets</h3>
    <p>Upload multiple budgets and compare them side-by-side to track changes over time.</p>
    <a href="/budget-history" class="btn btn-secondary">View History & Compare</a>
</div>
"""


print("""
════════════════════════════════════════════════════════════════════════════════
✅ COMPARISON ROUTES MODULE CREATED
════════════════════════════════════════════════════════════════════════════════

TO INTEGRATE:
1. Copy these routes to web_app_enhanced_PATH_A.py
2. Add the imports at the top
3. Add budget_history = {} global variable
4. Add the routes and helper functions
5. Modify analyze_budget route to save to history
6. Add comparison button to homepage

FILES NEEDED:
- budget_comparison.py (created ✓)
- comparison_charts.py (created ✓)
- comparison-styles.css (will create next)

════════════════════════════════════════════════════════════════════════════════
""")
