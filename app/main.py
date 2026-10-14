import logging
import random

from flask import Blueprint, render_template, jsonify, current_app

from .extensions import limiter
from .questions import get_all_questions, build_answer_url

logger = logging.getLogger(__name__)
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    total = len(get_all_questions())
    return render_template('index.html', total=total)


@main_bp.route('/api/random')
@limiter.limit("60 per minute")
def random_question():
    questions = get_all_questions()
    if not questions:
        logger.warning("Список вопросов пуст (%s)",
                       current_app.config['LIST_MD_PATH'])
        return jsonify({'success': False, 'message': 'Список вопросов пуст'}), 404

    item = random.choice(questions)
    return jsonify({
        'success': True,
        'question': item['question'],
        'breadcrumbs': item['breadcrumbs'],
        'answer_url': build_answer_url(item['anchor']),
    })