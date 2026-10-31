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