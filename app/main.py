import logging

from flask import Blueprint, render_template, jsonify, abort

from .extensions import limiter
from .questions import (
    list_sections,
    section_exists,
    get_section_items,
    count_main_questions,
    get_random_main_question,
    get_random_section_question,
)
from .ml_questions import count_ml_questions, get_random_ml_question

logger = logging.getLogger(__name__)
main_bp = Blueprint('main', __name__)


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


@main_bp.route('/api/random')
@limiter.limit("60 per minute")
def random_question():
    try:
        item = get_random_main_question()
    except Exception:
        logger.exception("Error on /api/random")
        return jsonify({
            'success': False,
            'message': 'Не удалось прочитать вопросы',
        }), 503
    if item is None:
        return jsonify({'success': False, 'message': 'Список вопросов пуст'}), 404
    return jsonify({
        'success': True,
        'question': item['question'],
        'answer': item['answer'],
    })


@main_bp.route('/api/<section>/random')
@limiter.limit("60 per minute")
def section_random(section):
    try:
        item = get_random_section_question(section)
    except Exception:
        logger.exception("Error on /api/%s/random", section)
        return jsonify({
            'success': False,
            'message': 'Не удалось прочитать вопросы',
        }), 503
    if item is None:
        return jsonify({'success': False, 'message': 'Список вопросов пуст'}), 404
    return jsonify({
        'success': True,
        'question': item['question'],
        'answer': item['answer'],
    })


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
        item = get_random_ml_question()
    except Exception:
        logger.exception("Error on /api/ml/random")
        return jsonify({
            'success': False,
            'message': 'Не удалось прочитать справочник',
        }), 503
    if item is None:
        return jsonify({
            'success': False,
            'message': 'Справочник пуст',
        }), 404
    return jsonify({
        'success': True,
        'id': item['id'],
        'category': item['category'],
        'question': item['question'],
        'answer': item['answer'],
    })