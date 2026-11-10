import click
from flask import Flask

from .questions import (
    list_sections,
    get_section_items,
    get_random_section_question,
)


def register_cli(app: Flask) -> None:
    @app.cli.command('list-sections')
    def list_sections_cli():
        """Перечислить все .md-файлы в QANDA_DIR с числом вопросов."""
        for s in list_sections():
            click.echo(f"  {s}.md: {len(get_section_items(s))} вопросов")

    @app.cli.command('count-questions')
    @click.argument('section', default='main')
    def count_questions_cli(section: str):
        """Сколько вопросов в SECTION.md (по умолчанию main)."""
        click.echo(f"{section}.md: {len(get_section_items(section))} вопросов")

    @app.cli.command('show-random')
    @click.argument('section', default='main')
    def show_random(section: str):
        """Случайный вопрос из SECTION.md (по умолчанию main)."""
        item = get_random_section_question(section)
        if item is None:
            click.echo(f"{section}.md пуст или не найден")
            return
        click.echo(f"Q: {item['question']}")
        click.echo(f"A: {item['answer'][:500]}")