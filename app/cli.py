import click
from flask import Flask

from .questions import count_questions, get_random_question
from .ml_questions import count_ml_questions, get_random_ml_question


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

    @app.cli.command('count-ml-questions')
    def count_ml_questions_cli():
        """Количество вопросов в ML/RAG справочнике."""
        click.echo(f"Найдено вопросов (ML): {count_ml_questions()}")

    @app.cli.command('show-ml-random')
    def show_ml_random():
        """Случайный вопрос из ML/RAG справочника."""
        item = get_random_ml_question()
        if item is None:
            click.echo("Справочник пуст или недоступен")
            return
        click.echo(f"[{item['category']}] Q: {item['question']}")
        click.echo(f"A: {item['answer'][:500]}")