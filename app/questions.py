"""Парсинг файла list.md — вытаскиваем вопросы и anchors."""
import logging
from pathlib import Path

from flask import current_app

logger = logging.getLogger(__name__)


def parse_list(path: str) -> list[dict]:
    """
    Разбирает list.md формата:
        - [Текст вопроса](#anchor)
    Возвращает список словарей {'question': ..., 'anchor': ...}.
    """
    questions: list[dict] = []
    p = Path(path)
    if not p.exists():
        logger.warning("list.md не найден по пути %s", path)
        return questions

    with p.open(encoding='utf-8') as f:
        for raw in f:
            line = raw.strip()
            if not line.startswith('- ['):
                continue
            try:
                question = line.split('[', 1)[1].split(']', 1)[0]
                anchor = line.split('(', 1)[1].split(')', 1)[0]
            except IndexError:
                # Строка нестандартного формата — пропускаем
                continue
            questions.append({'question': question, 'anchor': anchor})

    return questions


def get_all_questions() -> list[dict]:
    return parse_list(current_app.config['LIST_MD_PATH'])


def build_answer_url(anchor: str) -> str:
    base = current_app.config['ANSWER_BASE_URL'].rstrip('/')
    return f"{base}{anchor}"