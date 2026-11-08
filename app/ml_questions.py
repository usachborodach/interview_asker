"""Парсинг ML/RAG interview handbook из markdown-файла."""
import logging
import random
import re
from pathlib import Path

from flask import current_app

logger = logging.getLogger(__name__)

# Кеш на процесс: ключ = (путь, mtime). Перечитываем только при изменении.
_cache: dict = {'key': None, 'items': []}

_HEADER_RE = re.compile(
    r'^###\s*\[([^\]]+)\]\s*(.+)$',
    re.MULTILINE,
)
_NUMBER_PREFIX_RE = re.compile(r'^\d+\.\s*')


def _parse(content: str) -> list[dict]:
    """
    Разбирает markdown и возвращает список:
        {'id': int, 'category': str, 'question': str, 'answer': str}
    """
    matches = list(_HEADER_RE.finditer(content))
    if not matches:
        return []

    items = []
    for i, match in enumerate(matches):
        category = match.group(1).strip()
        raw_question = match.group(2).strip()
        question = _NUMBER_PREFIX_RE.sub('', raw_question)

        answer_start = match.end()
        answer_end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        answer = content[answer_start:answer_end]

        # Отрезаем хвостовые пустые строки и тематические разделители "---"
        lines = answer.split('\n')
        while lines and lines[-1].strip() in ('', '---'):
            lines.pop()
        answer = '\n'.join(lines).strip()

        items.append({
            'id': i,
            'category': category,
            'question': question,
            'answer': answer,
        })
    return items


def _load() -> list[dict]:
    path_str = current_app.config['ML_HANDBOOK_PATH']
    path = Path(path_str)
    if not path.exists():
        logger.warning("ML handbook не найден: %s", path_str)
        return []

    try:
        mtime = path.stat().st_mtime
    except OSError:
        logger.exception("Не удалось получить mtime: %s", path_str)
        return []

    key = (str(path), mtime)
    if _cache['key'] == key:
        return _cache['items']

    try:
        with path.open(encoding='utf-8') as f:
            content = f.read()
    except (OSError, UnicodeDecodeError):
        logger.exception("Не удалось прочитать ML handbook: %s", path_str)
        return []

    items = _parse(content)
    _cache['key'] = key
    _cache['items'] = items
    logger.info("ML handbook загружен: %d вопросов из %s", len(items), path_str)
    return items


def count_ml_questions() -> int:
    return len(_load())


def get_random_ml_question() -> dict | None:
    items = _load()
    if not items:
        return None
    return random.choice(items)