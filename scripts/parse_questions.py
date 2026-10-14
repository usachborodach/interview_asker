"""Standalone-вариант проверки парсинга list.md (без Flask)."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.questions import parse_list  # noqa: E402


def main() -> None:
    path = os.getenv('LIST_MD_PATH', 'list.md')
    questions = parse_list(path)
    print(f"Файл: {path}")
    print(f"Найдено вопросов (листьев): {len(questions)}")
    for i, q in enumerate(questions[:10], 1):
        crumbs = " › ".join(q['breadcrumbs'])
        prefix = f"[{crumbs}] " if crumbs else ""
        print(f"  {i}. {prefix}{q['question'][:80]}")


if __name__ == '__main__':
    main()