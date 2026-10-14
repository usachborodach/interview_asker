import click
from flask import Flask

from .questions import get_all_questions


def register_cli(app: Flask) -> None:
    @app.cli.command('list-questions')
    def list_questions():
        """Выводит количество вопросов, найденных в list.md."""
        qs = get_all_questions()
        click.echo(f"Найдено вопросов: {len(qs)}")

    @app.cli.command('show-question')
    @click.argument('index', type=int)
    def show_question(index: int):
        """Показать вопрос по индексу (для отладки)."""
        qs = get_all_questions()
        if not qs:
            click.echo("Список пуст")
            return
        if index < 0 or index >= len(qs):
            click.echo(f"Индекс вне диапазона 0..{len(qs) - 1}")
            return
        item = qs[index]
        click.echo(f"Q: {item['question']}")
        click.echo(f"A: {item['anchor']}")import click
from flask import Flask

from .questions import get_all_questions


def register_cli(app: Flask) -> None:
    @app.cli.command('list-questions')
    def list_questions():
        """Выводит количество вопросов, найденных в list.md."""
        qs = get_all_questions()
        click.echo(f"Найдено вопросов: {len(qs)}")

    @app.cli.command('show-question')
    @click.argument('index', type=int)
    def show_question(index: int):
        """Показать вопрос по индексу (для отладки)."""
        qs = get_all_questions()
        if not qs:
            click.echo("Список пуст")
            return
        if index < 0 or index >= len(qs):
            click.echo(f"Индекс вне диапазона 0..{len(qs) - 1}")
            return
        item = qs[index]
        click.echo(f"Q: {item['question']}")
        click.echo(f"A: {item['anchor']}")