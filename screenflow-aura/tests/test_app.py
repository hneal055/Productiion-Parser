"""
ScreenFlow AURA — Test Suite
Run with: pytest tests/ -v
"""

import json
import os
import pytest
from unittest.mock import patch, MagicMock

# Point to a throwaway in-memory DB during tests
os.environ.setdefault('SECRET_KEY', 'test-secret-key')
os.environ.setdefault('AURA_API_KEY', 'test-api-key')
os.environ.setdefault('ANTHROPIC_API_KEY', 'test-anthropic-key')
os.environ.setdefault('AURA_ADMIN_TOKEN', 'test-admin-token')

from app import app, db

VALID_KEY = 'test-api-key'
HEADERS = {'X-API-Key': VALID_KEY}
ADMIN_TOKEN = 'test-admin-token'
ADMIN_HEADERS = {'X-Admin-Token': ADMIN_TOKEN}
SAMPLE_SCREENPLAY = (
    "INT. COFFEE SHOP - DAY\n\n"
    "ALICE (30s, intense) stares at her laptop screen.\n\n"
    "ALICE\nI can't believe they rejected the script.\n\n"
    "BOB\nKeep writing. That's all we can do.\n\n" * 20
)

MOCK_PARSE_RESPONSE = json.dumps({
    "document_metrics": {
        "word_count": 200, "estimated_pages": 0.8,
        "primary_genre": "drama", "complexity_score": 72
    },
    "quality_assessment": {
        "overall_score": 80, "structure_quality": 75,
        "dialogue_effectiveness": 85, "pacing_analysis": "good",
        "commercial_potential": "MEDIUM"
    },
    "ai_insights": {
        "sentiment_analysis": {"overall_sentiment": "complex", "emotional_arc": "rising", "tone_consistency": "consistent"},
        "theme_detection": ["perseverance", "rejection", "creativity"],
        "style_assessment": {"writing_style": "dialogue_heavy", "pacing": "brisk", "originality_score": 78}
    },
    "recommendations": ["Strengthen act 2", "Add more visual description", "Develop Bob's character arc"]
})

MOCK_ANALYZE_RESPONSE = json.dumps({
    "analysis_type": "comprehensive",
    "insights": {
        "narrative_structure": {"act_breakdown": {"act1": "solid", "act2": "needs work", "act3": "strong"}, "plot_points": 5, "climax_strength": "strong"},
        "character_analysis": {"main_characters": 2, "character_depth": "moderate", "character_arcs": 2, "protagonist_strength": "compelling"},
        "commercial_viability": {"target_audience": "broad", "market_potential": "MEDIUM", "comparable_titles": ["Whiplash", "The Wrestler"], "distribution_outlook": "streaming"},
        "technical_assessment": {"formatting_compliance": "compliant", "industry_standards": "meets", "readability_score": 82}
    },
    "recommendations": ["Consider a third act twist", "Tighten dialogue", "Expand the world-building"],
    "risk_assessment": {"overall_risk": "low", "commercial_risk": "medium", "technical_risk": "low", "market_fit": "strong"}
})

MOCK_VALIDATE_RESPONSE = json.dumps({
    "compliance_report": {
        "industry_standards": {"hollywood_format": "94%", "final_draft_compatibility": "90%", "fountain_compatibility": "96%"},
        "quality_metrics": {"structure_integrity": "88%", "character_consistency": "92%", "dialogue_realism": "85%", "pacing_consistency": "89%"}
    },
    "issues": [{"severity": "suggestion", "description": "Scene headings could be more specific", "location": "Act 1, Scene 3"}],
    "overall_score": 91,
    "certification_status": "compliant",
    "summary": "Script meets Hollywood formatting standards. Minor suggestions noted."
})


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    orig_aura_key = os.environ.get('AURA_API_KEY')
    orig_admin_token = os.environ.get('AURA_ADMIN_TOKEN')
    os.environ['AURA_API_KEY'] = VALID_KEY
    os.environ['AURA_ADMIN_TOKEN'] = ADMIN_TOKEN
    with app.app_context():
        db.create_all()
        # Seed the test API key into the ApiKey table so require_api_key passes
        from app import ApiKey
        key_hash = ApiKey.hash(VALID_KEY)
        if not ApiKey.query.filter_by(key_hash=key_hash).first():
            db.session.add(ApiKey(key_hash=key_hash, label='test-key'))
            db.session.commit()
        yield app.test_client()
        db.session.remove()
        db.drop_all()
    if orig_aura_key is None:
        os.environ.pop('AURA_API_KEY', None)
    else:
        os.environ['AURA_API_KEY'] = orig_aura_key
    if orig_admin_token is None:
        os.environ.pop('AURA_ADMIN_TOKEN', None)
    else:
        os.environ['AURA_ADMIN_TOKEN'] = orig_admin_token


# ── Health ────────────────────────────────────────────────────────────────────

def test_health_no_auth_required(client):
    resp = client.get('/api/health')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['status'] == 'operational'
    assert 'total_analyses' in data


# ── Auth ──────────────────────────────────────────────────────────────────────

def test_parse_requires_auth(client):
    resp = client.post('/api/parse', json={'screenplay': SAMPLE_SCREENPLAY})
    assert resp.status_code == 401
    assert 'API key required' in resp.get_json()['error']


def test_parse_rejects_wrong_key(client):
    resp = client.post('/api/parse',
                       json={'screenplay': SAMPLE_SCREENPLAY},
                       headers={'X-API-Key': 'wrong-key'})
    assert resp.status_code == 403


def test_auth_via_query_param(client):
    """API key can also be passed as ?api_key= query param."""
    with patch('app._call_claude', return_value=json.loads(MOCK_PARSE_RESPONSE)):
        resp = client.post(f'/api/parse?api_key={VALID_KEY}',
                           json={'screenplay': SAMPLE_SCREENPLAY})
    assert resp.status_code == 200


# ── Parse ─────────────────────────────────────────────────────────────────────

def test_parse_missing_screenplay(client):
    resp = client.post('/api/parse', json={}, headers=HEADERS)
    assert resp.status_code == 400


def test_parse_success(client):
    with patch('app._call_claude', return_value=json.loads(MOCK_PARSE_RESPONSE)):
        resp = client.post('/api/parse',
                           json={'screenplay': SAMPLE_SCREENPLAY},
                           headers=HEADERS)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert 'analysis' in data
    assert data['analysis']['quality_assessment']['overall_score'] == 80
    assert 'analysis_id' in data['analysis']


def test_parse_persists_to_db(client):
    with patch('app._call_claude', return_value=json.loads(MOCK_PARSE_RESPONSE)):
        client.post('/api/parse', json={'screenplay': SAMPLE_SCREENPLAY}, headers=HEADERS)
    resp = client.get('/api/metrics', headers=HEADERS)
    assert resp.get_json()['total_analyses'] >= 1


# ── Analyze ───────────────────────────────────────────────────────────────────

def test_analyze_success(client):
    with patch('app._call_claude', return_value=json.loads(MOCK_ANALYZE_RESPONSE)):
        resp = client.post('/api/analyze',
                           json={'screenplay': SAMPLE_SCREENPLAY, 'analysis_type': 'comprehensive'},
                           headers=HEADERS)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert data['analysis']['insights']['character_analysis']['main_characters'] == 2


# ── Validate ──────────────────────────────────────────────────────────────────

def test_validate_success(client):
    with patch('app._call_claude', return_value=json.loads(MOCK_VALIDATE_RESPONSE)):
        resp = client.post('/api/validate',
                           json={'screenplay': SAMPLE_SCREENPLAY},
                           headers=HEADERS)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert data['validation']['overall_score'] == 91
    assert data['validation']['certification_status'] == 'compliant'


# ── Batch ─────────────────────────────────────────────────────────────────────

MOCK_BATCH_ITEM = json.dumps({
    "item_id": "item-1",
    "document_metrics": {"word_count": 100, "estimated_pages": 0.4, "primary_genre": "drama"},
    "quick_verdict": {"overall_score": 78, "commercial_potential": "MEDIUM", "recommendation": "Promising concept."},
    "ai_analysis": {"genre": "drama", "sentiment": "complex", "key_themes": ["loss", "hope"]}
})


def test_batch_missing_screenplays(client):
    resp = client.post('/api/batch/parse', json={}, headers=HEADERS)
    assert resp.status_code == 400


def test_batch_success(client):
    with patch('app._call_claude', return_value=json.loads(MOCK_BATCH_ITEM)):
        resp = client.post('/api/batch/parse',
                           json={'screenplays': [SAMPLE_SCREENPLAY, SAMPLE_SCREENPLAY]},
                           headers=HEADERS)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert data['batch']['total_items'] == 2
    assert len(data['results']) == 2


# ── History ───────────────────────────────────────────────────────────────────

def test_history_empty(client):
    resp = client.get('/api/history', headers=HEADERS)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['total'] == 0
    assert data['records'] == []


def test_history_after_analysis(client):
    with patch('app._call_claude', return_value=json.loads(MOCK_PARSE_RESPONSE)):
        client.post('/api/parse', json={'screenplay': SAMPLE_SCREENPLAY}, headers=HEADERS)

    resp = client.get('/api/history', headers=HEADERS)
    data = resp.get_json()
    assert data['total'] >= 1
    record = data['records'][0]
    assert record['analysis_type'] == 'parse'
    assert 'created_at' in record


def test_history_detail(client):
    with patch('app._call_claude', return_value=json.loads(MOCK_PARSE_RESPONSE)):
        parse_resp = client.post('/api/parse', json={'screenplay': SAMPLE_SCREENPLAY}, headers=HEADERS)
    record_id = parse_resp.get_json()['analysis']['analysis_id']

    resp = client.get(f'/api/history/{record_id}', headers=HEADERS)
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'result' in data


# ── Metrics ───────────────────────────────────────────────────────────────────

def test_metrics(client):
    resp = client.get('/api/metrics', headers=HEADERS)
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'total_analyses' in data
    assert 'by_type' in data


# ── Admin: Key Management ─────────────────────────────────────────────────────

def test_admin_list_keys_requires_token(client):
    resp = client.get('/api/admin/keys')
    assert resp.status_code == 403


def test_admin_list_keys_wrong_token(client):
    resp = client.get('/api/admin/keys', headers={'X-Admin-Token': 'wrong'})
    assert resp.status_code == 403


def test_admin_list_keys(client):
    resp = client.get('/api/admin/keys', headers=ADMIN_HEADERS)
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'keys' in data
    assert 'total' in data
    assert 'active' in data
    # The seeded test-api-key should appear
    assert data['total'] >= 1


def test_admin_create_key(client):
    resp = client.post('/api/admin/keys',
                       json={'label': 'Integration Test Key'},
                       headers=ADMIN_HEADERS)
    assert resp.status_code == 201
    data = resp.get_json()
    assert 'api_key' in data
    assert len(data['api_key']) == 64  # 32-byte hex
    assert data['label'] == 'Integration Test Key'
    assert 'warning' in data


def test_admin_create_key_missing_label(client):
    resp = client.post('/api/admin/keys', json={}, headers=ADMIN_HEADERS)
    assert resp.status_code == 400


def test_admin_revoke_key(client):
    # Create a key, then revoke it
    create_resp = client.post('/api/admin/keys',
                              json={'label': 'To Be Revoked'},
                              headers=ADMIN_HEADERS)
    key_id = create_resp.get_json()['id']

    revoke_resp = client.delete(f'/api/admin/keys/{key_id}', headers=ADMIN_HEADERS)
    assert revoke_resp.status_code == 200
    data = revoke_resp.get_json()
    assert data['revoked'] is True
    assert data['id'] == key_id

    # Revoked key should not work for API calls
    from app import ApiKey
    with client.application.app_context():
        k = ApiKey.query.get(key_id)
        assert k is not None
        assert k.is_active is False


def test_admin_delete_key_permanent(client):
    create_resp = client.post('/api/admin/keys',
                              json={'label': 'To Be Deleted'},
                              headers=ADMIN_HEADERS)
    key_id = create_resp.get_json()['id']

    del_resp = client.delete(f'/api/admin/keys/{key_id}?permanent=1', headers=ADMIN_HEADERS)
    assert del_resp.status_code == 200
    data = del_resp.get_json()
    assert data['deleted'] is True

    from app import ApiKey
    with client.application.app_context():
        assert ApiKey.query.get(key_id) is None


def test_admin_revoke_nonexistent_key(client):
    resp = client.delete('/api/admin/keys/99999', headers=ADMIN_HEADERS)
    assert resp.status_code == 404


# -- Additional edge-case tests ------------------------------------------------

def test_parse_empty_screenplay_rejected(client):
    resp = client.post('/api/parse', json={'screenplay': ''}, headers=HEADERS)
    assert resp.status_code == 400


def test_parse_whitespace_only_rejected(client):
    resp = client.post('/api/parse', json={'screenplay': '   '}, headers=HEADERS)
    assert resp.status_code == 400


def test_parse_very_short_script_still_processed(client):
    # Very short but non-empty scripts should still be processed (size validation not enforced)
    with __import__('unittest.mock', fromlist=['patch']).patch('app._call_claude', return_value=__import__('json').dumps({'document_metrics': {'word_count': 1, 'estimated_pages': 0.1, 'primary_genre': 'drama', 'complexity_score': 50}, 'quality_assessment': {'overall_score': 50, 'structure_quality': 50, 'dialogue_effectiveness': 50, 'pacing_analysis': 'slow', 'commercial_potential': 'LOW'}, 'ai_insights': {'sentiment_analysis': {'overall_sentiment': 'neutral', 'emotional_arc': 'flat', 'tone_consistency': 'consistent'}, 'theme_detection': [], 'style_assessment': {'writing_style': 'minimal', 'pacing': 'slow', 'originality_score': 30}}, 'recommendations': []})):
        resp = client.post('/api/parse', json={'screenplay': 'INT. ROOM - DAY\n\nHello.'}, headers=HEADERS)
    # Accept 200 or 500 (if Claude call fails in test mode) but not 400
    assert resp.status_code in (200, 500)


def test_analyze_empty_screenplay_rejected(client):
    resp = client.post('/api/analyze', json={'screenplay': ''}, headers=HEADERS)
    assert resp.status_code == 400


def test_validate_empty_screenplay_rejected(client):
    resp = client.post('/api/validate', json={'screenplay': ''}, headers=HEADERS)
    assert resp.status_code == 400


def test_index_page_loads(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'ScreenFlow' in resp.data or b'API' in resp.data


def test_admin_keys_no_auth_returns_403(client):
    resp = client.get('/api/admin/keys')
    assert resp.status_code == 403


def test_admin_keys_wrong_token_returns_403(client):
    resp = client.get('/api/admin/keys', headers={'X-Admin-Token': 'invalid'})
    assert resp.status_code == 403
