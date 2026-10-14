import os
import tempfile

os.environ.setdefault('SECRET_KEY', 'test')


LIST_MD = """\
- [Вопросы админам 2.0](#root)
    - [Железячные вопросы](#hw)
        - [Сервер не отвечает, как получить доступ](#q1)
        - [Что такое IPMI?](#q2)
    - [Linux](#linux)
        - [Расскажи про загрузку ОС](#q3)
- [Одиночный вопрос верхнего уровня](#q4)
мусорная строка без вопроса
"""


def _write_list_md(tmpdir: str) -> str:
    path = os.path.join(tmpdir, 'list.md')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(LIST_MD)
    return path


def test_app_creates():
    from app import create_app

    with tempfile.TemporaryDirectory() as tmp:
        os.environ['LIST_MD_PATH'] = _write_list_md(tmp)
        app = create_app()
        assert app is not None
        assert 'main.index' in app.view_functions
        assert 'main.random_question' in app.view_functions


def test_leaves_only_and_breadcrumbs():
    from app.questions import parse_list

    with tempfile.TemporaryDirectory() as tmp:
        path = _write_list_md(tmp)
        qs = parse_list(path)

    by_anchor = {q['anchor']: q for q in qs}

    # Только листья: категории ('#root', '#hw', '#linux') в вопросах быть не должно
    assert '#root' not in by_anchor
    assert '#hw' not in by_anchor
    assert '#linux' not in by_anchor

    # Ровно 4 листа
    assert len(qs) == 4

    # Breadcrumbs для вложенного вопроса
    assert by_anchor['#q1']['breadcrumbs'] == ['Вопросы админам 2.0', 'Железячные вопросы']
    assert by_anchor['#q3']['breadcrumbs'] == ['Вопросы админам 2.0', 'Linux']

    # Лист верхнего уровня — без родителей
    assert by_anchor['#q4']['breadcrumbs'] == []


def test_random_endpoint_returns_breadcrumbs():
    from app import create_app

    with tempfile.TemporaryDirectory() as tmp:
        os.environ['LIST_MD_PATH'] = _write_list_md(tmp)
        app = create_app()
        client = app.test_client()

        # Несколько раз, чтобы покрыть оба варианта — с breadcrumbs и без
        seen_with = False
        seen_without = False
        for _ in range(30):
            resp = client.get('/api/random')
            assert resp.status_code == 200
            data = resp.get_json()
            assert data['success'] is True
            assert isinstance(data['breadcrumbs'], list)
            assert data['answer_url'].startswith('https://')
            if data['breadcrumbs']:
                seen_with = True
            else:
                seen_without = True
            if seen_with and seen_without:
                break

        assert seen_with, "ни разу не выпал вопрос с breadcrumbs"
        assert seen_without, "ни разу не выпал вопрос верхнего уровня"


def test_index_renders():
    from app import create_app

    with tempfile.TemporaryDirectory() as tmp:
        os.environ['LIST_MD_PATH'] = _write_list_md(tmp)
        app = create_app()
        client = app.test_client()
        resp = client.get('/')
        assert resp.status_code == 200
        assert b'interview_asker' in resp.data
        assert b'\xd0\x92\xd1\x81\xd0\xb5\xd0\xb3\xd0\xbe' in resp.data  # "Всего" в utf-8