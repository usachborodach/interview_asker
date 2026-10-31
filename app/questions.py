"""Работа с вопросами из MongoDB."""
import logging
import random

from .extensions import get_collection

logger = logging.getLogger(__name__)


def count_questions() -> int:
    return get_collection().estimated_document_count()


def get_random_question() -> dict | None:
    """
    Возвращает случайный документ в виде:
        {'id': '...', 'question': '...', 'answer': '...'}
    или None, если коллекция пуста.
    """
    collection = get_collection()
    total = collection.estimated_document_count()
    if total == 0:
        return None

    idx = random.randrange(total)
    doc = collection.find_one(skip=idx)
    if doc is None:
        # estimated_document_count может быть неточным (недавние удаления),
        # тогда просто берём первый попавшийся.
        doc = collection.find_one()
        if doc is None:
            return None

    return {
        'id': str(doc['_id']),
        'question': doc['question'],
        'answer': doc['answer'],
    }