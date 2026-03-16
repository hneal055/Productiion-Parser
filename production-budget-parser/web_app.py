"""
================================================================================
Budget Analysis & Risk Management Web Application
NOW WITH SQLITE DATABASE INTEGRATION!
Enhanced with PATH A Features: Interactive Charts, Modern UI, Excel Export
================================================================================
"""

from flask import Flask, request, render_template, redirect, url_for, send_file, flash, jsonify, get_flashed_messages, session
import pandas as pd
import io
import os
import json
import uuid
import html as html_lib
import logging
from datetime import datetime
from functools import wraps

from dotenv import load_dotenv
from flask_migrate import Migrate, upgrade as migrate_upgrade
from werkzeug.utils import secure_filename
import anthropic

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv(override=True)

# API key auth for protected endpoints
from flask_auth import require_api_key
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect, generate_csrf

# Import database
from database_models import db, User, BudgetAnalysis, BudgetLineItem, BudgetComparison, get_recent_analyses

# Import your existing modules
from risk_manager import RiskManager

# Import PATH A modules
from charts_data import prepare_chart_data, generate_chart_html
from excel_exporter import export_to_excel

# Import COMPARISON modules
from budget_comparison import compare_budgets
from comparison_charts import generate_comparison_chart_html

# Initialize Flask app
app = Flask(__name__)
_secret_key = os.environ.get('SECRET_KEY')
if not _secret_key:
    raise RuntimeError('SECRET_KEY is not set. Add it to your .env file.')
app.secret_key = _secret_key

# Session cookie security
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('HTTPS', '').lower() == 'true'

# CSRF protection
csrf = CSRFProtect(app)

# Rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=['200 per day', '60 per hour'],
    storage_uri='memory://'
)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///budget_analysis.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)
migrate_ext = Migrate(app, db)

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'csv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create folders if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def _seed_admin():
    """Create default admin user from env vars if no users exist."""
    from sqlalchemy import inspect as sa_inspect
    try:
        if 'users' not in sa_inspect(db.engine).get_table_names():
            return
        username = os.environ.get('ADMIN_USERNAME', 'admin')
        password = os.environ.get('ADMIN_PASSWORD') or os.environ.get('APP_PASSWORD', '')
        if not password:
            return
        if not User.query.filter_by(username=username).first():
            user = User(username=username, is_admin=True)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            logger.info('Admin user "%s" created.', username)
    except Exception:
        logger.debug('_seed_admin skipped (tables not ready)', exc_info=True)


with app.app_context():
    _migrations_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'migrations')
    if os.path.isdir(_migrations_dir):
        migrate_upgrade()
    else:
        db.create_all()
    _seed_admin()


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return decorated


# Keep check_password for tests and backward compat
def check_password(candidate: str) -> bool:
    """Legacy single-password check — used by test suite."""
    import hmac
    app_password = os.environ.get('APP_PASSWORD', '')
    if not app_password:
        return False
    return hmac.compare_digest(candidate.encode(), app_password.encode())


def find_optimizations(df):
    """
    Find optimization opportunities in the budget
    
    Args:
        df: pandas DataFrame with budget data
        
    Returns:
        list: List of optimization recommendations
    """
    optimizations = []
    
    # Check for vendor consolidation opportunities
    if 'Vendor' in df.columns:
        vendor_counts = df['Vendor'].value_counts()
        if len(vendor_counts) > 10:
            optimizations.append({
                'category': 'Vendor Management',
                'recommendation': f'Consider consolidating vendors. Currently working with {len(vendor_counts)} different vendors.',
                'potential_savings': df['Amount'].sum() * 0.05,  # Estimate 5% savings
                'priority': 'MEDIUM'
            })
    
    # Check for high-cost items
    total = df['Amount'].sum()
    high_cost_items = df[df['Amount'] > total * 0.10]
    
    if len(high_cost_items) > 0:
        optimizations.append({
            'category': 'Cost Review',
            'recommendation': f'Review {len(high_cost_items)} high-cost items that each represent >10% of total budget.',
            'potential_savings': high_cost_items['Amount'].sum() * 0.10,  # Estimate 10% savings on high items
            'priority': 'HIGH'
        })
    
    # Check for duplicate descriptions
    if 'Description' in df.columns:
        duplicates = df[df.duplicated(subset=['Description'], keep=False)]
        if len(duplicates) > 0:
            optimizations.append({
                'category': 'Budget Cleanup',
                'recommendation': f'Found {len(duplicates)} potentially duplicate line items to review.',
                'potential_savings': 0,
                'priority': 'LOW'
            })
    
    # Department-specific recommendations
    if 'Department' in df.columns:
        dept_totals = df.groupby('Department')['Amount'].sum().sort_values(ascending=False)
        if len(dept_totals) > 0:
            top_dept = dept_totals.index[0]
            top_amount = dept_totals.iloc[0]
            if top_amount > total * 0.30:
                optimizations.append({
                    'category': 'Department Analysis',
                    'recommendation': f'{top_dept} represents {(top_amount/total*100):.1f}% of total budget. Consider detailed review.',
                    'potential_savings': top_amount * 0.08,
                    'priority': 'MEDIUM'
                })
    
    return optimizations


def generate_recent_analyses():
    """
    Generate HTML for recent analyses sidebar FROM DATABASE
    """
    html = """
        <div class="recent-analyses">
            <h3>📊 Recent Analyses</h3>
            <table class="recent-table">
                <thead>
                    <tr>
                        <th>File</th>
                        <th>Budget</th>
                        <th>Items</th>
                        <th>Risk</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    # Get recent analyses from database
    recent = get_recent_analyses(limit=10)
    
    for analysis in recent:
        risk_class = f"risk-{analysis.risk_level.lower()}"
        html += f"""
            <tr>
                <td><strong>{analysis.filename}</strong></td>
                <td>${analysis.total_budget:,.2f}</td>
                <td>{analysis.line_items}</td>
                <td><span class="risk-badge {risk_class}">{analysis.risk_level}</span></td>
                <td>
                    <a href="/analysis/{analysis.id}" class="btn btn-primary" style="padding: 8px 16px; font-size: 0.9rem;">
                        View
                    </a>
                </td>
            </tr>
        """
    
    html += """
            </tbody>
        </table>
    </div>
    """
    
    return html


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            return redirect(request.args.get('next') or url_for('index'))
        error = 'Invalid username or password.'
        logger.warning('Failed login attempt for "%s" from %s', username, request.remote_addr)

    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/')
@login_required
def index():
    """Homepage with upload form and recent analyses"""
    recent_analyses_html = generate_recent_analyses()
    # Build flash messages HTML
    messages = get_flashed_messages(with_categories=True)
    flash_html = ''
    for category, message in messages:
        color = '#c0392b' if category == 'error' else '#27ae60'
        flash_html += f'<div style="background:{color};color:white;padding:12px 20px;border-radius:8px;margin-bottom:12px;font-weight:600;">{html_lib.escape(message)}</div>'

    return render_template('home.html', flash_html=flash_html, recent_analyses_html=recent_analyses_html)


@app.route('/upload', methods=['POST'])
@login_required
@limiter.limit('20 per hour')
def upload_file():
    """Handle file upload and analysis - SAVE TO DATABASE"""
    if 'file' not in request.files:
        flash('No file uploaded', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        # Secure the filename
        filename = secure_filename(file.filename)
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Save uploaded file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}_{filename}")
        file.save(filepath)
        
        try:
            # Read CSV
            df = pd.read_csv(filepath)
            
            # Validate required columns
            required_cols = ['Category', 'Amount']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                flash(f'Missing required columns: {", ".join(missing_cols)}', 'error')
                return redirect(url_for('index'))

            # Validate Amount column is numeric
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
            invalid_rows = df['Amount'].isna().sum()
            if invalid_rows == len(df):
                flash('Amount column contains no valid numbers. Please check your CSV file.', 'error')
                return redirect(url_for('index'))
            if invalid_rows > 0:
                logger.warning('CSV %s has %d non-numeric Amount values — they will be treated as 0.', filename, invalid_rows)
                df['Amount'] = df['Amount'].fillna(0)
            
            # Perform risk analysis
            risk_manager = RiskManager()
            risk_analysis = risk_manager.analyze_risks(df)
            
            # Find optimizations
            optimizations = find_optimizations(df)
            
            # Calculate metrics
            total_budget = float(df['Amount'].sum())
            line_items = len(df)
            num_departments = len(set(df['Department'])) if 'Department' in df.columns else 0
            
            # Determine overall risk level
            risk_level = risk_analysis.get('overall_risk', 'MODERATE')
            risk_score = risk_analysis.get('risk_score', 0.0)
            
            # CREATE DATABASE RECORD
            analysis = BudgetAnalysis(
                id=file_id,
                filename=filename,
                total_budget=total_budget,
                line_items=line_items,
                num_departments=num_departments,
                risk_level=risk_level,
                risk_score=risk_score,
                dataframe_json=df.to_json(orient='records'),
                risk_analysis_json=json.dumps(risk_analysis),
                optimizations_json=json.dumps(optimizations),
                upload_date=datetime.now(),
                analysis_timestamp=datetime.now()
            )
            
            db.session.add(analysis)
            
            # Add individual line items
            for idx, row in df.iterrows():
                line_item = BudgetLineItem(
                    analysis_id=file_id,
                    category=str(row.get('Category', '')),
                    department=str(row.get('Department', '')) if 'Department' in df.columns else '',
                    description=str(row.get('Description', '')) if 'Description' in df.columns else '',
                    amount=float(row.get('Amount', 0)),
                    line_number=idx + 1
                )
                db.session.add(line_item)
            
            # Commit to database
            db.session.commit()
            
            flash(f'✅ Analysis complete and saved to database!', 'success')
            return redirect(url_for('view_analysis', file_id=file_id))
            
        except Exception as e:
            db.session.rollback()
            logger.error('Error analyzing file: %s', e, exc_info=True)
            flash('An error occurred while analyzing the file. Please check the file format and try again.', 'error')
            return redirect(url_for('index'))
    
    else:
        flash('Invalid file type. Please upload a CSV file.', 'error')
        return redirect(url_for('index'))


@app.route('/analysis/<file_id>')
@login_required
def view_analysis(file_id):
    """View detailed analysis results FROM DATABASE"""
    # Get analysis from database
    analysis = BudgetAnalysis.query.get(file_id)
    
    if not analysis:
        flash('Analysis not found', 'error')
        return redirect(url_for('index'))
    
    try:
        # Reconstruct DataFrame from JSON
        df = pd.read_json(io.StringIO(analysis.dataframe_json))
        risk_analysis = json.loads(analysis.risk_analysis_json)
        optimizations = json.loads(analysis.optimizations_json)
        
        # Prepare chart data
        chart_data = prepare_chart_data(df)
        
        # Calculate department stats if available
        dept_stats = []
        if 'Department' in df.columns:
            total = df['Amount'].sum()
            for dept in df['Department'].unique():
                dept_df = df[df['Department'] == dept]
                dept_total = dept_df['Amount'].sum()
                dept_stats.append({
                    'name': dept,
                    'total': dept_total,
                    'percentage': (dept_total / total * 100) if total > 0 else 0,
                    'items': len(dept_df)
                })
            dept_stats.sort(key=lambda x: x['total'], reverse=True)
        
        # Generate chart HTML
        charts_html = generate_chart_html(chart_data)
        
        # Extract data safely with defaults
        filename = analysis.filename
        total_budget = analysis.total_budget
        line_items = analysis.line_items
        timestamp = analysis.analysis_timestamp
        
        # Build line items table rows
        line_item_rows = ''
        cols = [c for c in ['Category', 'Department', 'Description', 'Vendor', 'Amount'] if c in df.columns]
        for _, row in df.iterrows():
            cells = ''
            for c in cols:
                val = row[c]
                if c == 'Amount':
                    cells += f'<td style="text-align:right;font-weight:600;">${float(val):,.2f}</td>'
                else:
                    cells += f'<td>{html_lib.escape(str(val))}</td>'
            line_item_rows += f'<tr>{cells}</tr>'

        header_cells = ''.join(f'<th>{html_lib.escape(c)}</th>' for c in cols)

        # Build budget (category) breakdown modal rows
        budget_rows = ''
        num_categories = 0
        if 'Category' in df.columns:
            cat_totals = df.groupby('Category')['Amount'].agg(['sum', 'count']).reset_index()
            cat_totals.columns = ['Category', 'Total', 'Items']
            cat_totals = cat_totals.sort_values('Total', ascending=False)
            num_categories = len(cat_totals)
            for _, row in cat_totals.iterrows():
                pct = (row['Total'] / total_budget * 100) if total_budget > 0 else 0
                bar_w = min(100, pct)
                budget_rows += f"""
                <tr>
                    <td><strong>{html_lib.escape(str(row['Category']))}</strong></td>
                    <td style="text-align:right;font-weight:600;">${row['Total']:,.2f}</td>
                    <td style="text-align:right;">{int(row['Items'])}</td>
                    <td style="min-width:160px;">
                        <div style="background:#e8f5e9;border-radius:4px;height:10px;overflow:hidden;">
                            <div style="width:{bar_w:.1f}%;background:#27ae60;height:100%;border-radius:4px;"></div>
                        </div>
                        <span style="font-size:0.8rem;color:#555;">{pct:.1f}%</span>
                    </td>
                </tr>"""

        # Build risk modal content
        risk_summary = risk_analysis.get('summary', {})
        risk_score = risk_summary.get('overall_risk_score', 0)
        risk_metrics = risk_analysis.get('metrics', {})
        risk_amount = risk_metrics.get('risk_amount', 0)
        risk_pct = risk_metrics.get('risk_percentage', 0)
        risk_level_label = risk_summary.get('risk_level', analysis.risk_level)

        risk_level_color = {'low': '#27ae60', 'moderate': '#f39c12', 'high': '#e74c3c', 'critical': '#8e0000'}.get(risk_level_label.lower(), '#f39c12')

        # Category rows
        risk_cat_rows = ''
        for cat_key, cat_data in risk_summary.get('risk_categories', {}).items():
            if cat_data['count'] == 0:
                continue
            label = cat_key.replace('_', ' ').title()
            pct = cat_data.get('percentage', 0)
            bar_w = min(100, pct)
            desc = cat_data.get('description', '')
            risk_cat_rows += f"""
            <tr>
                <td>
                    <strong>{html_lib.escape(label)}</strong>
                    <div style="font-size:0.78rem;color:#888;margin-top:2px;">{html_lib.escape(desc)}</div>
                </td>
                <td style="text-align:right;">{cat_data['count']}</td>
                <td style="text-align:right;font-weight:600;">${cat_data['amount']:,.2f}</td>
                <td style="min-width:140px;">
                    <div style="background:#fce4e4;border-radius:4px;height:10px;overflow:hidden;">
                        <div style="width:{bar_w:.1f}%;background:#e74c3c;height:100%;border-radius:4px;"></div>
                    </div>
                    <span style="font-size:0.78rem;color:#555;">{pct:.1f}%</span>
                </td>
            </tr>"""

        # Top risk items rows
        risk_item_rows = ''
        for item in risk_summary.get('high_risk_items', []):
            item_pct = item.get('percentage', 0)
            risk_item_rows += f"""
            <tr>
                <td>{html_lib.escape(str(item.get('description', 'Unknown')))}</td>
                <td>{html_lib.escape(str(item.get('department', '—')))}</td>
                <td style="text-align:right;font-weight:600;">${item.get('amount', 0):,.2f}</td>
                <td style="text-align:right;">{item_pct:.1f}%</td>
            </tr>"""

        # Build department modal rows
        dept_rows = ''
        num_depts = len(dept_stats)
        for d in dept_stats:
            bar_w = min(100, d['percentage'])
            dept_rows += f"""
            <tr>
                <td><strong>{html_lib.escape(str(d['name']))}</strong></td>
                <td style="text-align:right;font-weight:600;">${d['total']:,.2f}</td>
                <td style="text-align:right;">{d['items']}</td>
                <td style="min-width:140px;">
                    <div style="background:#e8eaf6;border-radius:4px;height:10px;overflow:hidden;">
                        <div style="width:{bar_w:.1f}%;background:var(--primary-color);height:100%;border-radius:4px;"></div>
                    </div>
                    <span style="font-size:0.8rem;color:#555;">{d['percentage']:.1f}%</span>
                </td>
            </tr>"""

        # ── Pre-computed display strings ──────────────────────────────────
        risk_score_fmt      = f"{risk_score:.0f}"
        risk_amount_fmt     = f"{risk_amount:,.0f}"
        risk_pct_1dp        = f"{risk_pct:.1f}"
        total_budget_0dp    = f"{total_budget:,.0f}"
        total_budget_2dp    = f"{total_budget:,.2f}"
        num_depts_display   = str(len(set(df['Department']))) if 'Department' in df.columns else 'N/A'
        risk_level_display  = analysis.risk_level
        timestamp_str       = timestamp.strftime('%B %d, %Y at %I:%M %p')
        file_id_short       = file_id[:8]

        # Fallbacks for empty risk rows
        if not risk_cat_rows:
            risk_cat_rows = '<tr><td colspan="4" style="padding:16px;color:#aaa;text-align:center;">No keyword-matched risk categories found</td></tr>'
        if not risk_item_rows:
            risk_item_rows = '<tr><td colspan="4" style="padding:16px;color:#aaa;text-align:center;">No high-cost risk items flagged</td></tr>'

        # ── Pre-compute risk assessment section ───────────────────────────
        risk_section_html = '<div class="section-card fade-in"><h2>\U0001f3af Risk Assessment</h2>'
        if 'items_by_category' in risk_analysis:
            for category, items in risk_analysis['items_by_category'].items():
                risk_section_html += (
                    f'<div class="risk-category">'
                    f'<h3>{category.replace("_", " ").title()} Risk ({len(items)} items)</h3>'
                    '<ul>'
                )
                for item in items[:5]:
                    risk_section_html += f'<li>{html_lib.escape(str(item.get("description", "N/A")))}: ${item.get("amount", 0):,.2f}</li>'
                if len(items) > 5:
                    risk_section_html += f'<li><em>...and {len(items) - 5} more items</em></li>'
                risk_section_html += '</ul></div>'
        risk_section_html += '</div>'

        # ── Pre-compute optimizations section ─────────────────────────────
        optimizations_section_html = ''
        if optimizations:
            optimizations_section_html = (
                '<div class="section-card fade-in">'
                '<h2>\U0001f4a1 Optimization Opportunities</h2>'
                '<div class="optimizations-grid">'
            )
            for opt in optimizations:
                priority_class = f"priority-{opt['priority'].lower()}"
                optimizations_section_html += (
                    f'<div class="optimization-card {priority_class}">'
                    f'<h3>{html_lib.escape(str(opt["category"]))}</h3>'
                    f'<p>{html_lib.escape(str(opt["recommendation"]))}</p>'
                    f'<div class="savings">Potential Savings: '
                    f'<strong>${opt["potential_savings"]:,.2f}</strong></div>'
                    f'<div class="priority-badge">{html_lib.escape(str(opt["priority"]))} PRIORITY</div>'
                    '</div>'
                )
            optimizations_section_html += '</div></div>'

        return render_template('analysis.html',
            filename=filename,
            file_id=file_id,
            file_id_short=file_id_short,
            timestamp_str=timestamp_str,
            total_budget_0dp=total_budget_0dp,
            total_budget_2dp=total_budget_2dp,
            line_items=line_items,
            num_depts_display=num_depts_display,
            risk_level_display=risk_level_display,
            risk_level_label=risk_level_label,
            risk_level_color=risk_level_color,
            risk_score_fmt=risk_score_fmt,
            risk_amount_fmt=risk_amount_fmt,
            risk_pct_1dp=risk_pct_1dp,
            header_cells=header_cells,
            line_item_rows=line_item_rows,
            risk_cat_rows=risk_cat_rows,
            risk_item_rows=risk_item_rows,
            budget_rows=budget_rows,
            dept_rows=dept_rows,
            num_categories=num_categories,
            num_depts=num_depts,
            charts_html=charts_html,
            risk_section_html=risk_section_html,
            optimizations_section_html=optimizations_section_html,
        )
        
    except Exception as e:
        logger.error('Error displaying analysis %s: %s', file_id, e, exc_info=True)
        flash('Unable to display analysis. Please try again or re-upload the file.', 'error')
        return redirect(url_for('index'))


@app.route('/export-excel/<file_id>')
@login_required
def export_excel_route(file_id):
    """Export analysis to formatted Excel file FROM DATABASE"""
    analysis = BudgetAnalysis.query.get(file_id)
    
    if not analysis:
        flash('Analysis not found', 'error')
        return redirect(url_for('index'))
    
    try:
        df = pd.read_json(io.StringIO(analysis.dataframe_json))
        
        # Prepare budget data with safe defaults
        budget_data = {
            'filename': analysis.filename,
            'total_budget': analysis.total_budget,
            'line_items': analysis.line_items,
            'num_departments': analysis.num_departments
        }
        
        # Get risk analysis
        risk_data = {
            'risk_level': analysis.risk_level,
            'overall_risk_score': analysis.risk_score
        }
        
        # Get optimizations
        optimizations = json.loads(analysis.optimizations_json)
        
        # Generate Excel file
        excel_filename = f"budget_analysis_{file_id}.xlsx"
        excel_path = os.path.join(app.config['OUTPUT_FOLDER'], excel_filename)
        
        export_to_excel(df, budget_data, risk_data, optimizations, excel_path)
        
        # Send file
        return send_file(
            excel_path,
            as_attachment=True,
            download_name=f"{budget_data['filename']}_analysis.xlsx",
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        logger.error('Error exporting Excel for %s: %s', file_id, e, exc_info=True)
        flash('Unable to generate Excel export. Please try again.', 'error')
        return redirect(url_for('view_analysis', file_id=file_id))


@app.route('/generate-pdf/<file_id>')
@login_required
def generate_pdf_report(file_id):
    """Generate PDF report for analysis FROM DATABASE"""
    analysis = BudgetAnalysis.query.get(file_id)
    
    if not analysis:
        flash('Analysis not found', 'error')
        return redirect(url_for('index'))
    
    try:
        from pdf_report_generator import generate_pdf_report as gen_pdf
        
        df = pd.read_json(io.StringIO(analysis.dataframe_json))
        
        # Prepare budget data with safe defaults
        filename = analysis.filename
        budget_data = {
            'filename': filename,
            'total_budget': analysis.total_budget,
            'line_items': analysis.line_items,
            'num_departments': analysis.num_departments,
            'risk_level': analysis.risk_level,
            'departments': {}
        }
        
        # Get department breakdown
        if 'Department' in df.columns:
            total = df["Amount"].sum()
            for dept, group in df.groupby("Department"):
                dept_total = group["Amount"].sum()
                budget_data['departments'][dept] = {
                    "amount": float(dept_total),
                    "percentage": float(dept_total / total * 100) if total > 0 else 0,
                    "items": len(group)
                }
        
        # Get risk analysis
        risk_data = {
            'risk_level': analysis.risk_level,
            'overall_risk_score': analysis.risk_score,
            'risk_categories': json.loads(analysis.risk_analysis_json).get('items_by_category', {})
        }
        
        # Get optimization data
        optimizations = json.loads(analysis.optimizations_json)
        
        # Generate PDF
        pdf_filename = f"budget_report_{file_id}.pdf"
        pdf_path = os.path.join(app.config['OUTPUT_FOLDER'], pdf_filename)
        
        gen_pdf(budget_data, risk_data, optimizations, pdf_path, visualizations=None)
        
        # Serve the PDF
        return send_file(
            pdf_path, 
            as_attachment=True,
            download_name=f"{filename}_report.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logger.error('Error generating PDF for %s: %s', file_id, e, exc_info=True)
        flash('Unable to generate PDF report. Please try again.', 'error')
        return redirect(url_for('view_analysis', file_id=file_id))


@app.route('/compare/<file_id>')
@login_required
def compare_page(file_id):
    """Show budget comparison page"""
    analysis = BudgetAnalysis.query.get(file_id)
    
    if not analysis:
        flash('Analysis not found', 'error')
        return redirect(url_for('index'))
    
    csrf_token = generate_csrf()

    # Get all analyses for comparison selection FROM DATABASE
    all_analyses = BudgetAnalysis.query.order_by(BudgetAnalysis.upload_date.desc()).all()
    
    # Remove current analysis from options
    other_analyses = [a for a in all_analyses if a.id != file_id]
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Compare Budgets</title>
        <link rel="stylesheet" href="/static/css/modern-styles.css">
    </head>
    <body>
        <div class="container">
            <div class="header fade-in">
                <h1>🔄 Budget Comparison</h1>
                <p>Compare <strong>{analysis.filename}</strong> with another budget</p>
            </div>
            
            <div class="section-card fade-in">
                <h2>Select Budget to Compare With:</h2>
                <form action="/compare/{file_id}" method="post" class="comparison-form">
                    <input type="hidden" name="csrf_token" value="{csrf_token}">
                    <div class="form-group">
                        <label for="compare_id">Choose Budget:</label>
                        <select name="compare_id" id="compare_id" required>
                            <option value="">-- Select a budget --</option>
    """
    
    for other in other_analyses:
        html += f"""
                            <option value="{other.id}">
                                {other.filename} - ${other.total_budget:,.2f} ({other.upload_date.strftime('%Y-%m-%d')})
                            </option>
        """
    
    html += """
                        </select>
                    </div>
                    <button type="submit" class="btn btn-primary">🔍 Compare Budgets</button>
                    <a href="/analysis/{file_id}" class="btn btn-secondary">← Back to Analysis</a>
                </form>
            </div>
        </div>
    </body>
    </html>
    """.replace('{file_id}', file_id)
    
    return html


@app.route('/compare/<file_id>', methods=['POST'])
@login_required
def compare_budgets_route(file_id):
    """Handle budget comparison FROM DATABASE"""
    compare_id = request.form.get('compare_id')
    
    if not compare_id:
        flash('Please select a budget to compare', 'error')
        return redirect(url_for('compare_page', file_id=file_id))
    
    # Get both analyses from database
    analysis1 = BudgetAnalysis.query.get(file_id)
    analysis2 = BudgetAnalysis.query.get(compare_id)
    
    if not analysis1 or not analysis2:
        flash('One or both analyses not found', 'error')
        return redirect(url_for('index'))
    
    try:
        # Reconstruct DataFrames
        df1 = pd.read_json(io.StringIO(analysis1.dataframe_json))
        df2 = pd.read_json(io.StringIO(analysis2.dataframe_json))
        
        # Perform comparison
        comparison_result = compare_budgets(df1, df2, analysis1.filename, analysis2.filename)
        
        # Save comparison to database
        comparison_record = BudgetComparison(
            analysis1_id=file_id,
            analysis2_id=compare_id,
            comparison_data_json=json.dumps(comparison_result),
            comparison_date=datetime.now()
        )
        db.session.add(comparison_record)
        db.session.commit()
        
        # Generate comparison charts
        comparison_charts = generate_comparison_chart_html(comparison_result)

        # ── Modal precomputation ──────────────────────────────────────────────
        diff_amount  = analysis2.total_budget - analysis1.total_budget
        diff_pct     = (diff_amount / analysis1.total_budget * 100) if analysis1.total_budget > 0 else 0
        abs_diff     = abs(diff_amount)
        higher_label = 'Budget A' if analysis1.total_budget >= analysis2.total_budget else 'Budget B'
        diff_dir_color = '#e74c3c' if diff_amount > 0 else '#27ae60'
        variance_warning_html = '<span class="cmp-warn-badge">⚠ HIGH VARIANCE</span>' if abs(diff_pct) >= 50 else ''

        cat_diff_rows = ''
        cat_pct_rows  = ''
        if 'category_changes' in comparison_result:
            cats    = comparison_result['category_changes']
            by_diff = sorted(cats.items(), key=lambda x: abs(x[1]['difference']), reverse=True)
            by_pct  = sorted(cats.items(), key=lambda x: abs(x[1]['percent_change']), reverse=True)
            for cat, d in by_diff[:10]:
                dv    = d['difference']
                arrow = '↑' if dv > 0 else '↓' if dv < 0 else '='
                c     = '#e74c3c' if dv > 0 else '#27ae60' if dv < 0 else '#666'
                cat_diff_rows += (
                    f'<tr><td><strong>{html_lib.escape(str(cat))}</strong></td>'
                    f'<td>${d["budget1_amount"]:,.2f}</td><td>${d["budget2_amount"]:,.2f}</td>'
                    f'<td style="color:{c};">{arrow} ${abs(dv):,.2f}</td></tr>'
                )
            for cat, d in by_pct[:10]:
                pct = d['percent_change']
                c   = '#e74c3c' if pct > 0 else '#27ae60' if pct < 0 else '#666'
                hw  = ' <span class="cmp-warn-badge" style="font-size:.7rem;">⚠ HIGH</span>' if abs(pct) >= 50 else ''
                cat_pct_rows += (
                    f'<tr><td><strong>{html_lib.escape(str(cat))}</strong></td>'
                    f'<td style="color:{c};">{pct:+.1f}%{hw}</td>'
                    f'<td>${d["budget1_amount"]:,.2f}</td><td>${d["budget2_amount"]:,.2f}</td></tr>'
                )

        modal_css = """<style>
.cmp-modal-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.55);z-index:1000;align-items:flex-start;justify-content:center;padding:40px 20px;overflow-y:auto;}
.cmp-modal-overlay.open{display:flex;}
.cmp-modal{background:#fff;border-radius:14px;width:100%;max-width:700px;box-shadow:0 20px 60px rgba(0,0,0,.3);overflow:hidden;animation:cmpSlide .22s ease;}
.cmp-modal.wide{max-width:860px;}
@keyframes cmpSlide{from{transform:translateY(-30px);opacity:0}to{transform:translateY(0);opacity:1}}
.cmp-mhdr{display:flex;justify-content:space-between;align-items:center;padding:18px 24px;background:#3498db;color:#fff;}
.cmp-mhdr h2{margin:0;font-size:1.1rem;}
.cmp-mclose{background:none;border:none;color:#fff;font-size:1.6rem;cursor:pointer;line-height:1;padding:0 4px;}
.cmp-mbody{padding:20px 24px;max-height:65vh;overflow-y:auto;}
.cmp-mfooter{padding:12px 20px;background:#f9f9f9;border-top:1px solid #eee;font-size:.85rem;color:#888;}
.cmp-stat-row{display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid #f0f0f0;}
.cmp-stat-row:last-child{border-bottom:none;}
.cmp-stat-row .label{color:#666;font-size:.9rem;}
.cmp-stat-row .val{font-weight:700;color:#2c3e50;}
.cmp-modal table{width:100%;border-collapse:collapse;font-size:.9rem;box-shadow:none;border-radius:0;}
.cmp-modal table thead th{background:#f4f6f9;padding:9px 12px;text-align:left;font-weight:700;color:#2c3e50;border-bottom:2px solid #ddd;text-transform:uppercase;font-size:.75rem;letter-spacing:.5px;position:sticky;top:0;}
.cmp-modal table tbody tr{border-bottom:1px solid #f0f0f0;}
.cmp-modal table tbody tr:hover{background:#f0f7ff;}
.cmp-modal table tbody td{padding:9px 12px;color:#444;}
.cmp-warn-badge{background:#fff3cd;color:#856404;padding:3px 8px;border-radius:12px;font-size:.8rem;font-weight:600;margin-left:6px;}
.cmp-dir-label{font-size:.82rem;color:#7f8c8d;margin-top:6px;}
.stat-card.clickable{cursor:pointer;}
</style>"""

        modal_js = """<script>
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        document.querySelectorAll('.cmp-modal-overlay.open').forEach(function(m) { m.classList.remove('open'); });
    }
});
</script>"""

        # Build comparison results page
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Budget Comparison Results</title>
            <link rel="stylesheet" href="/static/css/modern-styles.css">
            <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
            {modal_css}
        </head>
        <body>
            <div class="container">
                <div class="header fade-in">
                    <h1>🔄 Budget Comparison Results</h1>
                    <p>Comparing: <strong>{analysis1.filename}</strong> vs <strong>{analysis2.filename}</strong></p>
                    <p style="font-size: 0.9rem; color: #666;">
                        💾 Comparison saved to database
                    </p>
                </div>
                
                <!-- Summary Stats — Clickable Cards -->
                <div class="stats-grid fade-in">

                    <!-- Card A -->
                    <div class="stat-card clickable" onclick="document.getElementById('cmp-modal-a').classList.add('open')" title="Click for Budget A details">
                        <div class="stat-icon">📁</div>
                        <div class="stat-value" style="font-size:1.3rem;word-break:break-word;line-height:1.3;">{analysis1.filename[:28] + '…' if len(analysis1.filename) > 28 else analysis1.filename}</div>
                        <div class="stat-label">Budget A &nbsp;·&nbsp; ${analysis1.total_budget:,.2f}</div>
                        <div class="cmp-dir-label">Click to view details</div>
                    </div>

                    <!-- Card B -->
                    <div class="stat-card clickable" onclick="document.getElementById('cmp-modal-b').classList.add('open')" title="Click for Budget B details">
                        <div class="stat-icon">📁</div>
                        <div class="stat-value" style="font-size:1.3rem;word-break:break-word;line-height:1.3;">{analysis2.filename[:28] + '…' if len(analysis2.filename) > 28 else analysis2.filename}</div>
                        <div class="stat-label">Budget B &nbsp;·&nbsp; ${analysis2.total_budget:,.2f}</div>
                        <div class="cmp-dir-label">Click to view details</div>
                    </div>

                    <!-- Card C — Difference -->
                    <div class="stat-card clickable" onclick="document.getElementById('cmp-modal-diff').classList.add('open')" title="Click for category breakdown">
                        <div class="stat-icon">{'📈' if diff_amount > 0 else '📉'}</div>
                        <div class="stat-value">${abs_diff:,.2f}</div>
                        <div class="stat-label">Difference</div>
                        <div class="cmp-dir-label">{higher_label} is higher {variance_warning_html}</div>
                    </div>

                    <!-- Card D — Change -->
                    <div class="stat-card clickable" onclick="document.getElementById('cmp-modal-pct').classList.add('open')" title="Click for % change by category">
                        <div class="stat-icon">{'🔺' if diff_amount > 0 else '🔻'}</div>
                        <div class="stat-value" style="color:{diff_dir_color};">{diff_pct:+.1f}%</div>
                        <div class="stat-label">Change</div>
                        <div class="cmp-dir-label">Budget B vs Budget A {variance_warning_html}</div>
                    </div>

                </div>
                
                <!-- Comparison Charts -->
                <div class="section-card fade-in">
                    {comparison_charts}
                </div>
                
                <!-- Detailed Comparison -->
                <div class="section-card fade-in">
                    <h2>📋 Detailed Breakdown</h2>
        """
        
        # Add category comparison if available
        if 'category_comparison' in comparison_result:
            html += """
                    <table class="comparison-table">
                        <thead>
                            <tr>
                                <th>Category</th>
                                <th>Budget 1</th>
                                <th>Budget 2</th>
                                <th>Difference</th>
                                <th>% Change</th>
                            </tr>
                        </thead>
                        <tbody>
            """
            
            for category, data in comparison_result['category_comparison'].items():
                diff = data['budget2'] - data['budget1']
                pct_change = (diff / data['budget1'] * 100) if data['budget1'] > 0 else 0
                arrow = '↑' if diff > 0 else '↓' if diff < 0 else '='
                
                html += f"""
                            <tr>
                                <td><strong>{category}</strong></td>
                                <td>${data['budget1']:,.2f}</td>
                                <td>${data['budget2']:,.2f}</td>
                                <td style="color: {'red' if diff > 0 else 'green' if diff < 0 else 'black'};">
                                    {arrow} ${abs(diff):,.2f}
                                </td>
                                <td style="color: {'red' if pct_change > 0 else 'green' if pct_change < 0 else 'black'};">
                                    {pct_change:+.1f}%
                                </td>
                            </tr>
                """
            
            html += """
                        </tbody>
                    </table>
            """
        
        html += f"""
                </div>
                
                <!-- Actions -->
                <div class="actions fade-in">
                    <a href="/analysis/{file_id}" class="btn btn-secondary">← Back to Analysis</a>
                    <a href="/" class="btn btn-primary">🏠 Dashboard</a>
                </div>
            </div>

            <!-- Modal A — Budget A details -->
            <div class="cmp-modal-overlay" id="cmp-modal-a" onclick="if(event.target===this)this.classList.remove('open')">
                <div class="cmp-modal">
                    <div class="cmp-mhdr">
                        <h2>📁 Budget A — {html_lib.escape(analysis1.filename)}</h2>
                        <button class="cmp-mclose" onclick="document.getElementById('cmp-modal-a').classList.remove('open')">×</button>
                    </div>
                    <div class="cmp-mbody">
                        <div class="cmp-stat-row"><span class="label">Total Budget</span><span class="val">${analysis1.total_budget:,.2f}</span></div>
                        <div class="cmp-stat-row"><span class="label">Line Items</span><span class="val">{analysis1.line_items}</span></div>
                        <div class="cmp-stat-row"><span class="label">Departments</span><span class="val">{analysis1.num_departments}</span></div>
                        <div class="cmp-stat-row"><span class="label">Risk Level</span><span class="val">{html_lib.escape(analysis1.risk_level or '—')}</span></div>
                        <div class="cmp-stat-row"><span class="label">Uploaded</span><span class="val">{analysis1.upload_date.strftime('%b %d, %Y')}</span></div>
                    </div>
                    <div class="cmp-mfooter"><a href="/analysis/{file_id}" style="color:#3498db;font-weight:600;">View full analysis →</a></div>
                </div>
            </div>

            <!-- Modal B — Budget B details -->
            <div class="cmp-modal-overlay" id="cmp-modal-b" onclick="if(event.target===this)this.classList.remove('open')">
                <div class="cmp-modal">
                    <div class="cmp-mhdr">
                        <h2>📁 Budget B — {html_lib.escape(analysis2.filename)}</h2>
                        <button class="cmp-mclose" onclick="document.getElementById('cmp-modal-b').classList.remove('open')">×</button>
                    </div>
                    <div class="cmp-mbody">
                        <div class="cmp-stat-row"><span class="label">Total Budget</span><span class="val">${analysis2.total_budget:,.2f}</span></div>
                        <div class="cmp-stat-row"><span class="label">Line Items</span><span class="val">{analysis2.line_items}</span></div>
                        <div class="cmp-stat-row"><span class="label">Departments</span><span class="val">{analysis2.num_departments}</span></div>
                        <div class="cmp-stat-row"><span class="label">Risk Level</span><span class="val">{html_lib.escape(analysis2.risk_level or '—')}</span></div>
                        <div class="cmp-stat-row"><span class="label">Uploaded</span><span class="val">{analysis2.upload_date.strftime('%b %d, %Y')}</span></div>
                    </div>
                    <div class="cmp-mfooter"><a href="/analysis/{compare_id}" style="color:#3498db;font-weight:600;">View full analysis →</a></div>
                </div>
            </div>

            <!-- Modal C — Dollar difference by category -->
            <div class="cmp-modal-overlay" id="cmp-modal-diff" onclick="if(event.target===this)this.classList.remove('open')">
                <div class="cmp-modal wide">
                    <div class="cmp-mhdr">
                        <h2>📊 Dollar Difference — Category Breakdown</h2>
                        <button class="cmp-mclose" onclick="document.getElementById('cmp-modal-diff').classList.remove('open')">×</button>
                    </div>
                    <div class="cmp-mbody">
                        <p style="margin-bottom:14px;color:#555;font-size:.9rem;">
                            <strong>{higher_label}</strong> is ${abs_diff:,.2f} higher overall. {variance_warning_html}
                        </p>
                        <table>
                            <thead><tr><th>Category</th><th>Budget A</th><th>Budget B</th><th>Difference</th></tr></thead>
                            <tbody>{cat_diff_rows}</tbody>
                        </table>
                    </div>
                    <div class="cmp-mfooter">Sorted by largest absolute difference · Top 10 shown</div>
                </div>
            </div>

            <!-- Modal D — Percentage change by category -->
            <div class="cmp-modal-overlay" id="cmp-modal-pct" onclick="if(event.target===this)this.classList.remove('open')">
                <div class="cmp-modal wide">
                    <div class="cmp-mhdr">
                        <h2>📉 % Change — Category Breakdown</h2>
                        <button class="cmp-mclose" onclick="document.getElementById('cmp-modal-pct').classList.remove('open')">×</button>
                    </div>
                    <div class="cmp-mbody">
                        <p style="margin-bottom:14px;color:#555;font-size:.9rem;">
                            Budget B is <strong style="color:{diff_dir_color};">{diff_pct:+.1f}%</strong> vs Budget A overall. {variance_warning_html}
                        </p>
                        <table>
                            <thead><tr><th>Category</th><th>% Change</th><th>Budget A</th><th>Budget B</th></tr></thead>
                            <tbody>{cat_pct_rows}</tbody>
                        </table>
                    </div>
                    <div class="cmp-mfooter">Sorted by largest % swing · ⚠ HIGH = ±50% or more variance</div>
                </div>
            </div>

            {modal_js}
        </body>
        </html>
        """
        
        return html
        
    except Exception as e:
        db.session.rollback()
        logger.error('Error comparing budgets %s vs %s: %s', file_id, compare_id, e, exc_info=True)
        flash('Unable to complete budget comparison. Please try again.', 'error')
        return redirect(url_for('compare_page', file_id=file_id))


@app.route('/api/health', methods=['GET'])
@csrf.exempt
def health_check():
    """Health check endpoint — no auth required."""
    try:
        count = BudgetAnalysis.query.count()
        resp = jsonify({'status': 'ok', 'service': 'Budget Parser', 'analyses': count})
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp, 200
    except Exception as e:
        logger.error('Health check failed: %s', e)
        resp = jsonify({'status': 'error'})
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp, 500


@app.route('/api/ai-insights/<file_id>', methods=['POST'])
@require_api_key
@csrf.exempt
def ai_insights(file_id):
    """
    Generate AI-powered narrative insights for a budget analysis.
    Protected by API key: pass X-API-Key header (see api_keys.json / BUDGET_API_KEY in .env).
    """
    analysis = BudgetAnalysis.query.get(file_id)
    if not analysis:
        return jsonify({'error': 'Analysis not found'}), 404

    # Return cached insights if already generated
    if analysis.ai_insights_json:
        return jsonify({'success': True, 'insights': json.loads(analysis.ai_insights_json), 'cached': True})

    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        return jsonify({'error': 'ANTHROPIC_API_KEY not configured'}), 500

    try:
        risk_data = json.loads(analysis.risk_analysis_json or '{}')
        optimizations = json.loads(analysis.optimizations_json or '[]')

        prompt = f"""You are a senior film/TV production financial analyst. Review the following budget analysis and provide concise, actionable executive insights.

BUDGET SUMMARY:
- File: {analysis.filename}
- Total Budget: ${analysis.total_budget:,.2f}
- Line Items: {analysis.line_items}
- Departments: {analysis.num_departments}
- Risk Level: {analysis.risk_level} (score: {analysis.risk_score:.2f})
- Analyzed: {analysis.analysis_timestamp.strftime('%Y-%m-%d')}

RISK FLAGS:
{json.dumps(risk_data.get('items_by_category', {}), indent=2)[:2000]}

OPTIMIZATION OPPORTUNITIES:
{json.dumps(optimizations, indent=2)[:1000]}

Return ONLY a valid JSON object with this structure:
{{
  "executive_summary": "<2-3 sentence overview of the budget health>",
  "key_concerns": ["<concern 1>", "<concern 2>", "<concern 3>"],
  "top_recommendations": [
    {{"action": "<what to do>", "rationale": "<why>", "priority": "<HIGH|MEDIUM|LOW>"}},
    {{"action": "<what to do>", "rationale": "<why>", "priority": "<HIGH|MEDIUM|LOW>"}},
    {{"action": "<what to do>", "rationale": "<why>", "priority": "<HIGH|MEDIUM|LOW>"}}
  ],
  "budget_health_score": <integer 0-100>,
  "outlook": "<POSITIVE|CAUTIONARY|CRITICAL>"
}}"""

        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text.strip()
        if response_text.startswith('```'):
            response_text = response_text.split('\n', 1)[1]
            response_text = response_text.rsplit('```', 1)[0]

        insights = json.loads(response_text)

        # Cache in database
        analysis.ai_insights_json = json.dumps(insights)
        db.session.commit()

        return jsonify({'success': True, 'insights': insights, 'cached': False})

    except Exception as e:
        logger.error('Error generating AI insights for %s: %s', file_id, e, exc_info=True)
        return jsonify({'error': 'Unable to generate insights. Please try again.'}), 500


if __name__ == '__main__':
    print("=" * 80)
    print(">> Budget Analysis & Risk Management System")
    print("   NOW WITH DATABASE INTEGRATION!")
    print("=" * 80)
    print("\n** Features:")
    print("  * SQLite database storage (persistent data!)")
    print("  * Interactive Chart.js visualizations")
    print("  * Modern responsive UI design")
    print("  * Excel export with formatting")
    print("  * PDF report generation")
    print("  * Risk assessment & recommendations")
    print("  * Budget comparison tool")
    print("\n>> Starting server at: http://localhost:8082")
    print("=" * 80)
    print()
    
    app.run(debug=False, host='127.0.0.1', port=8082)