"""
Production Budget Parser — Test Suite
Run with: pytest tests/ -v
"""

import io
import json
import os
import pytest
from unittest.mock import patch, MagicMock

os.environ.setdefault('SECRET_KEY', 'test-secret-key-32chars-long-xx')
os.environ.setdefault('APP_PASSWORD', 'testpassword')
os.environ.setdefault('ANTHROPIC_API_KEY', 'test-anthropic-key')
os.environ.setdefault('BUDGET_API_KEY', 'test-budget-key')

from web_app import app, db

PASSWORD = 'testpassword'

SAMPLE_CSV = b"""Category,Department,Description,Amount
Director,Pre-Production,Director Fee,15000
Producer,Pre-Production,Producer Fee,10000
Crew,Production,Cinematographer,8000
Equipment,Production,Camera Package,5000
Location,Production,Studio Rental,12000
Post-Production,Post-Production,Video Editor,6000
Insurance,Production,Production Insurance,2000
Contingency,Production,10% Contingency,5800
"""


USERNAME = 'admin'


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    orig_pw = os.environ.get('APP_PASSWORD')
    os.environ['APP_PASSWORD'] = PASSWORD
    with app.app_context():
        db.create_all()
        # Create admin user for tests (skip if _seed_admin already created it)
        from database_models import User
        if not User.query.filter_by(username=USERNAME).first():
            u = User(username=USERNAME, is_admin=True)
            u.set_password(PASSWORD)
            db.session.add(u)
            db.session.commit()
        yield app.test_client()
        db.session.remove()
        db.drop_all()
    if orig_pw is None:
        os.environ.pop('APP_PASSWORD', None)
    else:
        os.environ['APP_PASSWORD'] = orig_pw


def login(client):
    return client.post('/login',
                       data={'username': USERNAME, 'password': PASSWORD},
                       follow_redirects=True)


# ── Health ────────────────────────────────────────────────────────────────────

def test_health_no_auth_required(client):
    resp = client.get('/api/health')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['status'] == 'ok'


# ── Auth ──────────────────────────────────────────────────────────────────────

def test_login_page_loads(client):
    resp = client.get('/login')
    assert resp.status_code == 200


def test_login_success_redirects(client):
    resp = client.post('/login', data={'username': USERNAME, 'password': PASSWORD}, follow_redirects=False)
    assert resp.status_code == 302


def test_login_wrong_password(client):
    resp = client.post('/login', data={'username': USERNAME, 'password': 'wrongpass'}, follow_redirects=True)
    assert b'Invalid' in resp.data


def test_empty_password_rejected(client):
    resp = client.post('/login', data={'username': USERNAME, 'password': ''}, follow_redirects=True)
    assert b'Invalid' in resp.data


def test_root_redirects_unauthenticated(client):
    resp = client.get('/', follow_redirects=False)
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


def test_logout_clears_session(client):
    login(client)
    client.get('/logout')
    resp = client.get('/', follow_redirects=False)
    assert resp.status_code == 302


def test_protected_routes_require_login(client):
    for path in ['/', '/upload', '/export-excel/fake-id', '/generate-pdf/fake-id']:
        resp = client.get(path, follow_redirects=False)
        assert resp.status_code in (302, 405), f'{path} should be protected'


def test_dashboard_accessible_after_login(client):
    login(client)
    resp = client.get('/')
    assert resp.status_code == 200


# ── Upload ────────────────────────────────────────────────────────────────────

def test_upload_requires_login(client):
    resp = client.post('/upload', data={})
    assert resp.status_code == 302


def test_upload_no_file_redirects(client):
    login(client)
    resp = client.post('/upload', data={}, follow_redirects=True)
    assert resp.status_code == 200


def test_upload_bad_extension(client):
    login(client)
    data = {'file': (io.BytesIO(b'content'), 'test.docx')}
    resp = client.post('/upload', data=data, content_type='multipart/form-data',
                       follow_redirects=True)
    assert resp.status_code == 200


def test_upload_valid_csv_creates_analysis(client):
    login(client)
    data = {'file': (io.BytesIO(SAMPLE_CSV), 'test_budget.csv')}
    resp = client.post('/upload', data=data, content_type='multipart/form-data',
                       follow_redirects=True)
    assert resp.status_code == 200
    # Should show analysis page content
    assert b'test_budget' in resp.data or b'Budget' in resp.data


def test_upload_invalid_csv_no_amount_column(client):
    login(client)
    bad_csv = b'Category,Department\nCrew,Production\n'
    data = {'file': (io.BytesIO(bad_csv), 'bad.csv')}
    resp = client.post('/upload', data=data, content_type='multipart/form-data',
                       follow_redirects=True)
    assert resp.status_code == 200
    assert b'Missing' in resp.data or b'missing' in resp.data


# ── Analysis persistence ──────────────────────────────────────────────────────

def test_analysis_stored_in_db(client):
    from web_app import db
    from database_models import BudgetAnalysis
    login(client)
    data = {'file': (io.BytesIO(SAMPLE_CSV), 'persist_test.csv')}
    client.post('/upload', data=data, content_type='multipart/form-data',
                follow_redirects=True)
    with app.app_context():
        count = BudgetAnalysis.query.count()
    assert count >= 1


def test_analysis_page_loads(client):
    from database_models import BudgetAnalysis
    login(client)
    data = {'file': (io.BytesIO(SAMPLE_CSV), 'analysis_test.csv')}
    client.post('/upload', data=data, content_type='multipart/form-data',
                follow_redirects=True)
    with app.app_context():
        record = BudgetAnalysis.query.first()
        if record:
            resp = client.get(f'/analysis/{record.id}')
            assert resp.status_code == 200


# ── Risk manager ──────────────────────────────────────────────────────────────

def test_risk_manager_analyzes_csv():
    import pandas as pd
    from risk_manager import RiskManager
    import io as _io
    df = pd.read_csv(_io.BytesIO(SAMPLE_CSV))
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
    rm = RiskManager()
    result = rm.analyze_risks(df)
    assert isinstance(result, dict)
    assert 'risk_score' in result or 'risk_level' in result or len(result) > 0


# ── check_password ────────────────────────────────────────────────────────────

def test_check_password_correct():
    from web_app import check_password
    os.environ['APP_PASSWORD'] = 'mypassword'
    assert check_password('mypassword') is True


def test_check_password_wrong():
    from web_app import check_password
    os.environ['APP_PASSWORD'] = 'mypassword'
    assert check_password('wrongpass') is False


def test_check_password_empty_env_returns_false():
    from web_app import check_password
    orig = os.environ.pop('APP_PASSWORD', None)
    try:
        assert check_password('') is False
        assert check_password('anything') is False
    finally:
        if orig:
            os.environ['APP_PASSWORD'] = orig
