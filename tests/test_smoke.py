import os
from pathlib import Path

os.environ.setdefault('SECRET_KEY', 'test')

import pytest


MAIN_MD = """\
# Что такое inode?
- Inode — структура метаданных файла.

---

# Что такое pod?
- Pod — минимальная единица планирования.
"""

BASE_MD = """\
# kubernetes. Что такое Deployment?
- контроллер над ReplicaSet'ами.

---

# kubernetes. Что такое pod?
- минимальная единица планирования.
"""

ML_HANDBOOK = """\
# 🚀 Ultimate Handbook

Intro text (должен быть проигнорирован).

---

### [RAG] 1. Что такое RAG?
RAG — Retrieval-Augmented Generation.

### [Python] 2. Что такое GIL?
GIL — Global Interpreter Lock.

---

### [ML] 3. Что такое Bias-Variance?
Компромисс между смещением и дисперсией.
"""


def _write_qanda(tmp_path: Path) -> str:
    (tmp_path / 'main.md').write_text(MAIN_MD, encoding='utf-8')
    (tmp_path / 'base.md').write_text(BASE_MD, encoding='utf-8')
    return str(tmp_path)


@pytest.fixture
def app(tmp_path):
    from app import create_app
    a = create_app()
    a.config['QANDA_DIR'] = _write_qanda(tmp_path)
    a.config['ML_HANDBOOK_PATH'] = str(tmp_path / 'handbook.md')
    (tmp_path / 'handbook.md').write_text(ML_HANDBOOK, encoding='utf-8')
    return a


@pytest.fixture
def client(app):
    return app.test_client()


# ---------- qanda main ----------

def test_index_renders(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'interview_asker' in resp.data
    assert b'\xd0\x92\xd1\x81\xd0\xb5\xd0\xb3\xd0\xbe' in resp.data  # "Всего"


def test_qanda_returns_only_main(client):
    resp = client.get('/qanda')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) == 2
    qs = {item['question'] for item in data}
    assert 'Что такое inode?' in qs
    assert 'Что такое pod?' in qs
    assert 'kubernetes. Что такое Deployment?' not in qs
    for item in data:
        assert set(item.keys()) == {'question', 'answer'}


def test_random_main_returns_question_and_answer(client):
    for _ in range(10):
        resp = client.get('/api/random')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        assert data['question']
        assert data['answer']


# ---------- qanda sections ----------

def test_section_index_renders(client):
    resp = client.get('/base')
    assert resp.status_code == 200
    assert b'/ base' in resp.data


def test_missing_section_returns_404(client):
    resp = client.get('/nonexistent')
    assert resp.status_code == 404


def test_qanda_section(client):
    resp = client.get('/qanda/base')
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 2
    assert all(item['question'].startswith('kubernetes.') for item in data)


def test_random_section(client):
    for _ in range(10):
        resp = client.get('/api/base/random')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        assert data['question'].startswith('kubernetes.')


def test_random_missing_section_returns_404(client):
    resp = client.get('/api/nonexistent/random')
    assert resp.status_code == 404
    assert resp.get_json()['success'] is False


def test_qanda_missing_section_returns_404(client):
    resp = client.get('/qanda/nonexistent')
    assert resp.status_code == 404


def test_section_name_is_sanitized(client):
    # попытка выйти за пределы директории — должна отбиться 404
    resp = client.get('/qanda/..%2Fetc%2Fpasswd')
    assert resp.status_code == 404


# ---------- ML handbook ----------

def test_ml_parser_ignores_preamble_and_strips_separators():
    from app.ml_questions import _parse

    items = _parse(ML_HANDBOOK)
    assert len(items) == 3
    assert items[0]['category'] == 'RAG'
    assert items[0]['question'] == 'Что такое RAG?'
    assert 'Retrieval-Augmented' in items[0]['answer']
    assert items[2]['category'] == 'ML'
    assert not items[2]['answer'].rstrip().endswith('---')


def test_ml_index_renders(client):
    resp = client.get('/Drewz1312-ml')
    assert resp.status_code == 200
    assert b'ML/RAG' in resp.data


def test_ml_random_endpoint(client):
    categories = set()
    for _ in range(20):
        resp = client.get('/api/ml/random')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        assert data['question']
        assert data['answer']
        assert data['category'] in ('RAG', 'Python', 'ML')
        categories.add(data['category'])
    assert len(categories) >= 2