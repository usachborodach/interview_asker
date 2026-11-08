import os
from unittest.mock import patch

os.environ.setdefault('SECRET_KEY', 'test')

import mongomock
import pytest


@pytest.fixture
def collection():
    client = mongomock.MongoClient()
    coll = client['interview_asker']['qanda']
    coll.insert_many([
        {'question': 'Что такое inode?', 'answer': '- Inode — структура метаданных файла.'},
        {'question': 'Что такое pod?',   'answer': '- Pod — минимальная единица планирования.'},
        {'question': 'Что такое NAT?',   'answer': '- NAT — преобразование адресов.'},
    ])
    return coll


@pytest.fixture
def client(collection):
    from app import create_app

    app = create_app()
    with patch('app.questions.get_collection', return_value=collection):
        with app.test_client() as c:
            yield c


def test_index_renders(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'interview_asker' in resp.data
    assert b'\xd0\x92\xd1\x81\xd0\xb5\xd0\xb3\xd0\xbe' in resp.data  # "Всего"


def test_random_returns_question_and_answer(client):
    seen = set()
    for _ in range(20):
        resp = client.get('/api/random')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        assert data['question']
        assert data['answer']
        seen.add(data['question'])
    assert len(seen) >= 2  # за 20 попыток из 3 документов — практически гарантированно


def test_random_empty_collection():
    from app import create_app

    empty = mongomock.MongoClient()['interview_asker']['qanda']
    app = create_app()
    with patch('app.questions.get_collection', return_value=empty):
        with app.test_client() as c:
            resp = c.get('/api/random')
            assert resp.status_code == 404
            assert resp.get_json()['success'] is False


def test_count_questions(collection):
    from app.questions import count_questions

    with patch('app.questions.get_collection', return_value=collection):
        assert count_questions() == 3


def test_qanda_returns_all_without_id(client):
    resp = client.get('/qanda')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) == 3
    for item in data:
        assert set(item.keys()) == {'question', 'answer'}
        assert item['question']
        assert item['answer']


def test_qanda_returns_empty_list_when_empty():
    from app import create_app

    empty = mongomock.MongoClient()['interview_asker']['qanda']
    app = create_app()
    with patch('app.questions.get_collection', return_value=empty):
        with app.test_client() as c:
            resp = c.get('/qanda')
            assert resp.status_code == 200
            assert resp.get_json() == []


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


def _write_ml_handbook(tmpdir: str) -> str:
    import os
    path = os.path.join(tmpdir, 'handbook.md')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(ML_HANDBOOK)
    return path


def test_ml_parser_ignores_preamble_and_strips_separators():
    from app.ml_questions import _parse

    items = _parse(ML_HANDBOOK)
    assert len(items) == 3
    assert items[0]['category'] == 'RAG'
    assert items[0]['question'] == 'Что такое RAG?'
    assert 'Retrieval-Augmented' in items[0]['answer']
    assert items[2]['category'] == 'ML'
    # хвостовой "---" не должен попасть в ответ
    assert not items[2]['answer'].rstrip().endswith('---')


def test_ml_index_renders(tmp_path):
    from app import create_app

    handbook = _write_ml_handbook(str(tmp_path))
    app = create_app()
    app.config['ML_HANDBOOK_PATH'] = handbook
    client = app.test_client()

    resp = client.get('/Drewz1312-ml')
    assert resp.status_code == 200
    assert b'ML/RAG' in resp.data


def test_ml_random_endpoint(tmp_path):
    from app import create_app

    handbook = _write_ml_handbook(str(tmp_path))
    app = create_app()
    app.config['ML_HANDBOOK_PATH'] = handbook
    client = app.test_client()

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

    assert len(categories) >= 2  # рандом работает


def test_ml_missing_file_returns_zero_count(tmp_path):
    from app import create_app

    app = create_app()
    app.config['ML_HANDBOOK_PATH'] = str(tmp_path / 'does-not-exist.md')
    client = app.test_client()

    resp = client.get('/Drewz1312-ml')
    assert resp.status_code == 200
    assert b'\xd0\x92\xd1\x81\xd0\xb5\xd0\xb3\xd0\xbe' in resp.data  # "Всего"

    resp = client.get('/api/ml/random')
    assert resp.status_code == 404
    assert resp.get_json()['success'] is False            