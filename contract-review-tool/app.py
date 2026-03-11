"""
Contract Review Tool - AI-Powered Contract Analysis
Copyright (c) 2024. All rights reserved.
"""

import logging
import os
import json
import hmac
from datetime import datetime
from functools import wraps

import anthropic
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, Response, stream_with_context
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
from werkzeug.utils import secure_filename

load_dotenv(override=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s',
)
logger = logging.getLogger(__name__)

# Import document processing libraries
try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Secret key — required for sessions
_secret_key = os.environ.get('SECRET_KEY')
if not _secret_key:
    raise RuntimeError('SECRET_KEY is not set. Add it to your .env file.')
app.secret_key = _secret_key

# Session cookie hardening
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  # Set True when serving over HTTPS

# SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///history.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

csrf = CSRFProtect(app)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=['200 per day', '60 per hour'],
    storage_uri='memory://',
)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx', 'doc'}


# ---------------------------------------------------------------------------
# Database model
# ---------------------------------------------------------------------------

class AnalysisHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256), nullable=False)
    analyzed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    fairness = db.Column(db.String(32), nullable=False, default='NEUTRAL')
    results_json = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'analyzed_at': self.analyzed_at.strftime('%Y-%m-%d %H:%M:%S'),
            'fairness': self.fairness,
        }


with app.app_context():
    db.create_all()


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return decorated


def check_password(candidate: str) -> bool:
    app_password = os.environ.get('APP_PASSWORD', '')
    if not app_password:
        return False
    return hmac.compare_digest(candidate.encode(), app_password.encode())


# ---------------------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        password = request.form.get('password', '')
        if check_password(password):
            session['logged_in'] = True
            next_url = request.args.get('next') or '/'
            return redirect(next_url)
        error = 'Incorrect password. Please try again.'
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ---------------------------------------------------------------------------
# File helpers
# ---------------------------------------------------------------------------

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_pdf(file_path):
    if not PYPDF_AVAILABLE:
        return "PDF processing not available. Please install pypdf."
    try:
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error extracting PDF text: {str(e)}"


def extract_text_from_docx(file_path):
    if not DOCX_AVAILABLE:
        return "DOCX processing not available. Please install python-docx."
    try:
        doc = docx.Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        return f"Error extracting DOCX text: {str(e)}"


def extract_text_from_file(file_path, filename):
    extension = filename.rsplit('.', 1)[1].lower()
    if extension == 'pdf':
        return extract_text_from_pdf(file_path)
    elif extension in ['docx', 'doc']:
        return extract_text_from_docx(file_path)
    elif extension == 'txt':
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading text file: {str(e)}"
    else:
        return "Unsupported file format"


# ---------------------------------------------------------------------------
# AI analysis
# ---------------------------------------------------------------------------

def _build_analysis_prompt(contract_text):
    """Build a concise prompt that targets 800-1200 output tokens (~15-20s generation)."""
    # Cap input to ~12,000 chars (~3,000 tokens) to bound total request time
    text = contract_text[:12000]
    if len(contract_text) > 12000:
        text += '\n\n[Document truncated — first 12,000 characters analyzed]'
    return f"""You are an expert contract analyst. Review this contract concisely.

CONTRACT:
{text}

Respond in this exact structure. Be concise — 1-2 sentences per item maximum.

KEY TERMS:
- Parties: [names and roles]
- Duration: [term length and dates]
- Payment: [amounts, schedule, method]
- Deliverables: [what each party must provide]
- Termination: [conditions and notice required]
- Renewal: [auto-renewal or extension terms]

RISK ANALYSIS:
- [HIGH/MEDIUM/LOW] [Risk title]: [1-sentence explanation. Quote: "relevant clause"]
(list 4-6 most important risks)

FAIRNESS ASSESSMENT:
[FAVORABLE/NEUTRAL/UNFAVORABLE]: [2-3 sentences explaining why]

NEGOTIATION POINTS:
- [Point title]: [specific language to propose and why it matters]
(list 3-4 points)"""


def stream_contract_analysis(contract_text, filename):
    """Generator: streams Claude tokens as SSE, saves to DB at completion."""
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        yield f"data: {json.dumps({'type': 'error', 'message': 'ANTHROPIC_API_KEY not configured'})}\n\n"
        return

    client = anthropic.Anthropic(api_key=api_key)
    prompt = _build_analysis_prompt(contract_text)
    full_text = []

    try:
        with client.messages.stream(
            model='claude-sonnet-4-6',
            max_tokens=1500,
            messages=[{'role': 'user', 'content': prompt}]
        ) as stream:
            for text in stream.text_stream:
                full_text.append(text)
                yield f"data: {json.dumps({'type': 'chunk', 'text': text})}\n\n"

        response_text = ''.join(full_text)
        analysis = parse_ai_response(response_text)
        analysis['raw_response'] = response_text
        analysis['filename'] = filename
        analysis['analyzed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        record = AnalysisHistory(
            filename=filename,
            fairness=analysis.get('fairness', 'NEUTRAL'),
            results_json=json.dumps(analysis)
        )
        db.session.add(record)
        db.session.commit()
        analysis['history_id'] = record.id

        yield f"data: {json.dumps({'type': 'done', 'analysis': analysis})}\n\n"

    except Exception as e:
        logger.error('Stream analysis error', exc_info=True)
        db.session.rollback()
        yield f"data: {json.dumps({'type': 'error', 'message': 'Analysis failed. Please try again.'})}\n\n"


def parse_ai_response(response_text):
    sections = {
        'key_terms': [],
        'risks': [],
        'fairness': 'NEUTRAL',
        'negotiation_points': []
    }

    lines = response_text.split('\n')
    current_section = None
    current_item = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if 'KEY TERMS' in line.upper():
            current_section = 'key_terms'
        elif 'RISK ANALYSIS' in line.upper():
            current_section = 'risks'
        elif 'FAIRNESS' in line.upper():
            current_section = 'fairness'
        elif 'NEGOTIATION' in line.upper():
            current_section = 'negotiation_points'
        elif line.startswith('-') or line.startswith('•'):
            if current_item:
                if current_section == 'key_terms':
                    sections['key_terms'].append(' '.join(current_item))
                elif current_section == 'risks':
                    sections['risks'].append(' '.join(current_item))
                elif current_section == 'negotiation_points':
                    sections['negotiation_points'].append(' '.join(current_item))
            current_item = [line[1:].strip()]
        else:
            if current_item:
                current_item.append(line)

    if current_item:
        if current_section == 'key_terms':
            sections['key_terms'].append(' '.join(current_item))
        elif current_section == 'risks':
            sections['risks'].append(' '.join(current_item))
        elif current_section == 'negotiation_points':
            sections['negotiation_points'].append(' '.join(current_item))

    for line in lines:
        if 'FAVORABLE' in line.upper():
            sections['fairness'] = 'FAVORABLE'
            break
        elif 'UNFAVORABLE' in line.upper():
            sections['fairness'] = 'UNFAVORABLE'
            break

    return sections


# ---------------------------------------------------------------------------
# Page routes (login-protected)
# ---------------------------------------------------------------------------

@app.route('/')
@login_required
def index():
    return render_template('analyze.html')


@app.route('/analyze')
@login_required
def analyze():
    return render_template('analyze.html')


@app.route('/batch')
@login_required
def batch():
    return render_template('batch.html')


@app.route('/contract')
@login_required
def contract():
    return render_template('contract.html')


@app.route('/results')
@login_required
def results():
    return render_template('results.html')


@app.route('/history')
@login_required
def history():
    records = AnalysisHistory.query.order_by(AnalysisHistory.analyzed_at.desc()).all()
    return render_template('history.html', records=records)


# ---------------------------------------------------------------------------
# API endpoints (login-protected)
# ---------------------------------------------------------------------------

@app.route('/upload', methods=['POST'])
@login_required
@csrf.exempt
@limiter.limit('10 per hour')
def upload_file():
    if 'contract' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['contract']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed. Please upload PDF, DOCX, or TXT'}), 400

    try:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        contract_text = extract_text_from_file(file_path, filename)
        os.remove(file_path)

        if not contract_text or len(contract_text.strip()) < 100:
            return jsonify({'error': 'Could not extract enough text from the file.'}), 400

    except Exception as e:
        logger.error('File processing error', exc_info=True)
        return jsonify({'error': 'Error processing file. Please try again.'}), 500

    return Response(
        stream_with_context(stream_contract_analysis(contract_text, filename)),
        mimetype='text/event-stream',
        headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'}
    )


@app.route('/api/analyze', methods=['POST'])
@login_required
@csrf.exempt
def api_analyze():
    import time
    data = request.get_json()
    if not data or not data.get('screenplay'):
        return jsonify({'success': False, 'error': 'No screenplay content provided'}), 400

    screenplay_text = data['screenplay']
    writer_info = data.get('writer_info', {})

    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        return jsonify({'success': False, 'error': 'ANTHROPIC_API_KEY not configured'}), 500

    try:
        client = anthropic.Anthropic(api_key=api_key)
        start_time = time.time()

        writer_context = ''
        if writer_info.get('name'):
            writer_context = f"\nWriter: {writer_info['name']} ({writer_info.get('experience', 'unknown experience')})"

        prompt = f"""You are a professional Hollywood screenplay analyst. Analyze the following screenplay content and return ONLY a valid JSON object — no markdown, no explanation, just the JSON.{writer_context}

SCREENPLAY:
{screenplay_text}

Return this exact JSON structure:
{{
  "quick_verdict": {{
    "commercial_score": <integer 0-100>,
    "recommendation": "<one-sentence recommendation>",
    "priority_level": "<HIGH PRIORITY | MEDIUM PRIORITY | LOW PRIORITY>",
    "estimated_roi": "<e.g. 2.5x-4x>"
  }},
  "detailed_analysis": {{
    "structural_breakdown": {{
      "pacing_score": <integer 0-100>,
      "act_breakdown": {{"act1": "<assessment>", "act2": "<assessment>", "act3": "<assessment>"}}
    }},
    "character_analysis": {{
      "main_characters": "<comma-separated list>",
      "character_depth_score": <integer 0-100>
    }},
    "market_potential": {{
      "market_potential": "<HIGH | MEDIUM | LOW> — <brief reason>",
      "target_audience": "<description>"
    }}
  }},
  "technical_metrics": {{
    "document_metrics": {{
      "primary_genre": "<genre>",
      "estimated_pages": <integer>,
      "character_count": <integer>
    }},
    "processing_time": "<X.Xs>"
  }}
}}"""

        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )

        elapsed = round(time.time() - start_time, 1)
        response_text = message.content[0].text.strip()

        if response_text.startswith('```'):
            response_text = response_text.split('\n', 1)[1]
            response_text = response_text.rsplit('```', 1)[0]

        result = json.loads(response_text)
        result['technical_metrics']['processing_time'] = f"{elapsed}s"

        return jsonify({'success': True, 'result': result})

    except Exception as e:
        logger.error('API analyze error', exc_info=True)
        return jsonify({'success': False, 'error': 'Analysis failed. Please try again.'}), 500


@app.route('/api/extract-text', methods=['POST'])
@login_required
@csrf.exempt
def extract_text():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Unsupported file type'}), 400

    try:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        text = extract_text_from_file(file_path, filename)
        os.remove(file_path)
        return jsonify({'text': text})
    except Exception as e:
        logger.error('Text extraction error', exc_info=True)
        return jsonify({'error': 'Text extraction failed. Please try again.'}), 500


@app.route('/api/batch/analyze', methods=['POST'])
@login_required
@csrf.exempt
def api_batch_analyze():
    import time
    data = request.get_json()
    if not data or not data.get('screenplays'):
        return jsonify({'success': False, 'error': 'No screenplays provided'}), 400

    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        return jsonify({'success': False, 'error': 'ANTHROPIC_API_KEY not configured'}), 500

    client = anthropic.Anthropic(api_key=api_key)
    results = []

    for item in data['screenplays']:
        screenplay_text = item.get('content', '')
        writer_info = item.get('writer_info', {})
        filename = item.get('filename', 'Unknown')

        if not screenplay_text.strip():
            continue

        try:
            start_time = time.time()
            writer_context = ''
            if writer_info.get('name'):
                writer_context = f"\nWriter: {writer_info['name']} ({writer_info.get('experience', 'unknown')})"

            prompt = f"""You are a professional Hollywood screenplay analyst. Analyze the following screenplay and return ONLY a valid JSON object — no markdown, no explanation, just the JSON.{writer_context}

SCREENPLAY:
{screenplay_text}

Return this exact JSON structure:
{{
  "assessment_id": "{filename}",
  "quick_verdict": {{
    "commercial_score": <integer 0-100>,
    "recommendation": "<one-sentence recommendation>",
    "priority_level": "<HIGH PRIORITY | MEDIUM PRIORITY | LOW PRIORITY>",
    "estimated_roi": "<e.g. 2.5x-4x>"
  }},
  "technical_metrics": {{
    "document_metrics": {{
      "primary_genre": "<genre>",
      "estimated_pages": <integer>,
      "character_count": <integer>
    }},
    "processing_time": "<X.Xs>"
  }}
}}"""

            message = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}]
            )

            elapsed = round(time.time() - start_time, 1)
            response_text = message.content[0].text.strip()

            if response_text.startswith('```'):
                response_text = response_text.split('\n', 1)[1]
                response_text = response_text.rsplit('```', 1)[0]

            result = json.loads(response_text)
            result['technical_metrics']['processing_time'] = f"{elapsed}s"
            results.append(result)

        except Exception as e:
            logger.error('Batch analyze error for %s', filename, exc_info=True)
            results.append({
                'assessment_id': filename,
                'error': 'Processing failed',
                'quick_verdict': {'commercial_score': 0, 'recommendation': 'Error during processing', 'priority_level': 'LOW PRIORITY', 'estimated_roi': 'N/A'},
                'technical_metrics': {'document_metrics': {'primary_genre': 'Unknown', 'estimated_pages': 0, 'character_count': 0}, 'processing_time': '0s'}
            })

    return jsonify({'success': True, 'results': results})


@app.route('/api/history/<int:record_id>')
@login_required
def api_history_detail(record_id):
    record = AnalysisHistory.query.get_or_404(record_id)
    data = json.loads(record.results_json)
    return jsonify(data)


@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'pypdf_available': PYPDF_AVAILABLE,
        'docx_available': DOCX_AVAILABLE
    })


if __name__ == '__main__':
    if not os.environ.get('ANTHROPIC_API_KEY'):
        logger.warning('ANTHROPIC_API_KEY is not set — AI analysis will fail.')
    app.run(debug=False, host='127.0.0.1', port=5001)
