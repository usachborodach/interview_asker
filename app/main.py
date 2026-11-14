import logging

from flask import Blueprint, render_template, jsonify, abort

from .extensions import limiter
from .deck import advance
from .questions import (
    list_sections,
    section_exists,
    get_section_items,
    get_section_version,
    get_main_items,
    count_main_questions,
)
from .ml_questions import (
    count_ml_questions,
    get_ml_version,
    _load as ml_load,
)

logger = logging.getLogger(__name__)
main_bp = Blueprint('main', __name__)


def _deck_response(result: dict):
    """Ответ эндпоинтов колоды: вопрос + позиция, чтобы фронт прятал «назад»."""
    item = result['item']
    payload = {
        'success': True,
        'question': item['question'],
        'answer': item['answer'],
        'position': result['position'],
    }
    for k in ('id', 'category'):
        if k in item:
            payload[k] = item[k]
    return jsonify(payload)


@main_bp.route('/api/random')
@limiter.limit("60 per minute")
def random_question():
    try:
        result = advance(get_main_items(), get_section_version('main'),
                         'qanda:main', +1)
    except Exception:
        logger.exception("Error on /api/random")
        return jsonify({
            'success': False,
            'message': 'Не удалось прочитать вопросы',
        }), 503
    if result is None:
        return jsonify({'success': False, 'message': 'Список вопросов пуст'}), 404
    return _deck_response(result)


@main_bp.route('/api/back')
@limiter.limit("60 per minute")
def back_question():
    try:
        result = advance(get_main_items(), get_section_version('main'),
                         'qanda:main', -1)
    except Exception:
        logger.exception("Error on /api/back")
        return jsonify({
            'success': False,
            'message': 'Не удалось прочитать вопросы',
        }), 503
    if result is None:
        return jsonify({'success': False, 'message': 'Список вопросов пуст'}), 404
    return _deck_response(result)


@main_bp.route('/api/<section>/random')
@limiter.limit("60 per minute")
def section_random(section):
    try:
        result = advance(get_section_items(section), get_section_version(section),
                         f'qanda:{section}', +1)
    except Exception:
        logger.exception("Error on /api/%s/random", section)
        return jsonify({
            'success': False,
            'message': 'Не удалось прочитать вопросы',
        }), 503
    if result is None:
        return jsonify({'success': False, 'message': 'Список вопросов пуст'}), 404
    return _deck_response(result)


@main_bp.route('/api/<section>/back')
@limiter.limit("60 per minute")
def section_back(section):
    try:
        result = advance(get_section_items(section), get_section_version(section),
                         f'qanda:{section}', -1)
    except Exception:
        logger.exception("Error on /api/%s/back", section)
        return jsonify({
            'success': False,
            'message': 'Не удалось прочитать вопросы',
        }), 503
    if result is None:
        return jsonify({'success': False, 'message': 'Список вопросов пуст'}), 404
    return _deck_response(result)


@main_bp.route('/')
def index():
    try:
        total = count_main_questions()
    except Exception:
        logger.exception("Error loading main questions")
        total = 0
    return render_template('index.html', total=total, section=None)


@main_bp.route('/<section>')
def section_index(section):
    if not section_exists(section):
        abort(404)
    items = get_section_items(section)
    return render_template('index.html', total=len(items), section=section)


@main_bp.route('/qanda')
@limiter.limit("30 per minute")
def all_qanda():
    try:
        items = get_section_items('main')
    except Exception:
        logger.exception("Error on /qanda")
        return jsonify({
            'success': False,
            'message': 'Не удалось прочитать вопросы',
        }), 503
    return jsonify(items)


@main_bp.route('/qanda/<section>')
@limiter.limit("30 per minute")
def all_qanda_section(section):
    if not section_exists(section):
        abort(404)
    return jsonify(get_section_items(section))


# ---------- ML/RAG handbook ----------

@main_bp.route('/Drewz1312-ml')
def ml_index():
    try:
        total = count_ml_questions()
    except Exception:
        logger.exception("Error loading ML handbook")
        total = 0
    return render_template('ml_index.html', total=total)


@main_bp.route('/api/ml/random')
@limiter.limit("60 per minute")
def ml_random_question():
    try:
        result = advance(ml_load(), get_ml_version(), 'ml', +1)
    except Exception:
        logger.exception("Error on /api/ml/random")
        return jsonify({
            'success': False,
            'message': 'Не удалось прочитать справочник',
        }), 503
    if result is None:
        return jsonify({
            'success': False,
            'message': 'Справочник пуст',
        }), 404
    return _deck_response(result)


@main_bp.route('/api/ml/back')
@limiter.limit("60 per minute")
def ml_back_question():
    try:
        result = advance(ml_load(), get_ml_version(), 'ml', -1)
    except Exception:
        logger.exception("Error on /api/ml/back")
        return jsonify({
            'success': False,
            'message': 'Не удалось прочитать справочник',
        }), 503
    if result is None:
        return jsonify({
            'success': False,
            'message': 'Справочник пуст',
        }), 404
    return _deck_response(result)