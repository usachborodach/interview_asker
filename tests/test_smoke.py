import os
import tempfile

os.environ.setdefault('SECRET_KEY', 'test')


def _write_list_md(tmpdir: str) -> str:
    path = os.path.join(tmpdir, 'list.md')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(
            "- [Первый вопрос](#anchor-one)\n"
            "- [Второй вопрос](#anchor-two)\n"
            "мусорная строка без вопроса\n"
        )
    return path


def test_app_creates():
    from app import create_app

    with tempfile.TemporaryDirectory() as tmp:
        os.environ['LIST_MD_PATH'] = _write_list_md(tmp)
        app = create_app()
        assert app is not None
        assert 'main.index' in app.view_functions
        assert 'main.random_question' in app.view_functions


def test_random_endpoint_returns_question():
    from app import create_app

    with tempfile.TemporaryDirectory() as tmp:
        os.environ['LIST_MD_PATH'] = _write_list_md(tmp)
        app = create_app()
        client = app.test_client()
        resp = client.get('/api/random')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        assert data['question'] in ('Первый вопрос', 'Второй вопрос')
        assert data['answer_url'].startswith('https://')
        assert data['answer_url'].endswith(('#anchor-one', '#anchor-two'))


def test_index_renders():
    from app import create_app

    with tempfile.TemporaryDirectory() as tmp:
        os.environ['LIST_MD_PATH'] = _write_list_md(tmp)
        app = create_app()
        client = app.test_client()
        resp = client.get('/')
        assert resp.status_code == 200
        assert b'interview_asker' in resp.data