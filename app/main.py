import logging

from flask import Blueprint, render_template, jsonify
from pymongo.errors import PyMongoError

from .extensions import limiter
from .questions import count_questions, get_random_question, get_all_questions

logger = logging.getLogger(__name__)
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    try:
        total = count_questions()
    except PyMongoError:
        logger.exception("MongoDB error on index")
        total = 0
    return render_template('index.html', total=total)


@main_bp.route('/api/random')
@limiter.limit("60 per minute")
def random_question():
    try:
        item = get_random_question()
    except PyMongoError:
        logger.exception("MongoDB error on /api/random")
        return jsonify({
            'success': False,
            'message': 'База данных недоступна',
        }), 503

    if item is None:
        logger.warning("Вопросы в MongoDB отсутствуют")
        return jsonify({'success': False, 'message': 'Список вопросов пуст'}), 404

    return jsonify({
        'success': True,
        'id': item['id'],
        'question': item['question'],
        'answer': item['answer'],
    })

@main_bp.route('/qanda')
@limiter.limit("30 per minute")
def all_qanda():
    try:
        items = get_all_questions()
    except PyMongoError:
        logger.exception("MongoDB error on /qanda")
        return jsonify({
            'success': False,
            'message': 'База данных недоступна',
        }), 503

    return jsonify(items)