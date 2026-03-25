"""
ScreenFlow AURA — AI-Powered Screenplay Analysis API
Rewritten from http.server to Flask with real Claude AI, SQLite persistence, and API key auth.
"""

import logging
import os
import json
import hmac
import hashlib
import time
from datetime import datetime
from functools import wraps

import anthropic
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate, upgrade as migrate_upgrade
from flask_sqlalchemy import SQLAlchemy

load_dotenv(override=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s',
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ── Config ──────────────────────────────────────────────────────────────────

_secret_key = os.environ.get('SECRET_KEY')
if not _secret_key:
    raise RuntimeError('SECRET_KEY is not set. Add it to your .env file.')
app.secret_key = _secret_key

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///aura.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=['500 per day', '120 per hour'],
    storage_uri='memory://',
)


# ── Model ───────────────────────────────────────────────────────────────────

class AuraAnalysis(db.Model):
    __tablename__ = 'aura_analyses'

    id = db.Column(db.Integer, primary_key=True)
    analysis_type = db.Column(db.String(32), default='parse')  # parse | analyze | validate | batch
    screenplay_excerpt = db.Column(db.Text)          # first 500 chars for reference
    word_count = db.Column(db.Integer, default=0)
    result_json = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    batch_size = db.Column(db.Integer, default=1)    # >1 for batch requests

    def to_dict(self):
        return {
            'id': self.id,
            'analysis_type': self.analysis_type,
            'word_count': self.word_count,
            'batch_size': self.batch_size,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'excerpt': (self.screenplay_excerpt or '')[:120] + '…'
            if len(self.screenplay_excerpt or '') > 120 else (self.screenplay_excerpt or ''),
        }


class ApiKey(db.Model):
    __tablename__ = 'api_keys'
    id = db.Column(db.Integer, primary_key=True)
    key_hash = db.Column(db.String(64), unique=True, nullable=False)  # SHA-256 hex
    label = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def hash(raw_key: str) -> str:
        return hashlib.sha256(raw_key.encode()).hexdigest()


def _seed_api_keys():
    """Seed default API key from AURA_API_KEY env var if no keys exist."""
    from sqlalchemy import inspect as sa_inspect
    try:
        if 'api_keys' not in sa_inspect(db.engine).get_table_names():
            return
        raw_key = os.environ.get('AURA_API_KEY', '')
        if not raw_key:
            return
        key_hash = ApiKey.hash(raw_key)
        if not ApiKey.query.filter_by(key_hash=key_hash).first():
            db.session.add(ApiKey(key_hash=key_hash, label='Default (from AURA_API_KEY env var)'))
            db.session.commit()
            logger.info('Default API key seeded.')
    except Exception:
        logger.debug('_seed_api_keys skipped (tables not ready)', exc_info=True)


with app.app_context():
    _migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
    if os.path.isdir(_migrations_dir):
        migrate_upgrade()
    else:
        db.create_all()
    _seed_api_keys()


# ── Auth ─────────────────────────────────────────────────────────────────────

def _get_request_api_key():
    return (
        request.headers.get('X-API-Key') or
        request.args.get('api_key') or
        (request.get_json(silent=True) or {}).get('api_key')
    )


def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        raw_key = _get_request_api_key()
        if not raw_key:
            return jsonify({'error': 'API key required', 'hint': 'Pass X-API-Key header'}), 401
        key_hash = ApiKey.hash(raw_key)
        active_key = ApiKey.query.filter_by(key_hash=key_hash, is_active=True).first()
        if not active_key:
            return jsonify({'error': 'Invalid API key'}), 403
        return f(*args, **kwargs)
    return decorated


def require_admin_token(f):
    """Protect admin routes with AURA_ADMIN_TOKEN env var (separate from API keys)."""
    @wraps(f)
    def decorated(*args, **kwargs):
        admin_token = os.environ.get('AURA_ADMIN_TOKEN', '')
        if not admin_token:
            return jsonify({'error': 'Admin access not configured (AURA_ADMIN_TOKEN not set)'}), 503
        provided = request.headers.get('X-Admin-Token', '')
        if not hmac.compare_digest(admin_token, provided):
            return jsonify({'error': 'Invalid admin token'}), 403
        return f(*args, **kwargs)
    return decorated


# ── Claude helper ─────────────────────────────────────────────────────────────

def _get_claude_client():
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        raise RuntimeError('ANTHROPIC_API_KEY not configured')
    return anthropic.Anthropic(api_key=api_key)


def _call_claude(prompt: str, max_tokens: int = 1500) -> dict:
    """Call Claude and parse JSON response. Retries once on transient errors."""
    client = _get_claude_client()
    last_err = None
    for attempt in range(2):
        if attempt:
            time.sleep(3)
        try:
            message = client.messages.create(
                model='claude-sonnet-4-6',
                max_tokens=max_tokens,
                messages=[{'role': 'user', 'content': prompt}]
            )
            text = message.content[0].text.strip()
            if text.startswith('```'):
                text = text.split('\n', 1)[1]
                text = text.rsplit('```', 1)[0]
            return json.loads(text)
        except (json.JSONDecodeError, Exception) as e:
            last_err = e
            logger.warning('Claude call attempt %d failed: %s', attempt + 1, e)
    raise last_err


# ── Demo mode helpers ─────────────────────────────────────────────────────────

def _is_demo():
    return os.environ.get('DEMO_MODE', '').lower() == 'true'


def _demo_parse(screenplay, words):
    import random
    genres = ['Drama', 'Thriller', 'Action', 'Comedy', 'Sci-Fi', 'Horror']
    return {
        'document_metrics': {
            'word_count': words,
            'estimated_pages': round(words / 250, 1),
            'primary_genre': random.choice(genres),
            'complexity_score': random.randint(65, 90),
        },
        'quality_assessment': {
            'overall_score': random.randint(72, 91),
            'structure_quality': random.randint(68, 88),
            'dialogue_effectiveness': random.randint(70, 90),
            'pacing_analysis': random.choice(['excellent', 'good', 'balanced']),
            'commercial_potential': random.choice(['HIGH', 'HIGH', 'MEDIUM']),
        },
        'ai_insights': {
            'sentiment_analysis': {
                'overall_sentiment': random.choice(['positive', 'complex', 'neutral']),
                'emotional_arc': random.choice(['rising', 'balanced', 'volatile']),
                'tone_consistency': 'consistent',
            },
            'theme_detection': ['Redemption', 'Ambition', 'Identity'],
            'style_assessment': {
                'writing_style': 'balanced',
                'pacing': 'deliberate',
                'originality_score': random.randint(70, 88),
            },
        },
        'recommendations': [
            'Strengthen the second-act turning point for greater audience impact.',
            'Consider adding a subplot to deepen character relationships.',
            'The opening scene effectively hooks the reader — maintain that energy throughout.',
        ],
        'processing_metadata': {
            'processing_time_ms': 1500,
            'ai_model_used': 'claude-sonnet-4-6',
            'word_count_processed': words,
        },
    }


def _demo_analyze(screenplay, words, analysis_type='comprehensive'):
    import random
    return {
        'analysis_type': analysis_type,
        'insights': {
            'narrative_structure': {
                'act_breakdown': {
                    'act1': 'Strong setup with clear character establishment.',
                    'act2': 'Compelling midpoint escalation and conflict.',
                    'act3': 'Satisfying resolution with emotional payoff.',
                },
                'plot_points': random.randint(5, 9),
                'climax_strength': random.choice(['strong', 'strong', 'moderate']),
            },
            'character_analysis': {
                'main_characters': random.randint(3, 6),
                'character_depth': random.choice(['deep', 'complex', 'moderate']),
                'character_arcs': random.randint(2, 4),
                'protagonist_strength': random.choice(['compelling', 'compelling', 'adequate']),
            },
            'commercial_viability': {
                'target_audience': random.choice(['broad', 'premium', 'genre-specific']),
                'market_potential': random.choice(['HIGH', 'HIGH', 'MEDIUM']),
                'comparable_titles': ['Parasite', 'Get Out'],
                'distribution_outlook': random.choice(['theatrical', 'streaming']),
            },
            'technical_assessment': {
                'formatting_compliance': 'compliant',
                'industry_standards': 'meets',
                'readability_score': random.randint(75, 92),
            },
        },
        'recommendations': [
            'The narrative arc is compelling — consider tightening act two pacing.',
            'Strong commercial appeal with broad audience targeting.',
            'Character motivations are clear and well-developed throughout.',
        ],
        'risk_assessment': {
            'overall_risk': 'low',
            'commercial_risk': 'low',
            'technical_risk': 'low',
            'market_fit': 'strong',
        },
        'processing_time_ms': 1800,
        'ai_model': 'claude-sonnet-4-6',
    }


def _demo_validate(screenplay, words):
    import random
    score = random.randint(82, 96)
    return {
        'compliance_report': {
            'industry_standards': {
                'hollywood_format': f'{random.randint(88, 97)}%',
                'final_draft_compatibility': f'{random.randint(85, 95)}%',
                'fountain_compatibility': f'{random.randint(90, 98)}%',
            },
            'quality_metrics': {
                'structure_integrity': f'{random.randint(85, 96)}%',
                'character_consistency': f'{random.randint(88, 97)}%',
                'dialogue_realism': f'{random.randint(82, 94)}%',
                'pacing_consistency': f'{random.randint(80, 93)}%',
            },
        },
        'issues': [
            {'severity': 'suggestion', 'description': 'Consider adding scene numbers for production draft.', 'location': 'Throughout'},
        ],
        'overall_score': score,
        'certification_status': 'compliant',
        'summary': 'Screenplay meets Hollywood industry standards with strong formatting compliance. Minor suggestions noted for production-ready polish.',
        'processing_time_ms': 900,
    }


def _demo_batch_item(label, text):
    import random
    words = len(text.split()) if text else 500
    score = random.randint(65, 92)
    genres = ['Drama', 'Thriller', 'Action', 'Comedy', 'Sci-Fi']
    return {
        'item_id': label,
        'document_metrics': {
            'word_count': words,
            'estimated_pages': round(words / 250, 1),
            'primary_genre': random.choice(genres),
        },
        'quick_verdict': {
            'overall_score': score,
            'commercial_potential': 'HIGH' if score >= 80 else 'MEDIUM',
            'recommendation': f"{'Strong greenlight candidate' if score >= 80 else 'Promising with revisions needed'} — notable commercial potential.",
        },
        'ai_analysis': {
            'genre': random.choice(genres),
            'sentiment': random.choice(['positive', 'complex', 'neutral']),
            'key_themes': ['Ambition', 'Identity'],
        },
        'processing_time_ms': 950,
    }


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    total = AuraAnalysis.query.count()
    return render_template('index.html', total=total)


@app.route('/api/health')
def health():
    total = AuraAnalysis.query.count()
    resp = jsonify({
        'status': 'operational',
        'service': 'ScreenFlow AURA',
        'version': '3.1.1',
        'total_analyses': total,
        'timestamp': datetime.utcnow().isoformat(),
    })
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/api/parse', methods=['POST'])
@require_api_key
@limiter.limit('20 per hour')
def parse():
    """Single screenplay parse — full AI analysis."""
    data = request.get_json(silent=True) or {}
    screenplay = data.get('screenplay', '')
    if not screenplay.strip():
        return jsonify({'error': 'screenplay is required'}), 400

    start = time.time()
    words = len(screenplay.split())

    if _is_demo():
        time.sleep(1.5)
        result = _demo_parse(screenplay, words)
        record = AuraAnalysis(analysis_type='parse', screenplay_excerpt=screenplay[:500], word_count=words, result_json=json.dumps(result))
        db.session.add(record)
        db.session.commit()
        result['analysis_id'] = record.id
        return jsonify({'success': True, 'analysis': result})

    prompt = f"""You are a professional Hollywood screenplay analyst. Analyze the following screenplay content and return ONLY a valid JSON object — no markdown, no explanation, just JSON.

SCREENPLAY ({words} words):
{screenplay[:8000]}

Return this exact JSON structure:
{{
  "document_metrics": {{
    "word_count": {words},
    "estimated_pages": {round(words / 250, 1)},
    "primary_genre": "<genre>",
    "complexity_score": <integer 0-100>
  }},
  "quality_assessment": {{
    "overall_score": <integer 0-100>,
    "structure_quality": <integer 0-100>,
    "dialogue_effectiveness": <integer 0-100>,
    "pacing_analysis": "<excellent|good|balanced|slow|rushed>",
    "commercial_potential": "<HIGH|MEDIUM|LOW>"
  }},
  "ai_insights": {{
    "sentiment_analysis": {{
      "overall_sentiment": "<positive|neutral|complex|dark>",
      "emotional_arc": "<rising|falling|balanced|volatile>",
      "tone_consistency": "<consistent|varied|inconsistent>"
    }},
    "theme_detection": ["<theme1>", "<theme2>", "<theme3>"],
    "style_assessment": {{
      "writing_style": "<descriptive|dialogue_heavy|action_oriented|balanced>",
      "pacing": "<brisk|deliberate|varied|consistent>",
      "originality_score": <integer 0-100>
    }}
  }},
  "recommendations": ["<rec1>", "<rec2>", "<rec3>"]
}}"""

    try:
        result = _call_claude(prompt, max_tokens=1200)
        elapsed_ms = round((time.time() - start) * 1000)
        result['processing_metadata'] = {
            'processing_time_ms': elapsed_ms,
            'ai_model_used': 'claude-sonnet-4-6',
            'word_count_processed': words,
        }

        record = AuraAnalysis(
            analysis_type='parse',
            screenplay_excerpt=screenplay[:500],
            word_count=words,
            result_json=json.dumps(result),
        )
        db.session.add(record)
        db.session.commit()
        result['analysis_id'] = record.id

        return jsonify({'success': True, 'analysis': result})

    except Exception as e:
        logger.error('Parse error', exc_info=True)
        return jsonify({'success': False, 'error': 'Analysis failed. Please try again.'}), 500


@app.route('/api/analyze', methods=['POST'])
@require_api_key
@limiter.limit('20 per hour')
def analyze():
    """Deep narrative analysis — character arcs, commercial viability, market fit."""
    data = request.get_json(silent=True) or {}
    screenplay = data.get('screenplay', '')
    analysis_type = data.get('analysis_type', 'comprehensive')
    if not screenplay.strip():
        return jsonify({'error': 'screenplay is required'}), 400

    start = time.time()
    words = len(screenplay.split())

    if _is_demo():
        time.sleep(1.8)
        result = _demo_analyze(screenplay, words, analysis_type)
        record = AuraAnalysis(analysis_type='analyze', screenplay_excerpt=screenplay[:500], word_count=words, result_json=json.dumps(result))
        db.session.add(record)
        db.session.commit()
        result['analysis_id'] = record.id
        return jsonify({'success': True, 'analysis': result})

    prompt = f"""You are a professional Hollywood screenplay analyst doing a {analysis_type} analysis. Return ONLY a valid JSON object — no markdown, no explanation.

SCREENPLAY ({words} words):
{screenplay[:8000]}

Return this exact JSON structure:
{{
  "analysis_type": "{analysis_type}",
  "insights": {{
    "narrative_structure": {{
      "act_breakdown": {{"act1": "<assessment>", "act2": "<assessment>", "act3": "<assessment>"}},
      "plot_points": <integer>,
      "climax_strength": "<strong|moderate|weak>"
    }},
    "character_analysis": {{
      "main_characters": <integer>,
      "character_depth": "<shallow|moderate|deep|complex>",
      "character_arcs": <integer>,
      "protagonist_strength": "<compelling|adequate|weak>"
    }},
    "commercial_viability": {{
      "target_audience": "<broad|niche|premium|genre-specific>",
      "market_potential": "<HIGH|MEDIUM|LOW>",
      "comparable_titles": ["<title1>", "<title2>"],
      "distribution_outlook": "<theatrical|streaming|limited|festival>"
    }},
    "technical_assessment": {{
      "formatting_compliance": "<compliant|minor-issues|needs-revision>",
      "industry_standards": "<meets|partially-meets|below>",
      "readability_score": <integer 0-100>
    }}
  }},
  "recommendations": ["<rec1>", "<rec2>", "<rec3>"],
  "risk_assessment": {{
    "overall_risk": "<low|medium|high>",
    "commercial_risk": "<low|medium|high>",
    "technical_risk": "<low|medium|high>",
    "market_fit": "<strong|moderate|weak>"
  }}
}}"""

    try:
        result = _call_claude(prompt, max_tokens=1500)
        elapsed_ms = round((time.time() - start) * 1000)
        result['processing_time_ms'] = elapsed_ms
        result['ai_model'] = 'claude-sonnet-4-6'

        record = AuraAnalysis(
            analysis_type='analyze',
            screenplay_excerpt=screenplay[:500],
            word_count=words,
            result_json=json.dumps(result),
        )
        db.session.add(record)
        db.session.commit()
        result['analysis_id'] = record.id

        return jsonify({'success': True, 'analysis': result})

    except Exception as e:
        logger.error('Analyze error', exc_info=True)
        return jsonify({'success': False, 'error': 'Analysis failed. Please try again.'}), 500


@app.route('/api/validate', methods=['POST'])
@require_api_key
@limiter.limit('20 per hour')
def validate():
    """Format and compliance validation."""
    data = request.get_json(silent=True) or {}
    screenplay = data.get('screenplay', '')
    if not screenplay.strip():
        return jsonify({'error': 'screenplay is required'}), 400

    start = time.time()
    words = len(screenplay.split())

    if _is_demo():
        time.sleep(1.2)
        result = _demo_validate(screenplay, words)
        record = AuraAnalysis(analysis_type='validate', screenplay_excerpt=screenplay[:500], word_count=words, result_json=json.dumps(result))
        db.session.add(record)
        db.session.commit()
        result['analysis_id'] = record.id
        return jsonify({'success': True, 'validation': result})

    prompt = f"""You are a professional screenplay format validator. Validate the following screenplay against industry standards and return ONLY a valid JSON object.

SCREENPLAY ({words} words):
{screenplay[:6000]}

Return this exact JSON structure:
{{
  "compliance_report": {{
    "industry_standards": {{
      "hollywood_format": "<percent as string, e.g. 92%>",
      "final_draft_compatibility": "<percent>",
      "fountain_compatibility": "<percent>"
    }},
    "quality_metrics": {{
      "structure_integrity": "<percent>",
      "character_consistency": "<percent>",
      "dialogue_realism": "<percent>",
      "pacing_consistency": "<percent>"
    }}
  }},
  "issues": [
    {{"severity": "<critical|warning|suggestion>", "description": "<issue>", "location": "<where in script>"}}
  ],
  "overall_score": <integer 0-100>,
  "certification_status": "<compliant|conditionally-compliant|non-compliant>",
  "summary": "<2-sentence summary of validation result>"
}}"""

    try:
        result = _call_claude(prompt, max_tokens=1500)
        elapsed_ms = round((time.time() - start) * 1000)
        result['processing_time_ms'] = elapsed_ms

        record = AuraAnalysis(
            analysis_type='validate',
            screenplay_excerpt=screenplay[:500],
            word_count=words,
            result_json=json.dumps(result),
        )
        db.session.add(record)
        db.session.commit()
        result['analysis_id'] = record.id

        return jsonify({'success': True, 'validation': result})

    except Exception as e:
        logger.error('Validate error', exc_info=True)
        return jsonify({'success': False, 'error': 'Validation failed. Please try again.'}), 500


@app.route('/api/batch/parse', methods=['POST'])
@require_api_key
@limiter.limit('5 per hour')
def batch_parse():
    """Batch parse multiple screenplays — returns an array of analyses."""
    data = request.get_json(silent=True) or {}
    screenplays = data.get('screenplays', [])
    if not screenplays:
        return jsonify({'error': 'screenplays array is required'}), 400

    if _is_demo():
        time.sleep(2.0)
        results = []
        for i, item in enumerate(screenplays):
            text = item if isinstance(item, str) else item.get('content', '')
            label = f'item-{i+1}' if isinstance(item, str) else item.get('filename', f'item-{i+1}')
            results.append(_demo_batch_item(label, text))
        return jsonify({'success': True, 'results': results, 'total': len(results), 'processing_time_ms': 2000})

    batch_start = time.time()
    results = []

    for i, item in enumerate(screenplays):
        text = item if isinstance(item, str) else item.get('content', '')
        label = f'item-{i+1}' if isinstance(item, str) else item.get('filename', f'item-{i+1}')
        words = len(text.split())

        prompt = f"""Analyze this screenplay excerpt and return ONLY a valid JSON object.

SCREENPLAY — {label} ({words} words):
{text[:4000]}

Return this exact JSON structure:
{{
  "item_id": "{label}",
  "document_metrics": {{
    "word_count": {words},
    "estimated_pages": {round(words / 250, 1)},
    "primary_genre": "<genre>"
  }},
  "quick_verdict": {{
    "overall_score": <integer 0-100>,
    "commercial_potential": "<HIGH|MEDIUM|LOW>",
    "recommendation": "<one-sentence recommendation>"
  }},
  "ai_analysis": {{
    "genre": "<genre>",
    "sentiment": "<positive|neutral|complex|dark>",
    "key_themes": ["<theme1>", "<theme2>"]
  }}
}}"""

        try:
            item_start = time.time()
            result = _call_claude(prompt, max_tokens=600)
            result['processing_time_ms'] = round((time.time() - item_start) * 1000)
            results.append(result)

            record = AuraAnalysis(
                analysis_type='batch',
                screenplay_excerpt=text[:500],
                word_count=words,
                result_json=json.dumps(result),
            )
            db.session.add(record)

        except Exception as e:
            logger.error('Batch item error for %s', label, exc_info=True)
            results.append({
                'item_id': label,
                'error': 'Processing failed',
                'quick_verdict': {'overall_score': 0, 'commercial_potential': 'N/A', 'recommendation': 'Processing error'}
            })

    db.session.commit()
    total_ms = round((time.time() - batch_start) * 1000)

    # Store a summary batch record
    batch_record = AuraAnalysis(
        analysis_type='batch',
        screenplay_excerpt=f'Batch of {len(screenplays)} items',
        word_count=sum(len((s if isinstance(s, str) else s.get('content', '')).split()) for s in screenplays),
        result_json=json.dumps({'batch_results': results}),
        batch_size=len(screenplays),
    )
    db.session.add(batch_record)
    db.session.commit()

    return jsonify({
        'success': True,
        'batch': {
            'batch_id': batch_record.id,
            'total_items': len(screenplays),
            'processed_items': sum(1 for r in results if 'error' not in r),
            'failed_items': sum(1 for r in results if 'error' in r),
            'total_processing_time_ms': total_ms,
        },
        'results': results,
    })


@app.route('/api/history')
@require_api_key
def history():
    """Return paginated list of past analyses from the database."""
    limit = min(int(request.args.get('limit', 50)), 200)
    offset = int(request.args.get('offset', 0))
    records = (
        AuraAnalysis.query
        .order_by(AuraAnalysis.created_at.desc())
        .offset(offset).limit(limit).all()
    )
    total = AuraAnalysis.query.count()
    return jsonify({
        'total': total,
        'limit': limit,
        'offset': offset,
        'records': [r.to_dict() for r in records],
    })


@app.route('/api/history/<int:record_id>')
@require_api_key
def history_detail(record_id):
    record = AuraAnalysis.query.get_or_404(record_id)
    data = record.to_dict()
    data['result'] = json.loads(record.result_json)
    return jsonify(data)


@app.route('/api/metrics')
@require_api_key
def metrics():
    """Real metrics from the database."""
    total = AuraAnalysis.query.count()
    by_type = db.session.query(
        AuraAnalysis.analysis_type,
        db.func.count(AuraAnalysis.id)
    ).group_by(AuraAnalysis.analysis_type).all()

    return jsonify({
        'total_analyses': total,
        'by_type': {t: c for t, c in by_type},
        'timestamp': datetime.utcnow().isoformat(),
    })


# ── Admin: Key Management ─────────────────────────────────────────────────────

@app.route('/api/admin/keys', methods=['GET'])
@require_admin_token
def admin_list_keys():
    """List all API keys (hashes never returned)."""
    keys = ApiKey.query.order_by(ApiKey.created_at.desc()).all()
    return jsonify({
        'keys': [
            {
                'id': k.id,
                'label': k.label,
                'is_active': k.is_active,
                'created_at': k.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
            for k in keys
        ],
        'total': len(keys),
        'active': sum(1 for k in keys if k.is_active),
    })


@app.route('/api/admin/keys', methods=['POST'])
@require_admin_token
def admin_create_key():
    """Generate a new API key. Raw key is returned ONCE — store it securely."""
    data = request.get_json(silent=True) or {}
    label = (data.get('label') or '').strip()
    if not label:
        return jsonify({'error': 'label is required'}), 400

    import secrets as _secrets
    raw_key = _secrets.token_hex(32)
    key_hash = ApiKey.hash(raw_key)

    if ApiKey.query.filter_by(key_hash=key_hash).first():
        return jsonify({'error': 'Key collision — try again'}), 500

    key = ApiKey(key_hash=key_hash, label=label, is_active=True)
    db.session.add(key)
    db.session.commit()
    logger.info('Admin created API key id=%d label=%s', key.id, label)

    return jsonify({
        'id': key.id,
        'label': key.label,
        'api_key': raw_key,
        'warning': 'Store this key securely — it will not be shown again.',
    }), 201


@app.route('/api/admin/keys/<int:key_id>', methods=['DELETE'])
@require_admin_token
def admin_revoke_key(key_id):
    """Revoke (deactivate) a key. Pass ?permanent=1 to hard-delete."""
    key = ApiKey.query.get_or_404(key_id)
    permanent = request.args.get('permanent', '').lower() in ('1', 'true', 'yes')

    if permanent:
        db.session.delete(key)
        db.session.commit()
        logger.info('Admin permanently deleted API key id=%d', key_id)
        return jsonify({'deleted': True, 'id': key_id})

    key.is_active = False
    db.session.commit()
    logger.info('Admin revoked API key id=%d label=%s', key_id, key.label)
    return jsonify({'revoked': True, 'id': key_id, 'label': key.label})


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    if not os.environ.get('ANTHROPIC_API_KEY'):
        logger.warning('ANTHROPIC_API_KEY is not set — AI calls will fail.')
    if not os.environ.get('AURA_API_KEY'):
        logger.warning('AURA_API_KEY is not set — all protected endpoints will return 500.')
    port = int(os.environ.get('PORT', 5003))
    app.run(debug=False, host='127.0.0.1', port=port)
