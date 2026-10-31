import click
from flask import Flask

from .questions import count_questions, get_random_question


def register_cli(app: Flask) -> None:
    @app.cli.command('count-questions')
    def count_questions_cli():
        """Выводит количество вопросов в MongoDB."""
        click.echo(f"Найдено вопросов: {count_questions()}")

    @app.cli.command('show-random')
    def show_random():
        """Показать случайный вопрос и ответ (для отладки)."""
        item = get_random_question()
        if item is None:
            click.echo("Список пуст")
            return
        click.echo(f"Q: {item['question']}")
        click.echo(f"A: {item['answer']}")