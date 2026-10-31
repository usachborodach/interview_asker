from flask import current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from pymongo import MongoClient

limiter = Limiter(key_func=get_remote_address)


def init_extensions(app) -> None:
    limiter.init_app(app)
    # MongoClient ленивый — коннект установится при первом запросе.
    # Таймауты маленькие, чтобы при недоступной Mongo не висеть 30 секунд.
    app.extensions['mongo_client'] = MongoClient(
        app.config['MONGO_URI'],
        serverSelectionTimeoutMS=2000,
        connectTimeoutMS=2000,
    )


def get_collection():
    """Возвращает коллекцию с вопросами из текущего приложения."""
    client = current_app.extensions['mongo_client']
    return client[current_app.config['MONGO_DB']][current_app.config['MONGO_COLLECTION']]