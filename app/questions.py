"""Парсинг файла list.md — извлекаем только листья дерева с breadcrumbs."""
import logging
from pathlib import Path

from flask import current_app

logger = logging.getLogger(__name__)


def _parse_line(raw: str) -> dict | None:
    """Парсит строку вида '        - [Текст](#anchor)'. Возвращает dict или None."""
    stripped = raw.strip()
    if not stripped.startswith('- ['):
        return None
    try:
        question = stripped.split('[', 1)[1].split(']', 1)[0]
        anchor = stripped.split('(', 1)[1].split(')', 1)[0]
    except IndexError:
        return None
    return {
        'indent': len(raw) - len(raw.lstrip(' ')),
        'question': question,
        'anchor': anchor,
        'children': [],
    }


def _build_tree(lines) -> list[dict]:
    """Строит лес по отступам. Возвращает список корневых узлов."""
    roots: list[dict] = []
    stack: list[tuple[int, dict]] = []

    for raw in lines:
        item = _parse_line(raw)
        if item is None:
            continue

        # Снимаем со стека всё, что не является строгим предком
        while stack and stack[-1][0] >= item['indent']:
            stack.pop()

        if stack:
            stack[-1][1]['children'].append(item)
        else:
            roots.append(item)

        stack.append((item['indent'], item))

    return roots


def _collect_leaves(roots: list[dict]) -> list[dict]:
    """Обходит дерево и возвращает только листья вместе с breadcrumbs."""
    leaves: list[dict] = []

    def walk(node: dict, crumbs: list[str]) -> None:
        if node['children']:
            for child in node['children']:
                walk(child, crumbs + [node['question']])
        else:
            leaves.append({
                'question': node['question'],
                'anchor': node['anchor'],
                'breadcrumbs': crumbs,
            })

    for root in roots:
        walk(root, [])

    return leaves


def parse_list(path: str) -> list[dict]:
    """
    Разбирает list.md, строит дерево по отступам и возвращает только
    листья — каждый в виде:
        {
          'question':    'Сервер не отвечает, ...',
          'anchor':      '#%D0%A1...',
          'breadcrumbs': ['Вопросы админам 2.0', 'Железячные вопросы'],
        }
    """
    p = Path(path)
    if not p.exists():
        logger.warning("list.md не найден по пути %s", path)
        return []

    with p.open(encoding='utf-8') as f:
        roots = _build_tree(f)

    return _collect_leaves(roots)


def get_all_questions() -> list[dict]:
    return parse_list(current_app.config['LIST_MD_PATH'])


def build_answer_url(anchor: str) -> str:
    base = current_app.config['ANSWER_BASE_URL'].rstrip('/')
    return f"{base}{anchor}"