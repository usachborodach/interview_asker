"""Вопросы из локальной директории с markdown-файлами.

Формат одного файла (например, base.md):

    # Вопрос 1
    Ответ 1 (markdown)
    
    ---
    
    # Вопрос 2
    Ответ 2 (markdown)

Разделитель — `\\n\\n---\\n\\n`. Вопрос — первая строка блока,
начинающаяся с `#`. Остальное — ответ.
"""
import logging
import random
import re
from pathlib import Path

from flask import current_app

logger = logging.getLogger(__name__)

_SEPARATOR = '\n\n---\n\n'
_SECTION_RE = re.compile(r'^[A-Za-z0-9_-]+$')

# Кеш на процесс: путь -> (mtime, size, items)
_cache: dict[str, tuple[float, int, list[dict]]] = {}


def _qanda_dir() -> Path:
    return Path(current_app.config['QANDA_DIR'])


def _parse_content(content: str) -> list[dict]:
    items = []
    for raw in content.split(_SEPARATOR):
        raw = raw.strip()
        if not raw:
            continue
        lines = raw.split('\n', 1)
        first = lines[0].strip()
        if not first.startswith('#'):
            continue
        question = first.lstrip('#').strip()
        answer = lines[1].strip() if len(lines) > 1 else ''
        items.append({'question': question, 'answer': answer})
    return items


def _valid_section(section: str) -> bool:
    return bool(section) and bool(_SECTION_RE.match(section))


def _load_file(path: Path) -> list[dict]:
    try:
        st = path.stat()
    except OSError:
        logger.warning("Cannot stat %s", path)
        return []

    key = str(path)
    cached = _cache.get(key)
    if cached and cached[0] == st.st_mtime and cached[1] == st.st_size:
        return cached[2]

    try:
        content = path.read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError):
        logger.exception("Cannot read %s", path)
        return []

    items = _parse_content(content)
    _cache[key] = (st.st_mtime, st.st_size, items)
    logger.info("Loaded %d questions from %s", len(items), path)
    return items


def list_sections() -> list[str]:
    d = _qanda_dir()
    if not d.exists():
        logger.warning("QANDA_DIR not found: %s", d)
        return []
    return sorted(p.stem for p in d.glob('*.md') if p.is_file())


def section_exists(section: str) -> bool:
    if not _valid_section(section):
        return False
    return (_qanda_dir() / f'{section}.md').is_file()


def get_section_items(section: str) -> list[dict]:
    if not _valid_section(section):
        return []
    path = _qanda_dir() / f'{section}.md'
    if not path.is_file():
        return []
    return _load_file(path)


def get_main_items() -> list[dict]:
    return get_section_items('main')


def count_main_questions() -> int:
    return len(get_main_items())


def get_random_section_question(section: str) -> dict | None:
    items = get_section_items(section)
    if not items:
        return None
    return random.choice(items)


def get_random_main_question() -> dict | None:
    return get_random_section_question('main')